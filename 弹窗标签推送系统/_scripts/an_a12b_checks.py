"""A12 补充：=1000 按注册月份出现的时点；500 是否回流礼；押注为 0 的老账号（累计口径检查）；网页新增是否拿不到 1000。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['rt'] = pd.to_datetime(d['注册时间'])
d['tenure'] = (pd.Timestamp('2026-09-16') - d['rt'].dt.normalize()).dt.days
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
d['pcls'] = np.where(d['plat'].isin(['android', 'ios', 'apk']), 'App', np.where(d['plat'] == '缺值', '缺值', '浏览器'))
d['rm'] = d['rt'].dt.to_period('M')
H, B = d['活动赠点'], d['游戏总押注']

print('== 注册月份（2025-01 起）：人数、赠点恰 1000 比例、赠点=0 比例、押注=0 比例、身份构成')
g = d[d['rt'] >= '2025-01-01'].groupby('rm')
t = g.agg(n=('活动赠点', 'size'), eq1000=('活动赠点', lambda h: round((h == 1000).mean() * 100, 2)),
          eq0=('活动赠点', lambda h: round((h == 0).mean() * 100, 2)),
          bet0=('游戏总押注', lambda b: round((b == 0).mean() * 100, 2)))
t['新增'] = g['身份'].apply(lambda s: (s == '新增').sum())
print(t.to_string())

print('\n== 赠点恰 500：身份分布、注册年份分布、押注中位')
f = d[H == 500]
print(f['身份'].value_counts().to_dict(), f['rt'].dt.year.value_counts().sort_index().to_dict(), '押注中位', f['游戏总押注'].median(), '押注=0', (f['游戏总押注'] == 0).sum())
print('回流中赠点 500–599 的人数', ((d['身份'] == '回流') & (H >= 500) & (H < 600)).sum(), ' 持續中', ((d['身份'] == '持續') & (H >= 500) & (H < 600)).sum(), ' 新增中', ((d['身份'] == '新增') & (H >= 500) & (H < 600)).sum())

print('\n== 押注=0 的人：身份分布；按注册年份（非新增）')
z = d[B == 0]
print('押注=0 共', len(z), z['身份'].value_counts().to_dict())
nz = z[z['身份'] != '新增']
print('非新增押注=0 按注册年份', nz['rt'].dt.year.value_counts().sort_index().to_dict())
print('非新增押注=0：赠点中位 %.0f，赠点=0 %d，储值>0 %d，会员等级中位 %.0f，0–7 天 %.2f%%' % (
    nz['活动赠点'].median(), (nz['活动赠点'] == 0).sum(), (nz['总充值金额'] > 0).sum(), nz['会员等级'].median(), (nz['days'] <= 7).mean() * 100))
old = nz[nz['rt'] < '2025-01-01']
print('2025 年以前注册、押注=0 的非新增 %d 人：会员等级中位 %.0f，等级>100 %d，储值>0 %d' % (
    len(old), old['会员等级'].median(), (old['会员等级'] > 100).sum(), (old['总充值金额'] > 0).sum()))
print('  其中身份', old['身份'].value_counts().to_dict())

print('\n== 新增：赠点 <1000 的平台构成 vs 全部新增；网页新增拿到 ≥1000 的比例')
new = d[d['身份'] == '新增']
for c in ['App', '浏览器']:
    x = new[new['pcls'] == c]
    print(c, len(x), '赠点<1000 %.2f%%，=0 %.2f%%，=1000 %.2f%%，>1000 %.2f%%' % (
        (x['活动赠点'] < 1000).mean() * 100, (x['活动赠点'] == 0).mean() * 100, (x['活动赠点'] == 1000).mean() * 100, (x['活动赠点'] > 1000).mean() * 100))
for p in ['mweb', 'mh5', 'h5', 'web', 'android', 'ios', 'apk']:
    x = new[new['plat'] == p]
    print('  ', p, len(x), '<1000 %.2f%%' % ((x['活动赠点'] < 1000).mean() * 100))

print('\n== 新增 =1000 且最后登录=注册日：注册在 8 天以前的人数（只来了注册当天）')
e = new[(new['活动赠点'] == 1000)]
one = e[(e['tenure'] == e['days'])]
print('=1000 且只在注册日登录 %d；其中注册 ≥8 天 %d；占全部新增 %.2f%%；占注册 ≥8 天新增 %.2f%%' % (
    len(one), (one['tenure'] >= 8).sum(), len(one) / len(new) * 100, (one['tenure'] >= 8).sum() / (new['tenure'] >= 8).sum() * 100))
print('注册 ≥8 天的新增 %d 人' % (new['tenure'] >= 8).sum())
print('只在注册日登录的新增（不论赠点）%d（%.2f%%）；其中赠点=1000 %d' % ((new['tenure'] == new['days']).sum(), (new['tenure'] == new['days']).mean() * 100, len(one)))
n8 = new[new['tenure'] >= 8]
o8 = n8[n8['tenure'] == n8['days']]
print('注册 ≥8 天的新增 %d 人中只在注册日登录 %d（%.2f%%）；其中赠点=1000 %d、>1000 %d、<1000 %d；押注中位 %.0f' % (
    len(n8), len(o8), len(o8) / len(n8) * 100, (o8['活动赠点'] == 1000).sum(), (o8['活动赠点'] > 1000).sum(), (o8['活动赠点'] < 1000).sum(), o8['游戏总押注'].median()))
print('  只在注册日登录者：>1000 的赠点中位 %.0f，押注中位 %.0f' % (o8.loc[o8['活动赠点'] > 1000, '活动赠点'].median(), o8.loc[o8['活动赠点'] > 1000, '游戏总押注'].median()))
print('注册 ≥8 天、来过不止一天的新增 %d：赠点=1000 %d（%.2f%%）' % (len(n8) - len(o8), ((n8['tenure'] != n8['days']) & (n8['活动赠点'] == 1000)).sum(), ((n8['tenure'] != n8['days']) & (n8['活动赠点'] == 1000)).sum() / (len(n8) - len(o8)) * 100))
print('新增 =1000 押注中位（全部 %.0f；只来注册日 %.0f；来过不止一天 %.0f）' % (e['游戏总押注'].median(), one['游戏总押注'].median(), e[e['tenure'] != e['days']]['游戏总押注'].median()))
