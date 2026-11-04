---
name: reporting-to-dk
description: "Reports to Dk follow the report-format skill (load it first): show the content itself conclusion-first in an HTML brief in 简报/, structure by layout not prose, put screenshots/tables on the page when he must judge them, and give the key facts before any decision (merged 10/16 from report-show-content-not-checklist, briefs-not-essays, decisions-need-key-facts)"
metadata:
  type: feedback
---

Rules live in the personal skill `~/.claude/skills/report-format/` (created 10/08 at Dk's request; load before any substantive report). Writing rules: 写作标准_合并版.md (its 现行说法 wins). The cases behind it:

**Content, not a where-to-look list (10/08).** Asked 「带我过一遍 02 和 03 的验收」, I gave a 「验收看哪几处」 checklist full of internal codes (序号 1′, K 列, 第 17 件, R 编号). Dk: 「我没看到我要看的内容，你不知道怎么汇报吗」. Present the content: conclusion → what changed / why (data) / what it's blocked on → decisions (背景、选项、推荐; 利弊 not listed separately since 10/9) → my findings. HTML brief in the project's `简报/`, `YYYY-MM-DD_主题.html`; translate agent jargon; show before/after of the actual rules.

**Not an essay (10/10).** On the 七天工作复盘 brief: 「简报的文字几乎堆在一起，毫无结构性，很难阅读，每次汇报我都像在读一篇长文，这不能叫汇报」. Structure by layout (number cards, side-by-side cards, tags, option cards with a 推荐 badge, short phrase tables); item length is judgment, not a cap. Template `assets/brief_template.html`; example 归档/简报_至1010/2026-10-10_七天工作复盘.html. In chat, explanations or 「直接给我介绍」 get plain text.

**Show the thing being judged (10/16).** A sheet asking Dk to judge 10 pages/decisions was text plus links: 「没图吗？全是纯文字？这符合写作标准吗？」 Put the screenshot or the table on the page, cropped or boxed; links only for the full source. (Same day, typesetting case: see [[writing-and-layout]].)

**Key facts before any decision (10/16).** On /grill-me about the self-loop I asked him to define done, a release threshold and rules-with-tests without showing how the loop runs, what the judge sees and says, or what I had already decided for him. After four answers: 「现在最大的问题是，我信息不全无法做出决策，你也没给我提供相关的关键信息，这是最重要的最重要的，因为这个问题导致我只能完全把权限交给你，我基本上蒙着头听你问这些问题」. Before a decision: how it works now traced through one real example; verbatim evidence (the judge's words next to his); what was already decided for him; what each option changes in practice. Answers given without these are provisional.

Related: [[what-goes-to-dk-and-boss]], [[judging-method]].

Case 10/19: asked Dk to judge/supplement criteria on static HTML pages linked only by chat links; Dk: 「我不知道在哪里补」「我说我都找不到这个文件」. When Dk must act on a page: send the file card AND open it for him; anything he fills in needs real controls (buttons/inputs saving to localStorage) served at http://localhost:8765 (project-files server) in the built-in browser pane — file-card previews are data: URLs and cannot save; read his input back with javascript_tool, never make him copy-paste.
