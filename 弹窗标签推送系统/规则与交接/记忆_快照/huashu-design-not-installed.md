---
name: huashu-design-not-installed
description: "10/15 Dk decided not to install the huashu-design skill; revisit only for popup visual mockups or demo animations, and then install as manual-invoke only"
metadata:
  node_type: memory
  type: project
  originSessionId: e3d8da53-40fd-429a-a45e-03724c156bc1
  modified: 2026-10-15T07:52:03.077Z
---

2026-10-15: Dk asked to install huashu-design (github.com/alchaincyf/huashu-design, MIT). After the conflict assessment he decided: 先不装，以后要做弹窗效果图或演示动画时再说.

Conflicts found by reading its SKILL.md v2.0 (the reasons for the decision):
- It requires three design directions for every new visual design, then ends the turn and waits for the user, unattended sessions included, and asks ≥10 questions up front. That breaks [[what-goes-to-dk-and-boss]] (写作标准 第二部分第 6 组「未知不阻塞推进」).
- Its trigger words include PPT/幻灯片/做个HTML页面/做个好看的. Its default deck is 1920×1080 HTML + PDF, and PPTX export needs Node + Playwright. That clashes with the python-pptx scripts + pl_pptx渲染.sh workflow ([[edit-in-place-render-fixed-folder]]).
- Loading SKILL.md costs ~28k tokens on every trigger.
- Aesthetic rules mostly yield to a user's own font and reference specs, so the conflict there is low.

**Why:** its benefit (high-fi mockups, clickable prototypes, animation/video) doesn't serve the current deck and backend-overview work, and auto-triggering would put risk on every deck.

**How to apply:** if Dk later needs popup visual mockups or demo animations, propose installing it via `git clone` into ~/.claude/skills/ (this Mac has no Node/npx/ffmpeg) and add `disable-model-invocation: true` to its frontmatter so it only runs on /huashu-design. When using it, waive the gate by saying 跳过三方向.
