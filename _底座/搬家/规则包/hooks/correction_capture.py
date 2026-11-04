#!/usr/bin/env python3
"""UserPromptSubmit 钩子（新版，10/29）：每轮附上全局规则全文和本对话定位；Dk 的消息像是在纠正时，再加一段固定做法。

替换 ~/.claude/hooks/correction_capture.py 后生效（不改 settings.json）。方案：
~/claude/_底座/想清楚/2026-10-29_第二级怎么组织与Dk不在时谁推进.md 4g（Dk 选 A）。

附加内容分四部分：
  1.【全局规则】每轮从磁盘读 ~/.claude/CLAUDE.md 全文，照原样附上，以此为准。
  2.【本对话定位】按钩子输入的 session_id，到 ~/claude/_底座/对话定位.md 找本对话那一条。
  3.【纠正提示】与旧版一字不差，仍只在 Dk 本人的消息命中时附（跳过列表之后）。
  4. 压缩记录：会话记录里出现新的压缩记号时，在 ~/claude/_底座/压缩记录.md 记一行（不附进上下文）。
第 1、2、4 部分在跳过列表之前，所以定时叫醒、子代理回报、别的对话发来的消息也会带上。

长度把关：附加内容超过 9,500 个字符（官方单段上限 10,000）时，第一行写截断提示，
优先保住截断提示、定位和纠正提示，全局规则截短，并记一条日志。
只加提示、不拦消息；任何异常都记进日志后放行。
"""
import datetime
import json
import os
import re
import sys
import traceback

LOG = os.path.expanduser("~/claude/_底座/纠正记录.md")

# 下面几个路径可用环境变量改，只供测试用；正式运行用默认值。
RULES = os.environ.get("DK_HOOK_RULES", os.path.expanduser("~/.claude/CLAUDE.md"))
POSITION = os.environ.get("DK_HOOK_POSITION", os.path.expanduser("~/claude/_底座/对话定位.md"))
COMPACT_LOG = os.environ.get("DK_HOOK_COMPACT_LOG", os.path.expanduser("~/claude/_底座/压缩记录.md"))
STATE_DIR = os.environ.get("DK_HOOK_STATE_DIR", os.path.expanduser("~/claude/_底座/设置/钩子状态"))
HOOK_LOG = os.environ.get("DK_HOOK_LOG", os.path.expanduser("~/claude/_底座/设置/钩子日志.txt"))

LIMIT = 9500
TRUNC_LINE = "附加内容超长，已截断，先用 Read 读 `~/.claude/CLAUDE.md` 全文和定位表本对话一条（`~/claude/_底座/对话定位.md`）。"

# ---- 以下三段与旧版 correction_capture.py 一字不差 ----
# 纠正、不满的常见说法。宁可多报：提示里写了「不是纠正就忽略」。
SIGNAL = re.compile(
    r"不对|不是这样|不是这个|错了|搞错|又(犯|错|出现|没|是这样)|怎么还|还是没|还是不|"
    r"说过|我说的是|我要的是|不是我要的|没看到|看不懂|读不懂|什么鬼|粗糙|简陋|"
    r"不符合|偏了|跑偏|没按|你没(有)?(看|想|做|查|按|理解)|为什么(没|不|又|还|要)|"
    r"重新(做|来|改|写)|退回|不通过|太(长|乱|挤|粗糙|啰嗦|密)|漏了|缺了|"
    r"不要再|别再|不要让我|别让我|这不(行|对|是)|有问题|问题在于|到底|失败了|"
    r"没(有)?(参考|参照|对齐|考虑|思考|想清楚|做到|写清|说清)"
)
# 自动任务、会话交接、通知不是 Dk 本人在纠正。
SKIP_PREFIX = ("<scheduled-task", "Background (from the session", "Task (from the session",
               "<task-notification", "<cross-session-message", "This session is being continued",
               "Another Claude session sent a message", "<agent-message")

CONTEXT = f"""【纠正提示｜钩子自动附加，可能误判；不是纠正就忽略本段】
这条消息看起来在纠正已经做过的事。按这个顺序处理：
1. 先用一句话复述 Dk 指出的问题，以及它背后的标准（按它针对的情况理解，不外推、不收紧）。
2. 按同一标准把整份稿件查完、一次改完，不只改被点到的那几处；改完重跑分角色验收再交。
3. 在 {LOG} 表格末尾追加一行：日期｜项目｜稿件｜Dk 原话（照抄）｜问题一句话｜现有规则有没有写到（写到了填文件名）。
不要为这一次纠正新建记忆或规则文件；规则由「整理纠正」统一合并。Dk 明说「以后都／每次／所有」时，在纠正记录这一行末尾标「通用」，由「整理纠正」写进对应的规则文件；记忆不放规则。"""
# ---- 以上三段与旧版一字不差 ----

RULES_HEAD = "【全局规则｜钩子每轮从磁盘读 ~/.claude/CLAUDE.md 全文附上；和对话开场加载的版本不同时，以此为准】"
POSITION_HEAD = "【本对话定位｜钩子按会话 ID 从 ~/claude/_底座/对话定位.md 附上】"
COMPACT_MARKS = (b'"compact_boundary"', b'"isCompactSummary":true')


def ulen(s):
    """按 UTF-16 码元数长度，和应用计上限的口径一致（中文每字 1）。"""
    return len(s.encode("utf-16-le")) // 2


def ucut(s, n):
    out, used = [], 0
    for ch in s:
        w = ulen(ch)
        if used + w > n:
            break
        out.append(ch)
        used += w
    return "".join(out)


def log(session, event, detail=""):
    try:
        os.makedirs(os.path.dirname(HOOK_LOG), exist_ok=True)
        with open(HOOK_LOG, "a", encoding="utf-8") as f:
            stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("%s｜%s｜%s｜%s\n" % (stamp, session or "-", event, detail.replace("\n", " ⏎ ")))
    except Exception:
        pass


def read_rules(session):
    try:
        with open(RULES, encoding="utf-8") as f:
            return RULES_HEAD + "\n" + f.read().strip()
    except Exception as e:
        log(session, "全局规则读取失败", repr(e))
        return RULES_HEAD + "\n（读取失败：%s。先用 Read 读 ~/.claude/CLAUDE.md 全文。）" % type(e).__name__


def find_position(session):
    """返回 (定位段落, 对话标题)。找不到返回未登记提示和空标题。"""
    not_found = ("本对话还没登记定位（会话 ID %s）。先按标题判断自己是哪个项目的主对话或分发，"
                 "登记进 `_底座/对话定位.md`；拿不准就问 Dk。") % (session or "未知")
    try:
        with open(POSITION, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        log(session, "定位表读取失败", repr(e))
        return POSITION_HEAD + "\n" + not_found, ""
    if session:
        for block in re.split(r"(?m)^(?=## )", text):
            head = block.split("\n", 1)[0]
            if head.startswith("## ") and session in head:
                title = head[3:].split(" ／ ", 1)[0].strip()
                return POSITION_HEAD + "\n" + block.strip(), title
    return POSITION_HEAD + "\n" + not_found, ""


def record_compaction(data, session, title):
    """会话记录里出现新的压缩记号时，在压缩记录里记一行。第一次见到某个会话只记基线。"""
    path = data.get("transcript_path") or ""
    if not session or not path or not os.path.isfile(path):
        return
    os.makedirs(STATE_DIR, exist_ok=True)
    state_file = os.path.join(STATE_DIR, re.sub(r"[^\w.-]", "_", session) + ".json")
    state = {}
    if os.path.isfile(state_file):
        try:
            with open(state_file, encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = {}
    size = os.path.getsize(path)
    first = "offset" not in state or size < state.get("offset", 0)
    start = 0 if first else state["offset"]
    if size == start and not first:
        return
    new = 0
    end = start
    with open(path, "rb") as f:
        f.seek(start)
        buf = f.read(size - start)
    cut = buf.rfind(b"\n")
    if cut >= 0:
        buf = buf[: cut + 1]
        end = start + cut + 1
    else:
        buf = b""  # 只有半行：这轮不计，等下一轮读到完整的行
    n_boundary = buf.count(COMPACT_MARKS[0])
    new = n_boundary if n_boundary else buf.count(COMPACT_MARKS[1])
    total = state.get("count", 0) + new
    if not first and new:
        head = not os.path.isfile(COMPACT_LOG)
        with open(COMPACT_LOG, "a", encoding="utf-8") as f:
            if head:
                f.write("# 压缩记录\n\n钩子自动记，每次压缩一行；11/12 对照 `纠正记录.md` 定换对话的压缩次数上限。"
                        "压缩记号按 Claude Code 会话记录的 compact_boundary／isCompactSummary 认（推断，试跑时核）。\n\n"
                        "| 时间 | 对话 | 会话 ID | 本对话累计第几次 |\n|---|---|---|---|\n")
            stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            for i in range(new):
                f.write("| %s | %s | %s | %d |\n" % (stamp, title or "未登记", session, state.get("count", 0) + i + 1))
    state = {"offset": end, "count": total if not first else new}
    tmp = state_file + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f)
    os.replace(tmp, state_file)


def is_correction(prompt):
    prompt = (prompt or "").strip()
    if not prompt or prompt.startswith(SKIP_PREFIX):
        return False
    # 只看 Dk 自己打的字：去掉系统注入的块。
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", prompt, flags=re.S)
    text = re.sub(r"<pasted_content[^>]*>.*?</pasted_content[^>]*>", "", text, flags=re.S)
    return bool(SIGNAL.search(text[:3000]))


def assemble(rules, position, correction, session):
    parts = [rules, position] + ([CONTEXT] if correction else [])
    full = "\n\n".join(parts)
    if ulen(full) <= LIMIT:
        return full
    # 超长：截断提示 + 定位 + 纠正提示优先，规则截短。
    keep = "\n\n".join([TRUNC_LINE, position] + ([CONTEXT] if correction else []))
    room = LIMIT - ulen(keep) - ulen("\n\n") * 2 - ulen("……（已截断）")
    if room > 0:
        out = "\n\n".join([TRUNC_LINE, ucut(rules, room) + "……（已截断）", position] + ([CONTEXT] if correction else []))
    else:
        out = ucut(keep, LIMIT)
    log(session, "附加内容超长已截断", "原长 %d，截后 %d" % (ulen(full), ulen(out)))
    return out


def main():
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        log("", "钩子输入不是 JSON", repr(e))
        return
    session = str(data.get("session_id") or "")
    rules = read_rules(session)
    position, title = find_position(session)
    try:
        record_compaction(data, session, title)
    except Exception:
        log(session, "压缩记录出错", traceback.format_exc(limit=3))
    correction = False
    try:
        correction = is_correction(data.get("prompt"))
    except Exception:
        log(session, "纠正判断出错", traceback.format_exc(limit=3))
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": assemble(rules, position, correction, session),
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("", "钩子出错", traceback.format_exc(limit=5))
    sys.exit(0)
