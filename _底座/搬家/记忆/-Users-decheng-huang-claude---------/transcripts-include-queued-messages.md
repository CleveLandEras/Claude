---
name: transcripts-include-queued-messages
description: "When extracting Dk's words from past sessions, read ~/.claude/projects/*/<session>.jsonl AND the queued_command attachments — messages Dk types mid-turn are not stored as user messages"
metadata:
  node_type: memory
  type: reference
  originSessionId: 511c6f40-83af-41b0-bbc6-a73b73fbefa8
  modified: 2026-10-09T08:14:16.226Z
---

Past Claude Code sessions are stored as `~/.claude/projects/<dir>/<session-id>.jsonl`. Messages Dk sends while I am still working are stored as records with `attachment.type == "queued_command"` (text in `attachment.prompt`), not as `type == "user"` messages. Compaction summaries also appear as user messages starting "This session is being continued…" and are not Dk's words.

引用 Dk 以前的话怎么查，见弹窗 `规则与交接/工作原则.md` 乙·5「引用 Dk 以前说的话」。
