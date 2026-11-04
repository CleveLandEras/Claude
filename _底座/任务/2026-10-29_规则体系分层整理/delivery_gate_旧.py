#!/usr/bin/env python3
"""Stop 钩子：交付闸门。

这一轮 Claude 在最后的回复里把一份本轮新改的文件交给 Dk，却没让验收官独立审过，
就拦一次，让它先审再交。只拦一次（stop_hook_active 时放行）；任何异常都放行。
回复末尾写「草稿，未交付」可以跳过。
"""
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime

REVIEWER = "验收官"
EXT = (".html", ".pptx", ".docx", ".xlsx", ".pdf", ".md")
# 工作文件、规则、记忆、临时文件不算交付物。
EXCLUDE_PARTS = ("/.claude/", "/memory/", "/过程记录/", "/规则与交接/", "/_底座/考试/",
                 "scratchpad", "/tmp/", "/private/var/", "/_scripts/")
EXCLUDE_NAMES = ("先看这里", "README", "MEMORY", "CLAUDE", "文件目录", "纠正记录", "验收清单", "全局规则_快照", "对齐卡")
DRAFT_MARK = re.compile(r"草稿[，,、\s]*未交付")
TAIL_BYTES = 16 * 1024 * 1024

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


def candidate_files(message, cwd):
    found = []
    for pat in PATH_PATTERNS:
        for m in pat.finditer(message):
            p = urllib.parse.unquote(m.group(1)).split("#")[0]
            p = re.sub(r":\d+$", "", p)
            if not p.lower().endswith(EXT) or p.startswith(("http://", "https://")):
                continue
            if not os.path.isabs(p):
                p = os.path.join(cwd or "", p)
            p = os.path.normpath(p)
            if any(x in p for x in EXCLUDE_PARTS):
                continue
            if os.path.basename(p).startswith(EXCLUDE_NAMES):
                continue
            if p not in found:
                found.append(p)
    return found


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

    for e in turn:
        if e.get("type") != "assistant":
            continue
        for c in e.get("message", {}).get("content", []) or []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in ("Agent", "Task"):
                if (c.get("input") or {}).get("subagent_type") == REVIEWER:
                    return  # 本轮已经让验收官审过

    changed = [p for p in candidate_files(message, cwd)
               if os.path.exists(p) and os.path.getmtime(p) >= turn_start - 5]
    if not changed:
        return

    names = "、".join(os.path.basename(p) for p in changed[:5])
    reason = (
        f"交付闸门：这一轮改过并要交给 Dk 的文件（{names}）还没有经过验收官独立审查。"
        f"先调用验收官（Agent 工具，subagent_type: {REVIEWER}），告诉它：文件路径、需求原文或对齐卡在哪、读者是谁；"
        "按它指出的问题改完再交，交付说明里写一句验收官的结论。"
        "如果这只是中间草稿、不交给 Dk，在回复末尾写「草稿，未交付」。"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
