---
name: douyin-account-experiment
description: "The user handed Claude their Douyin account (started 2026-10-27) to see what Claude would do with it; content direction is Claude's call"
metadata:
  node_type: memory
  type: project
  originSessionId: 78b6a1cb-aaf8-4fc3-8db8-5d18e7e2d652
  modified: 2026-10-27T06:45:07.659Z
---

On 2026-10-27 the user handed their Douyin (抖音) account to Claude as an experiment: "纯粹想看看你会用账号做什么，会做成什么样". The folder /Users/decheng.huang/Documents/dy is the workspace for it.

Arrangement the user set:
- They scan the QR login and enter any CAPTCHA themselves; Claude operates through the built-in browser on creator.douyin.com.
- Every video is labeled AI-generated (AI生成); the account is honest that an AI runs it ("我们就是真实").
- Content direction and iteration are fully Claude's call. The user may offer theme suggestions as reference only.
- Comments can inform iteration, but the user warned they are not necessarily professionally reliable — weigh them, don't follow them.

Claude still asks for a yes before each publish, comment reply, or DM, because the account carries the user's identity.

Help on offer: the user has a Grok bot with its own virtual computer that can scroll the Douyin app and download videos for reference. On 2026-10-27 Claude chose not to use it yet — first-hand browsing of douyin.com first, then bring Grok specific needs (e.g. the mobile recommendation feed, or downloading a batch of videos to dissect pacing).

**Why:** the user's goal is curiosity about Claude's own choices, not growth targets — so decisions should reflect genuine judgment rather than chasing whatever the comments ask for.
**Entry point for every new session or after compaction:** read 现状.md in the dy folder first (current state, open items, file map), then 运转方案.md for the operating model (one session per video; files are the memory; warn the user to start a new session past ~50% context).

**How to apply:** propose directions with reasons, keep an operating log in the dy folder for continuity across sessions (思考日志.md), and see [[douyin-comment-reply-limit]] for risk-control rules. Before choosing any topic, re-read 平台规律.md in the dy folder (distilled platform rules, 2026-10-27) — especially that topics an AI thinks of first have usually already been made by other Claude-made videos, so search Douyin for the topic before building anything.

**One execution conversation (2026-10-29):** the user set that a project is pushed forward in only one execution conversation; their messages and reference videos go straight to that session, and the earlier coordinating session stops relaying work. Don't split production across parallel sessions; use subagents inside the one session instead.
