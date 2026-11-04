---
name: check-sufficiency-before-done
description: "Passing checks ≠ done: before calling work ready, check goal fit and that each change's reason implies it, then walk real tasks + benchmark through the deliverable to find what's missing; stop only when the walk finds no gap, saying what was walked (merged 10/16 from check-framing-not-just-consistency + judge-sufficiency-not-just-correctness)"
metadata:
  type: feedback
---

Rule source: 工作原则乙·5 (10/16 wording). Cases:

**10/08 — goal fit and the why.** I told Dk 02/03 「可以验收」 after checking only internal correctness; Dk rejected 02 for missing the capability focus and the why. Agent review loops share the blind spot: they verify what the card asks, not whether the question is right. Before "ready": does it serve the stated goal (capability vs one-off config)? does each change have a reason that actually implies it? Only then numbers and consistency. (My inferred lesson, not a rule Dk stated. The old sentence template 「我们认为改动会让人群的指标变化」 is dropped: it invites effect metrics the popup project forbids.)

**10/14 night → 10/15 — absence is invisible.** The night task's endpoint was 「交验收／定稿」 with checks on facts > consistency > readability > wording; once all passed it declared 「无事可做」 at 01:25 and idled; I relayed it without questioning. Dk: 「完全没做任何事的宁静的夜晚过去，你却没有去思考文件是否足够好……后台集成数据是很明确要做的，但目前只有数据看板和操作界面有一些简陋的内容；弹窗的配置条件目前都有哪些纬度？缺不缺？……不是你能力不足，是你没去想」. My first fix, a rule 「不允许无事可做」, got: 「这条规则毫无意义，不是通过这样一句话就能解决的，要从实际出发，从第一性原理出发去解决」. (Earlier, 9/28, Dk also cancelled a 「不能停」 constraint as it forces drift.)

**How to apply:** build a reference of what should exist from reality — real users' tasks (current backend screenshots, colleague drafts, Jira history, Dk's words, product plan) plus a benchmark capability catalog with sources — and walk every task through the deliverable; break points and unjustified missing capabilities are the gaps. Stop only when the walk finds none, and say what was walked. Each gap Dk points out = a missing row in the reference, not a new slogan rule. Implemented as `分析/应有内容参照.md`, checklist items E1/P9, nightly task `popup-tag-push-night-global`. Related: [[judging-method]], [[stage-progression]].
