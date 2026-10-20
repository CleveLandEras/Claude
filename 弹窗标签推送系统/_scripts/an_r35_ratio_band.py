"""R34 / R35：① 从未储值押注 >1 百万的 1,904 人中银卡以上人数；② 押注 / 活动赠点 比值中位按同一押注段比较
（从未储值 vs 有储值，赠点 > 0 者），潜在付费中押注 ≤1 百万者的比值中位。不带参数运行，只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
pay, bet, gift = '总充值金额', '游戏总押注', '活动赠点'
for c in (pay, bet, gift):
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
df['卡组'] = np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上'))
df['付费'] = df[pay] > 0
print('剔除后', len(df), '有储值', int(df['付费'].sum()), '从未储值', int((~df['付费']).sum()))

np_ = df[~df['付费']]
big = np_[np_[bet] > 1e6]
print('\n== ① 从未储值押注>1百万', len(big), '其中银卡以上', int((big['卡组'] != '普卡').sum()),
      '；从未储值银卡以上', int((np_['卡组'] != '普卡').sum()),
      '，其中押注≤1百万', int(((np_['卡组'] != '普卡') & (np_[bet] <= 1e6)).sum()))

print('\n== ② 同押注段比值中位（赠点>0 者）==')
bands = [(1e4, 1e5), (1e5, 1e6), (1e6, 1e7), (1e7, 1e8), (1e8, np.inf)]
for lo, hi in bands:
    row = []
    for name, g in [('从未储值', np_), ('有储值', df[df['付费']])]:
        t = g[(g[bet] > lo) & (g[bet] <= hi) & (g[gift] > 0)]
        r = (t[bet] / t[gift]).median() if len(t) else float('nan')
        row.append(f'{name} {len(t)} 人 中位 {r:.1f}')
    print(f'押注 ({int(lo):,}, {hi:,.0f}]：', '；'.join(row))

pp = np_[np_[bet] > 1e4]
t = pp[(pp[bet] <= 1e6) & (pp[gift] > 0)]
print('\n潜在付费', len(pp), '；其中押注≤1百万且赠点>0', len(t), '比值中位', round((t[bet] / t[gift]).median(), 1))
t2 = pp[pp[gift] > 0]
print('潜在付费赠点>0', len(t2), '比值中位', round((t2[bet] / t2[gift]).median(), 1))
