---
name: team-design-overview-layer
description: "Big requirements need a team-facing layer (core + key design details, no long dev-level text) for 需求评审 — not a business case or a row-level spec; for 推送后台 that layer is the prototype since 10/16 (the separate design-overview deck read worse and is paused)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8c2b36fd-ce09-42ed-9fd3-7ac8dddab0f6
  modified: 2026-10-14T10:12:57.583Z
---

For a large requirement, Dk needs one file for 自己人 that conveys the core and the important design details, without the long developer-facing requirements: 「我们现在最需要的是一个给自己人看的东西，传达出去核心的内容，但也包括很多细节上的设计，只是没有那些冗长的细致要求和说明」 (2026-10-14, 推送后台). The 需求评审 judges this layer. Before this, I produced a go/no-go business case (wrong: building was decided) and then a 148-row spec table (too detailed).

Shape that worked as the answer: one-page overview diagram (pages + one push's path + key rules as labels) → background/goals/scope (do/not do) → core operator scenarios → one page per module (prototype crop + 3–6 key rules, each with a one-line why) → key decisions with their why (a rejected alternative may be named inside the reason; no option lists — 写作标准 「没有被否决的选项」, 判例 41; reconciled 10/14) → dependencies and open values → how to judge done → appendix links. Granularity test: drop a rule if removing it would not change the team's understanding of how the system works; fields, interfaces, error codes, full state tables stay in the dev spec. References: Stone Librande's one-page designs (games), Chinese studios' 概要设计 vs 详细设计, Shape Up pitch, Google design docs.

**Why:** the team must align and judge reasonableness quickly; dev specs are unread by them, business cases re-argue settled scope.

**How to apply:** when a requirement goes to review, ask which layer the reviewers judge; for team/requirement review, produce this overview; keep the dev spec and row-level tables for 研发评审. Related: [[stage-progression]], [[think-before-acting-on-dk-words]], [[writing-and-layout]].

Update 10/15–10/16: after the design-overview deck (5_设计概要.pptx) was rewritten, Dk: 「这个表述形式本身就不是那么好，还是原型那个文件更清晰一些。但是原型的内容问题依然很大」. 10/16 he approved: 需求评审 uses the prototype (overview page, every page, key rules); the design overview is paused and no longer maintained. The need stands (a 自己人 layer, no long dev-level text); the form changed — a static prototype carrying key rules beat a separate overview deck here (判例 43). Check whether an existing artifact already carries the layer before building a separate document for it.
