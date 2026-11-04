# 审查 2026-09-30：复算 02 第二、三张卡与提案引用的人数（只读）
import pandas as pd
P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
print('列：', list(df.columns))
df = df[~df['身份'].isin(['機器人', '測試帳號'])]
N = len(df)
print('分母', N)
card = pd.to_numeric(df['卡别'], errors='coerce')
dep = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
hi = card >= 3
print('金卡以上', hi.sum(), round(hi.sum() / N * 100, 2))
print('金卡以上且有储值（不剔 VIP、黑名单）', (hi & (dep > 0)).sum())
nv = ~df['身份'].isin(['VIP', '黑名單'])
print('金卡以上 VIP/黑名单', (hi & ~nv).sum())
print('金卡以上且有储值（剔 VIP、黑名单）', (hi & (dep > 0) & nv).sum())
print('金卡以上无储值', (hi & (dep <= 0)).sum(), '其中非 VIP 黑名单', (hi & (dep <= 0) & nv).sum())
never = dep <= 0
print('从未储值', never.sum(), round(never.sum() / N * 100, 2))
print('从未储值且累计押注 > 10000', (never & (bet > 10000)).sum(), round((never & (bet > 10000)).sum() / N * 100, 2))
print('全体累计押注 > 10000', (bet > 10000).sum())
g = df[hi & (dep > 0) & nv]
print('金卡以上有储值 身份分布', g['身份'].value_counts().to_dict())
lt = pd.to_datetime(g['最後登入時間'], errors='coerce')
days = (pd.Timestamp('2026-09-16') - lt.dt.normalize()).dt.days
print('其中 0-7 天', (days <= 7).sum())
lo = card.isin([1, 2])
print('普银有储值', (lo & (dep > 0)).sum(), '剔 VIP 黑名单', (lo & (dep > 0) & nv).sum())
print('卡别缺失', card.isna().sum(), '卡别取值', sorted(card.dropna().unique().tolist()))
tot = dep.sum()
print('金卡以上储值占比', round(dep[hi].sum() / tot * 100, 2), '普银人数', lo.sum(), round(lo.sum() / N * 100, 2))
