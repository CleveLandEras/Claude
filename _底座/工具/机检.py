#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机检：成品交给分角色验收之前，先用程序判这几样（确定的判断，不靠 Claude 的眼睛）。

  ① 断链：md 链接、html 的 href/src 指向本地文件的，相对成品所在目录解析，文件不存在算断；
          http(s) 链接不联网，只记数。
  ② 禁用词：给主管的稿禁「待核实」「替你定」「待验收」「资料没写或未确认」「可推翻」；
            给 Dk 的稿不禁这些，但禁「资料没写或未确认」。
            两种读者都禁自称可交、把检查推回读者的话：「可直接交」「可原样转发」「可直接转发」
            「可上线」「有问题你指出来」「需要的话我再改」（10/31 从验收清单原第 15 条移来）。
  ③ 交付链接：传 --任务文件 时，读它「## 交付」一节里「成品：」后的路径，
              必须是以 / 或 ~ 开头的完整路径且文件存在（裸文件名判不过）；
              「成品：」后面写了几个文件、其中有同一内容的几种格式或版本（同时有 .html 和 .pdf，
              或一个文件名是另一个的开头，如 X.pptx 与 X_带备注.pptx）判不过；几件不同的交付物只提示
              （一件成品只交一个文件，纠正记录 10/29「怎么这么多输出文件」「这三个不对，应该给的是一个md文件」）。
  ④ 脑图：文件名含「脑图」或「导图」的 .md（或传 --脑图），每个节点（标题行、列表项）
          不能带改动标记【新增】【调整】这类（读成改动记录），不能是句子或说明（含「。」「；」、
          两个以上「，」，或以「为什么：」「参照：」「做法：」这类开头；「轮流，每次换下一条」这种带一个限定的选项不算）；
          某个节点下面超过 6 个子节点只提示、不判不过（纠正记录 10/29 脑图节点写成句子、功能框架写成更新记录）。
  ⑤ 思考页：传 --任务文件 且任务文件写着「级别：中」或「级别：大」时，旁边同名文件夹里
            要有名字含「思考页」的文件（纠正记录 10/29「未经思考直接开始了工作」）。

用法：
  python3 机检.py <成品路径> --读者 主管|Dk [--任务文件 <路径>] [--脑图]
  python3 机检.py --自测

支持 .md .html .txt；.pptx 等其他格式只做③⑤（pptx 里的禁用词没查，靠评审看）。
输出：一行一项「过／不过：原因」（另有「提示：…」只提醒、不判不过），
最后一行「机检：过」或「机检：不过（n 项）」，不过时退出码 1。
"""
import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

BANNED_ALL = ["可直接交", "可原样转发", "可直接转发", "可上线", "有问题你指出来", "需要的话我再改"]
BANNED = {
    "主管": ["待核实", "替你定", "待验收", "资料没写或未确认", "可推翻"] + BANNED_ALL,
    "Dk": ["资料没写或未确认"] + BANNED_ALL,
}
CHANGE_MARK = re.compile(r"【\s*(新增|调整|修改|删除|改动|新)\s*】")
SENTENCE_MARK = re.compile(r"[。；]")
EXPLAIN_LABEL = re.compile(r"^\s*(?:\*\*)?(为什么|理由|原因|参照|参考|代价|做法|说明|备注|注|依据|目的)\s*(?:\*\*)?[:：]")
MAX_CHILDREN = 6
PATH_TOKEN = re.compile(
    r"`([^`]+)`|\]\(([^)]+)\)|((?:~|/)[^\s、，,；;（）()`<>「」\"]+)"
    r"|([^\s、，,；;（）()`<>「」\"/]+\.(?:md|html?|pdf|pptx?|xlsx?|docx?|png|jpe?g|xmind|txt|csv))",
    re.I,
)
TEXT_EXT = {".md", ".html", ".htm", ".txt"}
HTML_EXT = {".html", ".htm"}
SCHEME = re.compile(r"^([A-Za-z][A-Za-z0-9+.\-]*):")


# ---------- 小工具 ----------

def read_text(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")


def keep_newlines(m):
    """被删掉的片段只留下换行，这样后面的行号不变。"""
    return re.sub(r"[^\n]", "", m.group(0))


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def fmt_lines(lines, limit=5):
    uniq = sorted(set(lines))
    shown = "、".join(str(n) for n in uniq[:limit])
    more = "等" if len(uniq) > limit else ""
    return "第 " + shown + more + " 行"


def classify(target):
    """返回 (类别, 路径)。类别：http／local／skip。"""
    t = target.strip()
    if not t or t.startswith("#"):
        return "skip", ""
    if t.startswith("//"):
        return "http", t
    if re.search(r"\{\{|\$\{|<%", t):
        return "skip", ""
    m = SCHEME.match(t)
    if m:
        s = m.group(1).lower()
        if s in ("http", "https"):
            return "http", t
        if s == "file":
            return "local", unquote(re.sub(r"^file://(localhost)?", "", t, flags=re.I))
        return "skip", ""
    return "local", t


def local_exists(path_str, base_dir):
    p = path_str.split("#")[0].split("?")[0]
    if not p:
        return True
    for cand in (p, unquote(p)):
        c = os.path.expanduser(cand)
        try:
            full = Path(c) if os.path.isabs(c) else base_dir / c
            if full.exists():
                return True
        except OSError:
            continue
    return False


# ---------- ① 断链 ----------

def collect_md_links(text):
    """返回 [(行号, 目标)]。围栏代码块和行内代码里的不算。"""
    t = re.sub(r"```.*?```|~~~.*?~~~", keep_newlines, text, flags=re.S)
    t = re.sub(r"`[^`\n]*`", "", t)
    out = []
    for m in re.finditer(r"\]\(([^)\n]*)\)", t):
        s = m.group(1).strip()
        if s.startswith("<"):
            e = s.find(">")
            s = s[1:e] if e > 0 else s[1:]
        else:
            mt = re.match(r"^(.*?)\s+(?:\"[^\"]*\"|'[^']*')$", s)
            s = (mt.group(1) if mt else s).strip()
        out.append((lineno(t, m.start()), s))
    for m in re.finditer(r"^[ ]{0,3}\[[^\]\n]+\]:[ \t]*(<[^>\n]*>|\S+)", t, flags=re.M):
        s = m.group(1).strip("<>")
        # 引用式定义只认像网址或路径的，免得把「[注]: 说明」当链接
        if "/" in s or re.search(r"\.\w{1,5}$", s):
            out.append((lineno(t, m.start()), s))
    for m in re.finditer(r"<(https?://[^>\s]+)>", t):
        out.append((lineno(t, m.start()), m.group(1)))
    return out


def collect_html_links(text):
    t = re.sub(r"<!--.*?-->", keep_newlines, text, flags=re.S)
    # 脚本和样式的内容不查，但它们开头标签上的 src／href 要查
    t = re.sub(
        r"(<(script|style)\b[^>]*>)(.*?)(</\2\s*>)",
        lambda m: m.group(1) + re.sub(r"[^\n]", "", m.group(3)) + m.group(4),
        t,
        flags=re.S | re.I,
    )
    out = []
    for tag in re.finditer(r"<[A-Za-z][^>]*>", t):
        for m in re.finditer(
            r"""\b(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", tag.group(0), flags=re.I
        ):
            val = next(g for g in m.groups() if g is not None)
            out.append((lineno(t, tag.start() + m.start()), val))
    return out


def check_links(text, ext, base_dir):
    links = collect_html_links(text) if ext in HTML_EXT else collect_md_links(text)
    local_total, http_total, broken = 0, 0, []
    for ln, target in links:
        kind, path = classify(target)
        if kind == "http":
            http_total += 1
        elif kind == "local":
            if path.split("#")[0].split("?")[0] == "":
                continue
            local_total += 1
            if not local_exists(path, base_dir):
                broken.append((ln, target))
    if broken:
        shown = "；".join("第 %d 行「%s」" % (ln, t) for ln, t in broken[:8])
        more = "……" if len(broken) > 8 else ""
        return [("不过", "断链 %d 个（本地文件不存在）：%s%s" % (len(broken), shown, more))]
    return [("过", "链接：本地 %d 个都存在；http 链接 %d 个不联网检查（只记数）" % (local_total, http_total))]


# ---------- ② 禁用词 ----------

def html_visible(text):
    t = re.sub(r"<!--.*?-->", keep_newlines, text, flags=re.S)
    t = re.sub(r"<(script|style)\b.*?</\1\s*>", keep_newlines, t, flags=re.S | re.I)
    return re.sub(r"<[^>]*>", keep_newlines, t, flags=re.S)


def check_banned(text, reader, ext):
    vis = html_visible(text) if ext in HTML_EXT else text
    words = BANNED[reader]
    out = []
    for w in words:
        hits = [lineno(vis, m.start()) for m in re.finditer(re.escape(w), vis)]
        if hits:
            out.append(("不过", "禁用词「%s」出现 %d 次（%s）；给%s的稿不能有" % (w, len(hits), fmt_lines(hits), reader)))
    if not out:
        out.append(("过", "禁用词：给%s的稿，「%s」都没出现" % (reader, "」「".join(words))))
    return out


# ---------- ④ 脑图 ----------

def is_mindmap(prod, force=False):
    return force or (prod.suffix.lower() == ".md" and ("脑图" in prod.name or "导图" in prod.name))


def mindmap_nodes(text):
    """返回 [(行号, 层级, 节点文字)]。标题按 # 个数定层，列表项接在最近的标题下按缩进定层。围栏代码块不算。"""
    t = re.sub(r"```.*?```|~~~.*?~~~", keep_newlines, text, flags=re.S)
    nodes, head_level = [], -1
    for i, line in enumerate(t.splitlines(), 1):
        m = re.match(r"^(#{1,6})\s+(.*\S)", line)
        if m:
            head_level = len(m.group(1)) - 1
            nodes.append((i, head_level, m.group(2)))
            continue
        m = re.match(r"^([ \t]*)(?:[-*+]|\d+[.)])\s+(.*\S)", line)
        if m:
            indent = len(m.group(1).replace("\t", "  ")) // 2
            nodes.append((i, head_level + 1 + indent, m.group(2)))
    return nodes


def check_mindmap(text):
    nodes = mindmap_nodes(text)
    if not nodes:
        return [("提示", "脑图：没认出节点（只认标题行和列表项）")]
    out = []
    marks = [ln for ln, _lv, s in nodes if CHANGE_MARK.search(s)]
    plain = lambda s: re.sub(r"`[^`]*`|\*\*|__", "", s)
    def is_sentence(s):
        s = plain(s)
        return bool(SENTENCE_MARK.search(s) or s.count("，") >= 2 or EXPLAIN_LABEL.match(s))
    sents = [ln for ln, _lv, s in nodes if is_sentence(s)]
    if marks:
        out.append(("不过", "脑图：%d 个节点带改动标记（如【新增】【调整】，读起来是改动记录，不是功能框架）（%s）" % (len(marks), fmt_lines(marks))))
    if sents:
        out.append(("不过", "脑图：%d 个节点是句子或说明（含「。」「；」、两个以上「，」，或以「为什么：」「参照：」「做法：」这类开头），节点要写成字段名、选项名或默认值这样的短语，理由不进图（%s）" % (len(sents), fmt_lines(sents))))
    # 每个节点的子节点数
    stack, kids, over = [], {}, []
    for ln, lv, _s in nodes:
        while stack and stack[-1][1] >= lv:
            stack.pop()
        if stack:
            kids[stack[-1][0]] = kids.get(stack[-1][0], 0) + 1
        stack.append((ln, lv))
    over = [ln for ln, k in kids.items() if k > MAX_CHILDREN]
    if over:
        out.append(("提示", "脑图：%d 个节点下面超过 %d 个子节点（%s），看看能不能再分一层；只提示、不判不过" % (len(over), MAX_CHILDREN, fmt_lines(over))))
    if not marks and not sents:
        out.insert(0, ("过", "脑图：%d 个节点都是短语，没有改动标记" % len(nodes)))
    return out


# ---------- ⑤ 思考页 ----------

def check_thinking_page(task_file):
    tp = Path(task_file).expanduser()
    if not tp.is_file():
        return []
    m = re.search(r"^[-*\s]*\**级别\**\s*[:：]\s*\**\s*(小|中|大)", read_text(tp), flags=re.M)
    if not m:
        return [("提示", "任务文件没写「级别：」，思考页没查")]
    if m.group(1) == "小":
        return [("过", "思考页：小任务不要求")]
    folder = tp.with_suffix("")
    found = sorted(p.name for p in folder.glob("*思考页*")) if folder.is_dir() else []
    if found:
        return [("过", "思考页：%s 任务有 %s" % (m.group(1), "、".join(found[:3])))]
    return [("不过", "思考页：%s任务旁边的同名文件夹 %s 里没有思考页（中、大任务要先有审过的思考页再动手）" % (m.group(1), folder))]


# ---------- ③ 交付链接 ----------

def parse_after_label(rest):
    rest = rest.lstrip()
    m = re.match(r"`([^`]*)`", rest)
    if m:
        return m.group(1).strip()
    m = re.match(r"\[[^\]]*\]\(([^)]*)\)", rest)
    if m:
        return m.group(1).strip()
    m = re.match(r"[^\s、，,；;（）()`<>「」\"]+", rest)
    return m.group(0) if m else ""


def check_delivery(task_file):
    tp = Path(task_file).expanduser()
    if not tp.is_file():
        return [("不过", "交付链接：任务文件不存在：%s" % task_file)]
    lines = read_text(tp).splitlines()
    in_section, section = False, []
    for l in lines:
        if re.match(r"^##\s*交付", l):
            in_section = True
            continue
        if in_section and re.match(r"^##\s", l):
            in_section = False
        if in_section:
            section.append(l)
    if not any(re.match(r"^##\s*交付", l) for l in lines):
        return [("不过", "交付链接：任务文件里没有「## 交付」一节")]
    paths, labels = [], 0
    for l in section:
        for m in re.finditer(r"成品[:：]", l):
            labels += 1
            rest = l[m.end():]
            # 只看「成品：」这一句（到第一个「。」「；」为止），后面的补充说明不算成品
            rest = re.split(r"[。；;]", rest, maxsplit=1)[0]
            found = []
            for t in PATH_TOKEN.finditer(rest):
                tok = next(g for g in t.groups() if g is not None).strip()
                if "/" in tok or re.search(r"\.\w{1,5}$", tok):
                    found.append(tok)
            paths += found or [parse_after_label(rest)]
    if not labels:
        return [("不过", "交付链接：「## 交付」一节里没有「成品：」")]
    out = []
    uniq = list(dict.fromkeys(p for p in paths if p))
    if len(uniq) > 1:
        names = "、".join(os.path.basename(p) for p in uniq[:5])
        exts = {Path(p).suffix.lower() for p in uniq}
        stems = [Path(p).stem for p in uniq]
        variant = any(i != j and len(a) >= 2 and b.startswith(a)
                      for i, a in enumerate(stems) for j, b in enumerate(stems))
        if (exts & {".html", ".htm"} and ".pdf" in exts) or variant:
            out.append(("不过", "交付链接：「成品：」后面写了 %d 个文件（%s），其中有同一内容的几种格式或几个版本；一件成品只交一个文件，其他格式和过程件放子文件夹、不列给读者" % (len(uniq), names)))
        else:
            out.append(("提示", "交付链接：「成品：」后面写了 %d 个文件（%s）；几件不同的交付物可以，同一内容的不同格式只交一个" % (len(uniq), names)))
    for p in paths:
        if not p:
            out.append(("不过", "交付链接：「成品：」后面没有写路径"))
        elif not (p.startswith("/") or p.startswith("~")):
            out.append(("不过", "交付链接「%s」不是以 / 或 ~ 开头的完整路径（裸文件名或相对路径打不开）" % p))
        else:
            full = Path(os.path.expanduser(p))
            if not full.exists():
                out.append(("不过", "交付链接指向的文件不存在：%s" % p))
            else:
                out.append(("过", "交付链接：%s 存在%s" % (p, "（是文件夹）" if full.is_dir() else "")))
    return out


# ---------- 总入口 ----------

def run_checks(product, reader, task_file=None, mindmap=False):
    results = []
    prod = Path(product).expanduser() if product else None
    ext = prod.suffix.lower() if prod else ""
    if prod is None or not prod.is_file():
        results.append(("不过", "成品文件不存在或不是文件：%s" % product))
    elif ext in TEXT_EXT:
        text = read_text(prod)
        results += check_links(text, ext, prod.resolve().parent)
        results += check_banned(text, reader, ext)
        if is_mindmap(prod, mindmap):
            results += check_mindmap(text)
    else:
        results.append(("提示", "%s 格式只做交付链接这一项，断链和禁用词没查" % (ext or "无后缀")))
    if task_file:
        results += check_delivery(task_file)
        results += check_thinking_page(task_file)
    else:
        results.append(("提示", "没传 --任务文件，交付链接没查"))
    return results


def print_results(results):
    for s, msg in results:
        print("%s：%s" % (s, msg))
    n = sum(1 for s, _ in results if s == "不过")
    print("机检：过" if n == 0 else "机检：不过（%d 项）" % n)
    return 0 if n == 0 else 1


# ---------- 自测 ----------

def self_test():
    ok_all = True
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "存在的文件.md").write_text("x", encoding="utf-8")
        (d / "pic.png").write_text("x", encoding="utf-8")
        (d / "设计类任务做法_确认版.md").write_text("成品", encoding="utf-8")

        def w(name, content):
            p = d / name
            p.write_text(content, encoding="utf-8")
            return p

        def task(name, delivery_body):
            return w(name, "# 任务\n\n状态：进行中\n\n## 验收结论\n成品：假的.md\n\n## 交付\n%s\n\n## 交接记录\n无\n" % delivery_body)

        good_task = task("任务_好.md", "成品：%s" % (d / "设计类任务做法_确认版.md"))
        bare_task = task("任务_裸名.md", "成品：设计类任务做法_确认版.md")
        bare_bt_task = task("任务_裸名反引号.md", "- 成品：`设计类任务做法_确认版.md`（一个文件）")
        miss_task = task("任务_不存在.md", "成品：%s" % (d / "没有这个文件.md"))
        nosec_task = w("任务_无交付.md", "# 任务\n\n状态：进行中\n")
        nolabel_task = task("任务_无成品行.md", "验收：分角色验收通过")
        two_task = task("任务_两个成品.md", "成品：%s\n成品：%s" % (d / "设计类任务做法_确认版.md", d / "设计类任务做法_确认版_带备注.md"))
        diff_task = task("任务_两件不同.md", "成品：%s、%s" % (d / "设计类任务做法_确认版.md", d / "存在的文件.md"))
        three_task = task("任务_一行三个.md", "- 成品：功能框架_脑图.html、功能框架_思维导图.pdf、转给主管_说明草稿.md")
        mid_no = w("任务_中无思考页.md", "# 任务\n\n状态：进行中\n级别：中（一份交付物）\n\n## 交付\n成品：%s\n" % (d / "设计类任务做法_确认版.md"))
        mid_yes = w("任务_中有思考页.md", "# 任务\n\n状态：进行中\n- **级别**：大\n\n## 交付\n成品：%s\n" % (d / "设计类任务做法_确认版.md"))
        (d / "任务_中有思考页").mkdir()
        (d / "任务_中有思考页" / "思考页.md").write_text("问题、证据、做法", encoding="utf-8")

        cases = [
            # (名称, 期望判过, 成品, 读者, 任务文件, 结果里必须出现的字)
            ("好链接", True,
             w("好链接.md", "见[文件](存在的文件.md)和![图](pic.png)，还有[官网](https://example.com)。\n"),
             "主管", None, "本地 2 个都存在"),
            ("断链", False,
             w("断链.md", "见[文件](存在的文件.md)和[没有的](不存在.md)。\n"),
             "主管", None, "断链 1 个"),
            ("链接带锚点和标题也认", True,
             w("锚点.md", "[a](存在的文件.md#第二节) [b](<存在的文件.md> \"标题\") [c](#本页)\n"),
             "Dk", None, "本地 2 个都存在"),
            ("代码块里的断链不算", True,
             w("代码块.md", "正文\n\n```\n[x](不存在.md)\n```\n\n行内 `[y](也不存在.md)`\n"),
             "主管", None, "本地 0 个"),
            ("http 链接不联网只记数", True,
             w("http.md", "[a](https://example.com/a) [b](http://example.com/b)\n"),
             "主管", None, "http 链接 2 个"),
            ("html 好 href 和 src", True,
             w("好.html", "<html><body><a href=\"存在的文件.md\">a</a><img src='pic.png'><script>var a={href:x}</script></body></html>\n"),
             "主管", None, "本地 2 个都存在"),
            ("html 断 href", False,
             w("断.html", "<html><body>\n<a href=\"不存在.html\">a</a>\n</body></html>\n"),
             "主管", None, "第 2 行"),
            ("主管稿含「待核实」", False,
             w("主管_待核实.md", "这一项待核实。\n"),
             "主管", None, "「待核实」"),
            ("主管稿含「可推翻」", False,
             w("主管_可推翻.md", "按推荐做，可推翻。\n"),
             "主管", None, "「可推翻」"),
            ("主管稿没有禁用词", True,
             w("主管_干净.md", "结论先行。依据是行业做法。\n"),
             "主管", None, "都没出现"),
            ("Dk 稿含「待验收」", True,
             w("Dk_待验收.md", "状态：待验收。已替你定，可推翻。\n"),
             "Dk", None, "都没出现"),
            ("Dk 稿含「资料没写或未确认」", False,
             w("Dk_资料没写.md", "这一项资料没写或未确认。\n"),
             "Dk", None, "「资料没写或未确认」"),
            ("html 可见文字含禁用词", False,
             w("词.html", "<p>待核实</p>\n"),
             "主管", None, "「待核实」"),
            ("html 标签属性里的词不算", True,
             w("词2.html", "<p title=\"待核实\">好</p>\n"),
             "主管", None, "都没出现"),
            ("交付写裸文件名", False,
             w("成品1.md", "内容\n"),
             "Dk", bare_task, "完整路径"),
            ("交付写裸文件名（反引号包着）", False,
             w("成品1b.md", "内容\n"),
             "Dk", bare_bt_task, "完整路径"),
            ("交付写完整路径且存在", True,
             w("成品2.md", "内容\n"),
             "Dk", good_task, "存在"),
            ("交付写完整路径但文件不存在", False,
             w("成品3.md", "内容\n"),
             "Dk", miss_task, "不存在"),
            ("任务文件没有「## 交付」", False,
             w("成品4.md", "内容\n"),
             "Dk", nosec_task, "没有「## 交付」"),
            ("交付里没有「成品：」", False,
             w("成品5.md", "内容\n"),
             "Dk", nolabel_task, "没有「成品：」"),
            (".pptx 只做交付链接（路径对）", True,
             w("稿.pptx", "不是真的 pptx"),
             "主管", good_task, "存在"),
            (".pptx 只做交付链接（裸文件名）", False,
             w("稿2.pptx", "不是真的 pptx"),
             "主管", bare_task, "完整路径"),
            ("Dk 稿含「有问题你指出来」", False,
             w("Dk_推回.md", "已改完，有问题你指出来。\n"),
             "Dk", None, "「有问题你指出来」"),
            ("主管稿含「可原样转发」", False,
             w("主管_可转发.md", "这一页可原样转发。\n"),
             "主管", None, "「可原样转发」"),
            ("脑图带改动标记", False,
             w("功能框架_脑图.md", "# 后台\n- 弹窗\n  - 按人群配置 【新增】\n  - 次数上限\n"),
             "主管", None, "改动标记"),
            ("脑图节点是句子", False,
             w("讲解_脑图.md", "# 后台\n- 弹窗\n  - 新建弹窗规则\n    - 为什么：发对人是前提，运营要先知道发给谁\n"),
             "主管", None, "是句子"),
            ("脑图都是短语（带冒号和顿号也算短语）", True,
             w("干净_脑图.md", "# 后台\n- 游戏外推送\n  - 新建推播\n    - 名称（必填）\n    - 类别\n      - 服务通知：补偿、维护、账号安全\n      - 默认：营销\n"),
             "主管", None, "都是短语"),
            ("脑图一层 7 个子节点只提示", True,
             w("宽_脑图.md", "# 后台\n- 弹窗\n" + "".join("  - 字段%d\n" % k for k in range(7))),
             "主管", None, "超过 6 个子节点"),
            ("文件名不是脑图，句子不查", True,
             w("说明.md", "第一句，第二句。\n- 列表里也有句子，不查。\n"),
             "主管", None, "都没出现"),
            ("--脑图 强制按脑图查", False,
             w("框架.md", "- 弹窗\n  - 说明：先弹宣传图，点图再打开\n"),
             "主管", None, "是句子", True),
            ("脑图选项带一个限定不算句子", True,
             w("选项_脑图.md", "- 轮换方式\n  - 轮流，每次换下一条\n  - 每次进大厅，含从游戏返回\n"),
             "主管", None, "都是短语"),
            ("「成品：」那句之后的补充说明不算成品", True,
             w("成品6c.md", "内容\n"),
             "Dk", task("任务_补充说明.md", "- 成品：`%s`（13 页）。同一结论的另一种形式：同目录 `别的_脑图.md`。" % (d / "设计类任务做法_确认版.md")),
             "存在"),
            ("交付写了两件不同的交付物只提示", True,
             w("成品6b.md", "内容\n"),
             "Dk", diff_task, "几件不同的交付物可以"),
            ("交付写了两个成品", False,
             w("成品6.md", "内容\n"),
             "Dk", two_task, "几个版本"),
            ("交付一行写了三个文件", False,
             w("成品7.md", "内容\n"),
             "Dk", three_task, "3 个文件"),
            ("中任务没有思考页", False,
             w("成品8.md", "内容\n"),
             "Dk", mid_no, "没有思考页"),
            ("大任务有思考页", True,
             w("成品9.md", "内容\n"),
             "Dk", mid_yes, "思考页.md"),
        ]
        for case in cases:
            name, want_ok, product, reader, tf, must = case[:6]
            force = case[6] if len(case) > 6 else False
            results = run_checks(str(product), reader, str(tf) if tf else None, force)
            got_ok = all(s != "不过" for s, _ in results)
            blob = "\n".join("%s：%s" % r for r in results)
            right = (got_ok == want_ok) and (must in blob)
            if right:
                print("过：%s（机检判「%s」，符合预期）" % (name, "过" if got_ok else "不过"))
            else:
                ok_all = False
                print("不过：%s（期望判「%s」且含「%s」；实际判「%s」）\n    %s"
                      % (name, "过" if want_ok else "不过", must, "过" if got_ok else "不过", blob.replace("\n", "\n    ")))
    print("自测：全过" if ok_all else "自测：不过")
    return 0 if ok_all else 1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(
        prog="机检.py",
        description="成品交分角色验收之前先跑：断链、禁用词、交付链接（只一个）、脑图节点、中大任务的思考页。",
    )
    ap.add_argument("product", nargs="?", metavar="成品路径", help="成品文件（.md .html .txt；.pptx 只查交付链接）")
    ap.add_argument("--读者", dest="reader", type=lambda s: "Dk" if s.lower() == "dk" else s,
                    choices=["主管", "Dk"], help="给谁看的稿，决定用哪套禁用词")
    ap.add_argument("--任务文件", dest="task", help="传了才查交付链接")
    ap.add_argument("--脑图", dest="mindmap", action="store_true", help="文件名不含「脑图」「导图」时，强制按脑图查")
    ap.add_argument("--自测", dest="selftest", action="store_true", help="跑内置正反例")
    args = ap.parse_args()
    if args.selftest:
        return self_test()
    if not args.product or not args.reader:
        ap.error("需要 <成品路径> 和 --读者 主管|Dk（或用 --自测）")
    return print_results(run_checks(args.product, args.reader, args.task, args.mindmap))


if __name__ == "__main__":
    sys.exit(main())
