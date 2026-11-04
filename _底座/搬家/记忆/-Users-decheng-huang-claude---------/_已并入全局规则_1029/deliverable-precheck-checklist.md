---
name: deliverable-precheck-checklist
description: Case 10/19: clearly written principles (structure/boundaries) weren't followed because task briefs and checks omitted them; every deliverable brief now attaches 规则与交接/交付前必查.md and reports pass/fail per item
metadata:
  type: feedback
---

Case (10/19): the push-backend requirement-review version had unclear structure. The rule was explicit in 写作标准 (Part 2 group 1, the row 「边界看得见，先交代边界再讲内容」; two rows merged 10/19). Dk: 「你没看见这条还是原则没写清楚？找到未遵循原则的原因并解决掉这个问题」. Root cause: my brief didn't mention it; to save tokens I told the agent to read only the wording sections; pre-delivery checks covered only wording. Which principles got applied depended on what my brief happened to mention.

**Why:** agents (and I) only execute what the brief names and the checks test; a 270-line standard isn't read in full every time.

**How to apply:** attach `规则与交接/交付前必查.md` to every deliverable brief; require a per-item pass/fail in the hand-back; before sending to Dk, check item 1 (a context-free reader can say from the first screen how many parts/pages and what each covers, and from any page which part and which page they are on; if a sidebar TOC or contents page already shows the boundaries, don't add a second block). Don't narrow an agent's reading to one aspect when fixing another. Related: [[writing-and-layout]], [[size-deliverables-to-reader-time]].

Follow-up 10/19: Dk asked who is responsible for such a loophole (me — my brief caused it and I passed it). Then: 「我不是说必须要你全读一遍……但你需要确保没有这样的漏洞发生」. Cost-aware fix = checklist item 7: `_scripts/an_读者要读的.py` extracts first screen, titles + first line under each, page headers, ending (~1–2K chars); a Sonnet context-free reader audits it against 判例 types; I read the extract myself before sending. Briefs state the desired effect, not sentences to insert.

Item 8 added 10/19 (判例 48): for each function ask who does it in reality, how often, how long it takes to build, and compare with the manual way; one-off work that RD must hand-do (e.g. migrating hard-coded content into the backend) or that ops can do by hand in minutes is not made a backend function. Judge per case, no hard line. Project location: the rule is in 写作标准 Part 2 group 6 「每个功能先问……」; the check is in 规则与交接/交付前必查.md (entry table: 标准体系 第〇节).
