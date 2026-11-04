import pandas as pd
import numpy as np

p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['last'] = pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()
d['rec'] = (pd.Timestamp('2026-09-16') - d['last']).dt.days
d['r07'] = d['rec'] <= 7
d['grp'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
bins = [-np.inf, 10000, 100000, 1000000, 10000000, 100000000, np.inf]
labels = ['<=1万', '1万-10万', '10万-1百万', '1百万-1千万', '1千万-1亿', '>1亿']
d['bseg'] = pd.cut(d['游戏总押注'], bins=bins, labels=labels, right=True)
vip = d['身份'] == 'VIP'
print('VIP n', vip.sum(), 'bet==0', (d.loc[vip, '游戏总押注'] == 0).sum())
print('VIP by bseg x grp')
print(pd.crosstab(d.loc[vip, 'bseg'], d.loc[vip, 'grp']))
for name, x in [('all', d), ('noVIP', d[~vip])]:
    print('====', name, len(x))
    t = x.groupby(['bseg', 'grp'], observed=False)['r07'].agg(['sum', 'count'])
    t['pct'] = (t['sum'] / t['count'] * 100).round(2)
    print(t.loc['<=1万'])
    raw = x.groupby('grp')['r07'].mean() * 100
    print('raw', raw.round(2).to_dict(), 'gap', round(raw['金卡以上'] - raw['普卡'], 2))
    rate = x.groupby(['bseg', 'grp'], observed=False)['r07'].mean().unstack()
    w = x['bseg'].value_counts(normalize=True).reindex(labels)
    std = {}
    for g in ['普卡', '银卡', '金卡以上']:
        r = rate[g]
        ok = r.notna()
        std[g] = round(float((r[ok] * w[ok]).sum() / w[ok].sum() * 100), 2)
    print('std(all-weights)', std, 'gap', round(std['金卡以上'] - std['普卡'], 2))
