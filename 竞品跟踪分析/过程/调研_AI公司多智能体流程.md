# 调研：顶尖 AI 公司如何组织多智能体分析任务与质量把关（2026-10-15）

子任务调研回报原文整理。未单独标注的都是读过原文后的转述；OpenAI deep research 发布页（访问 403）与 CoVe 摘要来自二手转述。

## 一、Anthropic：一个规划者拆任务，多个执行者并行，产出写进文件，独立核查引用，按事先写好的标准验收；先用最简单的结构
- 编排者-执行者（2025-06-13）：主 agent 分析问题、定策略，并行派 3–5 个子 agent，汇总后决定是否追加；内部评测比单 agent 高 90.2%，token 约为普通聊天 15 倍。
- 子任务指令四要素：目标、输出格式、可用工具与来源、任务边界；指令含糊导致重复劳动和遗漏。
- 按复杂度定人数：简单事实 1 个；直接对比 2–4 个；复杂研究 10 个以上。早期出过为简单问题派 50 个子 agent 的问题。
- 产出落文件，只回传引用，避免层层失真；专门的引用 agent 把每条论断对到来源。
- 评估：约 20 个真实问题小样本；LLM 评委按事实准确、引用准确、完整性、来源质量、工具效率打分并给通过／不通过；人工测试仍能发现幻觉。
- 五种工作流（2024-12-19）：提示链（步骤间加程序检查）、路由、并行（分段或投票）、编排者-执行者、评估者-优化者。
- 长任务（2025-11-26）：先写功能清单（全部初始未通过），执行者只改状态；进度文件；每轮一项；标完成前端到端验证；常见失败是过早宣布完成、没测就标通过。
- 评估（2026-01-09）：程序判、模型判（要用人工校准）、人判；好任务是两位专家独立评判结论一致；先准备一份能通过的参考答案；按维度拆开、每维度一个评委、允许回答「判不了」；研究类查结论是否有依据、要点是否覆盖、来源质量。

## 二、OpenAI 与 Google：中心调度＋独立评审＋可核查引用；模型给自己打分不能代替独立核实
- OpenAI《A practical guide to building agents》（2025-04）：先把单 agent 用到极限再拆；管理者模式；指令拆成小步、写明边界；失败超阈值或高风险转人工。
- OpenAI deep research（2025-02）：附引用与思考摘要；承认会编造、推断出错、难分权威与传言。系统卡称幻觉率低于前代但仍存在。
- Google AI co-scientist（2025-02）：先把目标解析成「研究计划配置」并写明评价标准，后续自评都用它；分工为生成、反思、排序、进化、去重、元评审；评审分初审、联网全审、深度验证（拆成前提逐条独立判）；Elo 排序是自评，最终靠专家与实验验证。

## 三、看图类任务减少幻觉：先摘证据再下结论；每条结论可追溯；不看推理过程的复核者逐条判；多次独立结果互相比对
- 先逐字摘证据，成稿后逐条找支持，找不到就删；允许回答「不知道」；多跑几次，不一致处可能是幻觉（Anthropic 文档）。
- 多图编号便于引用；低质量、小图易出错，计数只是近似（Vision 文档）。
- 全新上下文的复核子 agent 只看产出和标准；被要求找问题的复核者总会找出一些，只报影响正确性的（Claude Code 文档）。CoVe：核查问题逐个独立回答。Woodpecker：把描述拆成问题，对照原图验证。
- 多个观察者交叉一致可降低幻觉（投票并行、多智能体辩论）。
- 区分观察与推断：GitLab UX 研究手册分观察、逐字原话、初步解读、可能方案四栏（来自 UX 研究实践）。
- 抽帧会漏快速画面（Gemini 视频理解文档）；据此推断「某功能不存在」类结论风险最高。

## 四、可执行流程（子任务的归纳）
规划（任务书、验收清单、分维度评分标准、参考样例）→ 观察（并行，只记看到的，先小样本校准）→ 核验（全新上下文，判支持／不支持／判不了，关键论断可多人独立做）→ 综合（只用已核验条目，结论挂论断编号）→ 分维度评审（不通过退回，设轮次上限）→ 人工抽检并校准评委。

## 查不到的
- 没有 AI 公司针对「看截图、看录像做竞品分析」的公开流程；第三、四节是通用做法的迁移。

## 来源
1. https://www.anthropic.com/engineering/multi-agent-research-system（2025-06-13）
2. https://www.anthropic.com/engineering/building-effective-agents（2024-12-19）
3. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents（2025-11-26）
4. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents（2026-01-09）
5. https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
6. https://platform.claude.com/docs/en/build-with-claude/vision
7. https://code.claude.com/docs/en/best-practices
8. https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
9. https://openai.com/index/introducing-deep-research/
10. https://cdn.openai.com/deep-research-system-card.pdf
11. https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
12. https://arxiv.org/abs/2502.18864
13. https://ai.google.dev/gemini-api/docs/video-understanding
14. https://arxiv.org/abs/2309.11495
15. https://arxiv.org/abs/2305.14325
16. https://arxiv.org/abs/2310.16045
17. https://handbook.gitlab.com/handbook/product/ux/ux-research/analyzing-research-data/
