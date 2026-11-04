---
name: backend-ui-static-readable-display
description: "Backend UI in requirements = static, information-complete display for reading, not clickable prototypes; settled in 通行证 (9/21) and restated 10/12 — check prior projects before asking"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8c2b36fd-ce09-42ed-9fd3-7ac8dddab0f6
  modified: 2026-10-12T06:22:42.563Z
---

For admin-backend requirements, show the interface in the most readable static form (readable first; full field detail folded, per 10/13 below); never build clickable/interactive prototypes. Mock data need not be real.

Dk's words: 9/21 20:59 (通行证, rejecting a clickable workbench) 「是展示用的，展示用的！……难道展示给别人的时候要一个个点击吗」; 9/21 22:00 「下拉栏是要用打开的状态展示出去，这样信息才多……产出几张原型图和少量介绍」, not tables and not a literal working backend; 9/21 20:23 「我们的内容不面向研发，只给运营看」; 9/22 「原型图肯定不能直接平铺……只要能展开看就可以了」 (when embedded in a plan). 10/12 (推送后台集成): 「不用可点击的原型，这个问题你之前问过我……把信息展示全，主要是为了提升阅读而不是互动性」「真实数据不需要」.

Accepted references: `~/Downloads/通行证后台配置原型.html` (static HTML ~1240px, Element-UI look, each screen = window frame with dropdowns drawn open, example rows, required/validation marks, 2–3 annotation cards: bold conclusion + one-line reason); `~/Downloads/新手通行证重构方案-3.pptx` p16–19 (real backend screenshots with blue 「新增」 marks + numbered 使用方式 steps).

10/13: the 25-screen 推送后台 mockup (every control detailed, all dropdowns open, notes as cards below) was too slow: 「原型图我感觉看得也很费时，原型图应该是比文字更轻松阅读的才对」. Readable ≠ maximal detail: one whole-page image per page, low density, numbered callouts with short notes beside, full field detail folded below (<details>), an overview figure first.

**Why:** the reader's job is to read and decide, not click around; re-asking a question Dk already answered in another project wastes their time.

**How to apply:** before asking Dk a format/method question, search earlier projects (incl. `~/.codex/sessions/` for Codex-era work) for an answer already given and reuse it. Related: [[stage-progression]], [[writing-and-layout]].
