---
name: size-deliverables-to-reader-time
description: Case 10/19: push-backend prototype (24万 readable chars) + requirements doc (60万) would take reviewers 1.5–3 days and RD 6–14 days to read by hand; Dk: 「不要再忽略现实自己写小说了，你这个应该是可以出一本书了」
metadata:
  type: feedback
---

Case (10/19): after a week of AI-driven deepening, the push-backend prototype held ~24万 readable chars and the requirements doc ~60万. The company reads everything by hand (no AI); reviewers mainly read the prototype, RD reads both; normal review prep is 1–2 hours. Estimated: reviewers 1.5–3 workdays, RD 6–14 workdays. Dk: 「精简版是肯定要的，原文根本不需要保留，因为没人会看，包括我都不会看。精简版就是正式的内容，重新瘦身，从实际出发，不要再忽略现实自己写小说了」.

**Why:** length was never checked against the readers' real reading time; every round of review/benchmarking only added text.

**How to apply:** before writing a deliverable, set a word budget from who reads it and how much time they realistically have (careful reading ~120–150 Chinese chars/min); measure with `_scripts/an_可读字数.py`; over budget → say where and why it is worth keeping (the budget is a reference, not a hard line; see the correction below). Rewrite from what the reader must do, don't trim a bloated draft. Long versions are material, archived, not maintained. Related: [[report-only-what-and-why]], [[token-and-scheduled-task-cost]].

Correction same day: I then proposed merging similar pages (SMS/FB/LINE into the push page with inline differences) to hit the budget; Dk: 「这样很难理解，不要为了压缩文字牺牲阅读体验，我们的核心目标不是单纯的压缩，而是为了更好的阅读」. The budget is a reference, not a hard line; cut only repetition, process notes, unused edge details and long sample data — never clarity. See [[writing-and-layout]]. Then: 「字数不是通过压缩来减少的，而是看看哪些内容其实没必要写，哪些才是核心内容」 — first get clear what is core and what needn't be written (a keep/drop table can help); how much to write for each piece is judged by what the reader needs (expand, one line, or partial). Word count is an outcome. When I then made it 「留下的写全，不留的整块不写」, Dk: 「这又是一个不合理的限制。你总是这样矫枉过正」 — relay Dk's principle as said; don't turn it into absolute rules. See [[think-before-acting-on-dk-words]].

Project location: 规则与交接/交付前必查.md items 5 and 6 (budget is a reference; reading experience first) and 规则与交接/推送后台_精简版任务说明.md.
