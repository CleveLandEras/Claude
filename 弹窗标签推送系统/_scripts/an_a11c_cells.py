"""A11 补充：A8 关键格内，普卡、银卡、金卡以上的会员等级、注册天数、储值对比；控制等级后卡别差距是否还在（Q32）。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['tenure'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间']).dt.normalize()).dt.days
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['cg'] = pd.cut(d['卡别'], [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上'])
bet, dep = d['游戏总押注'], d['总充值金额']

def show(mask, name):
    s = d[mask]
    print('\n==', name, len(s))
    g = s.groupby('cg', observed=True)
    print(g.agg(n=('卡别', 'size'), 等级中位=('会员等级', 'median'), 注册天数中位=('tenure', 'median'),
                储值中位=('总充值金额', 'median'), 押注中位=('游戏总押注', 'median'),
                近7天=('days', lambda x: round((x <= 7).mean() * 100, 2))).to_string())

show((bet > 1e6) & (bet <= 1e7) & (dep > 1e3) & (dep <= 1e4), 'A8 表3c 关键格：押注 1百万–1千万 × 储值 1千–1万')
show((bet > 1e7) & (bet <= 1e8), '押注 1千万–1亿')
show((bet > 1e7) & (bet <= 1e8) & (dep > 1e3) & (dep <= 1e4), '押注 1千万–1亿 × 储值 1千–1万')

# 在关键格内再按会员等级分段，看普卡 vs 银卡 的 0–7 天差距是否还在
s = d[(bet > 1e6) & (bet <= 1e7) & (dep > 1e3) & (dep <= 1e4)].copy()
qs = s['会员等级'].quantile([0, .25, .5, .75, 1]).to_numpy()
s['lq'] = pd.cut(s['会员等级'], np.unique(qs), include_lowest=True)
print('\n== 关键格内，按会员等级四分位分层的 0–7 天比例（格人数）')
t = s.groupby(['lq', 'cg'], observed=True).agg(n=('days', 'size'), r=('days', lambda x: round((x <= 7).mean() * 100, 2))).unstack()
print(t.to_string())
# MH 风险差：普卡 vs 银卡、普卡 vs 金卡以上，按等级四分位分层
def mh(s, a, b, key):
    num = den = 0.0
    for _, g in s.groupby(key, observed=True):
        x = g[g['cg'] == a]; y = g[g['cg'] == b]
        if len(x) < 30 or len(y) < 30: continue
        w = len(x) * len(y) / (len(x) + len(y))
        num += w * ((y['days'] <= 7).mean() - (x['days'] <= 7).mean()); den += w
    return num / den * 100 if den else float('nan')
print('按等级四分位分层 MH：银卡−普卡 %.2f；金卡以上−普卡 %.2f；金卡以上−银卡 %.2f' % (
    mh(s, '普卡', '银卡', 'lq'), mh(s, '普卡', '金卡以上', 'lq'), mh(s, '银卡', '金卡以上', 'lq')))
x = d[(bet <= 1e4) & (d['cg'] == '金卡以上')]
print('押注≤1万的金卡以上 %d 人，其中 VIP %d，押注=0 %d' % (len(x), (x['身份'] == 'VIP').sum(), (x['游戏总押注'] == 0).sum()))
v = d[d['身份'] == 'VIP']
print('VIP 押注段分布', pd.cut(v['游戏总押注'], [-np.inf, 1e4, 1e6, 1e8, np.inf]).value_counts().sort_index().to_dict())
print('不分层原值：普卡 %.2f 银卡 %.2f 金卡以上 %.2f' % tuple((s[s['cg'] == c]['days'] <= 7).mean() * 100 for c in ['普卡', '银卡', '金卡以上']))
