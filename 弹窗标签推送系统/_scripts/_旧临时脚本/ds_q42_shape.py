import pandas as pd
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
ex = ['機器人', '測試帳號']
print('raw', len(a), len(c), 'dup ids', a['会员编号'].duplicated().sum(), c['会员编号'].duplicated().sum())
a = a[~a['身份'].isin(ex)].copy()
c = c[~c['身份'].isin(ex)].copy()
for d in (a, c):
    d['ll'] = pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()
    d['rg'] = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
    d['pay'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
    d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
    d['days'] = (pd.Timestamp('2026-09-16') - d['ll']).dt.days
only = c[~c['会员编号'].isin(a['会员编号'])]
both = c[c['会员编号'].isin(a['会员编号'])]
print('only', len(only), 'both', len(both))
print('only ll range', only['ll'].min(), only['ll'].max(), 'days', only['days'].min(), only['days'].max())
print('both ll range(churn file)', both['ll'].min(), both['ll'].max())
m = both.merge(a, on='会员编号', suffixes=('_c', '_a'))
print('both ll range(active file)', m['ll_a'].min(), m['ll_a'].max())
for col in ['卡别', '会员等级', 'pay', 'bet', '身份', '登入平台', 'll']:
    print(' mismatch', col, int((m[col + '_c'] != m[col + '_a']).sum()))
act_816_831 = a[(a['ll'] >= '2026-08-16') & (a['ll'] <= '2026-08-31')]
print('active ll 8/16-8/31', len(act_816_831), 'of which in churn', act_816_831['会员编号'].isin(c['会员编号']).sum())
print('only 身份', only['身份'].value_counts().to_dict())
print('only 卡别', only['卡别'].value_counts().sort_index().to_dict())
print('only 平台', only['登入平台'].value_counts().to_dict())
print('active 平台', a['登入平台'].value_counts().to_dict())
print('only rg missing', only['rg'].isna().sum(), 'rg>=2026-08-01', int((only['rg'] >= '2026-08-01').sum()), 'rg>ll', int((only['rg'] > only['ll']).sum()))
# registration cohort 8/1-8/15 completeness
u = pd.concat([a[['会员编号', 'rg', 'll', '身份', 'pay', 'bet', '卡别']], only[['会员编号', 'rg', 'll', '身份', 'pay', 'bet', '卡别']]])
coh = u[(u['rg'] >= '2026-08-01') & (u['rg'] <= '2026-08-15')]
print('cohort 8/1-8/15', len(coh), 'in only', int(coh['会员编号'].isin(only['会员编号']).sum()), 'same-day-only', int((coh['ll'] == coh['rg']).sum()))
print(' cohort 身份', coh['身份'].value_counts().to_dict())
print(' daily reg 8/1-8/15', coh.groupby('rg').size().describe().round(1).to_dict())
coh2 = u[(u['rg'] >= '2026-08-18') & (u['rg'] <= '2026-09-08')]
print(' daily reg 8/18-9/8', coh2.groupby('rg').size().describe().round(1).to_dict())
print(' only rg<2026-08 but 身份', only[only['rg'] >= '2026-08-01']['身份'].value_counts().to_dict())
# deposit distribution by card in active
card = lambda s: s.map(lambda x: '普' if x == 1 else ('银' if x == 2 else '金+'))
a['cg'] = card(a['卡别']); only = only.assign(cg=card(only['卡别']))
for g in ['普', '银', '金+']:
    p = a.loc[a['cg'] == g, 'pay']
    print('active', g, 'pay q10/25/50', p.quantile([.1, .25, .5]).round().tolist())
gold_p10 = a.loc[a['cg'] == '金+', 'pay'].quantile(.1)
gold_p25 = a.loc[a['cg'] == '金+', 'pay'].quantile(.25)
for nm, d in [('active', a), ('act 15-31', a[a['days'] >= 15]), ('act 0-7', a[a['days'] <= 7]), ('only', only)]:
    low = d[d['cg'] != '金+']
    print(nm, 'n', len(d), '非金 pay>=gold p10', int((low['pay'] >= gold_p10).sum()), 'pay>=gold p25', int((low['pay'] >= gold_p25).sum()), '金+', int((d['cg'] == '金+').sum()))
    print('  ', nm, 'pay>0 share', round((d['pay'] > 0).mean() * 100, 2), 'pay sum', round(d['pay'].sum()), 'pay>=1e5 n', int((d['pay'] >= 1e5).sum()), 'bet0&pay>0', int(((d['bet'] == 0) & (d['pay'] > 0)).sum()))
    print('  ', nm, '卡别 by 会员等级 median', d.groupby('cg')['会员等级'].median().to_dict())
# top payers in only
print('only top10 pay', only.sort_values('pay', ascending=False)[['pay', 'bet', '卡别', '会员等级', '登入平台']].head(10).values.tolist())
print('only pay share top 1%', round(only['pay'].nlargest(int(len(only) * .01)).sum() / only['pay'].sum() * 100, 2))
