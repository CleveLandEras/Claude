---
name: github-repo-sync
description: "Dk's private GitHub repo Clarelive/Claude mirrors ~/claude; local git repo lives at ~/claude with a whitelist .gitignore; the report-format skill is copied into the repo as a snapshot (the memory snapshot 规则与交接/记忆_快照/ is frozen at 10/20)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 975bd6ba-9e71-41fd-9831-f6c09d25937c
  modified: 2026-10-20T02:51:07.795Z
---

- Repo: https://github.com/Clarelive/Claude (private). Set up 10/20 so work can continue in cloud sessions.
- Local repo root is `/Users/decheng.huang/claude` (the parent folder). Its `.gitignore` ignores everything except listed project folders; only `弹窗标签推送系统/` is listed so far (竞品跟踪分析 and the 通行证 files are not uploaded). Each project folder has its own `.gitignore` (no `_versions/`, old temp scripts, screenshots, archived drafts; `分析/` keeps only .md; `简报/` keeps 10/19 onward).
- Push works from local git via the macOS keychain (Dk entered a fine-grained token with Contents read/write on 10/20). The claude.ai GitHub connection only serves cloud sessions, not local git.
- The report-format copy does not sync by itself: `~/.claude/skills/report-format` → `弹窗标签推送系统/.claude/skills/report-format/`; refresh it before pushing when it changes. `规则与交接/记忆_快照/` is frozen at 10/20 and is not refreshed.
- `_scripts/*.py` find the project root from their own location (`_ROOT`), so they run in the cloud; the pptx render and screenshot tools only work on Dk's Mac.

Related: [[popup-project-02-rejected-capability-reframe]], [[parallel-sessions-coordination]].
