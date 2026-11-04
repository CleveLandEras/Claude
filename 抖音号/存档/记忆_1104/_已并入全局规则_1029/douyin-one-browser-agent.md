---
name: douyin-one-browser-agent
description: Only one agent may browse Douyin on the account at a time; five parallel browsing agents triggered a captcha on 2026-10-29
metadata:
  node_type: memory
  type: project
  originSessionId: 0edcdf4f-bd82-4c5f-8d27-fcd732bf2c32
  modified: 2026-10-29T03:11:26.887Z
---

On 2026-10-29 around 11:10, five subagents browsed douyin.com at the same time on the user's logged-in account (each told to "go slowly"). One hit Douyin's "验证码中间页" after about 12 page opens. Re-opening the same profile twice within seconds after a process restart may also have counted.

**Why:** per-agent pacing doesn't limit the total; five slow agents add up to one person opening dozens of pages in minutes, which looks like scraping and risks the account.
**How to apply:** at most one agent on Douyin (douyin.com or creator.douyin.com) at a time, 8–10 s between page opens (tightened 2026-10-29); queue further Douyin research instead of running it in parallel. Web research (WebSearch/WebFetch) can still run in parallel. Captchas are only for the user to solve — stop and ask. Related: [[douyin-comment-reply-limit]], [[douyin-self-direction]].
