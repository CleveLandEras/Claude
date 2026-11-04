---
name: benchmark-top-practices
description: 改后台方案、做审查或给优化建议前，先对标顶尖产品做法（弹窗项目有顶尖做法参考库），别只凭自己推
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7314682c-eb96-46bf-946c-48e110700044
  modified: 2026-10-28T04:37:19.387Z
---

2026-10-28 弹窗标签推送系统评审版：我连做了第一性原理、减法、整体过一遍，结论都是自己推出来的，只零星引用了参考库。Dk：「要参考顶尖的做法，别埋头自己弄」。

**Why:** 顶尖产品（Braze、OneSignal、MoEngage、CleverTap、Airship、Firebase、Appcharge 等）的做法是被大量运营验证过的；不对标就容易做出业界没人这么做的设计，或者漏掉通行的简单做法，Dk 还得自己去找依据。

**How to apply:**
- 弹窗项目先查 `弹窗标签推送系统/规则与交接/顶尖做法参考库/`（README 第 1 条就写了「设计每一个点之前先查这里」），查不到再上网查官方文档，查到的按 README 格式补进库。
- 每条建议写成「顶尖怎么做（带出处）→ 我们现在 → 差异 → 改不改」；和顶尖不同的地方要说清为什么。
- 只在当前项目文件夹里查（见 [[project-folder-boundary]]）。相关：[[check-competitors-first]]、[[stay-within-ask]]。

同日活动配置项目（商城）又一次：重做需求评审材料时 Dk 插话同一句。商城没有参考库，我上网查了国内大厂需求评审讲法（woshipm）、Google 设计文档（背景→目标与不做→概览→细节）、Shape Up 提案（问题用具体故事、时间预算、草图标新元素位置、风险点、明确不做）、Productboard 评审会建议（材料短、细节进预读文档、待定问题有负责人）。做材料类交付物同样适用：先查顶尖的结构再动笔。

2026-10-28 傍晚第三次：Dk 嫌评审材料观感差，我又自己埋头改版式，Dk：「要参考顶尖的做法这事我都重复一千遍了」。改版式也是设计，动手前同样先查。汇报幻灯片查到的通行做法：Duarte 三秒测试（一页一个观点，像广告牌）https://www.duarte.com/resources/guides-tools/the-glance-test/ ；麦肯锡／BCG 结论式标题，只读标题能串成故事（横向逻辑），正文只支撑标题（纵向逻辑），标题里有「和」「；」就拆页；Duarte slidedocs：留白、最多三层层级、统一视觉语言、数字放大。
