---
name: judging-method
description: "How to design AI review/judging (10/16): ground it in published top-lab practice, focus on judge accuracy; never ask Dk or a judge an open 「够不够用」 question — each item gets yes/no criteria with sources, a top-product comparison and reference cases; criteria coverage (a dimension table) is the main lever (merged 10/16 from ground-method-in-top-lab-practice + judgment-items-need-references)"
metadata:
  type: feedback
---

Project rule source: 标准体系 第三节「评审题库与新的评审方法」; work in progress in `规则与交接/评审题库/` (评审维度表.md, 进度与下一步.md).

**Ground the method in top-lab practice (10/16).** While grilling Dk on the self-loop I kept asking about peripheral mechanics I had invented (rules with test cases, release thresholds). Dk: 「最重要的评审判断怎么样才能准确，这个必须要参考顶尖ai科技公司的做法，不能盲目来。你要更多关注核心」; he couldn't weigh my test-case idea because it had no outside grounding. Self-invented methods had already failed here (判例 exams, stacked reviewers). So: research how Anthropic, OpenAI, Google and recognised practitioners do it (with sources), map our gaps to their practice, spend effort on judge accuracy.

**No open judgment questions (10/16).** After a 10-item sheet of open questions (「这个看板够不够用」 with screenshots): 「你没给参考标准，没给顶尖公司的做法，没有对比，让我凭空去判断，这样虽然也能判断但是很累工作量很大，你需要尽可能减少我的工作量啊。而且这个对我来说只是很费力，对AGENT评审来说，那就完全行不通了……即便同一个AGENT无上下文的判断几次可能说法都不一样，因为太开放而且没有参考依据、参考标准，和参考案例的对比。」 Every item = one-line question + 4–6 yes/no criteria with sources (Dk-decided / 写作标准 / industry practice) + comparison table (top product's way with source | ours) + reference cases (Dk's rejected version and the fixed one). Show the AI judge's per-criterion verdict next to Dk's column — Dk: 「AI 评审的结论要给我看，我不会被带着走，反而是减少我的工作量，缩短思考步骤」; the judge must be independent of whoever wrote the criteria.

**Coverage is the lever (10/16 evening).** After structured items 1–2: 「目前ai评审还是比较准确的，可能问题主要出在对问题的梳理」; item 1 missed whether the prototype design is rough — 「这不是ai评审的问题，这是问题不够全面的缘故」. Build a per-deliverable-type dimension table (HealthBench-style axes) and check every item covers every dimension. Related: [[check-sufficiency-before-done]], [[industry-standard-definitions-first]], [[reporting-to-dk]].
