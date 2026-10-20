"""R52：VIP 储值为 0 的人数；押注与储值两列都为 0 的账号规模（审查意见 2）。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['tenure'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间']).dt.normalize()).dt.days
v = d[d['身份'] == 'VIP']
dep0 = v['总充值金额'] <= 0
bet0 = v['游戏总押注'] == 0
print('VIP %d：储值>0 %d，储值≤0 %d（卡别 %s），其中押注也为 0 %d；储值>0 且押注=0 %d' % (
    len(v), (~dep0).sum(), dep0.sum(), v.loc[dep0, '卡别'].value_counts().sort_index().to_dict(), (dep0 & bet0).sum(), ((~dep0) & bet0).sum()))
pp = (d['总充值金额'] <= 0) & (d['游戏总押注'] > 1e4)
print('潜在付费代理 %d 人中 VIP %d' % (pp.sum(), (pp & (d['身份'] == 'VIP')).sum()))
print('VIP 储值≤0 者：会员等级中位 %.0f，注册天数中位 %.0f' % (v.loc[dep0, '会员等级'].median(), v.loc[dep0, 'tenure'].median()))

both = (d['总充值金额'] <= 0) & (d['游戏总押注'] == 0)
print('\n全体两列都为 0（储值≤0 且押注=0）%d 人，身份 %s' % (both.sum(), d.loc[both, '身份'].value_counts().to_dict()))
nv = d['身份'] != 'VIP'
x = d[both & nv & (d['身份'] != '新增')]
print('其中非 VIP 非新增 %d：会员等级 >100 的 %d，注册 ≥ 1 年的 %d，活动赠点=0 的 %d' % (
    len(x), (x['会员等级'] > 100).sum(), (x['tenure'] >= 365).sum(), (x['活动赠点'] == 0).sum()))
print('卡别 ≥2 且两列都为 0（非 VIP）%d' % (both & nv & (d['卡别'] >= 2)).sum())
