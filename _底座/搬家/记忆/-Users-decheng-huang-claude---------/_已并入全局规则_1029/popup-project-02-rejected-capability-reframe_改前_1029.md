---
name: popup-project-02-rejected-capability-reframe
description: "弹窗标签推送系统: where to start and the standing setup (10/16); live progress is NOT kept here — read 先看这里.md → 标准体系 第〇节 → the checklist's 第六节 进度"
metadata:
  type: project
---

Project `/Users/decheng.huang/claude/弹窗标签推送系统/`: popup / tag / push capability for a Taiwan slot-game platform; Dk reports to his boss 主管. Status changes daily and is kept only in the project files — this memory does not track it (10/16; an earlier version went stale: page counts, design-overview stage, a dead venv path).

**Start here:** `先看这里.md` (deliverables and their status) → `规则与交接/标准体系.md` 第〇节 (the entry table: where every rule and record lives and when to read it; rule precedence, what goes to Dk, day vs night, parallel sessions, main-context limits) → the relevant progress file (moved out of the checklists' 第六节 on 10/19): `过程记录/进度_弹窗标签推送方案.md` or `过程记录/进度_推送系统后台集成需求.md`; the checklists `规则与交接/标准_*.md` keep only the standard. Before acting, read `过程记录/对话分工.md` (who is editing what, 「待改」 list) and the latest `过程记录/夜间推进_<MMDD>夜.md`; lock shared files with `_scripts/pl_锁.py`.

**Two workstreams:** 弹窗标签推送方案 (progress deck for the boss, `弹窗标签推送方案/弹窗标签推送方案.pptx`); 推送系统后台集成需求 (stages in `规则与交接/推送系统后台集成需求.md` §八; 需求评审 uses the prototype `3_原型.html` since 10/16, the design overview `5_设计概要.pptx` is paused).

**Standing setup:** business rules in `规则与交接/已定事项.md` (capability-only goals; backend data may count post-click/post-send results but they never become plan goals or acceptance — 10/16); writing in `写作标准_合并版.md`; nightly scheduled task `popup-tag-push-night-global` 19:00–08:30, currently disabled (checked 10/19; re-decide after the weekly quota resets) (gate `_scripts/夜间_闸门.py`; walks the deliverables against `分析/应有内容参照.md`, proceeds on recommendations and lists them in a 「已按推荐做、可推翻」 table; pausing it = disabling the task, `暂停.txt` doesn't affect it); evaluation bank and judging method in `规则与交接/评审题库/` (being built 10/16 by another session). 判例 are calibration material, not rules.

**Lessons kept only here:** 10/14 calibration — when fresh judges keep finding ever-finer issues on the same item, stop and ask instead of looping (list it for Dk with my judgment and a default; don't block); the deck's P1 (boss can restate) fails only on a core misread or a real contradiction. 10/16 self-loop core conditions agreed with Dk (答复登记): the judge agrees with Dk (same information, same standard); information flows both ways between Dk and the loop; it can run and keep running — the first two were missing.

**Why:** Dk reads the project through these files; stale status in an always-loaded memory misleads every new session.

**How to apply:** never answer "where are we" from this memory — open the progress file under 过程记录/. Related: [[what-goes-to-dk-and-boss]], [[think-before-acting-on-dk-words]], [[stage-progression]], [[parallel-sessions-coordination]].
