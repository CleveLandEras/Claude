"""执行者用：打印设计卡中标题含 Q89 的卡全文，以及卡片标题索引。不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = 'Q93'
p = os.path.join(BASE, '过程记录', '设计卡.md')
lines = open(p, encoding='utf-8').read().split('\n')
heads = [i for i, l in enumerate(lines) if l.startswith('## ') or l.startswith('### ')]
for i in heads:
    if lines[i].startswith('## '):
        print(i + 1, lines[i][:100])
heads.append(len(lines))
for a, b in zip(heads, heads[1:]):
    if KEY in lines[a] and lines[a].startswith('## '):
        nxt = [h for h in heads if h > a and (h == len(lines) or lines[h].startswith('## '))][0]
        print('=' * 60)
        print('\n'.join(lines[a:nxt]))
