# Q312 复核：阶段 5、6 旧词残留与命中行（只读）
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE
terms = ['34', '13 项', '13／12／9', '回流时间点', '回流后首次登录事件', '首储购买', '订单明细', '月度储值', '读法乙', '读法甲', '事件与新近度层', '近 4 个月',
         '储值衰减', '储值下滑', '衰减', '过程指标', '25,972', '5,976', '13,449', '18,265', '13,368', '10,000', '140,000', '总控', '单人日推送上限', '推送统一后台与合计限量',
         '只覆盖推播、短信', '三格', '六格']
names = [(5, '方案选型'), (6, '方案设计')]
T = {i: textify(os.path.join(BASE, f'阶段{i}_{n}.html')).splitlines() for i, n in names}
print('| 词 | 阶段5 | 阶段6 |')
for t in terms:
    print(f'| {t} | ' + ' | '.join(str(sum(l.count(t) for l in T[i])) for i, _ in names) + ' |')
print('\n--- 命中行 ---')
skip = {'总控'}
for i, _ in names:
    for n, l in enumerate(T[i], 1):
        hit = [t for t in terms if t in l and t not in ('10,000',)]
        if hit:
            print(f'[阶段{i} 行{n}] ({",".join(hit)}) {l[:150]}')
