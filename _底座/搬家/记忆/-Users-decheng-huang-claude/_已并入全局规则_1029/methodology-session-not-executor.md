---
name: methodology-session-not-executor
description: Dk 在旁支对话里讨论方法、判断时，我只给方法论和结论，发给对应的执行对话去改，不自己动手、不在这里问要不要改
metadata:
  node_type: memory
  type: feedback
  originSessionId: 483ed0be-80d4-469b-8694-136af48ab2b4
  modified: 2026-10-29T03:11:34.647Z
---

Dk 在一个不是主执行对话的对话里问方法、问判断时，我的角色是给方法论的人：想清楚判断标准、推荐和依据，然后用 SendMessage 发给负责这件事的执行对话，由它去改文件、交 Dk 验收。

**Why:** Dk 10/29 原话：「你不是执行者，你是给方法论的人，你可以把你想清楚的发给对应的执行对话」。当时我在方法论对话里问 Dk 要不要按 A 改导图和给主管的说明。弹窗标签推送系统的规矩是 Dk 只在一个执行对话里推进，那个对话全权负责（见 [[popup-tag-push-loop]]）。

**How to apply:** 讨论出结论后，不在这里问要不要我来改。先用 ListAgents 或 list_sessions 找到对应的执行对话（同一个项目文件夹、标题对得上正在做的事），发一份它不用上下文也能看懂的说明：Dk 的原话、判断标准、套到实际的数据（带出处）、推荐、备选方案及代价、Dk 还没定的事。改完由执行对话直接交 Dk。
