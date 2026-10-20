---
name: token-and-scheduled-task-cost
description: "Control token use (10/15): one agent per task, grep not whole-file reads, cheaper model for mechanical work, no optional extra rounds; a pause file doesn't stop scheduled agents — disable the tasks themselves (merged 10/16 from control-token-consumption + pause-means-disable-scheduled-tasks)"
metadata:
  type: feedback
---

Project rule source: 标准体系 第四点五节 (10/15 起控制 token; replaces 10/14 「这个星期先不用收紧token」). Main-context discipline stays in [[main-context-orchestrate-only]] — that is about the main context, not about spawning more agents.

**Case 10/15 (推送后台原型措辞):** six wording agents, six readers and several whole-file agents (each re-reading the 4,300-line prototype and 2,500-line doc) burned ~4.3M tokens in a few hours. Dk: 「你需要控制token消耗了，这速度太快就到限制了。」 Dk's account has usage limits; fan-out multiplies big-file reading per agent.
How to apply (my defaults): one agent per task rather than per-section splits; scope tightly (grep instead of whole-file reads, screenshot only changed pages); cheaper model for mechanical work; skip optional second rounds unless Dk asks; write short briefs myself from reports in hand.

**Case 10/10–10/12 (paused agents kept waking):** pausing with `暂停.txt` left four scheduled tasks enabled; they woke every few minutes for ~46 hours just to read the pause file and exit. Dk asked on 10/12 whether idle tokens were burned — they were (「你注意token使用和上下文」「有没有空消耗过多的token？」).
How to apply: a pause file only for brief edits; for any real pause set `enabled: false` on each scheduled task (reversible) and say so; check `list_scheduled_tasks` when wrapping up a day. Unattended runs cannot change scheduled tasks, so a task can't disable itself: bound it with a date-limited cron plus a gate script whose STOP/WAIT exits cost one call (as for `popup-tag-push-night-global`; its gate does not read `暂停.txt`).

Case 10/19: core-five design push used ~2 billion tokens in 3 days (weekly quota 8% → 75%); 97% was cache re-reads. Mechanism: cost ≈ steps × context. Edit subagents loaded slices of a 1.41M-char prototype and a 0.74M-char requirements doc, then ran 130–200 steps carrying 240K–400K context each step. Fix: grep only the 20–60 relevant lines; one page/section per edit agent, ≤ ~40 steps, then a fresh agent; batch edits via one script; defer acceptance-case/trace syncing; one reviewer; Sonnet for mechanical work; split big deliverables into per-page/per-chapter sources with a build step.

Case 10/20 (cloud session, two review-version rounds, ~191M tokens, 96% cache re-reads): main conversation 76M — woken 25 times by subagent reports (36M) and 17 times by the stop-hook commit reminder (20M), only 19M on Dk's own messages; three subagents resumed across 4+ rounds grew to 380–580K context, excess over 150K ≈ 47M. The 10/19 lesson ("≤ ~40 steps, then a fresh agent") lived only here, not in 标准体系 第四点五节, so it wasn't applied. Now in 标准体系 第四点五节 (five defaults: no cross-round resume; commit before ending each turn; fewer wake-ups — one agent per round, review+reader test merged; hand off main at half context; downscaled image checks) and 任务说明模板. Details `分析/A92_token用量_1020.md`.
