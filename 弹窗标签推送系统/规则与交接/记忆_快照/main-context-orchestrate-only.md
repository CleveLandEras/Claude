---
name: main-context-orchestrate-only
description: "Main conversation only understands, decides, checks and reports; all hands-on work (render, screenshots, image viewing, script patching, big reads) goes to subagents; hand off at 50% context"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6f9d8da7-e937-415d-967d-a549dbc125bc
  modified: 2026-10-15T06:10:50.824Z
---

Dk 10/15, after one session used 76% of its context on a single, unclear instruction (「后台设计的交付物还需要再完善，还有很多问题」): 「你这个对话上下文已经76%，马上满了，我只能新开对话，但实际上你只是运行了我的一条指令……这是当前必须着急解决的问题，因为太严重」.

Measured cause (main context ≈ 761k tokens; fixed start ≈ 77k): command output ≈ 120k, 68 image Reads ≈ 109k, my own patch code ≈ 87k — all from doing the work myself in the main conversation (rebuilding the crop pipeline, five render-and-look rounds, 1,100-line generator edits). The project rule already said 主对话定方向和核对、子任务干活; I broke it.

**Why:** everything in the main context is re-read every turn and cannot be dropped; a full context forces Dk to restart and lose continuity, which costs him more than any single deliverable.

**How to apply:**
- Main conversation does only: restate Dk's words, decide direction and trade-offs, dispatch, check results by reading short reports or result files, report to Dk.
- Never in main: Read images (delegate visual checks; at most one small montage if unavoidable), read whole large files, run commands without `| head`/`tail`, or write patches longer than ~30 lines. Generation, rendering, cropping, script edits and visual QA go to subagents; their reply ≤200 words, details in a file.
- An unclear instruction gets a quick first pass: send Dk my reading and the problem list within one round (don't wait for a reply), then do the smallest useful piece before scaling up.
- At ~50% context, write a handoff into the progress file (过程记录/进度_*.md; the live handoff is the top of 先看这里.md) and move remaining work with `hand_off_to_session`; don't let Dk hit the limit.
- The numbers here (≤200-word subagent replies, ~30-line patches, 50% context handoff) are my defaults, not Dk's rules (标准体系 第〇节, 10/16); the orchestrate-only division itself stands.

Related: [[parallel-sessions-coordination]], [[stage-progression]], [[think-before-acting-on-dk-words]].
