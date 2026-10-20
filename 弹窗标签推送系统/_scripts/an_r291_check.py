# 执行者复算 R291/R292：全体有储值者集中度基准；潜在付费里的持續在场老账号
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
B = _ROOT + '/数据/'
df = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = list(df.columns)
idn = c[-1]; pay = c[6]; bet = c[7]; card = c[4]
df = df[~df[idn].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
df['age'] = (ref - pd.to_datetime(df[c[1]], errors='coerce').dt.normalize()).dt.days
df['dsl'] = (ref - pd.to_datetime(df[c[3]], errors='coerce').dt.normalize()).dt.days
print('N', len(df))
pp = df[(df[pay] <= 0) & (df[bet] > 10000)]
m = (pp[idn] == '持續') & (pp['dsl'] <= 7) & (pp['age'] >= 365)
print('潜在付费甲 n', len(pp), '其中持續在场>=365', int(m.sum()))
w = df[(df[pay] <= 0) & (df['dsl'] <= 7) & (df['age'] >= 365) & (df[idn] == '持續')]
print('持續未储值在场>=365 不限押注', len(w), '其中押注>10000', int((w[bet] > 10000).sum()))
s = df[df[pay] > 0][pay].sort_values(ascending=False)
n = len(s)
print('全体有储值者', n, '储值合计', s.sum())
print('头部1%', s.head(int(round(n * .01))).sum() / s.sum())
print('头部10%', s.head(int(round(n * .1))).sum() / s.sum())
g = df[(df[pay] > 0) & (df[card] >= 3)]
print('金卡以上有储值', len(g), g[pay].sum() / s.sum())
print('金卡以上占活跃', (df[card] >= 3).sum() / len(df))
