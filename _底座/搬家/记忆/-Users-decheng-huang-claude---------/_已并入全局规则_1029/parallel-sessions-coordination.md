---
name: parallel-sessions-coordination
description: Dk wants parallel sessions when work doesn't conflict (e.g. push work + improve work mode); coordinate via 对话分工.md and file locks, re-read rules entry before acting
metadata:
  type: feedback
---

Dk 10/15: 「一个项目同一时间只留一个对话做事不是很好，这样效率低，有时候有些事是可以同时做不冲突的，比如推进工作和改善工作模式两件事」. Rejected my proposal of one session per project.

**Why:** On 10/14 two sessions both improved the work mode (one diagnosed and reconciled rules, mine built the standards system) and a third pushed deliverables; they edited the same rule files and deck generator, so rules contradicted each other and I kept handing Dk questions another session had already settled.

**How to apply:** In 弹窗标签推送系统, register scope in `过程记录/对话分工.md`; before each action re-read 标准体系 第〇节 and the checklist progress (files may have changed — if the harness says a file changed on disk, read it before acting); lock shared files with `python3 _scripts/pl_锁.py 加 <文件> <谁>` and release after. Split sessions by non-overlapping work, not one-at-a-time. Related: [[what-goes-to-dk-and-boss]].
