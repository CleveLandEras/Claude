#!/usr/bin/env python3
"""Stop 钩子：交付闸门。

这一轮 Claude 在最后的回复里把一份「本对话本轮自己改过」的文件交出去，
却没登记在已验收的任务文件里，就拦一次（只认登记，不管评审叫什么）。
只拦一次（stop_hook_active 时放行）；任何异常都放行。
回复末尾写「草稿，未交付」可以跳过。

10/29 改（规则体系分层整理·必答⑧，验收第 1、2 次后补）：
- 「本轮改过」只认本对话自己的记录：本轮 Write/Edit/MultiEdit/NotebookEdit 写过的文件；
  或它的修改时间在本轮内，且本轮有一条会写文件的 Bash 命令（cat、head、ls、grep 这类只读命令不算）
  ——命令里出现了它的文件名或所在文件夹（全路径、~/ 路径、相对 ~/claude/ 或相对命令 cwd 的写法），
  或命令跑的是 `_scripts/` 下的脚本、而它就在命令的 cwd 里（输出路径写死在脚本里的出稿脚本）。
  别的对话、子代理改的，只在回复里提到或只读看过的，不拦（原来只按修改时间判，会误拦「产出汇报」转报别人的成品）。
- `/_底座/任务/` 下的文件（任务文件、思考页、同名过程文件夹）和名字以「思考页」开头的不算交付物。
- 放行只认这样的任务文件（`_底座/任务/` 下）：「状态：」行以「待验收」或「已完成」开头；
  「## 交付」一节里用完整路径登记了这个成品（参照、依据行里的不算；不按文件名比）；
  「## 验收结论」一节扣掉模板自带的行后还有内容；任务文件的修改时间晚于成品最后一次修改（验收后又改就不放行）。
- 拦截提示分角色：第一级不自己派评审；第二级和执行方按分角色验收的做法跑完、登记再交。

11/02 改（分角色验收上场、旧验收官退场）：
- 去掉「本轮调用过验收官就放行」的捷径，只认上面的登记：新做法要第二级判过了才改「待验收」，
  调用过一次评审不等于过。拦截提示里不写评审叫什么，也不写任何通过条件。
- EXCLUDE_PARTS 加 `/_底座/分角色验收/`、`/_底座/流程抽查/`（放的是规则和记录，不是交付物）。
- 模板「验收结论」一节换了格式；旧模板那一节的行做成常量 OLD_TEMPLATE_LINES，和现行模板的行一起扣掉。
"""
import json
import os
import re
import shlex
import sys
import urllib.parse
from datetime import datetime

EXT = (".html", ".pptx", ".docx", ".xlsx", ".pdf", ".md")
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
SHELL_TOOLS = ("Bash",)
HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(HOME, "claude")
TASK_DIR = os.path.join(WORKSPACE, "_底座", "任务")
TEMPLATE = os.path.join(WORKSPACE, "_底座", "模板", "对齐卡.md")
# 工作文件、规则、记忆、临时文件、任务文件与过程文件不算交付物。
EXCLUDE_PARTS = ("/.claude/", "/memory/", "/过程记录/", "/规则与交接/", "/_底座/考试/", "/_底座/任务/",
                 "/_底座/分角色验收/", "/_底座/流程抽查/",
                 "scratchpad", "/tmp/", "/private/var/", "/_scripts/")
EXCLUDE_NAMES = ("先看这里", "README", "MEMORY", "CLAUDE", "文件目录", "纠正记录", "验收清单", "全局规则_快照", "对齐卡",
                 "思考页")
DRAFT_MARK = re.compile(r"草稿[，,、\s]*未交付")
STATUS_LINE = re.compile(r"^[\s>*-]*\**状态\**[：:]\s*\**\s*(.*)$", re.M)
STATUS_OK = ("待验收", "已完成")
SECTION = re.compile(r"^##(?!#)\s*(.+?)\s*$", re.M)
REF_LABEL = re.compile(r"参照|参考|依据|出处")
FULL_PATH = re.compile(r"(?:/|~/)[^\s`'\"<>()（）\[\]]+")
TRAIL = "，。；、：,.;:！!？?」』"
MTIME_SLACK = 5  # 秒；和原来判「本轮内」用的余量一样
# 只读命令：一条 Bash 里每一段都是这些、又没有写到文件的重定向，就不算会写文件。其余命令（python3、bash、cp、mv、rsync…）都算。
READ_ONLY_CMDS = {"cat", "head", "tail", "ls", "grep", "egrep", "rg", "wc", "stat", "open", "file", "less", "more",
                  "diff", "cmp", "shasum", "md5", "sha256sum", "du", "df", "pwd", "cd", "echo", "printf", "which",
                  "type", "date", "tree", "sort", "uniq", "cut", "awk", "jq", "od", "hexdump", "readlink", "realpath",
                  "basename", "dirname", "test", "[", "true", "false", "find", "sed", "git", "mdls", "plutil"}
GIT_READ_ONLY = {"status", "log", "diff", "show", "ls-files", "rev-parse", "blame", "grep", "remote", "config"}
SCRIPTS_MARK = "_scripts/"
TAIL_BYTES = 16 * 1024 * 1024
TASK_MAX_BYTES = 2 * 1024 * 1024

# 模板「验收结论」一节 11/02 换成分角色验收的格式；按旧模板建、还没填的任务文件里的旧占位行照样扣掉。
# 以 # 开头的行、表格分隔行本来就跳过，不列。
OLD_TEMPLATE_LINES = {
    "执行自检（一行一条完成标准，不超过 15 行）",
    "| 完成标准 | 落在哪 | 过／不过 |",
    "- 成品：`…`",
    "- 读者｜可用时间：…（照抄对齐卡）",
    "- 我们是谁与产品性质：…（照抄对齐卡）",
    "- 程序判：<钩子或脚本名> 通过／不通过（不通过写哪一条）",
    "结论：通过／不通过（一句话说最大的问题）",
    "必判两项",
    "- 可用时间内读到重点：能／不能｜读到了哪些必答｜重点实际在哪",
    "- 符合作者角色与产品性质：符合／不符合｜位置｜原文「…」",
    "会被退回的问题（按严重度排，最多 10 条）",
    "1. [方向|事实|缺内容|结构|措辞|版面] 位置｜原文「…」｜问题｜依据｜建议怎么改",
    "清单结果：…",
    "没法判断的：…",
    "| 意见第几条 | 改了／没改 | 没改的理由（只有引出 Dk 原话才能不改） |",
    "- 结果：通过／退回（Dk 原话「…」）",
    "- Dk 发现、这次验收结论没指出的问题：…（每条加一道考题进 `~/claude/_底座/考试/题目.md`）",
    "- 通过的：记一份合格样本（收进 `考试/题目.md`，标「Dk 判通过」）",
}

PATH_PATTERNS = [
    re.compile(r"\]\(([^)\s]+)\)"),                                   # markdown 链接
    re.compile(r"`([^`\n]+?\.(?:html|pptx|docx|xlsx|pdf|md))(?::\d+)?`"),  # 反引号里的路径
    re.compile(r"(/Users/[^\s`'\"<>()（）]+?\.(?:html|pptx|docx|xlsx|pdf|md))"),
]


def parse_ts(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def is_human(entry):
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isSidechain"):
        return False
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        if any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
            return False
        text = "".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    else:
        return False
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S).strip()
    return bool(text) and not text.startswith(("<task-notification", "Another Claude session sent a message",
                                                "<agent-message", "<cross-session-message"))


def read_tail(path):
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        if size > TAIL_BYTES:
            fh.seek(size - TAIL_BYTES)
            fh.readline()
        raw = fh.read().decode("utf-8", errors="ignore")
    entries = []
    for line in raw.splitlines():
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries


def norm(p, cwd):
    p = os.path.expanduser(p)
    if not os.path.isabs(p):
        p = os.path.join(cwd or "", p)
    return os.path.normpath(p)


def is_excluded(p):
    if any(x in p for x in EXCLUDE_PARTS):
        return True
    return os.path.basename(p).startswith(EXCLUDE_NAMES)


def candidate_files(message, cwd):
    found = []
    for pat in PATH_PATTERNS:
        for m in pat.finditer(message):
            p = urllib.parse.unquote(m.group(1)).split("#")[0]
            p = re.sub(r":\d+$", "", p)
            if not p.lower().endswith(EXT) or p.startswith(("http://", "https://")):
                continue
            p = norm(p, cwd)
            if is_excluded(p):
                continue
            if p not in found:
                found.append(p)
    return found


def own_tool_uses(turn, cwd):
    """本对话本轮的工具调用 (名字, 输入, 是否报错, 当时的 cwd)。子代理的记录不在主 transcript 里，带 isSidechain 的也跳过。"""
    failed = set()
    for e in turn:
        content = e.get("message", {}).get("content") if e.get("type") == "user" else None
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                    failed.add(c.get("tool_use_id"))
    uses = []
    for e in turn:
        if e.get("type") != "assistant" or e.get("isSidechain"):
            continue
        for c in e.get("message", {}).get("content", []) or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                uses.append((c.get("name"), c.get("input") or {}, c.get("id") in failed, e.get("cwd") or cwd))
    return uses


def tilde(p):
    return "~" + p[len(HOME):] if p.startswith(HOME + os.sep) else None


HEREDOC = re.compile(r"(<<-?\s*(['\"]?)(\w+)\2)([^\n]*)\n.*?\n\3[ \t]*(?=\n|$)", re.S)
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|\n]")
FILE_REDIRECT = re.compile(r"(?<![<>&\-=])\d?>>?(?!&)\s*(?!/dev/null)[^\s&|;]")


def first_word(seg):
    try:
        words = shlex.split(seg, posix=True)
    except ValueError:
        words = seg.split()
    while words and (re.match(r"^\w+=", words[0]) or words[0] in ("sudo", "time", "nohup", "env", "command", "exec")):
        words = words[1:]
    return (os.path.basename(words[0]), words[1:]) if words else ("", [])


def writes_files(cmd):
    """这条 Bash 会不会写文件：有写到文件的重定向、sed -i，或有一段不是只读命令。"""
    body = HEREDOC.sub(r"\1\4", cmd)  # here-doc 的正文不算命令
    if FILE_REDIRECT.search(body) or re.search(r"\b(sed|perl)\s+(-\w+\s+)*-i", body):
        return True
    for seg in SEGMENT_SPLIT.split(body):
        word, args = first_word(seg.strip())
        if not word:
            continue
        if word not in READ_ONLY_CMDS:
            return True
        if word == "find" and any(a in ("-delete", "-exec", "-execdir") for a in args):
            return True
        if word == "git" and args and args[0] not in GIT_READ_ONLY:
            return True
    return False


def effective_cwd(cmd, cwd):
    """命令开头是 `cd X &&` 或 `cd X;` 时，按 X 算 cwd。"""
    m = re.match(r"\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)\s*(?:&&|;)", cmd)
    return norm(m.group(1).strip("\"'"), cwd) if m else cwd


def changed_by_me(p, uses, cwd, turn_start):
    """p 是不是本对话本轮改的：写入工具写过它；或它本轮被改过，且本轮有会写文件的 Bash 提到它（含相对 cwd 的写法），
    或跑了 `_scripts/` 下的脚本而它在命令的 cwd 里。"""
    for name, inp, failed, ucwd in uses:
        if name in WRITE_TOOLS and not failed:
            fp = inp.get("file_path") or inp.get("notebook_path")
            if fp and norm(fp, ucwd) == p:
                return True
    try:
        if os.path.getmtime(p) < turn_start - MTIME_SLACK:
            return False
    except OSError:
        return False
    d = os.path.dirname(p)
    base = [os.path.basename(p), d, tilde(d)]
    if d.startswith(WORKSPACE + os.sep):
        base.append(d[len(WORKSPACE) + 1:])
    for name, inp, _failed, ucwd in uses:
        if name not in SHELL_TOOLS:
            continue
        cmd = inp.get("command") or ""
        if not writes_files(cmd):
            continue
        ecwd = effective_cwd(cmd, ucwd)
        marks = list(base)
        for c in {ucwd, ecwd}:
            if c and os.path.isabs(c):
                marks += [os.path.relpath(p, c), os.path.relpath(d, c)]
        if any(m and m.strip("./") and m in cmd for m in marks):  # 只剩 . 或 .. 的相对写法不算提到
            return True
        if SCRIPTS_MARK in cmd and any(c and p.startswith(c.rstrip(os.sep) + os.sep) for c in (ucwd, ecwd)):
            return True
    return False


def sections(text):
    """{二级标题: 正文}；标题按开头的词认，如「验收结论（第二级填…）」记作以「验收结论」开头。"""
    out = []
    ms = list(SECTION.finditer(text))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append((m.group(1), text[m.end():end]))
    return out


def section(text, name):
    for title, body in sections(text):
        if title == name or title.startswith((name + "（", name + "(", name + " ")):
            return body
    return None


def template_lines():
    try:
        body = section(open(TEMPLATE, encoding="utf-8").read(), "验收结论") or ""
    except Exception:
        body = ""
    return {l.strip() for l in body.splitlines() if l.strip()} | OLD_TEMPLATE_LINES


def verdict_filled(body, tmpl):
    if body is None:
        return False
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    for l in body.splitlines():
        s = l.strip()
        if not s or s.startswith("#") or re.fullmatch(r"[|\-:\s]+", s) or s in tmpl:
            continue
        if re.fullmatch(r"[（(].*[)）]", s) or "…" in s:
            continue  # 括号里的填写说明、没填的占位
        return True
    return False


def registered_paths(body):
    """「## 交付」一节里用完整路径（/ 或 ~/ 开头）写的文件；参照、依据这类行跳过。"""
    paths = set()
    for line in (body or "").splitlines():
        label = re.split(r"[：:]", line, 1)[0] if re.search(r"[：:]", line) else ""
        if REF_LABEL.search(label):
            continue
        for m in FULL_PATH.finditer(line):
            p = urllib.parse.unquote(m.group(0)).rstrip(TRAIL)
            if p.startswith(("/", "~/")) and len(p) > 2:
                paths.add(os.path.normpath(os.path.expanduser(p)))
    return paths


def approved_tasks():
    """[(任务文件修改时间, 登记的成品完整路径集合)]，只收状态待验收／已完成、验收结论已填的任务文件。"""
    out = []
    if not os.path.isdir(TASK_DIR):
        return out
    tmpl = template_lines()
    for root, _dirs, files in os.walk(TASK_DIR):
        for name in files:
            if not name.endswith(".md"):
                continue
            fp = os.path.join(root, name)
            try:
                if os.path.getsize(fp) > TASK_MAX_BYTES:
                    continue
                text = open(fp, encoding="utf-8", errors="ignore").read()
                mtime = os.path.getmtime(fp)
            except Exception:
                continue
            m = STATUS_LINE.search("\n".join(text.splitlines()[:20]))  # 状态行在文件开头
            if not m or not m.group(1).strip().startswith(STATUS_OK):
                continue
            if not verdict_filled(section(text, "验收结论"), tmpl):
                continue
            paths = registered_paths(section(text, "交付"))
            if paths:
                out.append((mtime, paths))
    return out


def main():
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    message = data.get("last_assistant_message") or ""
    if not message or DRAFT_MARK.search(message):
        return
    transcript = data.get("transcript_path")
    if not transcript or not os.path.exists(transcript):
        return
    cwd = data.get("cwd") or ""

    entries = read_tail(transcript)
    start = 0
    for i, e in enumerate(entries):
        if is_human(e):
            start = i
    turn = entries[start:]
    turn_start = parse_ts(turn[0].get("timestamp", "")) if turn else None
    if turn_start is None:
        return

    uses = own_tool_uses(turn, cwd)
    if not any(n in WRITE_TOOLS + SHELL_TOOLS for n, _i, _f, _c in uses):
        return
    changed = [p for p in candidate_files(message, cwd)
               if os.path.exists(p) and changed_by_me(p, uses, cwd, turn_start)]
    if not changed:
        return

    tasks = approved_tasks()
    changed = [p for p in changed
               if not any(p in paths and mtime > os.path.getmtime(p) for mtime, paths in tasks)]
    if not changed:
        return  # 都已登记在验收过、验收后没再改的任务文件里

    names = "、".join(os.path.basename(p) for p in changed[:5])
    reason = (
        f"交付闸门：这一轮你改过并要交出去的文件（{names}）还没以完整路径登记在这样的任务文件「## 交付」里："
        "状态「待验收」或「已完成」、「## 验收结论」已填、登记后成品没再改。按你的角色处理："
        "【第一级】不自己派评审，把成品写进 `~/claude/_底座/任务/` 下对应的任务文件交第二级。"
        "【第二级和执行方】按 `~/claude/_底座/分角色验收/做法.md` 跑分角色验收，"
        "结论写进「验收结论」、成品登记进「交付」、状态改「待验收」再交。"
        "只是中间稿、先交给 Dk 看的，在回复末尾写「草稿，未交付」，并写明这一版验过没有、最大问题是什么。"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
