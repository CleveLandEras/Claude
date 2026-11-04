"""执行者用（Q89）：列出决策汇报.html 中 section / h2 / h3 行号，以及含「标签」「05」「SQL」的行号与前 220 字。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(BASE, '决策汇报.html'), encoding='utf-8').read().split('\n')
print('总行数', len(L))
for i, l in enumerate(L, 1):
    s = l.strip()
    if s.startswith('<section') or '<h2' in s or '<h3' in s or 'class="no"' in s:
        print(f'{i}: {s[:160]}')
print('-' * 40)
for i, l in enumerate(L, 1):
    if ('标签' in l or 'SQL' in l or '05' in l) and i > 0:
        print(f'{i}: {l.strip()[:220]}')
