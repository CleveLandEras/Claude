"""Q35：A8 表 3 / 3b 剔除 VIP 的影响；押注字段对非 VIP 是否漏记。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['tenure'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间']).dt.normalize()).dt.days
d['r07'] = d['days'] <= 7
d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
bb = [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf]
bl = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
d['betb'] = pd.cut(d['游戏总押注'], bb, labels=bl)
db = [-np.inf, 0, 1e3, 1e4, np.inf]
dl = ['≤0', '1–1千', '1千–1万', '>1万']
d['depb'] = pd.cut(d['总充值金额'], db, labels=dl)
vip = d['身份'] == 'VIP'
G = ['普卡', '银卡', '金卡以上']

print('VIP', vip.sum(), '押注=0', (d.loc[vip, '游戏总押注'] == 0).sum())
print('VIP 押注段 × 卡组'); print(pd.crosstab(d.loc[vip, 'betb'], d.loc[vip, 'cg']).reindex(columns=G, fill_value=0).to_string())

def seg_table(x):
    t = x.groupby(['betb', 'cg'], observed=False)['r07'].agg(['sum', 'count'])
    t['pct'] = (t['sum'] / t['count'] * 100).round(2)
    return t

for name, x in [('全部', d), ('不含 VIP', d[~vip])]:
    print('\n====', name, len(x))
    t = seg_table(x)
    print('≤1万 段：'); print(t.loc['≤1万'].to_string())
    print('1百万–1千万 段：'); print(t.loc['1百万–1千万'].to_string())
    raw = x.groupby('cg')['r07'].mean() * 100
    print('原始', raw.round(2).to_dict(), '差', round(raw['金卡以上'] - raw['普卡'], 2))
    rate = x.groupby(['betb', 'cg'], observed=False)['r07'].mean().unstack()
    for wname, wsrc in [('本口径全体押注段分布', x), ('本口径金卡以上押注段分布', x[x['cg'] == '金卡以上'])]:
        w = wsrc['betb'].value_counts(normalize=True).reindex(bl).fillna(0)
        std = {}
        for g in G:
            r = rate[g]; ok = r.notna() & (w > 0)
            std[g] = round(float((r[ok] * w[ok]).sum() / w[ok].sum() * 100), 2)
        print(wname, std, '差', round(std['金卡以上'] - std['普卡'], 2))
    # 表 3c 关键格
    c = x[(x['betb'] == '1百万–1千万') & (x['depb'] == '1千–1万')]
    print('表3c 关键格', {g: '%.2f%% (%d/%d)' % (c.loc[c['cg'] == g, 'r07'].mean() * 100, c.loc[c['cg'] == g, 'r07'].sum(), (c['cg'] == g).sum()) for g in G})

print('\n== ≤1万 段银卡：全部 vs 不含 VIP 中 VIP 人数')
s = d[(d['betb'] == '≤1万') & (d['cg'] == '银卡')]
print('银卡 %d 人，其中 VIP %d' % (len(s), (s['身份'] == 'VIP').sum()))
s = s[s['身份'] != 'VIP']
print('\n== 不含 VIP 的 ≤1万 段银卡 %d 人' % len(s))
print('押注=0 %d，押注中位 %.0f，押注分位 %s' % ((s['游戏总押注'] == 0).sum(), s['游戏总押注'].median(), s['游戏总押注'].quantile([.25, .5, .75, .9]).round(0).to_dict()))
print('储值中位 %.0f，储值分位 %s，从未储值 %d' % (s['总充值金额'].median(), s['总充值金额'].quantile([.1, .5, .9]).round(0).to_dict(), (s['总充值金额'] <= 0).sum()))
print('会员等级中位 %.0f，注册天数中位 %.0f，0–7 天 %.2f%%' % (s['会员等级'].median(), s['tenure'].median(), s['r07'].mean() * 100))
print('身份', s['身份'].value_counts().to_dict(), '平台', s['plat'].value_counts().to_dict())
print('活动赠点中位 %.0f' % s['活动赠点'].median())
rt = pd.to_datetime(s['注册时间'])
print('60 名银卡：押注=0 %d；其中 2025 年前注册 %d（属于 A12 第五节 1,565 人）；有储值 %d；押注>0 的 %d 人押注中位 %.0f、最大 %.0f' % (
    (s['游戏总押注'] == 0).sum(), ((s['游戏总押注'] == 0) & (rt < '2025-01-01')).sum(), (s['总充值金额'] > 0).sum(),
    (s['游戏总押注'] > 0).sum(), s.loc[s['游戏总押注'] > 0, '游戏总押注'].median(), s['游戏总押注'].max()))
print('押注=0 的 37 人平台', s.loc[s['游戏总押注'] == 0, 'plat'].value_counts().to_dict())

print('\n== 全体非 VIP：押注=0 的人')
nv = d[~vip]
z = nv[nv['游戏总押注'] == 0]
print('押注=0 %d（占非 VIP %.2f%%）' % (len(z), len(z) / len(nv) * 100), z['身份'].value_counts().to_dict())
a = z[z['总充值金额'] > 0]
print('押注=0 但储值>0：%d 人，储值合计 %.0f（占全部储值 %.3f%%），储值中位 %.0f，卡组 %s，身份 %s' % (
    len(a), a['总充值金额'].sum(), a['总充值金额'].sum() / d['总充值金额'].sum() * 100, a['总充值金额'].median(),
    a['cg'].value_counts().to_dict(), a['身份'].value_counts().to_dict()))
print('   其中储值 ≥ 1,000 的 %d，银卡以上 %d，0–7 天 %.2f%%' % ((a['总充值金额'] >= 1000).sum(), (a['cg'] != '普卡').sum(), a['r07'].mean() * 100))
b = z[z['会员等级'] > 100]
print('押注=0 但会员等级>100：%d 人，等级中位 %.0f，储值>0 %d，卡组 %s，身份 %s' % (
    len(b), b['会员等级'].median(), (b['总充值金额'] > 0).sum(), b['cg'].value_counts().to_dict(), b['身份'].value_counts().to_dict()))
c = z[(z['身份'] != '新增')]
print('押注=0 的非新增非 VIP %d：注册天数中位 %.0f，活动赠点中位 %.0f，活动赠点=0 %d，会员等级中位 %.0f' % (
    len(c), c['tenure'].median(), c['活动赠点'].median(), (c['活动赠点'] == 0).sum(), c['会员等级'].median()))
print('   活动赠点=0 且储值=0 且等级≤1：%d（像是注册后从未玩过、这次只登录）' % ((c['活动赠点'] == 0) & (c['总充值金额'] <= 0) & (c['会员等级'] <= 1)).sum())
print('   押注=0 且（储值>0 或 等级>100）：%d' % ((c['总充值金额'] > 0) | (c['会员等级'] > 100)).sum())
# 与潜在付费口径的关系：押注=0 且从未储值者不在潜在付费里；押注被漏记的人若真押注>1万，会被漏掉
w = nv[(nv['游戏总押注'] == 0) & (nv['总充值金额'] <= 0)]
print('押注=0 且从未储值（非 VIP）%d：会员等级>100 的 %d（若押注漏记，最可能漏进潜在付费的一批）' % (len(w), (w['会员等级'] > 100).sum()))
print('\n== 押注=0 的比例按登录平台（有储值者；持續；VIP）')
for name, x in [('有储值者', d[d['总充值金额'] > 0]), ('持續', d[d['身份'] == '持續']), ('VIP', d[vip])]:
    t = x.groupby('plat')['游戏总押注'].agg(n='size', z=lambda b: (b == 0).sum())
    t['pct'] = (t['z'] / t['n'] * 100).round(2)
    print(name); print(t.sort_values('n', ascending=False).to_string())
sus = d[(~vip) & (d['游戏总押注'] == 0) & (d['身份'] != '新增') & ((d['总充值金额'] > 0) | (d['会员等级'] > 100))]
print('可疑漏记（非 VIP、非新增、押注=0 且储值>0 或等级>100）%d 人，平台 %s' % (len(sus), sus['plat'].value_counts().to_dict()))
# 押注为 0 却是银卡以上的非 VIP
e = z[z['cg'] != '普卡']
print('押注=0 的非 VIP 银卡以上 %d：储值中位 %.0f，卡别 %s' % (len(e), e['总充值金额'].median(), e['卡别'].value_counts().sort_index().to_dict()))
