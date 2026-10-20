# Q315 / A82 第六节：阶段 4–8 逐词命中数，及「圈不准」「看不到效果」残留行（只读）
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE

terms = ['34', '13／12／9', '12／12／10', '13、12、9', '回流时间点', '回流后首次登录事件', '首储购买标记', '过程指标', '过程层指标', '事件层', '事件与新近度层',
         '关闭情况汇总', '推送记录汇总', '客户端上报', '圈不准', '圈不出', '看不到效果', '查不到', '效果看不到', '5 个根因', '订单明细', '读法乙']
names = [(4, '问题诊断'), (5, '方案选型'), (6, '方案设计'), (7, '方案验证'), (8, '结论汇总')]
texts = {i: textify(os.path.join(BASE, f'阶段{i}_{n}.html')).splitlines() for i, n in names}
print('| 检索词 | ' + ' | '.join(f'阶段{i}' for i, _ in names) + ' |')
for t in terms:
    print(f'| {t} | ' + ' | '.join(str(sum(l.count(t) for l in texts[i])) for i, _ in names) + ' |')
print('\n=== 残留行：圈不准 圈不出 看不到效果 查不到 效果看不到 ===')
for i, _ in names:
    for n, l in enumerate(texts[i], 1):
        hit = [t for t in ['圈不准', '圈不出', '看不到效果', '查不到', '效果看不到'] if t in l]
        if hit:
            print(f'[阶段{i} 行{n}] ({",".join(hit)}) {l[:160]}')
print('\n=== 回流时间点 / 回流后首次登录事件 命中行 ===')
for i, _ in names:
    for n, l in enumerate(texts[i], 1):
        hit = [t for t in ['回流时间点', '回流后首次登录事件', '登录新近度'] if t in l]
        if hit:
            print(f'[阶段{i} 行{n}] ({",".join(hit)}) {l[:120]}')
