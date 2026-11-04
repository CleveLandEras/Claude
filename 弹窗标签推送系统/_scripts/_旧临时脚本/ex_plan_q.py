"""打印推进计划第三节队列里未完成项全文（只读）。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
for l in open(os.path.join(BASE, '过程记录/推进计划.md'), encoding='utf-8'):
    if l.startswith('- [ ]'):
        print(l)
