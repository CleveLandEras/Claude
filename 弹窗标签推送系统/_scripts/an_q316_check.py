# Q316 复核：阶段 1–4 旧口径词残留（只读）
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE
terms = ['近 4 个月', '储值衰减', '储值下滑', '140,000', '少一半', '月度储值', '未首储', '首储购买', '读法乙', '读法甲', '25,972', '5,976', '13,449', '18,265', '11,356', '4,816', '3,677', '7,572', '互斥', '每人最多命中', '29,653', '10,000']
names = [(1, '需求分析'), (2, '人群分析'), (3, '现状盘点'), (4, '问题诊断')]
T = {i: textify(os.path.join(BASE, f'阶段{i}_{n}.html')).splitlines() for i, n in names}
print('| 词 | ' + ' | '.join(f'阶段{i}' for i, _ in names) + ' |')
for t in terms:
    print(f'| {t} | ' + ' | '.join(str(sum(l.count(t) for l in T[i])) for i, _ in names) + ' |')
print('\n--- 命中行（非 10,000）---')
for i, _ in names:
    for n, l in enumerate(T[i], 1):
        hit = [t for t in terms if t in l and t != '10,000']
        if hit:
            print(f'[阶段{i} 行{n}] ({",".join(hit)}) {l[:140]}')
