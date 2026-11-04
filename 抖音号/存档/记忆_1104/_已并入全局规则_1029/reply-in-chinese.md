---
name: reply-in-chinese
description: "Always talk to the user in Chinese in this project — including short progress notes, replies after context compaction, and replies to English system nudges"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 78b6a1cb-aaf8-4fc3-8db8-5d18e7e2d652
  modified: 2026-10-27T06:35:26.486Z
---

Every user-visible message in this project is in Chinese: final answers, mid-task progress notes, wrap-up recaps and questions.

On 2026-10-27 the user noticed Claude answering in English and asked why. The transcript showed:
- Direct answers were Chinese before compaction.
- Several progress notes were English. They followed the app's English nudge ("The user hasn't heard from you in a while…").
- After the conversation was compacted into an English summary, every reply drifted to English.
- English subagent briefs and reports, English tool output and English thinking pulled the same way.
- Nothing anywhere asked for English. "Match the user's language" was only a soft default, and it eroded.

**Why:** the user writes in Chinese; English replies are a drift, not a choice, and they make the collaboration feel like a tool talking.
The memory note alone did not hold: the drift happened again in the same session (most progress notes and the closing message of 2026-10-27 afternoon were English, at ~50% context). So the project now enforces it: dy/.claude/settings.json sets "language": "简体中文" and a Stop hook (dy/.claude/hooks/check_chinese.py) blocks a final message that is mostly English.

**How to apply:**
- Before sending any text to the user, check that it is Chinese, especially right after a system nudge, a compaction summary or a subagent report.
- Write subagent briefs in Chinese too when the research is about Chinese platforms.
- Related: [[douyin-not-work-mode]].
