"""只读：定位迭代记录里决策汇报 v103 一节的起止行号，及其后下一节标题。不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '过程记录', '迭代记录.md')
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
start = None
for i, l in enumerate(lines, 1):
    if l.startswith('### v103'):
        start = i
        print('v103 起', i)
    elif start and (l.startswith('### ') or l.startswith('## ')):
        print('下一标题', i, l[:60])
        break
for i, l in enumerate(lines, 1):
    if l.startswith('## '):
        print('节', i, l[:50])
