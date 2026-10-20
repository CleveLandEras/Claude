# Q190：核对审查 R253（2,524 人注册龄与赠点）、R260（同卡别 1%-99% 分位）。只读。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
df['reg_age'] = (ref - pd.to_datetime(df['注册时间'], errors='coerce').dt.normalize()).dt.days

# R253：普卡回流 从未储值且累计押注为 0
r = df[(df['身份'] == '回流') & (df['卡别'] == 1) & (df['总充值金额'] <= 0) & (df['游戏总押注'] == 0)]
print('普卡回流 从未储值且押注0', len(r))
print('注册龄 最小', r['reg_age'].min(), '中位', r['reg_age'].median(), '最大', r['reg_age'].max())
print('满365天', (r['reg_age'] >= 365).sum(), round((r['reg_age'] >= 365).mean() * 100, 2))
print('注册龄缺值', r['reg_age'].isna().sum())
print('活动赠点分布前6', r['活动赠点'].value_counts().head(6).to_dict())
print('赠点=0', (r['活动赠点'] == 0).sum(), '=500', (r['活动赠点'] == 500).sum(), '=1000', (r['活动赠点'] == 1000).sum())

# R260：有储值者各卡别累计储值分位（主数）
m = df[~df['身份'].isin(['VIP', '黑名單']) & (df['总充值金额'] > 0)]
names = {1: '普卡', 2: '银卡', 3: '金卡', 4: '白金卡', 5: '钻石卡', 6: '黑卡', 7: '至尊卡'}
for c in range(1, 8):
    s = m[m['卡别'] == c]['总充值金额']
    q = s.quantile([.01, .05, .25, .5, .75, .9, .95, .99]).round().tolist()
    print(names[c], len(s), 'P1/5/25/50/75/90/95/99', q, 'min', s.min(), 'max', s.max(), 'P99/P1', round(q[-1] / q[0], 1) if q[0] else None, 'P95/P5', round(q[6] / q[1], 1) if q[1] else None)
