"""Q13 / A3 补充：① 从未储值 × 累计押注门槛，按身份 × 卡组分列；② 25,972 与 25,962 的边界核对（>= 与 >）；
③ 回流有储值者按卡组的储值额中位数。不带参数运行，只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
pay, bet = '总充值金额', '游戏总押注'
df[pay] = pd.to_numeric(df[pay], errors='coerce').fillna(0)
df[bet] = pd.to_numeric(df[bet], errors='coerce').fillna(0)
df['身份3'] = df['身份'].replace({'VIP': '持續', '黑名單': '持續'})
df['卡组'] = np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上'))
df['付费'] = df[pay] > 0
print('剔除后', N, '有储值', int(df['付费'].sum()), '从未储值', int((~df['付费']).sum()))
print('总充值<0 人数', int((df[pay] < 0).sum()), '=0 人数', int((df[pay] == 0).sum()))

np_ = df[~df['付费']]
print('\n== 边界核对 ==')
for th in [1000, 10000, 50000, 100000]:
    print(f'押注>={th}', int((np_[bet] >= th).sum()), f'押注>{th}', int((np_[bet] > th).sum()),
          '恰好等于', int((np_[bet] == th).sum()))
# 另一种口径：从未储值 = 总充值==0（不含负值）
z = df[df[pay] == 0]
print('若从未储值取 =0：押注>=1万', int((z[bet] >= 10000).sum()), '>1万', int((z[bet] > 10000).sum()))

print('\n== 从未储值 × 押注门槛 × 身份 × 卡组（格内：人数 / 该身份×卡组从未储值人数） ==')
ids = ['新增', '回流', '持續']
cgs = ['普卡', '银卡', '金卡以上']
for k in ids:
    for c in cgs:
        s = np_[(np_['身份3'] == k) & (np_['卡组'] == c)]
        row = [f'>{th}: {int((s[bet] > th).sum())}' for th in [1000, 10000, 50000, 100000]]
        print(k, c, '从未储值', len(s), row)
print('\n== 从未储值 × 卡组合计 ==')
for c in cgs:
    s = np_[np_['卡组'] == c]
    print(c, len(s), [f'>{th}: {int((s[bet] > th).sum())}' for th in [1000, 10000, 50000, 100000]])

print('\n== 回流有储值者按卡组：人数、中位数 ==')
r = df[(df['身份3'] == '回流') & df['付费']]
for c in cgs:
    s = r[r['卡组'] == c]
    print(c, len(s), round(s[pay].median()) if len(s) else '—')
