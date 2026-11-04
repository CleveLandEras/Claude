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

**Why:** On 2026-10-09, while compiling Dk's writing standards, a user-messages-only export missed 4 of his sentences, including 9/28 「精炼的内容放汇报，完整的内容单独输出文件」 and 10/9 「活跃付费降为上线后观察？就不该出现这个指标好吗……」.

**How to apply:** Any time I quote, count or audit what Dk said in earlier sessions, include queued_command prompts, exclude summaries and task notifications, and verify each quote against the raw jsonl before presenting it as his. Related: [[writing-and-layout]], [[only-confirmed-principles]].
