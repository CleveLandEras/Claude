"""审查复算：R35 五个押注段比值中位、1,904 中银卡以上人数、A7 重叠在潜在付费上限下的含义（2026-09-28 13:43 审查）。只读，不带参数。"""
import os
import pandas as pd

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
gift = pd.to_numeric(df['活动赠点'], errors='coerce').fillna(0)
card = pd.to_numeric(df['卡别'], errors='coerce')
ident = df['身份'].replace({'VIP': '持續', '黑名單': '持續'})
nopay = amt <= 0
pay = amt > 0
pp = nopay & (bet > 10000)
bands = [(1e4, 1e5), (1e5, 1e6), (1e6, 1e7), (1e7, 1e8), (1e8, 1e13)]
for lo, hi in bands:
    for name, base in [('nopay', nopay), ('pay', pay)]:
        m = base & (bet > lo) & (bet <= hi) & (gift > 0)
        print(f'{lo:,.0f}-{hi:,.0f}', name, int(m.sum()), round((bet[m] / gift[m]).median(), 1))
big = nopay & (bet > 1e6)
print('1904', int(big.sum()), '银卡以上', int((big & (card >= 2)).sum()))
nr = pp & ident.isin(['新增', '回流'])
print('新增回流∩pp', int(nr.sum()), '新增回流有储值', int((pay & ident.isin(['新增', '回流'])).sum()))
