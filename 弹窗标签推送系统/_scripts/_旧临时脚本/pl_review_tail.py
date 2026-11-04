"""只读：列出审查记录各节标题（最后 12 个）及最后两节全文。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '过程记录', '审查记录.md')
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
for i, l in heads[-12:]:
    print(i + 1, l[:150])
start = heads[-2][0] if len(heads) >= 2 else 0
print('=' * 60)
for l in lines[start:]:
    print(l[:1500])
