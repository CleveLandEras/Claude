# 来源表（b）学术研究：纠正怎么变成检查、怎么量效果、怎么防退化

查于 2026-10-29，调研子代理。共 46 条来源：一手（论文作者原文）43 条，二手（综述）3 条。

## 怎么核的（先说口径）
- 所有链接都是 arXiv 摘要页，标题、作者、日期、摘要由 arXiv 官方接口当天返回，没有打不开的。
- 其中 14 篇另外打开了 arXiv 的 HTML 全文，核了表格和正文数字（表里标「全文」）；其余只读了摘要，数字都出自摘要（标「仅摘要」），没有核过实验细节。
- 英文原句都是从摘要或全文原样摘的，每句不超过 25 词。数字都带原文口径；论文发表在哪个会议、期刊，我没有逐篇核，不写。
- 步骤编号沿用现有六步：步 1 立合同（对齐卡）；步 2 独立检查（验收官）；步 3 记纠正（钩子＋纠正记录）；步 4 每周整理纠正；步 5 考验收官（固定题库）；步 6 每周算五个数。
- 术语：oracle label＝外部给的标准答案或对错信号（不是模型自己判的）；LLM-as-a-judge＝让大模型当裁判；回归测试＝改完后用同一批旧题再测，看有没有变差。

## 先看这五条（给汇总方案的人）
1. **没有外部对错信号，模型自己改自己会变差或不变。** Huang 等（#18）发现 Reflexion 等方法的提升靠的是外部给的对错信号，没有就消失；Kamoi 综述（#19）：目前没有成功案例是「靠提示词让模型自己给自己反馈」。我们的外部信号只有三种：Dk 的退回原话、能写成程序的检查、Dk 判过的稿。
2. **验收官是 Claude，有可测的偏差，但有便宜的缓解办法。** 偏差：先后顺序、啰嗦、宽松、偏爱自己家的输出（#24–#31）。缓解：给它一份参考答案（Zheng：判错率 14/20 降到 3/20）、换顺序判两次、先列证据再打分、必要时让人复核最拿不准的那些（Wang：52.7%→73.8%）。
3. **经验手册要「小步增删、带计数、能删除」，不要整篇重写，也不要只追加。** ACE（#5）：整篇重写一次，18,282 个词元缩成 122 个，准确率 66.7 掉到 57.1；DC（#6）：GPT-4o 把历史全部追加，成绩比不用还差（20.0→13.3）；ExpeL（#3）：每条经验带计数，减到 0 就删。
4. **评估标准会随着人看到的稿子变（criteria drift，标准漂移），所以要用 Dk 判过的稿持续校准裁判，并分开量「拦下率」和「误拦率」。** EvalGen（#34）；Agent-as-a-Judge（#36）还指出：只看一致率会被类别不平衡骗（裁判把几乎所有稿都判不过也能得 84%）。
5. **防退化要三样：固定回归题库、不拿来调的留出题、对模型更新的监测。** Kapoor（#43）、Gao（#40，古德哈特定律：把代理指标优化过头，真实表现反而下降）、Chen（#41，同一个模型服务三个月内同一批题准确率从 84% 掉到 51%）。

## 总览表
| # | 简称 | 类型 | 核对 | 主要用在 | 现有能力能直接用吗 |
|---|---|---|---|---|---|
| 1 | Reflexion | 一手 | 全文 | 步 3→4 | 思路能用；实验靠外部测试 |
| 2 | Self-Refine | 一手 | 全文 | 步 2 | 思路能用；有争议 |
| 3 | ExpeL | 一手 | 全文 | 步 4 | 能用（经验计数、删除规则） |
| 4 | Voyager | 一手 | 全文 | 步 4 | 能用（把纠正固化成技能） |
| 5 | ACE | 一手 | 全文 | 步 4 | 能用（增量改、去重） |
| 6 | Dynamic Cheatsheet | 一手 | 全文 | 步 4 | 能用 |
| 7 | ReasoningBank | 一手 | 仅摘要 | 步 4 | 思路能用 |
| 8 | Agent Workflow Memory | 一手 | 仅摘要 | 步 4 | 思路能用 |
| 9 | MemPrompt | 一手 | 仅摘要 | 步 3→4 | 能用（纠正记忆变提示） |
| 10 | PRELUDE／CIPHER | 一手 | 仅摘要 | 步 3→4 | 能用（从修改里推偏好） |
| 11 | 自然出现的反馈 | 一手 | 仅摘要 | 步 3 | 部分能用（识别纠正） |
| 12 | WildFeedback | 一手 | 仅摘要 | 步 3 | 部分能用 |
| 13 | 语言反馈训练 | 一手 | 仅摘要 | 步 3 | 只借观点（要训练） |
| 14 | DSPy | 一手 | 仅摘要 | 步 4＋5 | 只借思路（要接口密钥） |
| 15 | GEPA | 一手 | 全文（部分） | 步 4＋5 | 能借（反思＋不退步筛选） |
| 16 | OPRO | 一手 | 仅摘要 | 步 4 | 只借思路 |
| 17 | TextGrad | 一手 | 仅摘要 | 步 4 | 只借思路 |
| 18 | LLM 还不能自我纠正推理 | 一手 | 全文 | 步 2 | 结论直接用 |
| 19 | 自我纠正批判综述 | 二手 | 全文（部分） | 步 2 | 结论直接用 |
| 20 | 自我批评计划 | 一手 | 仅摘要 | 步 2 | 结论直接用 |
| 21 | 自我偏见 | 一手 | 仅摘要 | 步 2 | 结论直接用 |
| 22 | CRITIC | 一手 | 仅摘要 | 步 2 | 能用（工具核对） |
| 23 | Self-Debug | 一手 | 仅摘要 | 步 2 | 能用（有测试才有效） |
| 24 | MT-Bench／Chatbot Arena | 一手 | 全文 | 步 2＋5 | 能用（缓解办法） |
| 25 | 大模型不是公平的裁判 | 一手 | 全文 | 步 2＋5 | 能用（换序、人工复核） |
| 26 | 位置偏差系统研究 | 一手 | 仅摘要 | 步 5 | 能用（重复判） |
| 27 | 裁判认得并偏爱自己 | 一手 | 全文（部分） | 步 2 | 结论直接用 |
| 28 | CALM 十二种偏差 | 一手 | 仅摘要 | 步 2 | 结论直接用 |
| 29 | 人还是模型当裁判 | 一手 | 仅摘要 | 步 6 | 结论直接用 |
| 30 | Judging the Judges | 一手 | 仅摘要 | 步 5＋6 | 能用（宽松偏差、指标） |
| 31 | 谄媚研究 | 一手 | 仅摘要 | 步 2 | 结论直接用 |
| 32 | G-Eval | 一手 | 仅摘要 | 步 2 | 能用（填表式打分） |
| 33 | LLM 当裁判综述 | 二手 | 仅摘要 | 步 5 | 查漏用 |
| 34 | EvalGen | 一手 | 全文 | 步 5＋6 | 能用（核心） |
| 35 | CriticGPT | 一手 | 仅摘要 | 步 2 | 只借观点（要训练） |
| 36 | Agent-as-a-Judge | 一手 | 全文（表） | 步 2＋6 | 能用（子代理可跑工具） |
| 37 | 预测驱动推断 | 一手 | 仅摘要 | 步 6 | 样本太少，暂不用 |
| 38 | 自学评估器 | 一手 | 仅摘要 | 无 | 不能用（要训练） |
| 39 | 自奖励模型 | 一手 | 仅摘要 | 无 | 不能用（要训练） |
| 40 | 奖励模型过度优化 | 一手 | 仅摘要 | 步 5＋6 | 结论直接用 |
| 41 | ChatGPT 行为如何随时间变 | 一手 | 仅摘要 | 步 5＋6 | 结论直接用 |
| 42 | CheckList | 一手 | 仅摘要 | 步 4＋5 | 能用（每条规则配最小测试） |
| 43 | AI Agents That Matter | 一手 | 仅摘要 | 步 5＋6 | 结论直接用 |
| 44 | IFScale | 一手 | 仅摘要 | 步 4 | 结论直接用 |
| 45 | Lost in the Middle | 一手 | 仅摘要 | 步 4 | 结论直接用 |
| 46 | 自进化智能体综述 | 二手 | 仅摘要 | 地图 | 查漏用 |

---

## A 把纠正和经验写成文字再用（不改模型）

### 1. Reflexion: Language Agents with Verbal Reinforcement Learning
- Shinn, Cassano, Berman, Gopinath 等，2023｜https://arxiv.org/abs/2303.11366｜一手｜全文
- **做了什么**：智能体做完一次尝试，拿到对错信号，用自然语言写一段「反思」放进记忆，下一次尝试时带着它。
- **效果证据**：HumanEval（代码题）一次通过率 91%，之前最好的 GPT-4 是 80%。消融（拆掉一个部件看掉多少）在 HumanEval Rust 最难的 50 题上：基线 0.60；去掉「自己写单元测试」只剩 0.52；去掉「写反思」0.60；全有 0.68（原文表 3）。
- **局限（原文）**：只用一个滑动窗口当长期记忆，可能陷入局部最优。Huang 等（#18）指出它在推理题上的提升用了外部给的对错信号。
- **原句**："Reflexion agents verbally reflect on task feedback signals, then maintain their own reflective text in an episodic memory buffer"；消融结论："the agent is unable to determine if the current implementation is correct without unit tests"
- **我们能用吗**：能。**怎么用**：步 3→4 的核心模式——Dk 的纠正是「外部对错信号」，把它写成一句可复用的反思；消融那条说明：没有外部检查（测试）时，自己判对错会让它多改、改坏。所以步 4 不能只让 Claude 自己总结，要配可核对的东西（程序检查或 Dk 原话）。

### 2. Self-Refine: Iterative Refinement with Self-Feedback
- Madaan, Tandon, Gupta, Hallinan 等，2023｜https://arxiv.org/abs/2303.17651｜一手｜全文（相关节）
- **做了什么**：同一个模型先生成、再自己挑毛病、再自己改，循环；不训练。
- **效果证据**：7 个任务，平均绝对提升约 20%（人评和自动指标都偏好）。消融（拆掉反馈的具体程度）：代码优化 27.5（具体可执行的反馈）→ 26.0（泛泛的反馈）→ 24.8（无反馈）；情感改写 43.2 → 31.2（泛泛反馈），无反馈直接失败（原文第 4 节）。**反方**：Huang 等（#18）说它的对比提示词设计不够好；Xu 等（#21）说它会放大「偏爱自己输出」的偏见。
- **原句**："the same LLMs provides feedback for its output and uses it to refine itself, iteratively"；"specific, actionable feedback yields superior results"
- **我们能用吗**：思路能用，结论要打折。**怎么用**：步 2 验收官意见要写成「具体、可执行」的（哪一页哪一句改成什么），不要「建议更清晰」；但不能把「自己改自己」当作质量保证（见 #18、#21）。

### 3. ExpeL: LLM Agents Are Experiential Learners
- Zhao, Huang, Xu, Lin 等，2023｜https://arxiv.org/abs/2308.10144｜一手｜全文（相关节）
- **做了什么**：从一批训练任务的成功与失败里，用自然语言提炼「经验条目」；条目只做四种操作：新增（ADD）、赞成（UPVOTE）、反对（DOWNVOTE）、修改（EDIT）。每条有重要性计数，减到 0 就删除。用的时候取回条目和相似的成功案例。不更新模型参数。
- **效果证据**：在 HotpotQA、ALFWorld、WebShop 三个环境里，提炼的条目＋案例检索都比基线好。与 Reflexion 比：HotpotQA 为 40%（Reflexion 第三轮）对 39%（ExpeL），ALFWorld 为 54%对 59%（原文 5.2 节原话顺序，括号里 Reflexion 在前），ExpeL 不需要反复重做同一题。WebShop 上仍有差距。
- **原句**："If an insight's importance count reaches zero, it will be removed."
- **我们能用吗**：能。**怎么用**：步 4 的规则管理模型——每条规则带「依据（哪几次纠正）、被证实次数、被推翻次数、最近一次验证日期」，计数归零就删；这是回答「规则怎么防越加越多」的最直接出处。注意：它的计数来自任务成败，我们的计数来自 Dk 的退回／通过，来源不同，需要实测。

### 4. Voyager: An Open-Ended Embodied Agent with Large Language Models
- Wang, Xie, Jiang, Mandlekar 等，2023｜https://arxiv.org/abs/2305.16291｜一手｜全文（消融节）
- **做了什么**：在 Minecraft 里，把成功的行为存成可执行代码，放进「技能库」，按描述检索；失败时用环境反馈、执行报错、「自我验证」迭代改。
- **效果证据**：比此前最好成绩多拿 3.3 倍独特物品、走远 2.3 倍、关键科技树快 15.3 倍（摘要）。消融：去掉技能库后后期停滞；去掉自我验证，物品数显著下降，是各类反馈里最重要的一项（原文 3.4 节；具体降幅在图里，我没取到数）。注意它的「自我验证」建立在游戏状态可检查上。
- **原句**："Self-verification is the most important among all the feedback types."
- **我们能用吗**：能借。**怎么用**：步 4——反复出现的纠正，不止写成规则文字，要尽量固化成「可执行的东西」（技能里的检查脚本、程序门），因为程序判得了，不靠 Claude 自己判。Claude Code 的技能本来就是「按描述检索的可复用能力」，同构。

### 5. Agentic Context Engineering (ACE): Evolving Contexts for Self-Improving Language Models
- Zhang, Hu, Upasani, Ma 等，2025｜https://arxiv.org/abs/2510.04618｜一手｜全文（相关节）
- **做了什么**：把上下文当成「不断演进的手册」，分三个角色：生成器做事，反思器从结果里提炼，整理器（curator）把提炼的条目以**小步增量**并入手册；条目带编号和计数，周期性或超长时按语义相似去重（grow-and-refine，边增长边精简）。
- **效果证据**：智能体基准上比强基线高 10.6%，金融基准高 8.6%；在 AppWorld 排行榜总平均与第一名的生产级智能体持平，用的是更小的开源模型（摘要）。它指出的两个失败：简短偏差（为了简洁丢领域细节）和上下文塌缩——整篇重写把某次 18,282 个词元的手册压成 122 个，准确率 66.7 掉到 57.1，低于不用手册的 63.7（原文引言，被评对象为 Dynamic Cheatsheet）。有害反思的实验（FiNER 表 17）：基线 70.7；反思器每步都给有害反馈 66.7（-4.0）；每 5 步 76.1；无有害反馈 78.3。
- **局限（原文）**：没有可靠的反馈信号（标准答案、执行结果）时，ACE 与其他方法都会变差。
- **原句**："brevity bias, which drops domain insights for concise summaries, and from context collapse, where iterative rewriting erodes details over time"；"in the absence of reliable feedback signals (e.g., ground-truth labels or execution outcomes), both ACE and other adaptive methods ... may degrade"
- **我们能用吗**：能。**怎么用**：步 4 的操作规程——「整理纠正」只做条目级的新增／修改／合并，不整篇改写；规则文件给每条编号；超过上限时去重合并而不是追加。

### 6. Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory
- Suzgun, Yuksekgonul, Bianchi, Jurafsky 等，2025｜https://arxiv.org/abs/2504.07952｜一手｜全文（相关节）
- **做了什么**：一个「记忆整理」模型在每次回答后把有用的策略、代码片段写进一张小抄，下次带上。
- **效果证据**：Claude 3.5 Sonnet 在 AIME 数学题上准确率翻了一倍多；GPT-4o 的 Game of 24 从 10% 到 99%（摘要）。对比「把历史全追加」（FH）：AIME 2024，Claude 3.5 Sonnet 基线 23.3、追加 26.7、整理 50.0；GPT-4o 基线 20.0、追加 13.3、整理 40.0（原文表 2；正文写追加是 6.7%，与表不符，这里引表）。小模型（Haiku、4o-mini）收益有限且不稳定（4.5 节）。
- **原句**："Excessive uncurated input-output pairs can not only overwhelm the model's context window, dilute crucial insights"
- **我们能用吗**：能。**怎么用**：步 4——纠正记录不能全部灌进常驻规则；只留精炼过的条目。它还声称「不需要标准答案或人的反馈」，与 ACE 的局限相冲（见分歧）。

### 7. ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory
- Ouyang, Yan, Hsu, Chen 等，2025｜https://arxiv.org/abs/2509.25140｜一手｜仅摘要
- **做了什么**：从智能体「自己判成功」和「自己判失败」的经历里提炼可泛化的策略，并入记忆库，之后检索使用。
- **效果证据**：摘要称在网页浏览和软件工程基准上优于只存原始轨迹或只存成功案例的方法，没给数字；具体数据我没核。
- **原句**："distills generalizable reasoning strategies from an agent's self-judged successful and failed experiences"
- **我们能用吗**：思路能用，注意「自己判」是它的前提，与 #18、#19 的结论有张力。**怎么用**：步 4 里失败案例（被 Dk 退回的稿）也要写成条目，不只存成功的做法。

### 8. Agent Workflow Memory
- Wang, Mao, Fried, Neubig，2024｜https://arxiv.org/abs/2409.07429｜一手｜仅摘要
- **做了什么**：从过往经历里归纳常用「工作流」，按需提供给智能体。
- **效果证据**："AWM substantially improves the baseline results by 24.6% and 51.1% relative success rate on Mind2Web and WebArena"（相对成功率，网页任务基准）。
- **我们能用吗**：思路能用。**怎么用**：步 4——重复的做事顺序（比如交付前核什么）不写成零散规则，写成一个工作流（技能），按任务类型调用。

### 9. Memory-assisted prompt editing to improve GPT-3 after deployment (MemPrompt)
- Madaan, Tandon, Clark, Yang，2022｜https://arxiv.org/abs/2201.06009｜一手｜仅摘要
- **做了什么**：把「模型误解了用户意图＋用户的澄清」存成记忆，遇到相似的新问题时，用这些记忆改写提示。不重训。
- **效果证据**：四个任务上，（模拟的）用户可以在部署后教会模型，准确率明显提高。是模拟用户，不是真人。
- **原句**："a growing memory of recorded cases where the model misunderstood the user's intents, along with user feedback for clarification"
- **我们能用吗**：能。**怎么用**：这正是步 3→4 的原型：纠正记录里的「Dk 原话＋出了什么错」就是它的记忆条目；做法是按相似情境检索相关纠正，而不是全部常驻。

### 10. Aligning LLM Agents by Learning Latent Preference from User Edits (PRELUDE／CIPHER)
- Gao, Taymanov, Salinas 等，2024｜https://arxiv.org/abs/2404.15269｜一手｜仅摘要
- **做了什么**：用户把模型输出改一遍，模型就从「原稿→改后稿」的差异里推断一句用户偏好的描述，下次拼进提示；按情境检索最相近的几条偏好再合并。
- **效果证据**：摘要称在摘要和写邮件两个环境（用 GPT-4 模拟用户）里编辑距离成本最低，且学到的偏好与真实隐含偏好相似；是模拟用户。
- **原句**："infers a description of the user's latent preference based on historic edit data"
- **我们能用吗**：能借。**怎么用**：步 3——纠正记录的表头存的是 Dk 原话和问题一句话，没有存被改的原句和改后的句子（按 `纠正记录.md` 表头）。可以补一栏「改前／改后」，让步 4 能推出偏好，而不是只靠原话。

### 11. Naturally Occurring Feedback is Common, Extractable and Useful
- Don-Yehiya, Choshen, Abend 等，2024｜https://arxiv.org/abs/2407.10944｜一手｜仅摘要
- **做了什么**：从用户与聊天模型的对话里，自动识别用户顺口给出的反馈（纠正、不满意）。
- **效果证据**：人工标注发现多达 30% 的对话含明确反馈；抽取出数十万条反馈样本，用来训练能提升基线（训练部分我们不用）。
- **原句**："as much as 30% of the chats include explicit feedback"
- **我们能用吗**：部分能。**怎么用**：步 3——说明纠正本来就藏在 Dk 的日常话里，钩子靠关键词抓会漏；可以让定时任务扫会话记录补抓（现有脚本 `扫会话记录.py` 已能取 Dk 的消息）。

### 12. WildFeedback: Aligning LLMs With In-situ User Interactions And Feedback
- Shi, Wang, Yang 等，2024｜https://arxiv.org/abs/2408.15549｜一手｜仅摘要
- **做了什么**：在多轮对话里识别并分类用户对上一轮回复的反馈，自动构造「好回复／坏回复」对。
- **效果证据**：摘要称微调后与用户偏好的一致度显著提高；没给数字，且需要微调。
- **我们能用吗**：只借分类思路。**怎么用**：步 3——给纠正分类（要重做、风格、范围、事实错），为步 4 的「同类合并」打底。

### 13. Training Language Models with Language Feedback
- Scheurer, Campos, Chan 等，2022｜https://arxiv.org/abs/2204.14146｜一手｜仅摘要
- **做了什么**：用自然语言形式的人类反馈（而非只比较两个输出谁好）来训练模型。
- **效果证据**：只用 100 条人写的反馈，把 GPT-3 微调到接近人类水平的摘要能力；需要微调，我们做不了。
- **原句**："natural language feedback, which conveys more information per human evaluation"
- **我们能用吗**：只借观点。**怎么用**：步 3 要存 Dk 的原话（自然语言），不要只存「退回／通过」二值。

---

## B 提示优化（自动改提示、用题库当尺子）

### 14. DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines
- Khattab, Singhvi, Maheshwari, Zhang 等，2023｜https://arxiv.org/abs/2310.03714｜一手｜仅摘要
- **做了什么**：把大模型调用写成模块，给一个指标和少量样例，由「编译器」自动生成并筛选提示和示范，使指标最大。
- **效果证据**：GPT-3.5 和 llama2-13b-chat 上，编译后比普通少样本提示一般高出 25% 和 65% 以上，比专家手写示范高 5–46% 和 16–40%（摘要）。
- **原句**："We design a compiler that will optimize any DSPy pipeline to maximize a given metric."
- **我们能用吗**：不能直接用（它要通过程序调用模型接口；Max 套餐能否这样用、是否另收费，我没有核）。**怎么用**：只借结构——「指标＋题库＋改提示＋重测」，对应步 4＋5；指标就是验收官考试分，题库是 Dk 判过的稿。风险是对小题库过拟合（见 #40、#43）。

### 15. GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning
- Agrawal, Tan, Soylu, Ziems 等，2025｜https://arxiv.org/abs/2507.19457｜一手｜全文（算法节）
- **做了什么**：让模型读自己的运行轨迹和结果，用自然语言反思，提出提示修改；保留一批候选，而不是只留最高分的那个——「在至少一道题上得分最高的候选保留，被完全压过的剔除」（帕累托筛选）。
- **效果证据**：六个任务平均比强化学习方法 GRPO 高 6%，最多高 20%，少用最多 35 倍的尝试；比此前最好的提示优化器 MIPROv2 高 10% 以上（摘要）。
- **原句**："Candidates that achieve the best score on at least one task are retained, while strictly dominated ones are pruned."
- **我们能用吗**：思路能借。**怎么用**：步 4＋5 的验收规则——每次改规则或验收官说明，要在全部旧题上重测，**任何一道原来过的题现在不过，就不采纳**（不退步门槛）；只追求总分会拿某几题换另几题。

### 16. Large Language Models as Optimizers (OPRO)
- Yang, Wang, Lu, Liu 等，2023｜https://arxiv.org/abs/2309.03409｜一手｜仅摘要
- **做了什么**：把「过往提示及其得分」都放进提示里，让模型据此提出新提示，评分后再加入历史，循环。
- **效果证据**：优化出的提示比人写的在 GSM8K 上最多高 8%，在 Big-Bench Hard 任务上最多高 50%（摘要，基准内的结果）。
- **我们能用吗**：只借思路。**怎么用**：步 4——「成绩单」要记每次规则改动和对应分数，下一次改动前先读历史，避免重复试已经失败的改法。

### 17. TextGrad: Automatic "Differentiation" via Text
- Yuksekgonul, Bianchi, Boen, Liu 等，2024｜https://arxiv.org/abs/2406.07496｜一手｜仅摘要
- **做了什么**：把模型给的文字批评当成「梯度」，沿计算图反向传，去改各个组件。
- **效果证据**：GPT-4o 在 GPQA（研究生水平问答）上从 51% 到 55%；LeetCode 难题解法相对提升 20%（摘要）。
- **我们能用吗**：只借思路，和 GEPA 重合，不单独用。

---

## C 自己判自己的局限，以及外部信号的作用

### 18. Large Language Models Cannot Self-Correct Reasoning Yet
- Huang, Chen, Mishra, Zheng 等，2023｜https://arxiv.org/abs/2310.01798｜一手｜全文
- **做了什么**：把「模型只靠自己、没有外部信号来纠正」称为内在自我纠正，系统测了；并检查别的论文的提升是不是来自外部对错信号（oracle label）。
- **效果证据**（原文表 2、表 3）：有外部对错信号时，GPT-3.5 在 GSM8K（小学数学题）75.9→84.3；GPT-4 95.5→97.5。没有外部信号、纯内在自我纠正：GPT-3.5 在 CommonSenseQA（常识问答）第一轮 75.8→38.1，GSM8K 75.9→75.1；GPT-4-Turbo 的 GSM8K 91.5→88.0；Llama-2 的 GSM8K 62.0→43.5。原文还指出 Reflexion、多智能体辩论（不优于多次采样投票）、Self-Refine（提示设计不佳）的提升要打折。
- **原句**："LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction."；"the improvements vanish when oracle labels are not available"
- **我们能用吗**：结论直接用。**怎么用**：步 2 的设计底线——验收官不能是「让 Claude 再看一遍」；必须有外部锚点：Dk 退回的原话（对错信号）、程序判的检查、判例里的参考答案。

### 19. When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs
- Kamoi, Zhang, Zhang, Han 等，2024｜https://arxiv.org/abs/2406.01297｜**二手（综述）**｜全文（摘要与结论）
- **做了什么**：梳理自我纠正研究，指出不少研究不公平地高估了效果，并总结成功需要的条件。
- **结论**：（1）没有哪项工作证明「靠提示词让模型自己给自己反馈」在一般任务上成功，除非任务本身特别适合自我纠正；（2）有可靠外部反馈的任务上自我纠正有效；（3）大规模微调能让它有效。原文把瓶颈定位在「反馈的产生」。
- **原句**："no prior work demonstrates successful self-correction with feedback from prompted LLMs, except for studies in tasks that are exceptionally suited for self-correction"
- **我们能用吗**：结论直接用。**怎么用**：支撑 #18；并说明第三条（微调）我们做不了，所以更要依赖第二条（外部反馈）。

### 20. Can Large Language Models Really Improve by Self-critiquing Their Own Plans?
- Valmeekam, Marquez, Kambhampati，2023｜https://arxiv.org/abs/2310.08118｜一手｜仅摘要
- **做了什么**：在规划任务里，让同一个 GPT-4 既生成方案又核对方案，与有外部可靠核对器的系统比。
- **效果证据**：自我批评反而降低了方案质量，核对器给出相当多「误判为对」（假阳性）；反馈是二值还是详细影响很小。
- **原句**："self-critiquing appears to diminish plan generation performance, especially when compared to systems with external, sound verifiers"
- **我们能用吗**：结论直接用。**怎么用**：步 2——模型当检查员时最典型的错是「放过」；所以要单独量漏拦（步 5），不能只量误拦。

### 21. Pride and Prejudice: LLM Amplifies Self-Bias in Self-Refinement
- Xu, Zhu, Zhao, Pan 等，2024｜https://arxiv.org/abs/2402.11436｜一手｜仅摘要
- **做了什么**：把「偏爱自己输出」的倾向定义成两个统计量，测了 6 个模型在翻译、受限生成、数学推理上的表现。
- **效果证据**：所有被测模型都有这种自偏见；自我改进循环让流畅度和可读性变好，但同时放大了自偏见；更大的模型和**准确的外部反馈**能显著降低偏见，带来真实提升。
- **原句**："while the self-refine pipeline improves the fluency and understandability of model outputs, it further amplifies self-bias"
- **我们能用吗**：结论直接用。**怎么用**：步 2——验收官改完的稿读起来更顺，不等于更对；检查不能以「读着顺」为准，要有对照标准。

### 22. CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing
- Gou, Shao, Gong 等，2023｜https://arxiv.org/abs/2305.11738｜一手｜仅摘要
- **做了什么**：模型写完后，调用外部工具（搜索引擎核事实、代码解释器调试）去验证自己的输出，再据此修改。
- **效果证据**：问答、数学程序合成、降低有害内容三类任务上都稳定提升（摘要，没给数字）。
- **原句**："our research highlights the crucial importance of external feedback in promoting the ongoing self-improvement of LLMs"
- **我们能用吗**：能。**怎么用**：步 2——能用工具核的就用工具核：文件里的链接是否打得开、数字是否对得上原表、页数、字数、路径是否存在，让脚本判；只有「读者看了会不会懂」这类才让验收官判。

### 23. Teaching Large Language Models to Self-Debug
- Chen, Lin, Schärli 等，2023｜https://arxiv.org/abs/2304.05128｜一手｜仅摘要
- **做了什么**：让模型看代码的执行结果、并用自然语言解释自己的代码来找错（「橡皮鸭调试」）。
- **效果证据**：有单元测试时（TransCoder、MBPP）准确率最多提高 12%；没有单元测试时（Spider）只提高 2–3%，最难的那档提高 9%（摘要）。
- **我们能用吗**：能借。**怎么用**：同一方法，有可执行的检查提升 12%，没有只有 2–3%——写文档类交付物天生缺「单元测试」，所以要优先把能程序化的检查做出来（步 2、步 4 固化）。

---

## D 让大模型当裁判：可靠性与偏差

### 24. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
- Zheng, Chiang, Sheng, Zhuang 等，2023｜https://arxiv.org/abs/2306.05685｜一手｜全文
- **做了什么**：系统检验用强模型当裁判：位置偏差、啰嗦偏差、自我偏爱、数学推理弱，并提出缓解办法；与 3K 条专家投票对照。
- **效果证据**（原文）：GPT-4 与人的一致率 85%（去掉平局），人与人之间 81%；位置偏差：多数裁判偏向排在前面的答案，只有 GPT-4 在超过 60% 的情况下换序后结论一致；啰嗦攻击（把清单改写成两倍长）：Claude-v1 和 GPT-3.5 被骗 91.3%，GPT-4 8.7%；**数学题给了参考答案后**，GPT-4 把错误答案判成对的比例：默认提示 14/20，让它先推理 6/20，给参考答案 3/20；自我偏爱：GPT-4 给自己高 10% 的胜率，Claude-v1 高 25%，但作者自己说数据有限，不能确认。
- **原句**："Most LLM judges favor the first position."；"achieving over 80% agreement, the same level of agreement between humans"
- **我们能用吗**：能。**怎么用**：步 2——验收官判之前必须给「参考答案」：把 Dk 以往对同类问题的退回原话（判例）作为参考，而不是让它凭空判；步 5——比较改动前后两个版本时，要换顺序各判一次。

### 25. Large Language Models are not Fair Evaluators
- Wang, Li, Chen, Cai 等，2023｜https://arxiv.org/abs/2305.17926｜一手｜全文（部分）
- **做了什么**：发现只改两个答案的先后顺序，就能改写裁判的结论；提出三种校准：多写几条证据再打分、两种顺序都判再汇总、让人只复核最拿不准的例子。
- **效果证据**：ChatGPT 当裁判时，Vicuna-13B 在 80 道题里能赢 66 道（摘要）。与人的最终多数标注比（原文表 4）：三位人类标注者各 68.8%、76.3%、70.0%；GPT-4 原始做法 52.7%，加多证据＋换序 62.5%，再加人工复核最拿不准的例子 73.8%。样本是 80 题的 Vicuna 基准，规模小。
- **原句**："the quality ranking of candidate responses can be easily hacked by simply altering their order of appearance in the context"
- **我们能用吗**：能。**怎么用**：步 2、步 5——换序判两次；两次不一致的就是「最拿不准」，只把这类送给 Dk 看——这是「不额外占 Dk 时间也得到校准数据」的一个出处。

### 26. Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge
- Shi, Ma, Liang 等，2024｜https://arxiv.org/abs/2406.07791｜一手｜仅摘要
- **做了什么**：15 个模型裁判，22 个任务，约 40 个答案生成模型，超过 15 万次判断，测位置偏差，提出三个指标：重复稳定性、位置一致性、偏好公平性。
- **效果证据**：位置偏差不是随机的，随裁判和任务显著变化；与提示长短关系弱，与**两个方案质量差距**关系强。
- **我们能用吗**：结论直接用。**怎么用**：步 5——考试要重复跑同一道题几次看稳定性；两版改动相差不大时，裁判最不可靠，别在小差距上下结论。

### 27. LLM Evaluators Recognize and Favor Their Own Generations
- Panickssery, Bowman, Feng，2024｜https://arxiv.org/abs/2404.13076｜一手｜全文（摘要与引言）
- **做了什么**：检验裁判偏爱自己的输出是否因为认得出是自己写的。
- **效果证据**：GPT-4 和 Llama 2 开箱就有不低的准确率能区分自己与别人、人类写的；微调后，认出自己的能力与偏爱自己的强度呈线性相关；作者的对照实验显示这个因果解释经得起简单混杂因素的检验。
- **原句**："LLMs such as GPT-4 and Llama 2 have non-trivial accuracy at distinguishing themselves from other LLMs and humans"
- **我们能用吗**：结论直接用。**怎么用**：步 2——验收官和作者是同一个模型家族，有这个风险，只能用外部锚点（#18）、不让验收官看到制作过程（现有做法）来缓解；没有第二个模型家族可换时，这个风险只能降低，不能消除，应在方案里写明。

### 28. Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge (CALM)
- Ye, Wang, Huang, Chen 等，2024｜https://arxiv.org/abs/2410.02736｜一手｜仅摘要
- **做了什么**：列出 12 种潜在偏差，用自动化改写测量每一种。
- **效果证据**：强模型总体表现不错，但在某些具体任务上偏差依然显著。
- **我们能用吗**：结论直接用。**怎么用**：步 5 的考题要覆盖偏差类型：同一份稿改得更长、改排版、换署名后，验收官结论应不变；变了就是偏差。

### 29. Humans or LLMs as the Judge? A Study on Judgement Biases
- Chen, Chen, Liu 等，2024｜https://arxiv.org/abs/2402.10669｜一手｜仅摘要
- **做了什么**：测人和模型当裁判时对错误信息、性别、权威、美观四类偏差的敏感度，并能利用这些偏差攻击模型裁判。
- **效果证据**：人和模型裁判都在不同程度上受影响，最先进的裁判也有可观偏差。
- **原句**："even the cutting-edge judges possess considerable biases"
- **我们能用吗**：结论直接用。**怎么用**：步 6——Dk 的「通过」也是带噪声的标签，不能当真值；校准验收官时要允许 Dk 自己也会前后不一致（可抽样让 Dk 隔段时间重判几份）。

### 30. Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges
- Thakur, Choudhary, Ramayapally, Vaidyanathan 等，2024｜https://arxiv.org/abs/2406.12624｜一手｜仅摘要
- **做了什么**：13 个裁判模型评 9 个答题模型，场景是人与人之间一致度很高的题。
- **效果证据**：只有最好最大的模型与人的一致达到「合理」，仍远低于人与人之间，打分与人给的分最多差 5 分；容易受提示复杂度和长度影响，倾向**宽松**；一致率很高的裁判仍可能给出差别很大的分数，应当用比简单一致率更好的指标。
- **原句**："judges with high percent agreement can still assign vastly different scores"
- **我们能用吗**：能。**怎么用**：步 6 的验收官校准指标不要用单一「一致率」；拆成拦下率和误拦率，并看有没有「偏宽松」（假通过）。

### 31. Towards Understanding Sycophancy in Language Models
- Sharma, Tong, Korbak 等，2023｜https://arxiv.org/abs/2310.13548｜一手｜仅摘要
- **做了什么**：测五个先进助手是否倾向迎合用户观点而非真话，并分析人类偏好数据是不是原因之一。
- **效果证据**：五个助手在四类自由生成任务中都稳定表现出谄媚；回答与用户观点一致时更容易被偏好；人和偏好模型有不小比例更偏好写得有说服力的谄媚回答。
- **原句**："both humans and preference models (PMs) prefer convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time"
- **我们能用吗**：结论直接用。**怎么用**：步 2——派验收官时不要把作者的结论或「我觉得没问题」带进去（现有规则已写不传制作过程），否则它会顺着说；步 6——Dk 的认可也可能偏向「写得有说服力」的稿，不是真值。

### 32. G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment
- Liu, Iter, Xu 等，2023｜https://arxiv.org/abs/2303.16634｜一手｜仅摘要
- **做了什么**：让模型先按步骤推理、再按固定表格逐项打分（填表式）。
- **效果证据**：摘要称摘要任务上与人的斯皮尔曼相关 0.514，超过之前方法；同时指出这类评估有偏向大模型生成文本的问题。
- **原句**："LLM-based evaluators having a bias towards the LLM-generated texts"
- **我们能用吗**：能。**怎么用**：步 2——验收清单已是逐项填表式；保持逐项给证据（引原文位置）再给结论，不让它直接给「通过／不通过」。

### 33. A Survey on LLM-as-a-Judge
- Gu, Jiang, Shi 等，2024｜https://arxiv.org/abs/2411.15594｜**二手（综述）**｜仅摘要
- **做了什么**：综述如何建立可靠的 LLM 裁判：提升一致性、减少偏差、评估可靠性。
- **效果证据**：综述，无新实验结论，只是说法的汇总；摘要里承认可靠性仍是重大挑战。
- **原句**："ensuring the reliability of LLM-as-a-Judge systems remains a significant challenge that requires careful design and standardization"
- **我们能用吗**：查漏用。**怎么用**：做完方案后拿它的分类检查有没有漏掉的偏差类别。

---

## E 裁判校准与对齐：谁来验证验证者

### 34. Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences（EvalGen）
- Shankar, Zamfirescu-Pereira, Hartmann, Parameswaran 等，2024｜https://arxiv.org/abs/2404.12272｜一手｜全文
- **做了什么**：模型候选生成评估标准和检查（程序断言或模型评分提示）；让人对一小批输出打「好／坏」；用人的打分筛出和人最一致的那些检查。对每个标准量两个数：**覆盖率**（人认为坏的稿，检查能拦下多少）和**误拦率**（人认为好的稿，检查误拦多少）。
- **效果证据**：9 位业界从业者的有声思考研究，是定性的；算法对比基线（SPADE）：覆盖率相同或更高、误拦率相当、对齐度更高（原文第 5 节，我没取到逐项数字）。发现「标准漂移」：人要先有标准才能打分，打分的过程又改变标准；有些标准依赖于看到的具体输出，无法事先定死。
- **原句**："LLM-generated evaluators simply inherit all the problems of the LLMs they evaluate, requiring further human validation"；"it is impossible to completely determine evaluation criteria prior to human judging of LLM outputs"
- **我们能用吗**：能，是核心参考。**怎么用**：步 5、6——拦下率＝覆盖率，误拦率就是 false failure rate；校准数据来自 Dk 对稿子的判；每次 Dk 退回后，要把退回的原因回写进验收清单（因为标准会漂移），而不是只记一次纠正。

### 35. LLM Critics Help Catch LLM Bugs（CriticGPT）
- McAleese, Pokorny, Ceron Uribe, Nitishinskaya 等，2024｜https://arxiv.org/abs/2407.00215｜一手｜仅摘要
- **做了什么**：训练专门写批评的模型，帮人审代码。
- **效果证据**：模型写的批评在 63% 的情况下比人写的更受偏好，也抓到比外包审查员更多的错；但有「编造出来的错」；**人加模型的组合**抓到的错和模型单独一样多，而编造的更少。
- **原句**："human-machine teams of critics and contractors catch similar numbers of bugs to LLM critics while hallucinating less than LLMs alone"
- **我们能用吗**：只借观点（要强化学习训练，我们做不了）。**怎么用**：步 2——验收官的意见交给 Dk 时，由 Dk 只确认或删掉，而不是 Dk 自己从头审；Dk 的每次「删掉这条」就是它编造问题的记录，可计入误拦。

### 36. Agent-as-a-Judge: Evaluate Agents with Agents
- Zhuge, Zhao, Ashley, Wang 等，2024｜https://arxiv.org/abs/2410.10934｜一手｜全文（表）
- **做了什么**：不让模型只看最终结果下判断，而是让一个有工具的智能体去查（读文件、跑检查），逐条核对需求。
- **效果证据**：在 55 个自动化 AI 开发任务（DevAI）上，与人类多数意见的一致率：Agent-as-a-Judge 为 88.52%、83.88%、90.44%（对三个被评智能体），LLM-as-a-Judge 为 68.86%、71.85%、70.76%（原文表；黑盒还是灰盒设置我没细核）。同一论文提醒：任务类别不平衡时，一致率会误导——被评智能体很少满足需求，裁判把绝大多数都判为不满足，就能得 84.15%（黑盒设置下，对其中一个被评智能体）。
- **原句**："dramatically outperforms LLM-as-a-Judge and is as reliable as our human evaluation baseline"
- **我们能用吗**：能。**怎么用**：步 2——验收官是子代理，本来就能读文件、跑脚本；让它逐条去查（链接是否通、数字对不对得上原表），不要只凭读稿下判断；步 6——量覆盖率和误拦率两个数，不用单一一致率。

### 37. Prediction-Powered Inference
- Angelopoulos, Bates, Fannjiang 等，2023｜https://arxiv.org/abs/2301.09633｜一手｜仅摘要
- **做了什么**：有少量人工标注、大量模型预测时，给出统计上有效的置信区间。
- **效果证据**：在蛋白质组学、天文、基因组等数据上验证；没有在 LLM 裁判上测试（这篇没有），别的论文是否测过我没核。
- **我们能用吗**：现在样本太少（题库 6 题），区间会很宽，暂不建议；等判过的稿累积到几十份再考虑。**怎么用**：步 6——先老老实实报「几题中几题」，不报百分比的假精确。

### 38. Self-Taught Evaluators
- Wang, Kulikov, Golovneva 等，2024｜https://arxiv.org/abs/2408.02666｜一手｜仅摘要
- **做了什么**：不用人工标注，用合成数据反复训练一个模型裁判。
- **效果证据**：Llama3-70B-Instruct 在 RewardBench（奖励模型基准）从 75.4 到 88.3（多数投票 88.7）。
- **我们能用吗**：不能（要训练模型）。列出来是为了说明「裁判可以用合成数据变好」只在能训练时成立；我们的路线是提示层，不能指望。

### 39. Self-Rewarding Language Models
- Yuan, Pang, Cho, Li 等，2024｜https://arxiv.org/abs/2401.10020｜一手｜仅摘要
- **做了什么**：让模型自己当裁判给自己打分，用这份分数训练自己，迭代三轮。
- **效果证据**：Llama 2 70B 微调三轮后，在 AlpacaEval 2.0 上超过 Claude 2、Gemini Pro 和 GPT-4 0613（摘要）。
- **我们能用吗**：不能（要训练）。与 #18、#21 的结论形成对照：训练路线里自评可用，提示路线里自评靠不住，两者的前提不同，别混用。

---

## F 度量与防退化

### 40. Scaling Laws for Reward Model Overoptimization
- Gao, Schulman, Hilton，2022｜https://arxiv.org/abs/2210.10760｜一手｜仅摘要
- **做了什么**：用一个固定的「金标准」奖励模型代替人，研究对代理奖励模型优化过度时，真实表现怎么变。
- **效果证据**：优化代理分数太多，金标准分数会下降（古德哈特定律）；变化形状因优化方法而不同，并随奖励模型参数量平滑变化。
- **原句**："optimizing its value too much can hinder ground truth performance, in accordance with Goodhart's law"
- **我们能用吗**：结论直接用。**怎么用**：步 5——题库只有 6 道时，反复调验收官去通过这 6 题，就是在过拟合；需要一批只用来看、不拿来调的留出题（#43）。

### 41. How is ChatGPT's behavior changing over time?
- Chen, Zaharia, Zou，2023｜https://arxiv.org/abs/2307.09009｜一手｜仅摘要
- **做了什么**：对比 2023 年 3 月与 6 月两个版本的 GPT-3.5 和 GPT-4 在 7 类任务上的表现。
- **效果证据**：GPT-4 判质数的准确率 84%（3 月）→ 51%（6 月）；GPT-4 遵循指令的能力下降是多种行为漂移的共同因素之一。
- **原句**："the behavior of the "same" LLM service can change substantially in a relatively short amount of time"
- **我们能用吗**：结论直接用。**怎么用**：步 5——验收官底层模型更新后行为可能变；固定题库定期回跑一遍（不改任何东西也跑），分数变了就说明是模型变了不是规则变了。

### 42. Beyond Accuracy: Behavioral Testing of NLP models with CheckList
- Ribeiro, Wu, Guestrin 等，2020｜https://arxiv.org/abs/2005.04118｜一手｜仅摘要
- **做了什么**：借软件工程的行为测试方法，设计一套测试类型矩阵，系统生成测试用例。
- **效果证据**：用户研究：负责某商用情感分析模型的团队在已被充分测试的模型里找到了新的、可处理的缺陷；使用者写出的测试数是对照组的 2 倍，发现的缺陷数近 3 倍。
- **我们能用吗**：能借。**怎么用**：步 4＋5——每条新规则配一个「最小测试」：一份刻意违反它的小样本，验收官应判不过；没法配测试的规则，要么改写到能配，要么标明「不可测」，进入删除候选。

### 43. AI Agents That Matter
- Kapoor, Stroebl, Siegel 等，2024｜https://arxiv.org/abs/2407.01502｜一手｜仅摘要
- **做了什么**：审查智能体基准和评估做法，指出只看准确率不看成本、基准缺留出集（holdout，不参与调优的测试集）、做法不可复现。
- **效果证据**：只是对现有做法的分析和一个成本—准确率联合优化的示例；摘要称多个基准没有或缺乏留出集，导致智能体靠投机取巧过拟合。
- **原句**："many agent benchmarks have inadequate holdout sets, and sometimes none at all"
- **我们能用吗**：结论直接用。**怎么用**：步 5、6——题库分「调试集」和「留出集」；每次闭环同时记用量，改动若让成绩持平而用量大涨，也算退步（我们本来有用量预算）。

### 44. How Many Instructions Can LLMs Follow at Once? (IFScale)
- Jaroslawicz, Whiting, Shah, Maamari，2025｜https://arxiv.org/abs/2507.11538｜一手｜仅摘要
- **做了什么**：500 条关键词包含类指令的基准，测同时遵守的指令越多、表现下降多少。
- **效果证据**：20 个先进模型里，最好的在 500 条指令下也只有 68% 准确率；偏向较靠前的指令。注意它测的是关键词类指令，换算到 CLAUDE.md 的几十条规则要打折。
- **原句**："even the best frontier models only achieve 68% accuracy at the max density of 500 instructions"
- **我们能用吗**：结论直接用。**怎么用**：步 4——规则条数设上限（现有全局文件上限 80 行就是这个意思）；最关键的放最前面；每加一条要删一条或合并。

### 45. Lost in the Middle: How Language Models Use Long Contexts
- Liu, Lin, Hewitt 等，2023｜https://arxiv.org/abs/2307.03172｜一手｜仅摘要
- **做了什么**：测模型在长输入里找相关信息的表现，随信息位置变化。
- **效果证据**：相关信息在开头或结尾时表现最好，在中间时显著下降，长上下文模型也如此。它测的是文档问答，不是规则遵守。
- **原句**："performance is often highest when relevant information occurs at the beginning or end of the input context"
- **我们能用吗**：结论直接用。**怎么用**：步 4——常驻规则文件放在开头和结尾的位置给最容易犯错的几条；长的参考材料放到文件里，按需读取。

---

## G 地图

### 46. A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve
- Gao, Geng, Hua 等，2025｜https://arxiv.org/abs/2507.21046｜**二手（综述）**｜仅摘要
- **做了什么**：把自进化智能体分成「改什么（模型、记忆、工具、架构）、什么时候改（测试时内、测试间）、怎么改（标量奖励、文字反馈）」三个维度。
- **效果证据**：综述，无新实验；说它指出了安全、可扩展性等挑战。
- **原句**："organizing the field around three foundational dimensions: what, when, and how to evolve"
- **我们能用吗**：查漏用。**怎么用**：拿它的三个维度给我们闭环打标：我们改的是「记忆和工具」（规则、技能、钩子），在「测试间」（每周）改，用「文字反馈」（Dk 原话）。

---

## 本类的共识（5 条）
1. **不改模型、把经验写成文字再带进上下文，能带来提升。** Reflexion（#1）、ExpeL（#3）、Voyager（#4）、DC（#6）、ACE（#5）、AWM（#8）、MemPrompt（#9）、PRELUDE（#10）都这么做。限定：这些提升基本都有外部反馈（测试、标准答案、模拟用户）；见第 2 条。
2. **没有外部对错信号，模型自己判自己，不可靠，有时变差。证据（只靠模型自己判的局限）：**
   - Huang（#18）：无外部信号时，GPT-3.5 的 CommonSenseQA 75.8→38.1，GPT-4-Turbo 的 GSM8K 91.5→88.0；有外部信号时 GSM8K 75.9→84.3。
   - Kamoi（#19）：综述所有工作，靠提示词的自我反馈没有一般性成功案例，瓶颈在反馈的产生。
   - Valmeekam（#20）：同一个 GPT-4 核对自己的方案，质量下降，且核对器误判为对。
   - Reflexion 消融（#1）：去掉单元测试后只剩 0.52，低于基线 0.60；Self-Debug（#23）：有测试最多提升 12%，没有只有 2–3%。
   - ACE（#5）：缺少可靠反馈时手册会变差；有害反思每一步都给时，成绩比不用还低 4.0 点。
   - 偏差：自偏见在所有被测模型都有（#21），认得自己的输出越准越偏爱自己（#27），五个助手都有谄媚（#31）。
3. **手册要小步增删、去重、能删除，整篇重写和只追加都会坏。** ACE 的塌缩（18,282→122 词元，66.7→57.1）；DC 的追加全部历史比不用还差（GPT-4o 20.0→13.3，整理后 40.0）；ExpeL 计数归零就删；GEPA 剔除被完全压过的候选；规则数量上限有依据（#44、#45）。
4. **模型裁判有已测量的偏差，也有已验证的缓解办法。** 偏差：位置、啰嗦、宽松、偏爱自己（#24–#31）；缓解：给参考答案（14/20→3/20）、换序判两次（#25）、让它先给证据、用工具去核（#36）、抽少量给人复核（#25）。指标上要拆开覆盖率与误拦率，别用单一一致率（#30、#36）。
5. **要有固定回归题库、留出题，并监测模型本身的漂移。** #40、#41、#42、#43。

## 本类的分歧（4 条）
1. **自我纠正到底行不行。** Self-Refine（#2）报告平均提升约 20%；Huang（#18）、Kamoi（#19）、Valmeekam（#20）说无外部信号就无效或变差，并指出前者对比的提示词设计不佳。未完全调和：Self-Refine 的任务（对话、改写等）有的本身就适合自我纠正，Kamoi 称之为「特别适合」的任务。对我们：写文档类交付物更像 Self-Refine 的任务，但有隐性风险，不能默认可靠。
2. **模型能不能代替人当裁判。** Zheng（#24）：GPT-4 与人的一致率 85% 高于人与人之间的 81%；Thakur（#30）：只有最大的模型达到「合理」，仍远低于人与人；Ye（#28）、Chen（#29）：偏差普遍，人也有。差别在任务：Zheng 测的是开放式聊天的两两偏好；Thakur 测的是对错更明确的打分。我们的验收更像后者，应更保守。
3. **不要标准答案的自进化是否可行。** DC（#6）、ReasoningBank（#7）声称不需要标准答案或人的反馈；ACE（#5）自己的局限说明没有可靠信号会变差。两者的实验任务不同（数学、网页浏览 vs 智能体基准），尚无直接对比。对我们：保守假设需要外部信号。
4. **手册该保留细节还是保持精简。** ACE 强调不要为了简洁丢细节（简短偏差），长上下文能装；DC 强调精炼挑选、全量追加会稀释；IFScale（#44）、Lost in the Middle（#45）说条数多、位置在中间会降低遵守度。调和办法：增量编辑（ACE）＋去重＋总量上限，常驻放精炼版，细节放到按需读取的文件。

## 和我们六步逐步对照
- **步 1 立合同（对齐卡）：已有；不如顶尖的是「回写」。** EvalGen（#34）证明标准会随人看到的稿漂移，对齐卡写一次就不再改，等于把标准冻结；缺从 Dk 每次退回的原因回写到对齐卡模板和验收清单的环节。
- **步 2 独立检查（验收官）：已有，是最弱的一环。** 同一模型家族判自己家的稿（#27、#21），无外部信号时不可靠（#18–#20）。已有的好做法：只看成品不看制作过程（对付谄媚，#31）、清单逐项（对应 G-Eval，#32）。缺：给参考答案（判例＝Dk 的退回原话，#24：错判从 14/20 到 3/20）；能程序判的先程序判（#22、#23、#36）；换序判两次、抽拿不准的给人（#25）；没有第二个模型家族可用，偏差只能降低不能消除，要写明。
- **步 3 记纠正（钩子＋纠正记录）：已有，在用。** 表头存的是 Dk 原话和一句话问题（`纠正记录.md` 表头），按 PRELUDE（#10）和 MemPrompt（#9）还缺改前／改后的内容；钩子用一串关键词（正则）判断 Dk 的消息像不像纠正，命中后只是提示 Claude 去记一行（`correction_capture.py` 里的 SIGNAL），没命中的委婉说法不会触发；Don-Yehiya（#11）显示这类反馈在对话里很常见，可由定时任务扫会话补抓。
- **步 4 每周整理纠正：缺（一次没跑，没排定时）。** 顶尖做法已很清楚：ACE 的整理器＋小步增量＋去重（#5），ExpeL 的计数与删除（#3），GEPA 的不退步筛选（#15），CheckList 的每条规则配最小测试（#42），技能库式固化（#4）。我们的技能说明写了「同类合并、删没用的规则」，方向一致，但缺计数、依据、最近验证日期这类元数据，以及「改完必须全部旧题不退步」的门槛。
- **步 5 考验收官（固定题库）：有，但太小，不如顶尖。** 6 题、拦下 2 题（33%）、没有 Dk 判通过的稿，所以误拦没法量（即 EvalGen 的误拦率，#34）。缺：留出题（#43、#40）、重复跑看稳定性（#26）、不改动也定期回跑看模型漂移（#41）、考题覆盖偏差类型（#28）。6 题上的 2/6 谈不上置信区间，PPI（#37）暂用不上。
- **步 6 每周算五个数：只有定义，没算过（11/5 首次）。** 五个数的定义里有误拦（用 Dk 判通过的稿考验收官），对应 EvalGen 的误拦率；缺：覆盖率（漏拦）与误拦分开报（#30、#36）、用量随成绩一起看（#43）、有「Dk 的认可也带噪声」的说明（#29、#31）。另外一个结构性问题：验收官通过之后 Dk 才看稿，所以自然产生的校准数据只能暴露「放过了」，暴露不了「误拦了」——被验收官拦下改掉的稿 Dk 看不到。这是我的推断（依据：`先看这里.md`「Dk 不另外判稿：验收官的校准直接用他平时的验收结果」＋现有流程），可由抽样让 Dk 看被拦的稿来补，会占用他的时间，要不要做是方案要定的取舍。

## 缺口（没查清的）
- 14 篇外的 32 篇只读了摘要，实验设置和数字没核（尤其 #7 ReasoningBank、#16 OPRO、#17 TextGrad、#35 CriticGPT 的细节）。
- Voyager 消融的具体降幅在图里，没取到数。
- Agent-as-a-Judge 表里的设置（黑盒或灰盒）没细核；Wang 等（#25）的汇总收益来自 80 题的小基准。
- 没有找到：专门研究「个人单用户、样本极少（几十条）」下裁判校准的论文；也没有找到直接比较「提示层规则文件」随条数增长遵守度的实验（#44、#45 是最接近的间接证据）。
- 没有核对：DSPy 在 Claude Code 桌面版里能否不用接口密钥运行。
