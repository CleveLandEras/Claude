---
name: industry-standard-definitions-first
description: "For metrics/segment definitions that have common industry standards (churn, at-risk, active, returning, payer conversion, push delivery/open), research industry sources and check thresholds against data before writing them"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8b5e6536-7231-4c29-80db-4e948f5486b9
  modified: 2026-10-10T02:42:28.644Z
---

Before writing any definition or metric that the industry already has a common standard for (流失／潜在流失、活跃、回流、留存、潜在付费／付费转化、推送送达与点开率 etc.), search industry sources (WebSearch) and the platform's own data first; treat internal materials' wording only as a reference. Validate thresholds with data (e.g., is the threshold above the non-payer median?).

**Why:** 2026-10-10 Dk on the popup project deck: 「潜在流失应该是按活跃度来判定的吧，你怎么用的储值啊，这感觉常识性的东西你都有偏差了，说明你没参考行业的标准，这种很常用很有标准的内容会出问题是不应该的，你得仔细排查这种问题，多搜寻资料作为标准」. I had carried over 「储值衰减」 from an internal mind map and set 潜在付费 at 近 4 个月押注 > 10,000, which was below the non-payer median (20,252).

**How to apply:** When drafting or reviewing, list every definition with an industry norm, cite the norm and the data check next to it, and audit existing drafts for the same issue. Related: [[popup-project-02-rejected-capability-reframe]], [[check-sufficiency-before-done]].
