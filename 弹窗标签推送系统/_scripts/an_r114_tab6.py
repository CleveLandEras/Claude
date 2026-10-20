"""R113 / R114：A24 表 6——机会 × 问题，持平倍数与每 1% 倍数两组（S / R）。只读，不带参数。
人群与单位复用 an_q76_perf.py（load、expose；已剔除機器人、測試帳號），O1、O4 定义照 an_q77_opp.py。
潜力型 D2、D4b 的 1% 弹性（NT$，S、R 下同一个数）取 A23 表 4 已审定值。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import math
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, _ROOT + '/_scripts')
from an_q76_perf import load, expose  # noqa: E402

g, U = load()
TS, TR = U['S'].sum(), U['R'].sum()
print(f'总额 S {TS:,.0f}  R {TR:,.0f}')
a = g['a'].copy()
m = (a['tenure'] / 30.44).clip(lower=1)
a['R'] = (a['dep'].clip(lower=0) / m).where(a['tenure'].notna())
a['cg'] = np.where(a['卡别'] == 1, '普卡', np.where(a['卡别'] == 2, '银卡', '金卡以上'))
a['r07'] = a['days'] <= 7

PROB = {}
for k, ids in {'D1': set(g['D1']['会员编号']), 'D3': set(g['D3']['会员编号']), 'D8 独有': set(g['UQ']['会员编号'])}.items():
    e = expose(U, ids, TS, TR)
    PROB[k] = (e['S'], e['R'], e['n'])
    print(f'{k}: n={e["n"]:,} S {e["S"]:,.0f}（{e["S"] / TS * 100:.2f}%） R {e["R"]:,.0f}（{e["R"] / TR * 100:.2f}%）；每 1% S {e["S"] / 100:,.0f} R {e["R"] / 100:,.0f}；D 人均 S {e["S"] / e["n"]:,.0f}')

# 潜力型 1% 弹性（NT$；A23 表 4）
POT = {'D4b 均值参照': 148904, 'D4b 中位参照': 16706, 'D2 均值参照': 5973, 'D2 中位参照': 667}

o1 = a[a.r07 & (a.dep > 0) & a['nov']]
k = math.ceil(len(o1) * 0.01)
top = o1.nlargest(k, 'R')
rest = o1[~o1['会员编号'].isin(top['会员编号'])]
o4 = a[(a['身份'] == '回流') & a.r07]
ROWS = {
    'O1 全部': set(o1['会员编号']),
    'O1 金卡以上': set(o1.loc[o1.cg == '金卡以上', '会员编号']),
    f'O1 R 前 1%（{k}）': set(top['会员编号']),
    'O1 其余': set(rest['会员编号']),
    'O4 回流在场': set(o4['会员编号']),
}
print('\n===== 表 6（持平 = 问题暴露 ÷ 机会底盘；每 1% 倍数 = 机会每 1% ÷ 问题每 1%）')
for name, ids in ROWS.items():
    e = expose(U, ids, TS, TR)
    s, r = e['S'], e['R']
    print(f'\n{name}: n={e["n"]:,} 底盘 S {s / TS * 100:.2f}% R {r / TR * 100:.2f}%；每 1% = S {s / 100:,.0f} / R {r / 100:,.0f}（NT$ 当量）')
    for p, (ps, pr, pn) in PROB.items():
        print(f'   vs {p}: 持平 S {ps / s * 100:.1f}% R {pr / r * 100:.1f}%｜每 1% 倍数 S {s / ps:.2f} R {r / pr:.2f}')
    for p, v in POT.items():
        print(f'   vs {p}: 每 1% 倍数 S {s / 100 / v:.2f} R {r / 100 / v:.2f}')

# 动作量换算（提醒 46）
d1s, d1r, d1n = PROB['D1']
print(f'\nD1 每 1% ≈ {d1n / 100:.1f} 名风险层高卡的历史价值（S {d1s / 100:,.0f}）')
e = expose(U, ROWS['O1 其余'], TS, TR)
print(f'O1 其余每 1% = 在场付费者（去掉前 1%）多付约 1%：S {e["S"] / 100:,.0f}；折合 D1 风险层人均 S {d1s / d1n:,.0f} 的 {e["S"] / 100 / (d1s / d1n):.1f} 人')
print(f'   R：O1 其余每 1% {e["R"] / 100:,.0f}；D1 人均 R {d1r / d1n:,.0f} → {e["R"] / 100 / (d1r / d1n):.1f} 人')
