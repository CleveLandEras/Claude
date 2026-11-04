---
name: logs-newest-first-real-clock
description: Dk wants running logs newest-first, and timestamps must come from the real clock, never estimated by an agent
metadata:
  type: feedback
---

Long running logs that Dk reads (e.g. 进展日志.md) go newest-first. Any timestamp an unattended agent writes must come from the machine clock (a script like `_scripts/now.py` / `log_<role>.py`), not the model's guess.

**Why:** 2026-10-08 Dk: "进展日志这么长肯定应该新的放上面。我疑惑的是为什么有未来的时间？" — scheduled agents can only run whitelisted python scripts, can't see the clock, and wrote times 10–50 minutes in the future.

**How to apply:** When designing agent workflows, give them a clock script and a write-log script that stamps time and inserts at the top; never ask an agent to type a time itself. Related: [[popup-project-02-rejected-capability-reframe]].
