import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
print('rows', len(d))
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(d)
print('N', N)
amt = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
d['amt'] = amt
d['pay'] = amt > 0
tot = amt.sum()
print('total', tot, 'neg n', (amt < 0).sum(), 'neg sum', amt[amt < 0].sum())
print('payers', d['pay'].sum(), d['pay'].mean())
print('身份 values', d['身份'].value_counts().to_dict())


def grp(key):
    g = d.groupby(key)
    for k, s in g:
        ps = s[s['pay']]
        print(k, len(s), round(len(s) / N * 100, 2), len(ps), round(len(ps) / len(s) * 100, 2),
              round(s['amt'].sum() / tot * 100, 2),
              round(ps['amt'].mean(), 0) if len(ps) else '-', ps['amt'].median() if len(ps) else '-')


print('== 身份')
grp('身份')
print('== 卡别')
grp('卡别')
d['cg'] = d['卡别'].map(lambda x: '1普' if x == 1 else ('2银' if x == 2 else '3金+'))
d['id3'] = d['身份'].replace({'VIP': '持續', '黑名單': '持續'})
print('== id3')
grp('id3')
print('== id x cg (raw身份)')
grp(['身份', 'cg'])
print('== cg')
grp('cg')
# concentration
ps = d[d['pay']].sort_values('amt', ascending=False)
n = len(ps)
for q in [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]:
    k = int(n * q)
    print('payer top', q, k, round(ps['amt'].head(k).sum() / tot * 100, 2), ps['amt'].iloc[k - 1])
al = d.sort_values('amt', ascending=False)
for q in [0.01, 0.1]:
    k = int(N * q)
    print('all top', q, k, round(al['amt'].head(k).sum() / tot * 100, 2))
g = d[d['cg'] == '3金+']
print('gold+ nonpay', (g['amt'] <= 0).sum(), 'normal>=10000', ((d['卡别'] == 1) & (d['amt'] >= 10000)).sum())
# registration
rt = pd.to_datetime(d['注册时间'], errors='coerce')
print('reg null', rt.isna().sum())
d['rt'] = rt
for idn in ['回流', '持續']:
    s = d[d['身份'] == idn]
    v = s['rt'].dropna()
    print(idn, len(s), len(v), round((v.dt.year <= 2023).mean() * 100, 2), v.median())
# 新增 payer <200 share etc (for 环节1 distribution)
for idn, s in d[d['pay']].groupby('id3'):
    print(idn, len(s), round((s['amt'] <= 50).mean() * 100, 2), round(((s['amt'] > 50) & (s['amt'] <= 200)).mean() * 100, 2), s['amt'].median())
