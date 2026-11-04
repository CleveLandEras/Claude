"""执行者用：打印推进计划第三节队列各行（行号 + 前 200 字）。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(BASE, '过程记录', '推进计划.md'), encoding='utf-8').read().split('\n')
on = False
for i, l in enumerate(L, 1):
    if l.startswith('## 三'):
        on = True
    elif l.startswith('## ') and on:
        break
    if on and l.strip():
        print(i, l[:200])
