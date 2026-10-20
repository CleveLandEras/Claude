import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
snap = pd.Timestamp('2026-09-16')
ll = pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()
lld = (snap - ll).dt.days
dep = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
up = (dep <= 0) & (bet >= 20000) & (lld <= 14)
card = pd.to_numeric(df['卡别'], errors='coerce')
a = (up & card.isin([1, 2])).sum()
print(a, up.sum(), a / up.sum() * 100)
print(df.loc[up, '卡别'].value_counts(dropna=False))
