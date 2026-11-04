---
name: writing-and-layout
description: "All writing, wording and layout rules for Dk live in 弹窗标签推送系统/规则与交接/写作标准_合并版.md (现行说法 wins; + 演示稿观感标准 as my reference defaults, 措辞审查流程 for 呈交版); this memory keeps one line per rule plus Dk's words and the cases (merged 10/16 from 14 writing/layout memories)"
metadata:
  type: feedback
---

Source of truth: `/Users/decheng.huang/claude/弹窗标签推送系统/规则与交接/写作标准_合并版.md` (maintain only this .md; the old .html copy and its generator were retired to 归档/规则_旧 and _scripts/_旧临时脚本 on 10/19, no sync needed). Dk 10/09 「这个文件作为标准参考」; 10/10 resolved its open list: 「建议全采纳。B7收录但是不按原文收录……改成通用做法后收录。B8不收录 B9收录 整理后同步一下」. Precedence: its 现行说法 beats 工作原则乙, the report-format skill and my notes; project business rules (popup 工作原则甲·1 / 已定事项: 活跃、付费 never appear) stay stricter than its generic 「只作观察指标」. Items it marks 主对话理解/主对话补 are my defaults, not Dk's lines (10/16). B8 removed 「不用角标编号指代」「我纠正之后，不再复述理由」, but no-internal-codes still stands. 演示稿观感标准.md is my compilation from published sources: its numbers are starting defaults, never pass/fail lines.

One line per rule (where in 写作标准) — Dk's words — case:

- **Structure first, no word caps; boundaries visible** (结构组, 壬). 10/08 「为什么有字数上限……结构清晰是最重要的事情」 (caps made agents cut reasoning); 10/08 「需求分析的内容太平铺了，看得很费劲啊，没有结构性」; 10/09 V1 「整体的结构性是什么样的？我还是没看清楚，而且逻辑联系是什么样的也没看出来」 (condensing pushed the argument links into folds); 10/14 「对阅读来说，结构性强的一个重要的点是边界，让人看得见边界在哪里，能在内心里把大小和形状框起来，就不会感到无尽的漫长。所以最重要的是首先把界限说清楚」; 10/14 prototype 「最严重的问题是结构不清晰」 (判例 40) → follow the structure the reader knows (product menu), overview first.
- **Pair 现状 with its 做法** (结构组, 辛; 已定事项 21; 判例 25). 10/12 V4: 「现状和解决方案一般是要放在一块前后立刻看的，要不然看完现状再看后面的已经对应不起来了，这太考验读者的记忆力什么的了。这种阅读门槛要尽可能的降低，这是原则之一」.
- **Define a set where it is first named** (结构组, 辛; 措辞审查 9; 判例 29). 10/13 on 「5 类　人群各看一套弹窗」: 「对于读者来说不要让他有存疑，这里就要把五类是什么写出来，而不是让他记住有五类然后之后再看是哪五类」. "Too many → breakdown + where the full list is" is my default.
- **Title doesn't restate its subheads; carries the biggest change** (标题组, 辛; 措辞审查 10; 判例 31). 10/13 run-on title over three same-named cards: 「就是个累赘，单纯重复而且耗时更长」; replacing it with a bare count lost the point: 「清晰是底线，如果不清晰宁愿不承载更大作用，但这个能不能既要清晰又要承载呢」.
- **Wording survives a context-free paraphrase; 呈交版 gets a wording review** (措辞组, 辛; `措辞审查流程.md`; case `分析/A88_措辞理解测试.md`). 10/12: 8/8 readers misread four V4 lines (e.g. 「推送、效果、对照共用同一套人群标签」); 「这几句话分别让无上下文的agent去读…如果理解的不准确，说明表述不清晰」「这些措辞问题必须搞清楚搞透，然后记录在原则里」「我们以后给呈交版内容需要专门对措辞审查」. 10/13 recurrence: 「标点符号的问题还是没改过来」 → run `_scripts/pl_逗号句清单.py` on the whole deck. A full round ≈16 readers / ~1M tokens: test the worst sentences first.
- **Don't repeat subjects the context fixes; read the whole draft for repeated patterns** (措辞审查 11; 判例 45). 10/15: 63 prototype blocks opened with 「运营」, agents had added subjects mechanically: 「永远是运营在开头，这三个字真的有必要？真的认真检查措辞了吗？」. Situational, not a ban on subjects.
- **Professional, concise, direct; no coined terms or regional jargon** (措辞组; 已定事项 7). 10/08 「用词能不能专业点，看着像在给小学生解释，简洁直接就行了不用刻意去这样措辞」; 「措辞要直接简洁，但不要缺信息……我都没法转述给别人到底能力目标是什么」 (「现状盘点」 clear, 「能力目标」 not); 10/09 「建统一触达层这句话我就看不懂啥意思」; 10/12 TOC that explained each chapter: 「这个也介绍吗？感觉把读者当做小学生对待了一样，多余的篇幅」.
- **No meta info; don't narrow the column; desktop only** (要删掉的内容; 视觉组). 10/09 「约 2 分钟这种无效信息给我删干净啊，别整这种东西出来，纯浪费读者精力的」; 「更挤了是因为宽度变窄了」 (I had narrowed 860→800px; keep ~1000–1080px); 「我们不考虑手机端的显示」. No card-in-card is my own practice.
- **Reading experience over brevity; auxiliary marks get their own section** (取舍顺序 4, 视觉组, 庚; 判例 24). 10/12 cost tags on every mockup screen: 「这些成本标签非要写可以单开一个篇幅去写，别影响读者看核心内容，看的分心，精简篇幅是没错，但不要过分追求到牺牲阅读体验，这是界限，这种原则你要记录」. Denominators stay next to their numbers.
- **Basic typesetting** (视觉组; 观感标准 §七点五). 10/12 「这三句话居然只用两行，看着很难受啊……那就要分三行才对啊。就找找类似基础的排版问题还有没有」; 「这三行前面哪怕给打个点，间隙稍微大点呢？这也太粗糙了吧」. A 、 inside one sentence is not a split point; 「我没说数字必须带单位」. My added defaults: no line-start punctuation, no orphan char, consistent CJK/Latin spacing. Case 10/16: judging page with 14px gray text in a 330px column and tall unmarked screenshots — 「我咋感觉还是读的很费劲？是不是字体格式什么的问题？」 → 16px / 1.8 dark text, 720px text block, cropped images with red boxes, ~2,000 chars.
- **Layout states only true relations** (结构组「版面的排法」; 观感标准 §七点六; 判例 32). 10/13 two unrelated problems side by side with one demoted to a subtitle: 「这样的布局有问题」; 「这就需要你去了解顶尖的做法，而不是没了解瞎整」. Left/right = compare, title/subtitle = rank, one box = one group; splitting pages is 「最省事的办法」, not the only one.
- **Pick the display form from the content's structure** (视觉组, 写每一节前…). 10/10 V4 page 2 as four flat rows: 「数字和结论的意义我看不到……这个四结构明显可以用好得多的方式展示，而不是像表格一样平铺……完全没考虑换形式展示。这个遗漏要记录，不该遗漏」. Comparing 2–3 forms first is my default; big numbers only if they visibly prove the title. Plans never discuss 排期 (「排期不是方案要考虑的事情，我们这是方案」, 已定事项 19).
- **Bring my own look-and-feel standards; density ramps up** (协作与交付; 视觉组). 10/12 「我不想一条一条的说明观感到底怎么样才算好，你自己应该有标准的，就算没有应该也查得到的」; 「我没感觉到信息密度有一个缓冲……要有个递增的感觉」, then 「这不是最重点的问题……可能算是节奏上的问题，不算很大」. 10/13 task rows not grouped: 「这个你如果参考一些顶尖的设计应该是能清晰这种标准的，没参考顶尖的标准是一个需要记录的问题」 (判例 38).

Related: [[reporting-to-dk]], [[only-confirmed-principles]], [[fresh-agent-for-visual-design]].

Case 10/19: labels coined in our chat (「核心五件」「一个入口」「写死迁入」, headings like 「看什么、不看什么、细到什么程度」) leaked into the prototype and the review-version brief. Dk: 「注意措辞……不要展示这种无上下文的对话性内容……我们是有原则的，参考原则即可」. When briefing agents, mark which wording is internal and require industry-standard terms in deliverables.

Case 10/19 (判例 46): in the review version, a page title 「按用户分群推送」 was good but its long-sentence subtitle describing the feature was not. Dk: 「不要通过这种用标题介绍的长句子方式……但凡了解正式的顶级的专业的优秀的做法肯定就不会这样……没有参考顶级标准是个问题」. Titles are read most — check them against top practice for that document type (Microsoft / Google style guides: short, clear, scannable); prototype/review page titles = short noun phrases, key points as 2–4 short phrases below; 「标题即结论」 from consulting decks must not be applied blindly to every document type.

Case 10/19 (判例 47): to satisfy 「边界看得见」 I briefed 「结尾写明『评审内容到此结束』」 and the agent also wrote 「最后一页是待定事项，之后没有其他内容」. Dk: 「请告诉我这是什么？」 Boundaries are shown by structure (overview, page numbers, separators), never by sentences explaining how to read; I saw it in my own first-screen check and let it pass.

Same day, second instance: I briefed 「每页先一句话说这页要评审判断什么」 → 16 per-page 「评审判断」 lines + part bands + a map column. Dk: 「评审判断是过程读者需要的，不是正式读者需要的，正式的文件力求精简，怎么可能放这种内容啊」. Process-reader guidance (what to judge, how to read) never goes into the formal document.

Same day, third instance: my checklist asked readers to tell 「第几页、还剩多少」, so the agent wrote page headers 「本部分第 4 页（共 5 页）全稿第 5 页（共 16 页），后面还有 11 页」. Dk: 「请你把这些水分抽干，不要给文件注水。这是正式文档！」 Use standard conventions (「推播　5 / 16」); write checks as effects, not as sentences the agent will paste in.

Then I over-trimmed to 「5 / 16」; Dk: 「过于简单缺少关键信息，犯了措辞两大忌的第二个」 (the two taboos: 不精准、缺信息). Fix by goal, not by swinging: 「第 5 页 / 共 16 页」.

Project authority for the 10/19 cases above: merged into 写作标准 on 10/19 (Part 2 group 1 row 「边界看得见，先交代边界再讲内容」 incl. page-number form and no second boundary block; group 2 「标题简洁，按同类文档的顶尖写法」; group 6 「每个功能先问……」; group 7 「正式文件不注水……」); 规则与交接/交付前必查.md holds the per-item checks; cases in 判例 46–48 and 矫枉过正记录.md.
