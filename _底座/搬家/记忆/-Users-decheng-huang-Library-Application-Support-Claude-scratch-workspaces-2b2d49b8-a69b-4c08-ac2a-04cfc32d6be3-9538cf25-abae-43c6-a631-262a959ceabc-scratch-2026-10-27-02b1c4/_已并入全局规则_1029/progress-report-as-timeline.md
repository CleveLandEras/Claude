---
name: progress-report-as-timeline
description: "When Dk asks how progress went (进度如何) after unattended/supervised work, give a timestamped timeline of concrete actions, not a per-task status table"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d4a835dc-087c-4485-bc20-68c09a50c5cf
  modified: 2026-10-29T01:26:03.203Z
---

When Dk asks "昨天进度如何" or similar about work done while away, answer with a timeline: each row is a time + which task + the concrete thing done (file written, check run, message sent). Don't give a per-task "where it stands / what you need to do" table.

**Why:** On 2026-10-29 I answered with a per-task status table and Dk said "我想看的不是这些 是什么时间具体做了什么".

**How to apply:** Use file modification times (`find -newermt` + `stat`) and the supervisor transcript's send timestamps as the time source; they're verifiable. Mark anything taken only from a session's own report. Put idle gaps up front. Related: [[supervision-dont-let-sessions-idle]].
