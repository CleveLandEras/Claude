---
name: douyin-workflow-measure-references
description: "Before making or revising a 抖音 video, follow dy/制作工作流.md — measure 2–3 top references' first 15 s with tools/watch/beats.py and compare numbers, instead of self-review loops"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 08ca51fa-7e23-4605-b9c7-145c2054a82d
  modified: 2026-10-28T06:03:13.382Z
---

Make every 抖音 video by the workflow in dy/制作工作流.md. Measure references, lock pacing, then polish. Don't iterate by watching my own cut and trusting my feelings.

**Why:** On 2026-10-28 the 《等待》 opening had gone through a dozen self-review rounds, and each round overcorrected or dropped something already decided. The 号主: "视频制作的工作流一定要了解顶尖的做法，而不只是沉浸在自己世界中，这样反复审和改是很难有成效的。" When I finally measured three top videos second by second, I found four gaps that a dozen rounds of self-review had missed. They're recorded in dy/videos/001_等待/节拍对照.md and in rule 29 of dy/剪辑认知.md:
- the references have few shots, with many events inside each shot;
- the open question stays on screen until it is answered;
- text is read in one place only;
- 0–4% of the frames are static, against our 40%.

**How to apply:**
- Pick references by structure, not by style. Run `.venv/bin/python -I tools/watch/beats.py <video> <outdir> 15` on them and on our cut. Compare shots, events per shot, question and payoff seconds, number of reading spots and static %.
- Fix only the largest measured gaps. Re-measure after the fix to confirm.
- Check the 7 opening rules and the keep-list before and after every change. Brief any reviewer on both.
- Treat reviewer suggestions as hypotheses: measure before changing.
- Reuse already-downloaded reference videos; don't bulk-download (protocol 5.1).

- For the look (not pacing), score with Vincent's 7-dimension rubric via a fresh judge subagent that sees only the video. Anchors: 5 student, 6 template, 7 pro, 8 agency, 9 award. Verify each finding before changing anything. On 2026-10-28 the 《等待》 look sample went 5.4 → 5.9 → 5.7 over three judges. The ceiling was figures and props built from primitives (circles and capsules), not small fixes.

Related: [[douyin-editing-not-style]], [[douyin-self-direction]].
