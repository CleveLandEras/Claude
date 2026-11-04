# 来源表 (a)：AI 公司官方

查于 2026-10-29，调研子代理写。共 27 条：一手 26 条（官方文档、官方工程博客、作者本人文章、论文摘要页），二手 1 条（第 24 条）。第 17 条的原文 PDF 已下载但本机提不出文字，只核到二手转述，已标。

**怎么核的引文**：我把原页面用命令行重新抓下来，逐句在页面文字里检索。标「已核」＝原句在原页面里找到了；标「未逐字核」＝只来自网页抓取工具的摘要，原页面里没检索到同一句，用时请再对一遍。所有引文都是英文原句，≤25 词。

**读法**：步骤指任务文件里的六步——①立合同（对齐卡）②独立检查（验收官）③记纠正（钩子＋纠正记录）④每周整理纠正 ⑤考验收官（固定题库）⑥每周算五个数。

---

## 一、Anthropic（16 条）

### 1. Building effective agents
- 谁：Anthropic 工程博客，Erik S.、Barry Zhang；2024-12-19
- 链接：https://www.anthropic.com/engineering/building-effective-agents
- 一手
- 做了什么：把「评估-优化循环」列为一种工作流——一个模型生成，另一个模型评价并反馈，循环；说适用条件是评判标准清楚、反复改有可量的收益。又说智能体每一步要从环境里拿「真实结果」，并设置停止条件（如最大轮数），关键点停下来问人。
- 原文一句（已核）：「…while another provides evaluation and feedback in a loop.」「when we have clear evaluation criteria, and when iterative refinement provides measurable value」「gain "ground truth" from the environment at each step」「stopping conditions (such as a maximum number of iterations)」
- 效果证据：只是说法（经验总结，没有对照实验）。
- 我们能不能用：能。验收官＝评价者，主模型＝生成者，现在就是这个结构。
- 怎么用：步骤②。提醒两点：评价者要有「清楚的标准」（对齐卡的「算完」）；循环要有轮数上限（我们的定时任务清单要写停机条件，已在全局规则第 6 条）。

### 2. How we built our multi-agent research system
- 谁：Anthropic 工程博客；2025-06-13
- 链接：https://www.anthropic.com/engineering/multi-agent-research-system
- 一手
- 做了什么：评估从约 20 个真实用法的问题起步；用一次 LLM 调用、一份提示给输出打 0–1 分并判通过与否，当裁判；人工测试仍必不可少；让 Claude 自己诊断失败并改提示，还做了「工具测试智能体」重写出问题的工具描述；全量生产追踪来系统地查失败。
- 原文一句（已核）：「a set of about 20 queries representing real usage patterns」「most consistent and aligned with human judgements」「manual testing remains essential」
- 效果证据：有数字，但是内部自述：一次提示改动把成功率从 30% 提到 80%（「from 30% to 80%」，已核）；工具描述被智能体重写后，后续智能体任务完成时间下降 40%（「40% decrease in task completion time」，已核）。无外部复现。
- 我们能不能用：能。只用到「小题库＋单次裁判＋人工抽看」，都是本地可做的。
- 怎么用：步骤⑤题库不必大，20 题左右就够早期用（我们现在 6 题，偏少）；步骤④让 Claude 读失败样本、提改法，但改动要过步骤⑤的重测。

### 3. Demystifying evals for AI agents
- 谁：Anthropic 工程博客，Mikaela Grace、Jeremy Hadfield、Rodrigo Olivares、Jiri De Jonghe；2026-01-09
- 链接：https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- 一手
- 做了什么：评估从真实失败起步；分「能力题」（起点通过率低、测还做不到的）和「回归题」（通过率应近 100%、防退化）；打分器三类——程序判、模型判、人判；模型判要用专家人工标注校准，并给裁判一个「不知道」的出口；题库会饱和（全做对就没有提升空间）；必须读转录才能确认评估量的是对的；题库是「活的」，要有人负责。
- 原文一句（已核）：「20-50 simple tasks drawn from real failures is a great start」「should start at a low pass rate」「nearly 100% pass rate」「closely calibrated with human experts」「living artifact」
- 效果证据：有一个旁证：某模型在 CORE-Bench 上先得 42%，修掉评分器的 bug 并放宽脚手架后升到 95%（取自抓取摘要，未逐字核）——说明评估本身会错。方法本身没有对照实验。
- 我们能不能用：能，是本类里对我们最贴的一篇。
- 怎么用：步骤⑤把题库分成「回归组」（Dk 退回过、已修好的，验收官应全拦）和「能力组」（还拦不住的）；步骤②验收官的输出要有「拿不准」一档；步骤⑥题库全拦了就要补新题（防饱和）。

### 4. Effective context engineering for AI agents
- 谁：Anthropic 工程博客，Prithvi Rajasekaran 等；2025-09-29
- 链接：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- 一手
- 做了什么：主张给模型「最小的高信号信息集」；CLAUDE.md 这类文件一开始就整个放进上下文；结构化笔记＝把笔记写到上下文之外的记忆里；提示里硬塞复杂脆弱逻辑、工具集过大是常见失败。
- 原文一句（已核）：「smallest possible set of high-signal tokens」「bloated tool sets」「structured note-taking」
- 效果证据：只是说法。
- 我们能不能用：能。直接支持「全局规则上限 80 行、规则别越加越多」。
- 怎么用：步骤④整理时的删减依据；规则常驻 vs 按需加载的取舍依据。

### 5. Writing effective tools for AI agents
- 谁：Anthropic 工程博客，Ken Aizawa；2025-09-11
- 链接：https://www.anthropic.com/engineering/writing-tools-for-agents
- 一手
- 做了什么：用真实用法造一批评估题，每题要有可核对的结果；读原始转录（含工具调用），因为智能体没说的往往比说了的更重要；把转录整批贴给 Claude 让它分析并改工具；用留出的测试集防止对「训练用题」过拟合。
- 原文一句（已核）：「held-out test sets」「what agents omit in their feedback and responses」（后半句原文还有「can often be more important than what they include」）
- 效果证据：自述有：留出集上相对专家手写版和 Claude 生成版都有进一步提升（具体数字未给）；一个详细回复 206 词元、精简版 72 词元（抓取摘要，未逐字核）。
- 我们能不能用：能。「留出集」尤其关键：改验收清单后只用同一批旧题重考，等于拿答案考自己。
- 怎么用：步骤⑤题库留一部分不参与调规则、只在改完后复考一次；步骤④让 Claude 读整批纠正记录而不是只看一条。

### 6. Equipping agents for the real world with Agent Skills
- 谁：Anthropic 工程博客，Barry Zhang、Keith Lazuka、Mahesh Murag；2025-10-16
- 链接：https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- 一手
- 做了什么：技能按「分级披露」加载（启动时只放名字和描述，用到才读正文）；建议让 Claude 把成功做法和常见错误沉淀进技能；用代表性任务跑一遍找出能力缺口再补技能。
- 原文一句（已核）：「Progressive disclosure is the core design principle」「capture its successful approaches and common mistakes」
- 效果证据：只是说法。
- 我们能不能用：能。
- 怎么用：步骤③④——「成功做法」也要记（不只记纠正）；步骤④：被反复纠正的某一类做法，写成技能而不是堆进常驻规则。

### 7. Effective harnesses for long-running agents
- 谁：Anthropic 工程博客，Justin Young；2025-11-26
- 链接：https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- 一手
- 做了什么：跨很多轮对话的任务，用进度文件＋git 提交当记忆；功能清单用 JSON 写成「失败／通过」，智能体只准改通过与否字段，不准删改测试；智能体常常过早宣布全部完成，所以要求像真实用户一样做端到端测试后才能标通过。
- 原文一句（已核）：「It is unacceptable to remove or edit tests」；失败模式原文含「declares victory」（完整句：Claude declares victory on the entire project too early，只核到前两个词，其余来自抓取摘要）
- 效果证据：只是说法（定性，没有数字）。
- 我们能不能用：能。
- 怎么用：步骤①：「算完」写成一份通过／未通过清单，Claude 不能自己删条目；步骤②：验收官核「过早宣布完成」；交接记录＝进度文件。

### 8. Building agents with the Claude Agent SDK
- 谁：Anthropic（claude.com 博客），Thariq Shihipar 等；2025-09-29
- 链接：https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- 一手
- 做了什么：把智能体循环概括为「收集上下文→行动→验证→重复」；验证的三种办法：规则型反馈（最好）、视觉反馈、LLM 当裁判（不够稳、慢）。
- 原文一句（已核）：「gather context -> take action -> verify work -> repeat」「clearly defined rules for an output」「not a very robust method」
- 效果证据：只是说法。
- 我们能不能用：能。
- 怎么用：步骤②：能写成规则、用程序判的检查先写成程序（例如交付闸门检查文件里有没有「待验收」标注），LLM 验收官只管程序判不了的。

### 9. Claude Code：Best practices（最佳实践）
- 谁：Anthropic 官方文档；抓取日 2026-10-29（页面无发布日）
- 链接：https://code.claude.com/docs/en/best-practices （旧地址 docs.claude.com 自动跳转到此）
- 一手
- 做了什么：①「软」做法（提示、CLAUDE.md）与「硬」做法（钩子、拒绝规则）分开：每次必须发生的事用钩子；②给 Claude 一个能跑出通过／不通过的检查，并要证据（命令和输出）；③Stop 钩子退出码 2 会把 Claude 拉回去继续干，连续拦 8 次后系统强制放行；④让没看过写作过程的新子代理来审，不被写作者的思路带偏；⑤审查提示里要写「跳过风格」，否则审查者总会找出点什么；⑥CLAUDE.md 里放「你已经纠正过两次的事」；⑦强制项要少，钩子也会误触发。
- 原文一句（已核）：「If you keep adding emphasis to a `CLAUDE.md` line and Claude still misses it, that's a sign the line belongs in a hook.」「A reviewer that's asked to find problems will always find *something*.」「If you ever find yourself at forty of them, most are probably preferences that Claude could have weighed on its own.」「Every hook and deny rule will occasionally fire when it shouldn't, and someone has to maintain each one.」
- 效果证据：只是说法（产品文档，没有对照实验）。
- 我们能不能用：能，且就是我们的平台。
- 怎么用：步骤②验收官给任务时写明「只审对齐卡里的项，别找风格问题」（防误拦）；步骤④分流规则——重复犯且零例外→钩子，其余→常驻规则／技能；钩子总数要设上限。

### 10. Claude Code：Hooks（钩子）
- 谁：Anthropic 官方文档
- 链接：https://code.claude.com/docs/en/hooks
- 一手
- 做了什么：列出钩子事件（会话开始、用户提交提示、工具调用前后、Stop、子代理结束、压缩前后等）；命令型钩子靠退出码 2 阻断；提示型和代理型钩子由另一个模型判，不是确定性的。
- 原文一句（已核）：「Exit with code 2 to block the action.」；提示型、代理型钩子不确定的那句在第 9 条文档里（「A `prompt` or `agent` hook asks *another model* to decide, so it isn't deterministic either.」，已核）
- 效果证据：功能文档，不适用。
- 我们能不能用：能。我们已有 `correction_capture.py` 等钩子。但据任务文件，Claude 自己改钩子会被权限拦截，需要 Dk 跑命令。
- 怎么用：步骤③的触发（用户提交提示时记纠正）；步骤②的程序检查放在 Stop 钩子里。

### 11. Claude Code：Memory（CLAUDE.md、自动记忆）
- 谁：Anthropic 官方文档
- 链接：https://code.claude.com/docs/en/memory
- 一手
- 做了什么：两套记忆——CLAUDE.md（人写的规则）和自动记忆（Claude 自己写的，类型里有「纠正和你认可的做法」）；CLAUDE.md 目标 200 行以内，自动记忆只载入前 200 行或 25KB；说明「同样的纠正你输入了第二次」就该写进 CLAUDE.md；`/doctor prompt-audit` 能检查过时、互相矛盾的指令，只给修改建议，不自动改。
- 原文一句（已核）：「Claude treats them as context, not enforced configuration.」「Auto memory lets Claude learn from your corrections without manual effort.」「target under 200 lines per CLAUDE.md file」「You type the same correction or clarification into chat that you typed last session」；记忆类型原文：「corrections you give Claude and approaches you confirm」
- 效果证据：只是说法；官方自述「指令越具体越精简，Claude 越能一致遵守」。
- 我们能不能用：能。需核：本机 Claude Code 版本是否 ≥ 2.1.283（`/doctor prompt-audit` 要求）。
- 怎么用：步骤③官方也把「纠正」和「认可的做法」一起记——我们只记了纠正；步骤④每周跑一次 prompt-audit 找矛盾和过时规则；「同一纠正出现第二次」当作升级为规则的触发线。

### 12. Claude Code：Sub-agents（子代理）
- 谁：Anthropic 官方文档
- 链接：https://code.claude.com/docs/en/sub-agents
- 一手
- 做了什么：子代理是带 YAML 头的 Markdown 文件；有独立上下文窗口、可限制工具（白名单或黑名单）、可指定模型；看不到主对话的历史。
- 原文一句（已核）：「Each subagent runs in its own context window with a custom system prompt」「It doesn't see your conversation history」
- 效果证据：功能文档，不适用。
- 我们能不能用：能，验收官就是一个子代理。
- 怎么用：步骤②：验收官给「只读」工具，防止它顺手改被审文件；题库里的稿件由「没看过写作过程」的验收官来判，这是官方认可的独立性来源（但仍是同一家族的模型，见下文分歧）。

### 13. Claude Code：Skills（技能）
- 谁：Anthropic 官方文档
- 链接：https://code.claude.com/docs/en/skills
- 一手
- 做了什么：技能分级加载；CLAUDE.md 里某一段长成「流程」就该变成技能；可以 `context: fork` 在独立子代理里跑技能；官方给了测试技能的做法——新开会话、有技能与无技能各跑一遍对比，并提供 `skill-creator` 插件跑评估、`/skill-doctor` 看哪些技能从没被调用。
- 原文一句（已核）：「Seeing a skill trigger tells you Claude found it, not that it did what you intended.」「A fresh session matters because leftover context from authoring the skill will mask gaps」「a section of CLAUDE.md has grown into a procedure rather than a fact」
- 效果证据：功能文档，不适用。
- 我们能不能用：能。「整理纠正」「验收官考试」本身就是技能。
- 怎么用：步骤⑤改完技能后，用「有／无」对照各考一次；步骤⑥「从没被调用的技能」可当作体检项。

### 14. Claude Code：/goal（目标条件）
- 谁：Anthropic 官方文档
- 链接：https://code.claude.com/docs/en/goal
- 一手
- 做了什么：设一个完成条件，每轮结束后由另一个小模型判是否达成，没达成就让 Claude 继续；官方说明评判者不调用工具、只能看对话里已经出现的东西；条件要写成「一个可量的终态＋怎么证明＋不许变的约束＋轮数／时间上限」。
- 原文一句（已核）：「completion is decided by a fresh model rather than the one doing the work.」「It does not call tools, so it can only judge what Claude has already surfaced in the conversation.」
- 效果证据：功能文档，不适用。
- 我们能不能用：能，但只适用于会话内；跨天的定时任务用它不合适。
- 怎么用：步骤①：对齐卡「算完」可以照 `/goal` 的四要素写，才能被「另一个模型」判；步骤②：验收官同样只能判「对话或文件里已摆出来的证据」，所以执行方必须附证据（命令输出、文件路径）。

### 15. Claude Code：桌面版定时任务
- 谁：Anthropic 官方文档
- 链接：https://code.claude.com/docs/en/desktop-scheduled-tasks
- 一手
- 做了什么：三种定时——云端、桌面、会话内 `/loop`。桌面任务可读本机文件，但电脑要开着；睡眠错过的只补跑一次；手动权限模式遇到没批准的工具会卡住等人；批准过「总是允许」的工具之后自动放行；任务可用 `update_scheduled_task` 给自己改时间；任务说明存在 `~/.claude/scheduled-tasks/<名>/SKILL.md`。
- 原文一句（已核）：「Tasks only run while the desktop app is running and your computer is awake.」「Desktop starts exactly one catch-up run for the most recently missed time and discards anything older.」「If a task runs in Manual mode and needs to run a tool it doesn't have permission for, the run stalls until you approve it.」
- 效果证据：功能文档，不适用。
- 我们能不能用：能，是步骤④⑤⑥「不靠谁记得」的载体；限制要如实写进方案：电脑睡着就跳过；首次运行要点「立即运行」逐项批准工具。云端任务只在新克隆的仓库里跑、读不到本机 `~/.claude/`（该页对照表为「No (fresh clone)」），不适合改我们的规则文件。
- 怎么用：步骤④每周整理、⑥每周算数，都建成桌面定时任务；用「开机保持唤醒」；清单里写「错过则补跑一次」的容忍。是否会被权限拦截需实测（任务文件里要求实测，本表没测）。

### 16. Claude Code：用 evals 测试插件（`claude plugin eval`）
- 谁：Anthropic 官方文档
- 链接：https://code.claude.com/docs/en/plugin-evals
- 一手
- 做了什么：官方自带的评估工具——每个用例是一条提示＋若干打分器（正则、是否调用了某工具、文件是否存在，这几种不花钱；另有模型当裁判的评分，花用量）；每个用例默认跑 3 次；同时跑「无插件」基线，算出有插件比无插件多得多少分；低于阈值退出码为 1，可进持续集成；要固定模型版本，免得把模型升级误当成插件退化。
- 原文一句（已核）：「One run of a non-deterministic agent tells you little, so each case runs three times by default.」「If a case scores 1.0 both with and without the plugin, the plugin isn't what made it pass.」「Every eval run and every judge grader is a real model call on your account」
- 效果证据：功能文档，不适用。
- 我们能不能用：部分。它面向「插件」；验收官和规则文件不是插件。能不能把我们的验收官或技能打成插件再用它，需实测（本表没测）。每次评估都耗你套餐用量，要计入周额度预算。
- 怎么用：步骤⑤的做法可以直接借：每题跑 3 次取平均；每条新规则做「有这条／没这条」对照，两边都满分的规则就不是它起的作用——这是「规则越加越多怎么删」的现成判据；步骤⑥记下当次的模型版本。

---

## 二、OpenAI（5 条）

### 17. A practical guide to building agents（智能体实践指南）
- 谁：OpenAI；2025-04
- 链接：https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- 一手，但原文 PDF 本机提不出文字（已下载 7MB，无 PDF 文本工具），以下内容只来自二手转述，未核
- 做了什么（二手转述）：说要有护栏和人工介入机制（高风险动作、连续失败时转人）；一份二手摘要称其建议先用最强模型做基线、再用评估测小模型能否替代——只找到这一个来源，需对照原文确认。
- 原文一句：未能核到，不引。
- 效果证据：只是说法。
- 我们能不能用：能用的只有「失败多次转人」的思路。
- 怎么用：步骤②：验收官连续 N 轮判不过，转 Dk，而不是无限重做（已有全局规则第 19 条「验收官判不过的项不能自己否决」，思路一致）。
- 备注：发布月份取自二手转述，未核。

### 18. Self-Evolving Agents：自动重训练智能体手册
- 谁：OpenAI Cookbook（与 Bain 合写，Calvin Maguranis 等）；页面无日期，标注已归档、可能含过时接口
- 链接：https://developers.openai.com/cookbook/examples/partners/self_evolving_agents/autonomous_agent_retraining （旧地址 cookbook.openai.com 自动跳转）
- 一手
- 做了什么：基线智能体出结果→四个打分器（程序判 3 个＋模型判 1 个）打分→没过就把打分反馈交给一个「元提示智能体」重写系统提示→最多重试 3 次→仍不过就通知工程师；每一版提示都存成带编号、时间、评估编号的版本，可回退，选累计得分最高的版本；还介绍了 GEPA（带训练集和验证集划分的提示进化方法，论文 arXiv:2507.19457）。
- 原文一句（部分已核）：「The optimization is not always successful」（已核，原句后半为「…so being able to roll back the prompt version is important」，未逐字核）；页面另称打分反馈的质量「crucially important」（已核），静态元提示有「过拟合」风险（关键词已核）。
- 效果证据：只是示例演示。抓取摘要里没有改前改后的对比数字；页面自己承认优化不总是成功。
- 我们能不能用：思路能，自动化部分不能全用：我们没有服务器，可由「整理纠正」技能每周手动触发一次，不能无人值守地改规则（任务边界）。
- 怎么用：步骤④：每次改规则前后各存一版、写明分数、能回退（我们用 git 提交即可，不需要新系统）；页面建议新提示上线前加人工批准，对应 Dk「五处出现」之一。

### 19. Working with evals（评估指南）
- 谁：OpenAI 开发者文档
- 链接：https://developers.openai.com/api/docs/guides/evals （旧地址 platform.openai.com 自动跳转）
- 一手
- 做了什么：评估流程三步：把任务写成评估→用测试输入跑→分析结果再改提示；数据是「输入＋标准答案」的 JSONL；有字符串比对等打分器；并列出下一步：检测提示退化、同时比较多个提示和模型。
- 原文一句：无需引。要点：页面写明 OpenAI 的 Evals 平台将在 2026-10-31 起对现有用户变成只读、2026-11-30 关闭（日期已核在页面里，措辞未逐字核）。
- 效果证据：功能文档，不适用。
- 我们能不能用：不能当平台用——它要关了，也要联网调接口。只借「输入＋标准答案」的题库格式。
- 怎么用：步骤⑤题库用本地文件存；不依赖厂商评估平台（避免它下线后断掉）。

### 20. Evaluation best practices（评估最佳实践）
- 谁：OpenAI 开发者文档
- 链接：https://developers.openai.com/api/docs/guides/evaluation-best-practices
- 一手
- 做了什么：提倡「评估驱动开发」，早评、常评；数据要混合生产数据、专家造的例子和历史日志，要含典型、边缘、对抗三类；评估要持续，每次改动都跑；LLM 裁判有位置偏好、啰嗦偏好，建议两两比较或通过／不通过制、先写理由再打分、评分细则写清楚；自动裁判要拿人工评分校准，校准好了再放大使用。
- 原文一句（已核）：「Adopt eval-driven development」「Log everything」；裁判偏差一项只核到「Position bias」，「verbosity」一词在原页面没检索到，用时请再对。
- 效果证据：只是说法。
- 我们能不能用：能。
- 怎么用：步骤③「记下所有」——纠正记录之外，Dk 通过的稿也要留（做误拦测试的素材）；步骤②验收官用通过／不通过加理由，不打 1–10 分。

### 21. Building resilient prompts using an evaluation flywheel（评估飞轮）
- 谁：OpenAI Cookbook；飞轮图出自 Shreya Shankar、Hamel Husain 的课程资料（2025）；页面无日期，已归档
- 链接：https://developers.openai.com/cookbook/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel
- 一手
- 做了什么：分析→度量→改进循环。分析：挑约 50 条失败样本逐条写笔记（开放编码），再归成大类（轴向编码），数各类占比（例子里排期问题 35%、格式问题 10%）；度量：每类失败做成自动打分器；用裁判打分器要和专家标注对齐，同时看「抓出坏的比例」和「放过好的比例」，不看单一准确率（总说通过的裁判也能「准确」95%）；数据按约 20%／40%／40% 分给示例、调试、最后留出检验。
- 原文一句（已核）：「You can't improve what you can't measure」；其余是抓取摘要，未逐字核。
- 效果证据：示例数字是演示，不是效果实验。
- 我们能不能用：能，是本类里对步骤④⑤最直接的方法。
- 怎么用：步骤④纠正记录的整理照「写笔记→归类→数占比→占比最大的类先处理」；步骤⑤验收官既要报「拦下率」（抓坏的）也要报「误拦率」（放过好的，现在没量，因为没有 Dk 判通过的稿）；题库切一份留出检验。

---

## 三、Google（3 条）

### 22. Evaluate Gen AI agents（Vertex AI／Gemini 企业版智能体平台：评估智能体）
- 谁：Google Cloud 文档；抓取日 2026-10-29（页面已改名，搜索结果里同时出现 Vertex AI 与 Gemini Enterprise Agent Platform 两种地址）
- 链接：https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-agents
- 一手（页面很长，抓取只读了前面一部分；关键词已在原页面核到）
- 做了什么：把智能体评估分成「最终回答」和「轨迹」（工具调用序列）两块；轨迹指标有完全匹配、按顺序匹配、任意顺序匹配、精确率、召回率、是否用了某工具；默认自带「耗时」「是否出错」两个指标；可自定义含模型当裁判的指标。
- 原文一句（已核）：「whether or not the agent achieved its goal」（指最终回答评估）；指标名 `trajectory_exact_match`、`trajectory_in_order_match` 已核在页面。
- 效果证据：功能文档，不适用。
- 我们能不能用：概念能借，工具不能（要上 Google Cloud）。
- 怎么用：步骤②⑤：把「做对了没」（最终成品）和「过程对不对」（有没有先立对齐卡、有没有走验收官）分开计；过程可由程序从任务文件里核（有无对齐卡、有无验收结论）。

### 23. ADK：Evaluate（智能体开发套件的评估）
- 谁：Google 智能体开发套件文档
- 链接：https://adk.dev/evaluate/ （旧地址 google.github.io/adk-docs 自动跳转）
- 一手
- 做了什么：评估集文件（每个用例含用户输入、期望的工具调用序列、参考回答）；默认两个判据——工具调用序列完全匹配（默认 1.0）、回答与参考的相似度（默认 0.8）；效率指标（词元、调用次数、耗时）只报告不判失败，用来发现成本退化；有「把现场行为与已录基线对比」的命令，用于持续集成。
- 原文一句（已核）：「fast, predictable, and suitable for frequent automated checks」
- 效果证据：功能文档，不适用。
- 我们能不能用：概念能借：「便宜的程序判据每次都跑，贵的模型判据少跑」。
- 怎么用：步骤⑥五个数里加一个「只看、不判」的用量指标（每圈花多少周额度），防成本悄悄涨。

### 24. Agents Companion（Google 智能体白皮书续篇）
- 谁：Google，Antonio Gulli、Lavi Nigam、Julia Wiesinger、Vladimir Vuskovic 等；2025-02
- 链接：原文未能打开（搜索只给出二手介绍，如 https://www.marktechpost.com/2025/05/06/google-releases-76-page-whitepaper-on-ai-agents-a-deep-technical-dive-into-agentic-rag-evaluation-frameworks-and-real-world-architectures/ ，该二手页我也没打开读正文）；2024-09 的前作《Agents》Kaggle 链接（https://www.kaggle.com/whitepaper-agents）本次请求返回 404，未能打开。
- 二手
- 做了什么（二手转述，未核）：有「评估轨迹与工具使用」「评估最终回答」「人在回路评估」几章；说人的判断适合主观质量，并用来校准自动评估。
- 原文一句：无。
- 效果证据：只是说法。
- 我们能不能用：同第 20 条，没有新增。
- 怎么用：不单独用。

---

## 四、Microsoft（3 条）

### 25. Agent evaluators（Microsoft Foundry：智能体评估器）
- 谁：Microsoft Learn 文档；页面标注日期 2026-09-30
- 链接：https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators
- 一手
- 做了什么：把评估器分成「系统评估」（任务完成、是否遵守指令、意图是否理解对……）和「过程评估」（工具选对没、参数对没、工具结果用对没）；输出统一为通过／不通过加理由，1–5 分的先按阈值转成二元；组合评估器把多项合成一次裁判调用以省钱；另有「任务路径效率」对照标准动作序列，用于回归测试；多数标注预览版、无服务保证。
- 原文一句（已核）：「function like unit tests for agentic systems」
- 效果证据：功能文档，不适用。
- 我们能不能用：概念能借，工具不能（要 Azure）。
- 怎么用：步骤②：验收官输出就用「逐项通过／不通过＋一句理由」，哪一项没过一眼看到；「任务遵守指令」一项等于核对齐卡「边界」。

### 26. AgentEval（AutoGen 的任务有用度评估）
- 谁：Microsoft AutoGen 0.2 博客，James Woffinden-Luey、Julia Kiseleva；2024-06-21（论文：Arabzadeh 等，EMNLP 2024，本次没打开论文）
- 链接：https://microsoft.github.io/autogen/0.2/blog/2024/06/21/AgentEval
- 一手
- 做了什么：三个角色——「评判标准提议者」根据任务和成败样例提出标准；「打分者」按标准打分；「验证者」去掉重复标准、检查标准是否稳定、能否区分正常与噪声／对抗样本。博客自己说验证部分还在开发中，并建议由领域专家复核标准。
- 原文一句：未逐字核（博客原文含「criteria verification is still under development」，来自抓取摘要）。
- 效果证据：博客没给数值结果，只称在数学题（12,500 题）和家务模拟任务上「找出了相关标准」；没有和人工判断做直接对比。
- 我们能不能用：思路能，但不确定值得做：让 Claude 从 Dk 退回的稿里归纳「评判标准」再由 Dk 确认——和第 21 条的归类做法重叠。
- 怎么用：步骤④：归出的「Dk 的退回标准」要由 Dk 过目一次（五处出现之一），再写进验收清单。

### 27. Agent Lightning：用强化学习训练任何智能体
- 谁：Microsoft Research，Xufang Luo 等；2025-08-05（arXiv:2508.03680）
- 链接：https://arxiv.org/abs/2508.03680
- 一手（仅读了摘要页）
- 做了什么：把智能体执行和训练分开，对智能体的行为轨迹做强化学习，改的是模型参数。
- 原文一句：无需引。
- 效果证据：摘要称在文本转 SQL、检索增强、数学工具使用上「稳定持续提升」，没给数字；只是说法。
- 我们能不能用：不能。要训练模型，我们改不了 Claude 的参数。
- 怎么用：不用。列出来是为了说明「自我改进」在公司里有两条路——改提示／规则（我们能走）和改模型（我们不能走）。

---

## 本类的共识（5 条）

1. **从真实失败起步，小题库就够。** Anthropic 说 20–50 题（第 3 条）、多智能体系统用约 20 题（第 2 条）、OpenAI 飞轮约 50 条失败样本（第 21 条）。三家不约而同。
2. **能用程序判的先用程序判；模型当裁判必须用人工标注校准。** Anthropic（第 3、8 条）、OpenAI（第 20、21 条）、Claude Code 官方的评估工具（第 16 条，正则等判据免费、模型判据花钱）一致。
3. **每次改动都要在同一批题上重测，并能退回。** OpenAI 的提示版本与回退（第 18 条）、Anthropic 的回归题近 100% 通过（第 3 条）、Claude Code 评估工具超阈值即退出码 1（第 16 条）、Google ADK 的基线对比（第 23 条）。
4. **常驻指令要短、要少；长了就拆成按需加载，或硬化成钩子。** Anthropic 上下文工程（第 4 条）、Claude Code 每个 CLAUDE.md 目标 200 行以内（第 11 条）、技能正文按需才加载（第 13 条；该页「正文 500 行以内」的说法在原页面没检索到同一措辞，未逐字核，这里不采用）、强制项（钩子、拒绝规则）要少，多到四十个就多半是偏好（第 9 条）。
5. **读失败样本本身是不能省的人工步骤。** Anthropic 第 3、5 条、OpenAI 第 21 条（逐条写笔记再归类）。

## 本类的分歧（4 条）

1. **模型当裁判靠不靠得住。** Anthropic 多智能体团队发现一次调用、一份提示的裁判「最一致、最贴近人」（第 2 条）；Anthropic 智能体 SDK 文章却说它「不够稳、延迟代价高」（第 8 条）；OpenAI 列出位置偏好、啰嗦偏好（第 20 条）。收敛点：靠人工标注校准，并优先用规则和程序判。
2. **自动改写提示，要不要人批。** OpenAI 示例是自动循环改写，但自己警告会过拟合当前打分反馈、建议上线前人工批准（第 18 条）；Claude Code 的自动记忆是 Claude 自己写、无需批准（第 11 条），而 `/doctor prompt-audit` 只给建议、不自动改（第 11 条）。
3. **看过程还是看结果。** Google 和 Microsoft 把「工具调用序列对不对」做成一等指标（第 22、25 条）；Anthropic 和 Claude Code 文档更强调结果能不能验证（测试通过、截图、端到端，第 7、9 条）。这是我的读法，不是原文明说的分歧。
4. **硬规则与软规则的边界。** Claude Code 官方：零例外的才用钩子，其余留给 CLAUDE.md（第 9 条）；但钩子也会误触发，「钩子也是要维护的」（第 9 条）；另有提示型钩子不是确定性的（第 9、10 条）。该放哪边没有机械标准。

## 和我们六步逐步对照

- **①立合同（对齐卡）：已有，做法对。** 官方的「完成条件」写法更严：一个可量的终态、怎么证明、不许变的约束、轮数上限（第 14 条）；功能清单让执行方不能自己删条目（第 7 条）。我们的「算完」是文字，比官方的差一点：没有一份执行方改不了的通过／未通过清单。
- **②独立检查（验收官）：已有，但弱于顶尖做法。** 官方的独立性来源是「没看过写作过程的新会话」（第 9、12 条），我们已具备；但缺三样：先用程序判、再用模型判（第 8 条）；用 Dk 的实际判断校准，且同时量「拦下的」和「放过好的」（第 21 条，我们只量了拦下率 2/6，没量误拦）；验收官输出「拿不准」一档（第 3 条）。
- **③记纠正（钩子＋纠正记录）：已有，方向与官方一致。** 官方的自动记忆也记「纠正」（第 11 条）。缺：官方同时记「你认可的做法」，我们只记了纠正，所以没有 Dk 判通过的稿，误拦率量不了。
- **④每周整理纠正：缺（一次没跑）。** 顶尖做法是闭环：写笔记→归类→数占比→改→重测→能回退（第 18、21 条）；规则分流（零例外→钩子，其余→规则／技能，第 9、13 条）；定期查矛盾和过时（`/doctor prompt-audit`，第 11 条）。桌面定时任务能承载，但电脑要醒着、首次要逐项批准工具（第 15 条）。
- **⑤考验收官（固定题库）：已有，但太小、结构单一。** 6 题低于官方起步量 20–50（第 3 条）；没分回归组与能力组；没留出集（第 5 条）；不清楚是否每题多跑几次（官方默认 3 次，第 16 条；我们现状待核）；没做「有这条规则／没这条规则」对照（第 16 条）。
- **⑥每周算五个数：缺（第一次定在 11/5）。** 顶尖做法：记录模型版本，免得把模型升级当成退化（第 16 条）；加一个只记录、不判失败的用量指标（第 23 条）；题库全拦住时要补新题防饱和（第 3 条）。本类没有讲「指标被刷」的问题（古德哈特），留给 (e) 类。

## 未能打开或未核清的

- 第 17 条 OpenAI 实践指南 PDF：已下载，本机提不出文字，内容仅二手。
- 第 24 条：Google 两份白皮书原文均未能打开。
- Microsoft 技术社区文章「Evaluating AI Agents: A Practical Guide with Microsoft Foundry」（https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/evaluating-ai-agents-a-practical-guide-with-microsoft-foundry/4500224）：页面能下载但正文没读出来（只拿到标题），未用。
- AutoGen AgentEval 论文（博客称 arXiv:2405.02178；搜索结果出现 arXiv:2402.09015，两个编号不一致，未核）：未打开。
- 第 16、14、11 条涉及的命令有版本要求（如 `/doctor prompt-audit` 需 v2.1.283 以上；桌面定时任务需 Claude 桌面版 1.1.5368 以上，页面写明）。本机版本我没查，需实测。
