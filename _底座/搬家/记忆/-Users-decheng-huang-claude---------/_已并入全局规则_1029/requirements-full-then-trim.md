---
name: requirements-full-then-trim
description: "Dk's rule for requirements — write the ideal, complete set; let cost trimming happen in discussion with superiors; separately list quick low-cost wins"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 975bd6ba-9e71-41fd-9831-f6c09d25937c
  modified: 2026-10-19T09:21:14.963Z
---

Write requirements and plans in their ideal, complete form — don't pre-cut items because of cost, dev effort, or current backend limits. Tag each with cost/dependency tiers (short-term config / mid small dev / long big dev) so Dk and superiors can trim in discussion; whatever survives is the scope. Always add a separate, explicit list of short-term, low-cost, quick-impact actions (what, for whom, expected effect, how to verify).

**Why:** 2026-10-08 Dk: 「我们写需求肯定是往好了写往全面了写，写完之后可能与上级讨论后会考虑成本后发现这个不要那个也不要，但留下来点这就可以了，然后我们有什么短期快速提升的低成本操作也写清楚。这才是对的模式。」 Earlier work had pre-trimmed by "本期只用现有功能" and a 15-scenario cap.

**How to apply:** In requirement/plan docs, never write "本期不做" for cost reasons — put cost in a tier column instead; boundaries are only for things that aren't requirements at all (content, pricing). Related: [[what-goes-to-dk-and-boss]], [[writing-and-layout]].

**Case, 10/19 (push backend, hardcoded-push migration):** "complete" ≠ turning every process into a backend feature. I had designed a 迁入 button, migration records, phased rollout/reconciliation as backend functions. Dk: migration is RD connecting each hardcoded item into the backend one by one, real developer work, not a click; 「这一个功能让RD去开发得花多久啊，运营自己记的话总共才花几分钟，这些不考虑吗？」 Before making something a feature, ask who really does it, how often, and dev cost vs the manual alternative; one-off work done by RD or recorded by ops in minutes belongs in the requirement as an RD work list, not as a feature.
