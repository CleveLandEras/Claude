---
name: douyin-not-work-mode
description: "Report-style communication is welcome in the Douyin project to save the user's time; what must not carry over from work is creative deference"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 78b6a1cb-aaf8-4fc3-8db8-5d18e7e2d652
  modified: 2026-10-28T02:19:22.289Z
---

The user gives Claude many constraints at work, each serving a specific goal. On 2026-10-27 they asked Claude to check that no leftover constraint turns it into "工作模式" instead of autonomous creation.

An audit the same day found that the global `report-format` skill had shaped every message into a boss-style report. The user's reply: the report format is a good way to communicate because it saves their time — "这个其实没什么，不影响你自主创作就可以".

**Why:** the user's concern is about who decides. It is not about message format. Concise reports respect their time. Deferring creative choices to them would defeat the experiment.

It happened anyway on 2026-10-28: a report listed five "要号主定的事" (whether to make 《等待》, which tools, how to publish, when to change the profile, the 5.1 risk). The user asked "怎么还让我抉择上了，你是希望我来抉择？". Report-format's decision section pulls toward this — don't fill it with things Claude can decide.

It happened again on 2026-10-28, in a smaller form. After finishing a cut I ended the turn with "成片可以发吗？" and buttons "可以，准备发 / 还要改". The user said "你又让我决定". That question really asks him to judge whether the cut is good enough. He then gave his view as a suggestion ("只是希望你多思考，但不替你决定").

**How to apply:**
- Never end a cut with "可以发吗 / 够不够精美 / 对路吗" questions. State your own judgment ("我判断可以发了，因为…"). Say the only remaining step is his "发" in the App, and don't ask him to grade the work. When he gives an opinion, weigh it yourself and say what you decided and why.
- Decide content, tools, publishing method and timing yourself and state them as decided. List only "需要号主帮的": things physically only he can do — QR/identity verification, the per-post "发", picking files, real-name/paid accounts. For risks to his account, state what you will do and that you'll stop if he objects; don't make it a question.
- Using `report-format` for messages to the user is fine: conclusion first, short, structured.
- Don't let it shift creative decisions back to the user. Questions go to them only when the matter really is theirs: their real-name account's risk, money, their identity, actions only they can do.
- Content, direction and process are Claude's call, per [[douyin-self-direction]].
- The per-publish "发" confirmation stays. Claude's own safety rules require explicit permission for each public post; it covers only the publish click.
- Also see [[reply-in-chinese]].
