---
name: claude-usage-diagnosis-1029
description: 2026-10-29 对 Dk 用 Claude 方式的体检报告在 用好Claude/；同日另一条对话把「开工／验收官／整理纠正／验收官考试」框架装进了 ~/.claude，工作文件在 _底座/
metadata:
  type: reference
---

- 报告：`/Users/decheng.huang/claude/用好Claude/2026-10-29_使用诊断.html`（结论：纠正→加规则是最大损耗，规则约 32 万字、76% 的纠正早有规则、定时任务 72% 空转占一半 token；该换成「样本→测闸门→改方法」）。补件在 `用好Claude/框架包/`（全局 CLAUDE.md 草稿、PostToolUse 钩子、记忆合并表 32→11、定时任务处置）。
- 同日 14:04–14:10 另一条对话装进 `~/.claude` 的框架：技能 开工（对齐卡）、整理纠正、验收官考试；代理 验收官；钩子 delivery_gate.py（Stop）、correction_capture.py（UserPromptSubmit）；纠正记录与考试在 `/Users/decheng.huang/claude/_底座/`。
- 10/29 下午两套已由「opus 诊断」对话合并（Dk 没有指定由谁合并，是那条对话发起的，可叫停）：全局规则以「任何工作先立合同」统领，共 30 条；补件里输出样式和两个钩子已放进 ~/.claude，钩子要 Dk 同意后登记进设置才生效。合并后的总报告：`/Users/decheng.huang/claude/_底座/简报/2026-10-29_协作诊断与自迭代框架.html`。

接到改工作方式这类话题怎么做，见 `~/claude/用好Claude/先看这里.md`。
