# Q314 / A81 第六节：阶段 1–8 逐词命中数与命中行（只读）
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE

terms = ['潜在付费', '潜在流失', '储值衰减', '储值下滑', '衰减', '近 4 个月', '近4个月', '月度储值', '未首储', '首储购买', '读法乙', '读法甲',
         '10,000', '25,972', '5,976', '13,449', '18,265', '11,356', '4,816', '3,677', '互斥', '命中 2 类', '月度窗口']
files = [os.path.join(BASE, f'阶段{i}_{n}.html') for i, n in
         [(1, '需求分析'), (2, '人群分析'), (3, '现状盘点'), (4, '问题诊断'), (5, '方案选型'), (6, '方案设计'), (7, '方案验证'), (8, '结论汇总')]]
texts = {i + 1: textify(p).splitlines() for i, p in enumerate(files)}
print('| 检索词 | ' + ' | '.join(f'阶段{i}' for i in range(1, 9)) + ' |')
for t in terms:
    row = []
    for i in range(1, 9):
        row.append(str(sum(l.count(t) for l in texts[i])))
    print(f'| {t} | ' + ' | '.join(row) + ' |')

focus = ['储值衰减', '储值下滑', '近 4 个月', '近4个月', '月度储值', '未首储', '首储购买', '读法乙', '读法甲', '10,000', '25,972', '5,976',
         '13,449', '18,265', '11,356', '4,816', '3,677', '互斥', '命中 2 类', '月度窗口']
print('\n=== 命中行 ===')
for i in range(1, 9):
    seen = set()
    for n, l in enumerate(texts[i], 1):
        hit = [t for t in focus if t in l]
        if hit and n not in seen:
            seen.add(n)
            print(f'[阶段{i} 行{n}] ({",".join(hit)}) {l[:150]}')
print('\n=== 潜在付费/潜在流失 命中行数（仅数） ===')
for i in range(1, 9):
    print(i, sum(1 for l in texts[i] if '潜在付费' in l), sum(1 for l in texts[i] if '潜在流失' in l))
