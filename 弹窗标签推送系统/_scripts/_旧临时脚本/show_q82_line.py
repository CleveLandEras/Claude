"""打印推进计划中 Q82 队列行的行号与末尾 160 字。不带参数运行。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
for i, l in enumerate(open(os.path.join(BASE, '过程记录', '推进计划.md'), encoding='utf-8').read().split('\n')):
    if l.startswith('- [x] Q82'):
        print(i + 1, '…' + l[-160:])
