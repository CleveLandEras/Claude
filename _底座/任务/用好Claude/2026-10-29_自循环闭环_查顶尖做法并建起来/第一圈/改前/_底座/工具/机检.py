#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机检：成品交给验收官之前，先用程序判三样（确定的判断，不靠 Claude 的眼睛）。

  ① 断链：md 链接、html 的 href/src 指向本地文件的，相对成品所在目录解析，文件不存在算断；
          http(s) 链接不联网，只记数。
  ② 禁用词：给主管的稿禁「待核实」「替你定」「待验收」「资料没写或未确认」「可推翻」；
            给 Dk 的稿不禁这些，但禁「资料没写或未确认」。
  ③ 交付链接：传 --任务文件 时，读它「## 交付」一节里「成品：」后的路径，
              必须是以 / 或 ~ 开头的完整路径且文件存在（裸文件名判不过）。

用法：
  python3 机检.py <成品路径> --读者 主管|Dk [--任务文件 <路径>]
  python3 机检.py --自测

支持 .md .html .txt；.pptx 等其他格式只做③。
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

BANNED = {
    "主管": ["待核实", "替你定", "待验收", "资料没写或未确认", "可推翻"],
    "Dk": ["资料没写或未确认"],
}
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
    paths = []
    for l in section:
        for m in re.finditer(r"成品[:：]", l):
            paths.append(parse_after_label(l[m.end():]))
    if not paths:
        return [("不过", "交付链接：「## 交付」一节里没有「成品：」")]
    out = []
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

def run_checks(product, reader, task_file=None):
    results = []
    prod = Path(product).expanduser() if product else None
    ext = prod.suffix.lower() if prod else ""
    if prod is None or not prod.is_file():
        results.append(("不过", "成品文件不存在或不是文件：%s" % product))
    elif ext in TEXT_EXT:
        text = read_text(prod)
        results += check_links(text, ext, prod.resolve().parent)
        results += check_banned(text, reader, ext)
    else:
        results.append(("提示", "%s 格式只做交付链接这一项，断链和禁用词没查" % (ext or "无后缀")))
    if task_file:
        results += check_delivery(task_file)
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
        nolabel_task = task("任务_无成品行.md", "验收官：通过")

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
        ]
        for name, want_ok, product, reader, tf, must in cases:
            results = run_checks(str(product), reader, str(tf) if tf else None)
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
        description="成品交验收官之前先跑：断链、禁用词、交付链接。",
    )
    ap.add_argument("product", nargs="?", metavar="成品路径", help="成品文件（.md .html .txt；.pptx 只查交付链接）")
    ap.add_argument("--读者", dest="reader", type=lambda s: "Dk" if s.lower() == "dk" else s,
                    choices=["主管", "Dk"], help="给谁看的稿，决定用哪套禁用词")
    ap.add_argument("--任务文件", dest="task", help="传了才查交付链接")
    ap.add_argument("--自测", dest="selftest", action="store_true", help="跑内置正反例")
    args = ap.parse_args()
    if args.selftest:
        return self_test()
    if not args.product or not args.reader:
        ap.error("需要 <成品路径> 和 --读者 主管|Dk（或用 --自测）")
    return print_results(run_checks(args.product, args.reader, args.task))


if __name__ == "__main__":
    sys.exit(main())
