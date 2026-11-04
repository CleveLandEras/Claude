# 设计者试算（只读）：检验「月化储值代理 = 累计储值 / 账号月龄」能否作为跨诊断的统一单位
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
act = pd.read_csv(BASE + '近一月活跃_20260916.csv', encoding='utf-8-sig')
chn = pd.read_csv(BASE + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
bad = ['機器人', '測試帳號']
act = act[~act['身份'].isin(bad)].copy()
chn = chn[~chn['身份'].isin(bad)].copy()
chn = chn[~chn['会员编号'].isin(act['会员编号'])].copy()
act['src'] = 'act'
chn['src'] = 'left'
df = pd.concat([act, chn], ignore_index=True)

ref = pd.Timestamp('2026-09-16')
df['reg'] = pd.to_datetime(df['注册时间'], errors='coerce')
df['last'] = pd.to_datetime(df['最後登入時間'], errors='coerce')
df['regd'] = (ref - df['reg'].dt.normalize()).dt.days
df['lastd'] = (ref - df['last'].dt.normalize()).dt.days
df['pay'] = df['总充值金额'].clip(lower=0)
df['mon'] = (df['regd'] / 30.44).clip(lower=1)
df['rate'] = df['pay'] / df['mon']
df['card'] = df['卡别']
df['vip'] = df['身份'].isin(['VIP', '黑名單'])
print('rows act/left/all', len(act), len(chn), len(df), 'reg missing', df['reg'].isna().sum())

a = df[df.src == 'act']
tot_rate = a['rate'].sum()
print('active pay sum', round(a['pay'].sum()), 'active rate-proxy sum', round(tot_rate))
print('merged rate-proxy sum', round(df['rate'].sum()))
s = a['rate'].sort_values(ascending=False)
print('top10 share of active proxy', round(s.head(10).sum() / tot_rate * 100, 2), 'top1% share', round(s.head(int(len(s) * 0.01)).sum() / tot_rate * 100, 2))
print('VIP share of proxy', round(a.loc[a.vip, 'rate'].sum() / tot_rate * 100, 2), 'VIP share of stock', round(a.loc[a.vip, 'pay'].sum() / a['pay'].sum() * 100, 2))

def g(mask, name, base=df):
    x = base[mask]
    print(f"{name}: n={len(x)}, stock={round(x['pay'].sum())}, proxy/mo={round(x['rate'].sum())}, proxy share act={round(x['rate'].sum()/tot_rate*100,2)}%, stock share act={round(x['pay'].sum()/a['pay'].sum()*100,2)}%, payer%={round((x['pay']>0).mean()*100,2)}, med tenure d={x['regd'].median()}")

hi = df['card'].between(3, 7)
g(hi & ~df.vip & (df['lastd'] >= 8), 'D1 risk (hi, nonVIP, >=8d incl left)')
g(hi & ~df.vip & (df['lastd'] <= 7), 'hi nonVIP 0-7d')
g(df['身份'].eq('回流') & (df['lastd'] >= 8), 'D3 risk')
g(df['身份'].eq('回流') & (df['lastd'] <= 7), 'returners 0-7d present')
g(df['身份'].eq('持續') & (df['lastd'] <= 7), 'continuing 0-7d')
g((df['lastd'] >= 8), 'D8 all')
g(df['reg'] >= '2026-08-18', 'new cohort 8/18+ (actual flow)')
g((df['reg'] >= '2026-08-18') & (df['reg'] <= '2026-09-08') & (df['last'].dt.normalize() == df['reg'].dt.normalize()), 'D2 day-1 only')
g((df['reg'] >= '2026-08-18') & (df['reg'] <= '2026-09-08') & (df['last'].dt.normalize() != df['reg'].dt.normalize()), 'new 8/18-9/08 came back')
g((df['pay'] <= 0) & (df['lastd'] <= 7) & ~df.vip, 'D4b never-paid 0-7d')
g((df['pay'] > 0) & (df['lastd'] <= 7) & ~df.vip, 'active payers 0-7d')
g((df['pay'] > 0) & (df['pay'] <= 100) & (df['lastd'] <= 7) & ~df.vip, 'small payers <=100 0-7d')
# U2: D8 unique, registered before 8/1, high bet vs reference P50
refg = df[(df.src == 'act') & (df['lastd'] <= 7) & (df['card'] == 1) & ~df.vip]
p50 = refg['游戏总押注'].median()
d1 = hi & ~df.vip & (df['lastd'] >= 8)
d2 = (df['reg'] >= '2026-08-18') & (df['reg'] <= '2026-09-08') & (df['last'].dt.normalize() == df['reg'].dt.normalize())
d3 = df['身份'].eq('回流') & (df['lastd'] >= 8)
uniq = (df['lastd'] >= 8) & ~(d1 | d2 | d3)
u2 = uniq & (df['reg'] < '2026-08-01')
g(uniq, 'D8 unique')
g(u2, 'U2')
g(u2 & (df['游戏总押注'] >= p50), 'U2 high bet')
# proxy vs tenure: does lifetime-average inflate young accounts?
a2 = df[(df.src == 'act') & (df['pay'] > 0)]
for lo, hi_ in [(0, 30), (31, 90), (91, 365), (366, 1095), (1096, 99999)]:
    x = a2[a2['regd'].between(lo, hi_)]
    print('payers tenure', lo, hi_, 'n', len(x), 'median rate', round(x['rate'].median(), 1), 'mean rate', round(x['rate'].mean(), 1))
# card threshold cross-check: hi-card 0-7d nonVIP median rate vs 1,500/mo (gold 3,000 per ~2 months)
x = df[hi & ~df.vip & (df['lastd'] <= 7) & (df.src == 'act')]
print('hi 0-7 median rate', round(x['rate'].median(), 1), 'share rate<1500', round((x['rate'] < 1500).mean() * 100, 1))
