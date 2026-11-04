---
name: token-and-scheduled-task-cost
description: 放暂停文件停不了定时任务，要停用（10/10–10/12 的实例）
metadata:
  type: feedback
---

放暂停文件（`暂停.txt`）停不了定时任务：10/10–10/12 四个定时任务照样每几分钟醒一次读暂停文件，空耗约 46 小时。要停就把每个定时任务设成 `enabled: false`（可恢复）。
