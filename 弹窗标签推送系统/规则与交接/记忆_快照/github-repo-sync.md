---
name: github-repo-sync
description: "Dk's private GitHub repo Clarelive/Claude mirrors ~/claude; local git repo lives at ~/claude with a whitelist .gitignore; memory and the report-format skill are copied into the repo as snapshots"
metadata:
  node_type: memory
  type: reference
  originSessionId: 975bd6ba-9e71-41fd-9831-f6c09d25937c
  modified: 2026-10-20T02:51:07.795Z
---

- Repo: https://github.com/Clarelive/Claude (private). Set up 10/20 so work can continue in cloud sessions.
- Local repo root is `/Users/decheng.huang/claude` (the parent folder). Its `.gitignore` ignores everything except listed project folders; only `弹窗标签推送系统/` is listed so far (竞品跟踪分析 and the 通行证 files are not uploaded). Each project folder has its own `.gitignore` (no `_versions/`, old temp scripts, screenshots, archived drafts; `分析/` keeps only .md; `简报/` keeps 10/19 onward).
- Push works from local git via the macOS keychain (Dk entered a fine-grained token with Contents read/write on 10/20). The claude.ai GitHub connection only serves cloud sessions, not local git.
- Snapshots that do not sync by themselves: this memory folder → `弹窗标签推送系统/规则与交接/记忆_快照/`; `~/.claude/skills/report-format` → `弹窗标签推送系统/.claude/skills/report-format/`. Refresh them before pushing when they change.
- `_scripts/*.py` find the project root from their own location (`_ROOT`), so they run in the cloud; the pptx render and screenshot tools only work on Dk's Mac.

Related: [[popup-project-02-rejected-capability-reframe]], [[parallel-sessions-coordination]].
