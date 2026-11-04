"""执行者用：打印推进计划中以 61. 62. 63. 开头的口径约束行。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for i, l in enumerate(open(os.path.join(BASE, '过程记录', '推进计划.md'), encoding='utf-8').read().split('\n'), 1):
    if l.startswith(('61.', '62.', '63.', '64.')):
        print(i, l)
