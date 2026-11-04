"""审查复算：从未储值却押注极大的账号规模（2026-09-28 12:18 审查）。只读，不带参数。"""
import os
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
gift = pd.to_numeric(df['活动赠点'], errors='coerce').fillna(0)
nopay = amt <= 0
pp = nopay & (bet > 10000)
print('列名', list(df.columns))
for th in [1e5, 1e6, 1e7, 1e8]:
    print(f'从未储值 押注>{th:,.0f}', int((nopay & (bet > th)).sum()))
print('pp 赠点中位', gift[pp].median(), '押注/赠点 中位', (bet[pp] / gift[pp].replace(0, np.nan)).median())
pay = amt > 0
print('有储值 赠点中位', gift[pay].median(), '押注/赠点 中位', (bet[pay] / gift[pay].replace(0, np.nan)).median())
print('pp 赠点=0', int((pp & (gift == 0)).sum()))
