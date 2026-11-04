"""审查 2026-09-29 00:2x：独立复算 A25 / A27 / A28 关键数（只读）。不 import 执行者脚本。"""
import os
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, '数据')
act = pd.read_csv(os.path.join(D, '近一月活跃_20260916.csv'), encoding='utf-8-sig')
lap = pd.read_csv(os.path.join(D, '八月登录流失名单_20260916.csv'), encoding='utf-8-sig')
bad = ['機器人', '測試帳號']
act = act[~act['身份'].isin(bad)].copy()
lap = lap[~lap['身份'].isin(bad)].copy()
print('活跃', len(act), '流失名单', len(lap))
act['src'] = 'act'
lap_only = lap[~lap['会员编号'].isin(act['会员编号'])].copy()
lap_only['src'] = 'leave'
m = pd.concat([act, lap_only], ignore_index=True)
print('合并', len(m), '离开', len(lap_only))

asof = pd.Timestamp('2026-09-16')
m['last'] = pd.to_datetime(m['最後登入時間'], errors='coerce')
m['reg'] = pd.to_datetime(m['注册时间'], errors='coerce')
m['days'] = (asof.normalize() - m['last'].dt.normalize()).dt.days
m['S'] = m['总充值金额']
age = (asof - m['reg']).dt.total_seconds() / 86400 / 30.44
age_d = (asof.normalize() - m['reg'].dt.normalize()).dt.days / 30.44
m['R'] = m['S'].clip(lower=0) / age.clip(lower=1)
m['R_d'] = m['S'].clip(lower=0) / age_d.clip(lower=1)
print('S 总额', m['S'].sum(), 'R 总额(秒)', round(m['R'].sum()), 'R 总额(日)', round(m['R_d'].sum()), 'R 缺', m['R'].isna().sum())

nv = ~m['身份'].isin(['VIP', '黑名單'])
o1 = m[(m.src == 'act') & (m.days <= 7) & (m.S > 0) & nv].copy()
print('O1', len(o1), '金卡以上', (o1['卡别'] >= 3).sum())
for col in ['R', 'R_d']:
    thr = o1[col].quantile(0.99)
    top = o1.nlargest(134, col)
    rest = o1.drop(top.index)
    hr = rest[rest['卡别'] >= 3]
    print(f'[{col}] 大户 134 全金卡以上?', (top['卡别'] >= 3).all(), '其余', len(rest), '高卡去大户', len(hr))
    print(f'  高卡去大户 占其余 人数 {len(hr)/len(rest):.3f} S {hr.S.sum()/rest.S.sum():.3f} R {hr[col].sum()/rest[col].sum():.3f}')
    print(f'  高卡去大户 R 合计 {hr[col].sum():,.0f} 1% {hr[col].sum()*0.01:,.0f} 人均 {hr[col].sum()*0.01/len(hr):.1f} 中位 {hr[col].median():.1f} 均值 {hr[col].mean():.1f} P99 {hr[col].quantile(.99):.0f}')
    print(f'  主行 R 合计 {rest[col].sum():,.0f} S {rest.S.sum():,.0f}')

d1 = m[(m['卡别'] >= 3) & nv & ((m.src == 'leave') | (m.days >= 8))].copy()
print('D1', len(d1), '待再来', (d1.src == 'act').sum(), '离开', (d1.src == 'leave').sum(),
      '8-14', ((d1.src == 'act') & (d1.days <= 14)).sum())
print('D1 S', d1.S.sum(), 'R', round(d1.R.sum()))
for col in ['R', 'S']:
    v = d1[col].clip(lower=0).sort_values(ascending=False).values
    cs = v.cumsum() / v.sum()
    k80 = int(np.searchsorted(cs, 0.8) + 1)
    print(f'  D1 {col} 均值 {v.mean():.1f} 中位 {np.median(v):.1f} 倍 {v.mean()/np.median(v):.2f} K50 {int(np.searchsorted(cs,.5)+1)} K80 {k80} K90 {int(np.searchsorted(cs,.9)+1)} 前K80人均 {v[:k80].mean():,.0f}')
    for sub in ['act', 'leave']:
        w = d1[d1.src == sub][col].clip(lower=0).sort_values(ascending=False).values
        c2 = w.cumsum() / w.sum()
        print(f'    {sub} n {len(w)} K80 {int(np.searchsorted(c2,.8)+1)}')

# 等价与持平（R 口径，高卡去大户）
top = o1.nlargest(134, 'R'); rest = o1.drop(top.index); hr = rest[rest['卡别'] >= 3]
one = hr.R.sum() * 0.01
v = d1.R.sort_values(ascending=False).values
print('等价：均值型', one / v.mean(), '中位型', one / np.median(v), 'K80 人均型', one / v[:168].mean())
print('持平：高卡去大户', d1.R.sum() / hr.R.sum(), '主行', d1.R.sum() / rest.R.sum(), '主行 S', d1.S.sum() / rest.S.sum(), '高卡 S', d1.S.sum() / hr.S.sum())

# 同条件差距 G 切分 A（O1 金卡以上 5,280）
hc = o1[o1['卡别'] >= 3].copy()
hc['cg'] = hc['卡别'].clip(upper=6)
regd = (asof.normalize() - hc['reg'].dt.normalize()).dt.days
hc['rg'] = pd.cut(regd, [-1, 365, 1095, 1e9], labels=['a', 'b', 'c'])
G = 0
for _, g in hc.groupby(['cg', 'rg'], observed=True):
    med = g.R.median(); G += (med - g.R[g.R < med]).sum()
print('G(R) 切分A', G, '占高卡R', G / hc.R.sum())

# A27 App 类
for sub in ['act', 'leave']:
    x = d1[d1.src == sub]
    app = x['登入平台'].astype(str).str.lower().isin(['android', 'ios', 'apk'])
    print('D1', sub, 'App', app.sum(), f'{app.mean():.4f}', '平台值', x['登入平台'].value_counts().to_dict())

# A28 S3：D1 待再来天数分档
a = d1[d1.src == 'act']
print('D1 待再来 8-30', (a.days <= 30).sum(), '31', (a.days == 31).sum(), '>31', (a.days > 31).sum())
print('活跃 days 分布尾', act.shape, m[m.src == 'act'].days.max(), '离开 days 范围', m[m.src == 'leave'].days.min(), m[m.src == 'leave'].days.max())
