# 来源表 (c)：一线实践者

查于 2026-10-29，调研子代理。共 38 条，其中一手 35 条、二手 3 条（第 16、25、26 条）。
说明：
- 每条链接都在本次实际打开过，没有打不开的；Boris Cherny 的原帖（X 上的串）没找到，只有转述，已标二手。
- 「原文」一栏的英文句子是抓取工具返回的，我没有再逐字对照原页面；验收官抽查时以原页面为准。
- 第 3 条（Hamel 与 Shreya 的 FAQ）全文约 15.4 万字，我只读了前 10 万字。
- Simon Willison 没有专门写 CLAUDE.md／AGENTS.md 的文章（搜索未命中），第 12–14 条用的是他写智能体循环、检查和技能的文章。
- 步骤编号：① 立合同　② 独立检查（验收官）　③ 记纠正　④ 每周整理纠正　⑤ 考验收官　⑥ 每周算五个数。
- 词：「抓出率」(TPR) ＝真有问题的稿子里被检查抓出的比例；「放行率」(TNR) ＝没问题的稿子里被正确放行的比例。

## 一、错误分析与裁判对齐（Hamel Husain、Shreya Shankar）

### 1. Your AI Product Needs Evals｜Hamel Husain｜2024-03-29
- 链接：https://hamel.dev/blog/posts/evals/
- 一手（作者本人文章）
- 做了什么：把「看数据」当核心工作，先给样本打好／坏二元标签；失败案例持续变成单元测试（Rechat 的助手 Lucy 有「数百条」）；三层：每次改动跑单元测试、定期人工＋模型评、重大改版后才做 A/B；测试结果随时间记录、画图看某类错误修复前后的占比。
- 效果证据：案例（Rechat），无通过率数字。文中说 Lucy 早期提示词调优后停滞，修一个失败常冒出另一个。
- 能用：能。只用文件和脚本即可。
- 怎么用：③④——纠正记录里的每条是一个「失败案例」，整理时变成一条可重跑的检查（考题）；⑥ 里按类记录某类错误的出现次数随时间的变化。
- 原文："You must remove all friction from the process of looking at data."

### 2. Using LLM-as-a-Judge For Evaluation: A Complete Guide｜Hamel Husain｜2024-10-29，2026-09-01 改过
- 链接：https://hamel.dev/blog/posts/llm-judge/
- 一手
- 做了什么：「批注影子法」(critique shadowing)：选一个说了算的领域专家，让他对样本给通过／不通过和一段文字批注；批注当作裁判提示词里的示例；与专家比一致度，迭代到够用；再在没见过的数据上做错误分析。起步约 30 条样本，直到不再出现新的失败类型。数据切成训练 10–20%、调试 40–45%、测试 40–45%（测试集只跑一次）；报告抓出率和放行率，不只报一致率（例：总是放行、错误率 5% 的集合，一致率也有 95%）。
- 效果证据：有案例数字。Honeycomb 的查询助手三轮迭代后与专家一致度超过 90%；作者自称帮助过 30 多家公司；文中示例表里某分段失败率 75%（20 条）。「批注示例提高一致度 15–20%」是作者自述，无公开研究。
- 能用：能，但要 Dk 当那个「专家」。成本在于 Dk 要给批注。
- 怎么用：⑤——把「Dk 判过的稿」作为专家标注，考验收官时分别报抓出率和放行率（我们现在只有抓出率，因为没有 Dk 判通过的稿）；②——验收官的提示词里放 Dk 的批注原句作示例。
- 原文："You have to go through the process again and measure the results."（模型更新等重大变化后）

### 3. AI Evals: Everything You Need to Know（FAQ）｜Hamel Husain、Shreya Shankar｜2026-09-18，09-21 更新
- 链接：https://hamel.dev/blog/posts/evals-faq/
- 一手
- 做了什么：把整套做法写成问答。错误分析四步：收真实记录→在自己笔记里记下失败（开放编码）→归成失败分类表（轴向编码）→循环到不再出新类型。至少看 100 条；前 30 条自己标。确定性规则能判的用代码检查，需要人式判断的才用 LLM 裁判；每种失败一个裁判，不做「总体质量」一个裁判；「只对提示词修完后仍然存在的失败建自动检查，简单修复不需要检查设施」。每种失败标 100–200 条再校准裁判。维护：重大改动后重做错误分析，常规 2–4 周一轮（至少 100 条新记录），两轮之间每周看 10–20 条异常；「总是通过的检查降频或下线，贵的（LLM 裁判）比便宜的先退」；每条检查保持二元，汇报「全过率」（一条样本只有全部检查都过才算过），不做加权综合分；检查分组、区分「阻断发布」和「可容忍」。
- 效果证据：作者经验（50+ 公司），无对照实验。
- 能用：能，且是本类里最直接回答「检查越加越多怎么办」的一条。
- 怎么用：④ 整理时先问「简单规则一行能解决吗」，只有重复出现的才升级成检查；⑤ 题库按失败类型分组，每组分别报数；⑥ 五个数用「全过率」口径，不做综合分；新增「N 周没触发的检查降频、一年没触发的下线」。
- 原文："Generic evaluations waste time and create false confidence when you use them as quality measures."

### 4. A Field Guide to Rapidly Improving AI Products｜Hamel Husain｜2025-03-24
- 链接：https://hamel.dev/blog/posts/field-guide/
- 一手
- 做了什么：强调错误分析是投入产出比最高的活动；最重要的投入是自建数据查看器（一键反馈、全上下文、可筛选）；通用指标（「有用度分」）制造虚假进步感；少数几个贴合真实用户问题的二元指标，加详细批注。
- 效果证据：案例。NurtureBoss 日期类请求失败率 66%，针对性修复后成功率 33%→95%；三类问题占全部问题 60% 以上。「查看器让迭代快 10 倍」无数据。
- 能用：能（查看器可以是一个本地网页或表格）。
- 怎么用：③④——纠正记录做成可按类筛选的表，而不是堆在一个长文件里；先数每类占比，从占比最大的几类下手。
- 原文："Can you show me how you're measuring if any of this actually works?"

### 5. Evals Skills for Coding Agents｜Hamel Husain、Shreya Shankar｜2026-03-02，08-31 改过
- 链接：https://hamel.dev/blog/posts/evals-skills/ （代码库 hamelsmu/evals-skills，我没打开）
- 一手
- 做了什么：把上面的方法做成给编程智能体用的「技能」包：入口 evals-start；审计 eval-audit；找失败类型 error-discovery；造合成数据；写裁判提示词；校准裁判 validate-evaluator（划分数据、抓出率／放行率、偏差修正）；做人工标注界面。审计的几个子项可并行交给子代理。
- 效果证据：只说法。作者自述帮助 50+ 公司，文中无基准结果。
- 能用：能。形态就是 Claude Code 的技能，可直接对照借鉴写法。
- 怎么用：⑤ 参照 validate-evaluator 的流程重写「验收官考试」；④ 参照 error-discovery 的「先聚类再定规则」。
- 原文："These skills are only a starting point. To make them better, tune them to be more specific to your data and domain."

### 6. Data Flywheels for LLM Applications｜Shreya Shankar｜2024-07-01
- 链接：https://www.sh-reya.com/blog/ai-engineering-flywheel/
- 一手
- 做了什么：定期抽样生产输出并标注，带时间戳存库；标注用来选裁判的示例，优先选「人判和模型判不一致」的例子；低分输出每天或每周复查并修，修的结果存下来当示范；指标集合不应一成不变，需要定期重新评估；让智能体建议新指标，但要工程师核。
- 效果证据：只是说法。作者明说主动学习选例的提升「待定」。
- 能用：能。
- 怎么用：③⑤——Dk 每次验收、退回、改稿都带日期存进纠正记录（不要求他另写）；⑤ 题库优先收「验收官判错的稿」（和 Dk 判断不一致的）。
- 原文："Humans need to be in the loop for evaluation regularly, as human preferences on LLM outputs change over time."

### 7. Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences｜Shankar、Zamfirescu-Pereira、Hartmann、Parameswaran、Arawjo｜2024-04-18
- 链接：https://arxiv.org/abs/2404.12272
- 一手（论文；属学术类，作者同为实践者，放此处作对照）
- 做了什么：提出 EvalGen：让用户给一小批输出打分，系统生成候选检查（代码或裁判提示词），挑出和用户打分最吻合的。发现「标准漂移」：人要先有标准才能打分，但打分的过程又在改标准。
- 效果证据：用户研究（论文），非生产效果。
- 能用：思路能用，工具本身不用。
- 怎么用：①④——标准不要一次写死：对齐卡里的「算完」允许在 Dk 退回后改，并把改动记下来（防止漂移）；整理纠正时问「这次退回是否说明我们的标准变了」。
- 原文："LLM-generated evaluators simply inherit all the problems of the LLMs they evaluate"

## 二、Eugene Yan

### 8. Product Evals in Three Simple Steps｜Eugene Yan｜2025-11
- 链接：https://eugeneyan.com/writing/product-evals/
- 一手
- 做了什么：三步：标一小批数据（二元，至少 50–100 条失败样本、200+ 总样本，优先真实失败）；对齐 LLM 评估器（约 75/25 切分，每个维度一个评估器，成对比较换顺序跑两次防位置偏差）；每次改配置都跑评估。用精确率、召回率（看失败类）、Cohen's Kappa 衡量对齐；基准是人的水平而不是完美（人与人之间 Kappa 常只有 0.2–0.3）。
- 效果证据：有计算和案例。200 条样本、缺陷率 3% 时 95% 置信区间约 ±2.4%，上界 5.4% 超过 5% 的要求；400 条时 ±1.7%；一个团队约 4 周建好评估设施，之后两周跑了数十次实验。
- 能用：能。置信区间的算法直接可用在题库小样本上。
- 怎么用：⑤⑥——所有分数带分母和区间（我们现在 6 题，区间极宽，要明说「不足以下结论」）；⑥ 每次改验收清单都重跑题库，形成「改动→重考」的固定动作。
- 原文："The benchmark is human performance, not perfection."

### 9. Stop Blaming the LLM-as-Judge—Fix Your Process Instead（原题 An LLM-as-Judge Won't Save The Product—Fixing Your Process Will）｜Eugene Yan｜页面只写「一年多前」
- 链接：https://eugeneyan.kit.com/posts/an-llm-as-judge-won-t-save-your-product-fixing-your-process-will
- 一手（作者的邮件订阅页镜像）
- 做了什么：评估是科学方法：观察数据→标注成败平衡的样本→提出假设→用基线对照做实验→量化→迭代。自动评估器要拿人的标注校准；人要定期抽样标注、看客户反馈，优先用隐式行为反馈。
- 效果证据：只是说法，无案例（作者承认文中数字多为推广信息）。
- 能用：能（道理层面）。
- 怎么用：②——验收官不能替代 Dk 的抽样；⑥ 里保留「Dk 抽样复核的比例」这类能看出人没缺席的数。
- 原文："If we're not actively reviewing AI outputs and customer feedback, automated evaluators won't save our product."

### 10. Task-Specific LLM Evals that Do & Don't Work｜Eugene Yan｜2024-03
- 链接：https://eugeneyan.com/writing/evals/
- 一手
- 做了什么：现成通用指标和应用表现几乎不相关，要按任务建窄评估；能二元就二元；分类任务分开看精确率和召回率；对 LLM 裁判持怀疑态度（G-Eval 召回低、费用至少翻倍、灵敏度差）。
- 效果证据：有数字。HaluEval 上 ChatGPT 和 Claude 2 区分事实／幻觉摘要只有 53.8%–58.5%；Voiceflow 换模型后意图分类掉 10%，被评估套件抓到；微调 NLI 模型把 ROC-AUC 从 0.56 提到 0.85。
- 能用：结论能用（不要信通用裁判）；数字是 2024 年的旧模型，不能直接套。
- 怎么用：②——验收官判断前先用脚本能判的（章节是否齐、数字是否带分母）；换模型或改验收官说明后必须重考，防静默变差。
- 原文："They barely correlate with application-specific performance and aren't discriminative enough to use in production."

### 11. Patterns for Building LLM-based Systems & Products｜Eugene Yan｜约 2023-08（页面未写日期，据正文推断）
- 链接：https://eugeneyan.com/writing/llm-patterns/
- 一手
- 做了什么：「收集反馈」一节：数据是少数护城河，反馈要在设计时就嵌进产品；显性反馈（点赞）和隐性反馈（接受／改写／忽略）；评估集每次改动后跑一遍抓回退。
- 效果证据：只是说法，引了他人的数字（GPT-4 与人一致 85%，人与人 81%）。
- 能用：能（观念）。
- 怎么用：③——Dk 的隐性反馈（直接拿去用、改了几处、退回）比让他另写评语便宜，从任务文件状态变化（待验收→已完成／退回）和他改稿的 diff 里取。
- 原文："Thus, we want to be deliberately thinking about collecting user feedback when designing our UX."

## 三、Simon Willison

### 12. Designing agentic loops｜Simon Willison｜2025-09-30
- 链接：https://simonwillison.net/2025/Sep/30/designing-agentic-loops/
- 一手
- 做了什么：智能体循环靠「清楚的成功标准＋能自己检查的工具」，典型是自动化测试；适合调试失败的测试、优化慢查询、升级依赖这类有明确成败的问题；要给权限和预算设上限（他用一个预算 5 美元的专用组织让 Claude Code 试 Dockerfile）。
- 效果证据：个人案例，无数字。
- 能用：能。
- 怎么用：①——对齐卡「算完」必须能被程序或验收官判，写不出就不做（我们已有这条，Simon 与之吻合）；④ 定时任务的预算和停机条件同理。
- 原文："A common theme in all of these is automated tests."

### 13. Writing about Agentic Engineering Patterns｜Simon Willison｜2026-02-23
- 链接：https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/ （子章节 https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/ 我未打开）
- 一手
- 做了什么：说明他的「智能体工程」指南：智能体能跑代码，所以能自己测试并迭代；红／绿测试先行让智能体写出更简洁可靠的代码。本页不讨论规则文件或从错误里学习。
- 效果证据：只是说法（本页）。
- 能用：理念能用，页面信息少。
- 怎么用：①②——先写会失败的检查，再改稿，改到检查通过：对「规则改动」同样适用——先把 Dk 退回的那份稿加进题库（会失败），再改规则，再重考。
- 原文："allowing them to test that code and iterate on it independently of turn-by-turn guidance from their human supervisor."

### 14. Claude Skills are awesome, maybe a bigger deal than MCP｜Simon Willison｜2025-10-16
- 链接：https://simonwillison.net/2025/Oct/16/claude-skills/
- 一手
- 做了什么：技能就是一个 Markdown 文件加可选的脚本；会话开始只读每个技能 frontmatter 里的简介，「每个技能只占几十个词元」，用到时才加载全文；主要担忧是沙箱和注入。
- 效果证据：只是说法。
- 能用：我们就在用。
- 怎么用：④——「整理纠正」的产出里，窄而偶发的做法放技能（按需加载），不放常驻的 CLAUDE.md。注意第 32 条（Vercel）有反例：技能常常没被触发。
- 原文："Skills are conceptually extremely simple: a skill is a Markdown file telling the model how to do something."

## 四、Claude Code 与智能体用户怎么写规则、怎么从错误里改

### 15. My AI Adoption Journey｜Mitchell Hashimoto｜2026-02-05
- 链接：https://mitchellh.com/writing/my-ai-adoption-journey
- 一手
- 做了什么：「驾具工程」(harness engineering)：每次智能体犯错，就花时间造一个让它不再犯的办法——简单问题在 AGENTS.md 加一行，复杂的写脚本（截图、过滤式测试运行）并在 AGENTS.md 里告诉它有这个脚本；让智能体有办法验证自己的工作。
- 效果证据：个人案例。他说 Ghostty 项目的 AGENTS.md「几乎完全解决」了其中针对的坏行为，无前后数据；文中没谈文件变大怎么办。
- 能用：能，且就是我们「纠正→规则」的主流做法。
- 怎么用：③④——每条纠正按「一行规则／一个脚本或钩子／不立」三选一；能做成脚本的优先做脚本。
- 原文："anytime you find an agent makes a mistake, you take the time to engineer a solution"

### 16. 10 Tips from Inside the Claude Code Team｜paddo.dev 转述 Boris Cherny 的帖子｜2026-02-01
- 链接：https://paddo.dev/blog/claude-code-team-tips/
- 二手（博主转述 Claude Code 创建者在 X 上的帖子；原帖未找到）
- 做了什么：团队让 Claude 在被纠正后更新 CLAUDE.md「以免再犯」；反复编辑，直到出错率明显下降（博主转述）；验证时让 Claude 对比自己和主分支的行为来证明可用。
- 效果证据：只是说法；唯一的量化说法是出错率「明显下降」，没给数字；页面不含 CLAUDE.md 大小的建议。
- 能用：能。
- 怎么用：③④——纠正后的标准动作是：让 Claude 自己起草规则，Dk 不必写；但「出错率明显下降」要有口径才算数，对应 ⑥。
- 原文："Claude is eerily good at writing rules for itself."（归于 Boris Cherny；另一句 "Update your CLAUDE.md so you don't make that mistake again." 是博主转述的提示语）

### 17. Writing a good CLAUDE.md｜Kyle（HumanLayer）｜2025-11-25
- 链接：https://www.humanlayer.dev/blog/writing-a-good-claude-md
- 一手
- 做了什么：作者估计前沿思考模型能比较稳定地遵守约 150–200 条指令，Claude Code 系统提示本身已占约 50 条；Claude Code 会在 CLAUDE.md 外加一条提示说「内容可能不相关」，所以不通用的内容容易被忽略；风格类规则交给代码检查器，用 Stop 钩子运行；任务专用内容放单独文件，CLAUDE.md 只列目录和简介；不要用自动生成的 CLAUDE.md；他们的根文件不到 60 行。
- 效果证据：引了一篇指令遵循论文（见第 35 条）；本人承认这个话题「没有被很严格地研究过」；其余是作者的分析和经验。
- 能用：能。
- 怎么用：④——给 `~/.claude/CLAUDE.md`（上限 80 行）设「指令条数」而非行数预算；能用钩子判的规则迁出。
- 原文："Never send an LLM to do a linter's job"

### 18. How I Use Every Claude Code Feature｜Shrivu Shankar｜2025-11-02
- 链接：https://blog.sshh.io/p/how-i-use-every-claude-code-feature
- 一手
- 做了什么：CLAUDE.md「从小开始，按 Claude 做错的地方补」；他的 monorepo 根文件严格控制在 13KB，工具文档要有约 30% 工程师在用才进根文件（他自称阈值是随意定的）；复杂工具先包成简单脚本，只记脚本；「该做」写在 CLAUDE.md，「必须做」用钩子（例：提交前检查测试通过标记的 PreToolUse 钩子），并避免在写入时拦截，让智能体先做完计划再检查结果；翻看会话日志和 CI 日志里的错误，把解法回写。
- 效果证据：个人经验；没有 CLAUDE.md 改动对质量影响的测量。
- 能用：能，几乎是同一套工具。
- 怎么用：③④——纠正来源不只是 Dk 当面纠正，还包括 Claude 自己在会话日志里的失败和被钩子拦下的记录；硬规则做成钩子（但钩子要 Dk 跑命令改，见任务文件现状）。
- 原文："Your CLAUDE.md should start small, documenting based on what Claude is getting wrong."

### 19. Just Talk To It（页面无标题与署名；站点 steipete.me，据站名和站内链接判断是 Peter Steinberger）｜约 2025-10（据页内引用的 10 月 7 日文章推断）
- 链接：https://steipete.me/posts/just-talk-to-it
- 一手（个人站点）
- 做了什么：他的 agents 文件约 800 行，「像一堆组织的伤疤」；不是他写的，是 Codex 写的，出了什么事就让它往里加一条简短的话；打算以后清理。反对把 RAG、子代理等机器堆太重。
- 效果证据：纯个人经历。他说模型「大体会遵守里面的条目」。
- 能用：作为反面参照：不设退役机制，文件就长成这样。
- 怎么用：④——这是「规则越加越多」的典型状态，和第 17、18、25 条对照看；我们要设上限和退役。
- 原文："My Agent file is currently ~800 lines long and feels like a collection of organizational scar tissue."

### 20. Agentic Coding Recommendations｜Armin Ronacher｜2025-06-12
- 链接：https://lucumr.pocoo.org/2025/6/12/agentic-coding/
- 一手
- 做了什么：智能体要快而清楚的反馈：日志同时写文件，工具快速响应、误用时报清楚；用 CLAUDE.md 一句话告诉智能体「调试模式下邮件打到标准输出」，它就能自己找登录链接走完流程。
- 效果证据：个人案例，无数字。
- 能用：能。
- 怎么用：②④——检查脚本的输出要「报清楚错在哪」，让 Claude 自己改；纠正如果能变成一句事实性提示（工具在哪、日志在哪）比抽象原则有效。
- 原文："it automatically consults the log for the necessary link to click."

### 21. Ralph Wiggum as a "software engineer"｜Geoffrey Huntley｜2025-07-14
- 链接：https://ghuntley.com/ralph/
- 一手
- 做了什么：一行 Bash 循环反复把同一个提示文件喂给智能体，每轮全新上下文，一轮只做计划文件里的一件事；出错就调整输入（加提示、改规格、维护测试／类型检查组成的「反压」），他的说法是每次出错 Ralph 就被「调音」一次；列表漂移就丢掉重生成。
- 效果证据：轶事。声称一个约 5 万美元的合同以 297 美元完成 MVP（据转发的一条消息）；作者承认输出有缺陷，更适合新项目。
- 能用：形态能用（定时任务就是「外面套循环」），但他没有防退化的度量。
- 怎么用：④ 定时任务的「一圈」每次全新上下文、只读磁盘上的文件，状态靠文件（与我们现在的做法一致）。
- 原文："Each time Ralph does something bad, Ralph gets tuned - like a guitar."

### 22. Superpowers: How I'm using coding agents in October 2025｜Jesse Vincent｜2025-10-09
- 链接：https://blog.fsck.com/2025/10/09/superpowers/
- 一手
- 做了什么：新写的技能先拿子代理做压力场景测试（时间压力、沉没成本等）——「给技能做测试驱动开发」，每次失败后加强说明；让 Claude 从两千多份过去会话的记忆文件里挖出可新增的技能。
- 效果证据：只是说法（「比预期好得多」，无指标）；回头测过去的技能时，大多数问题已被现有技能覆盖。
- 能用：能。
- 怎么用：⑤——改规则前，用「会触发这条规则的场景」让一个子代理跑一次，验证规则真的改变行为；与第 18、25 条的「新开会话测试」一致。
- 原文："Claude was quizzing the subagents like they were on a gameshow."

### 23. Harness engineering for coding agent users｜Birgitta Böckeler（martinfowler.com）｜2026-04-02
- 链接：https://martinfowler.com/articles/harness-engineering.html
- 一手
- 做了什么：把驾具分成「引导」（事前，如规范、技能）和「传感器」（事后，如检查器、测试、AI 审查）；只有反馈会重复犯错，只有事前引导则永远不知道规则有没有用；确定性控制又快又便宜、每次改动都跑，推断式控制（LLM 判断）慢、贵、不确定但能补判断；人的工作是「掌舵」——同类问题再现就加强引导或传感器；还有定期跑的传感器抓缓慢漂移；评价驾具的覆盖度与质量是未解难题。
- 效果证据：无量化数据，案例来自 Thoughtworks 团队，作者自己说行为类驾具「尚未解决」。
- 能用：能，是本类里对我们六步最贴的框架。
- 怎么用：②——验收官应分「脚本能判」（确定性）和「必须读懂才能判」（推断式）两层，前者先跑；⑥——加一个防误读的数：某个检查长期不触发时，要分辨是质量高还是检测弱（用题库里已知的坏稿去验）。
- 原文："If sensors never fire, is that a sign of high quality or inadequate detection mechanisms?"

### 24. claude-md-management 插件（claude-md-improver 技能＋/revise-claude-md 命令）｜Anthropic 官方插件库，作者署名 Isabella He｜日期页面未写
- 链接：https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management
- 一手（README；评分标准在 `skills/claude-md-improver` 里，我没打开）
- 做了什么：improver 对照代码库审计 CLAUDE.md 的质量并打分；revise 命令在会话结束时把本次学到的写进 CLAUDE.md。
- 效果证据：无。
- 能用：形态能用（也许能直接装），但装插件是改配置，要 Dk 动手；注意市面上有同名仿冒版，要从官方库装。
- 怎么用：④——「每周整理纠正」可借鉴这两个动作：会话末提议、定期审计；不直接采用其评分（标准未知）。
- 原文："Tools to maintain and improve CLAUDE.md files - audit quality, capture session learnings, and keep project memory current."

### 25. How to Audit and Fix a Bloated CLAUDE.md File｜Brandon Waselnuk（Unblocked，卖上下文引擎的厂商）｜2026-07-31
- 链接：https://getunblocked.com/blog/audit-fix-bloated-claude-md/
- 二手（作者本人文章，但数字多为转引他人研究；厂商有商业立场）
- 做了什么：减法：量出文件实际占用；删掉能从代码里读出的内容；每条规则对照 git 历史和当前代码核，命令全跑一遍；去掉互相矛盾和重复的。测试：新开会话跑会触发该规则的任务，看行为变不变；记一周重复纠正，重复说明规则没生效；硬约束从文字移到钩子、检查器、持续集成。
- 效果证据：引了第 33、34 条两项研究；作者自己没有单个文件的前后合规数据，「删掉三分之一」是预期而非测量。
- 能用：能。
- 怎么用：④ 每周整理的清单直接用；⑥ 「同类纠正重犯次数」做数。
- 原文："Rules files are advisory; hooks, linters, and CI are deterministic."

### 26. Rule Lifecycle Metadata for Prunable Instruction Surfaces｜agentpatterns.ai（无署名知识库）｜无发布日期，最后审阅 2026-06-13
- 链接：https://www.agentpatterns.ai/instructions/rule-lifecycle-metadata/
- 二手（综合性文章，无署名，主要依据另一份课程材料）
- 做了什么：给每条规则加三个字段：`source`（为什么加）、`applies_to`（何时生效）、`retire_when`（满足什么条件可安全删）；没有退役条件的规则删起来全凭判断，所以人们不敢删，文件只增不减；「没有退役条件、也没有近期被调用证据」的叫「僵尸规则」。
- 效果证据：只有一个示例（220 条减到 71 条），无对照；引了第 35 条的 68% 数字。
- 能用：做法能用（就是给规则多写两列）；证据弱。
- 怎么用：④——纠正记录里每条规则都带「来源（哪次纠正）」和「退役条件」，每周整理时检查退役条件是否已满足。
- 原文："Every instruction should have a source ('why was this rule added?')"（页面引自另一份课程讲义）

## 五、编程工具内置的规则与记忆机制

### 27. Cursor Rules｜Cursor 官方文档｜无日期（取于 2026-10-29）
- 链接：https://cursor.com/docs/context/rules
- 一手（官方文档）
- 做了什么：规则分四类：一直生效、智能按需、按文件匹配生效、手动调用；单条规则建议不超过 500 行并拆小；写具体可执行的内容；引用文件而不是拷贝内容，免得过时；不要把风格指南抄进规则（用检查器），不要写智能体本来就知道的命令；「先简单，只在发现智能体反复犯同一个错时才加规则」；规则进 git，出错时更新。
- 效果证据：只是说法。文档里没有正式的清理流程。
- 能用：做法能用（我们的 CLAUDE.md＋技能就是同类分层）。
- 怎么用：④——「重复犯错才加」作为进规则的门槛：一次纠正只记录，同类第二次出现才升级成规则（与我们全局规则「单次纠正只在那件事上生效」一致）。
- 原文："Start simple. Add rules only when you notice Agent making the same mistake repeatedly."

### 28. Devin Knowledge｜Devin 官方文档｜无日期
- 链接：https://docs.devin.ai/product-guides/knowledge
- 一手
- 做了什么：知识条目有「触发描述」和内容，相关时才取用；Devin 会根据对话反馈建议新条目或改旧条目，用户可编辑、驳回或重生成；条目保持窄、一件事一条；不删而是停用；页面开头说明 Knowledge 正在被弃用并迁到 Skills。
- 效果证据：只是说法。
- 能用：做法能用：「建议→人审→采纳或驳回」是一个好流程。
- 怎么用：③④——整理纠正时 Claude 起草「建议条目」，Dk 只对有业务取舍的点回一句；窄而按需的内容放技能。
- 原文："Devin will retrieve a Knowledge item when its current work is related to the specified triggers."

### 29. Cline Memory Bank｜Cline 官方文档｜无日期
- 链接：https://docs.cline.bot/prompting/cline-memory-bank
- 一手
- 做了什么：一组 Markdown 文件（项目简介、产品背景、当前上下文、系统模式、技术背景、进度），说「update memory bank」时复查全部文件；上下文快满时先更新记忆库再开新对话；没有裁剪或大小的建议。
- 效果证据：无；官方只给了描述性说法（「把无状态助手变成持久的开发伙伴」）。
- 能用：形态能用；我们的「先看这里.md」就是同类。
- 怎么用：④ 现状／下一步写在固定文件（已有）；注意它没有退役机制，别照搬。
- 原文："Memory Bank files are regular markdown files in your project that both you and Cline can access."

### 30. Aider Conventions｜Aider 官方文档｜无日期
- 链接：https://aider.chat/docs/usage/conventions.html
- 一手
- 做了什么：用一个简短的 CONVENTIONS.md，以只读方式加载（可被提示缓存）；示例对比：有它时 Aider 用了指定的库并加了类型标注，没有则不然。
- 效果证据：单个示例，无统计。页面不讲如何保持简短或从错误中更新。
- 能用：能，但信息量少。
- 怎么用：仅作参照：最简形态是「一个短文件＋只读加载」。
- 原文："It's best to load the conventions file with `/read CONVENTIONS.md` or `aider --read CONVENTIONS.md`."

### 31. Windsurf（Cascade）Memories and Rules｜官方文档（站点已并入 Devin 文档域名）｜无日期
- 链接：https://docs.devin.ai/desktop/cascade/memories （原 docs.windsurf.com 重定向到此）
- 一手
- 做了什么：记忆由工具自动生成、存在本地、只对当前工作区有效；规则由人定义，可全局、工作区或进 AGENTS.md；有硬上限：全局规则 6000 字符，工作区每个规则文件 12000 字符；官方建议要共享、可靠复用的知识用规则而非记忆，因为规则「可进版本控制、可共享、能明确控制何时生效」；记忆只适用旧版智能体。
- 效果证据：只是说法。
- 能用：做法能用：自动记忆和人审规则分开，重要的走规则。
- 怎么用：④——Claude 自动写的内容（如记忆文件）只当线索，进入常驻规则必须经「整理纠正」；给常驻规则设字数硬上限。
- 原文："Rules are version-controlled, shareable with your team, and give you explicit control over activation."

## 六、规则多少、放哪里的证据（含少量跨类的学术来源）

### 32. AGENTS.md outperforms skills in our agent evals｜Jude Gao（Vercel）｜2026-01-27
- 链接：https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals
- 一手
- 做了什么：用自己的评估集（Next.js 16 的新接口，构建／检查／测试评分）比较四种设置。
- 效果证据：有数字。无文档 53%；技能默认 53%；技能加明确要求调用 79%；AGENTS.md 里放压缩到 8KB 的文档索引 100%。技能在 56% 的用例里根本没被调用。作者的局限声明：只测了自家评估集、技能适合用户触发的垂直流程、两者互补；模型未写明。
- 能用：结论能用，但是一个领域的结果。
- 怎么用：④——决定「放常驻文件还是放技能」时别凭感觉：必须每次都生效的放常驻（但要短），技能的触发词要在整理时用实际任务验证是否被触发。
- 原文："Without those instructions, skills performed no better than having no documentation at all."

### 33. Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?｜Gloaguen、Mündler、Müller、Raychev、Vechev（ETH Zurich 等）｜2026-02-12，v3 改于 2026-09-29
- 链接：https://arxiv.org/abs/2602.11988
- 一手（论文；属学术类，因直接回答「规则越多越好吗」放此处）
- 做了什么：在 SWE-bench 任务（用模型生成的上下文文件）和新收集的带开发者自写上下文文件的真实议题上，比较有无上下文文件。
- 效果证据：有。上下文文件总体上没有提高任务成功率，平均推理成本增加超过 20%；对模型生成和开发者自写的都成立；智能体会认真遵守其中指令，导致更多探索和测试，但并没解决更多议题；仓库概览无帮助；适合写「非标准做法」。（摘要未给具体成功率百分比。）
- 能用：能，是反对「盲目加规则」的最强证据。
- 怎么用：④——每条规则要能说出它改变了什么具体行为，写「项目概览」类内容不进常驻文件；作者原话建议上线前要严格评估。
- 原文："providing context files does not generally improve task success rates"

### 34. On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents｜Lulla 等｜2026-01-28，v2 改于 2026-03-30
- 链接：https://arxiv.org/abs/2601.20404
- 一手（论文）
- 做了什么：在 10 个仓库的 124 个拉取请求上，比较有无 AGENTS.md 时智能体的运行时间和词元用量。
- 效果证据：有 AGENTS.md 时中位运行时间低 28.64%，输出词元少 16.58%，任务完成情况「相当」。度量的是效率，不是正确率；摘要没写具体用了哪个智能体。
- 能用：作为第 33 条的对照：规则能省时间，但不一定提高成功率。
- 怎么用：⑥——如果要证明规则有效，度量口径要说清是正确率还是效率。
- 原文："while maintaining a comparable task completion behavior"

### 35. How Many Instructions Can LLMs Follow at Once?（IFScale）｜Jaroslawicz、Whiting、Shah、Maamari｜2025-07-15
- 链接：https://arxiv.org/abs/2507.11538
- 一手（论文）
- 做了什么：用 500 条「关键词必须出现」的指令嵌在写商业报告的任务里，测 20 个模型在指令密度上升时的准确率下降。
- 效果证据：最好的前沿模型在 500 条时只有 68%；三种下降模式；偏向靠前的指令；主要错误是漏掉指令。注意：任务是关键词包含，和我们的规则种类不同，只能说明「指令越多越漏」的方向，不能拿 68% 当我们的数。
- 能用：作为「设上限」的理由。
- 怎么用：④——常驻规则设条数上限（见第 17 条的估计）并把它写进整理流程。
- 原文："even the best frontier models only achieve 68% accuracy at the max density of 500 instructions."

### 36. How Long Contexts Fail｜dbreunig.com（页面未署名，据站名为 Drew Breunig）｜2025-06-22
- 链接：https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html
- 一手
- 做了什么：把长上下文的失败分四类：中毒（错误进了上下文被反复引用）、分心、混淆（多余内容，如过多工具）、冲突（新旧信息矛盾）。
- 效果证据：引用他人研究。工具数从 19 增到 46 时小模型由成功变失败；微软／Salesforce 的研究中把提示拆成多轮后平均掉 39%，o3 由 98.1 降到 64.1。
- 能用：作为分类很有用：规则互相冲突、过时的规则=「冲突」和「中毒」。
- 怎么用：④——整理时专门查「两条规则互相矛盾」「规则里写的事实已过时」两类。
- 原文："It turns out there can be such a thing as too many tools."

### 37. How to Fix Your Context｜dbreunig.com（页面未署名，据站名为 Drew Breunig）｜2025-06-26
- 链接：https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html
- 一手
- 做了什么：六种办法：检索、工具装载（只挂相关工具）、上下文隔离（子代理）、剪枝、摘要、卸载（存到外面）。
- 效果证据：引用他人研究。工具少于 30 个时选工具准确率最多提高到 3 倍；Anthropic 的多智能体研究系统比单智能体 Opus 4 在其内部评估高 90.2%；卸载加领域提示在某基准上最多提高 54%。
- 能用：能。
- 怎么用：④——「整理纠正」本身派子代理做（隔离），主对话只收结论；常驻文件只放必须每次用的。
- 原文："Every token in the context influences the model's behavior, for better or worse."

## 七、Felix Rieseberg

### 38. How to be more ambitious: A tutorial for humans with models｜Felix Rieseberg｜2026-10-13
- 链接：https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/
- 一手
- 做了什么：先给模型自检的工具（能取崩溃报告、把版本对应到提交、能连三个系统的电脑复现并验证修复）；不让模型评自己，要用它能跑的外部工具得到即时反馈；让模型对假设做对抗式检验，并在没见过的数据上验证预测；新流程和旧流程并行跑一段时间；最后把目标交给 Claude（「让我们的应用不崩溃」）。
- 效果证据：只是说法（逸事，没有他自己工作流的数字；文中也没有提规则文件）。我们已有一份对本文的评估：`~/claude/_底座/任务/2026-10-29_评估视频方法能否改进工作模式.md`。
- 能用：能。「新旧并行」「不让模型评自己」两条直接适用。
- 怎么用：②⑤——验收官不能只由 Claude 判（外部工具＝脚本检查＋Dk 标注的题库）；改规则时新旧各考一次（并行比较）。
- 原文："Do _not_ ask the model to judge itself."

# 本类的共识和分歧

## 共识
1. 从看真实失败开始，不从预设标准开始（第 1–4、9、15、18、23 条）。Hamel 与 Shreya 把它列为最重要的活动；Mitchell、Shrivu、Böckeler 的「出错→补办法」是同一动作。证据以案例为主（NurtureBoss 33%→95%、Honeycomb 一致度 90% 以上），没有对照实验。
2. 检查用二元通过／不通过，每种失败一个检查，不做综合分（第 1、3、4、8、10 条）。
3. 能用确定性工具判的，不让 LLM 判（第 3、17、18、23、25 条）：钩子、检查器、测试、脚本优先；规则文件只是「建议」。
4. 用 LLM 当裁判，必须拿人的标注校准，并分开报抓出率和放行率；不让模型评自己（第 2、7、8、9、38 条）。
5. 规则要短、窄、按需、有来源，并且只在重复犯错后才加（第 17、18、27、28、31 条）。
6. 标准会随看输出而漂移，所以要周期性重做，不是一次定死（第 2、6、7 条）。

## 分歧
1. 规则文件到底有没有用。第 33 条（ETH Zurich）说总体不提高成功率、成本增加 20% 以上；第 34 条说运行时间少 29%；第 32 条说常驻索引 100% 对比技能 79%；Mitchell 说「几乎完全解决」但无数据。调和：说非标准做法有用，概览没用；不要凭感觉，要测。
2. 谁来写规则。第 16 条（Claude Code 团队）说让 Claude 自己写；第 17 条说别自动生成；第 31 条说自动记忆不如人审规则；第 19 条是让 Codex 写、人不审，结果 800 行。共同点：自动生成可以，但要有人审和上限。
3. 多长算长。第 17 条：不到 300 行、约 150–200 条指令；第 27 条：500 行；第 31 条：6000 / 12000 字符；第 18 条：13KB；第 19 条：800 行仍在用；第 25 条转述 Anthropic 目标是 200 行以内（转述，我没查官方原页）。没有哪个数字有对照实验支撑。
4. 技能还是常驻。第 14 条（Simon）看好技能的省词元；第 32 条发现技能常没被触发；第 28 条显示 Devin 反过来把 Knowledge 迁到 Skills。
5. LLM 裁判能不能用。Eugene 2024 年持怀疑（第 10 条）；他和 Hamel 后来的做法是「校准后用，且只用于代码判不了的失败」（第 3、8 条）。

## 「规则／记忆越加越多」实践者怎么处理
- 立门槛，不让新规则轻易进：重复犯错才加（第 27 条）；简单修复不建检查设施（第 3 条）。
- 设预算：Shrivu 的 13KB 和「30% 的人用才进根文件」（第 18 条）；Windsurf 的字符硬上限（第 31 条）；HumanLayer 的指令条数估计（第 17 条）；Vercel 把 40KB 压到 8KB（第 32 条）。
- 迁出：风格类→检查器；硬规则→钩子；窄而偶发→技能或子文件；复杂工具→脚本（第 17、18、25 条）。
- 退役：总是通过的检查降频，贵的先退（第 3 条）；规则记 `source` 和 `retire_when`（第 26 条，证据弱）；Devin 停用而不删（第 28 条）；对照代码和 git 历史核实每条（第 25 条）。
- 度量：记一周内重复纠正，重复说明规则没生效（第 25 条）；Claude Code 团队说改到出错率明显下降（第 16 条，无口径）。
- 不处理的：第 19 条只说「以后会清理」。
- 缺口：没有任何一个来源对「删规则后表现变好了」做过对照测试（第 25 条明说没有前后数据；网上的「190 行减到 123 行合规更好」是单人轶事，我没拿来列）。所以我们只能自己用题库测。
- 适用性提醒：这一类的证据主要来自「开发 LLM 产品」和「写代码」，不是「个人助手写业务文档」；搬到我们这里是类比，不是直接证据。

# 和我们六步逐步对照

- ① 立合同：已有，且比多数实践者的「成功标准」更完整（读者、算完、预算、边界）（对照第 12、15、38 条）。缺口：「算完」是 Claude 起草的，没有来自 Dk 过去退回的失败类型清单（第 1–4 条先做错误分析再定标准；第 7 条说标准会漂移，需允许改并记录）。
- ② 独立检查：已有验收官，但不如顶尖做法。没有确定性那一层（脚本能判的先判，第 23、17、25 条）；验收官是 Claude，没经过抓出率和放行率校准（第 2、8、38 条）；检查按「总体」而不是按失败类型拆（第 3 条）；没有「Dk 判通过的稿」，放行率无法测。
- ③ 记纠正：已有，是顶尖做法的起点（第 15、16、18 条）。缺的是「归类」：Hamel 的开放编码到轴向编码，把 40 行变成失败类型表（第 1、3、4 条）；也没有把 Dk 的验收／退回带日期记成标注（第 6、11 条）；来源只有 Dk 当面纠正，没有会话日志和钩子拦截记录（第 18 条）。
- ④ 每周整理：缺。一次没跑过。顶尖做法有三块我们没有：升级门槛（重复才立，第 27、3 条）、预算和上限（第 17、18、31、35 条）、退役机制（第 3、26、28 条）。
- ⑤ 考验收官：有雏形，规模远不如。我们 6 题；Hamel 建议每种失败标 100–200 条，Eugene 要求 200 条以上、至少 50–100 条失败（第 3、8 条），小于 60 条时置信区间常常太宽（第 2 条）。缺：训练／调试／测试的划分（防过拟合）、放行率、按失败类型分组、带分母和区间的汇报。对一个人用，不可能照抄这么大，但要明说区间并按失败类型小组报数。
- ⑥ 每周算五个数：缺，11/5 第一次。顶尖做法给的口径：二元、全过率、不做综合分（第 3 条）；带样本量和区间（第 8 条）；防「传感器不响」被误读为质量好（第 23 条）；能直接对应纠正闭环的候选是「同类纠正重犯次数」（第 25、16 条）。
- 六步里整体缺的一环：错误分析（把纠正归成失败类型，再决定每类变成规则、脚本、钩子、考题或不立）；它应放在 ③ 和 ④ 之间。
