import pandas as pd
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
print('cols', list(c.columns))
ex = ['機器人', '測試帳號']
a = a[~a['身份'].isin(ex)]
c = c[~c['身份'].isin(ex)]
idcol = '会员编号' if '会员编号' in c.columns else c.columns[0]
only = c[~c[idcol].isin(a[idcol])]
both = c[c[idcol].isin(a[idcol])]
print('churn rows', len(c), 'only', len(only), 'both', len(both))
def card(s):
    return s.map(lambda x: '普卡' if x == 1 else ('银卡' if x == 2 else '金卡以上'))
for name, d in [('active', a), ('churn_only', only)]:
    pay = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
    bet = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
    print('==', name, len(d))
    print(' 身份', d['身份'].value_counts().to_dict())
    print(' 卡别', card(d['卡别']).value_counts().to_dict())
    print(' 有储值', int((pay > 0).sum()), round((pay > 0).mean() * 100, 2))
    print(' 储值合计', round(pay.sum()), ' 押注>1万且从未储值', int(((bet > 10000) & (pay <= 0)).sum()))
    g = d.assign(p=pay, cd=card(d['卡别'])).groupby('cd')['p'].sum()
    print(' 储值按卡别', g.round().to_dict())
    print(' 平台', d['登入平台'].value_counts().head(6).to_dict())
    reg = pd.to_datetime(d['注册时间'], errors='coerce')
    print(' 注册<2026-08', int((reg < '2026-08-01').sum()))
tot = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0).sum() + pd.to_numeric(only['总充值金额'], errors='coerce').fillna(0).sum()
print('合并储值', round(tot))
v = a[a['身份'] == 'VIP']
vb = pd.to_numeric(v['游戏总押注'], errors='coerce').fillna(0)
vp = pd.to_numeric(v['总充值金额'], errors='coerce').fillna(0)
z = v[vb == 0]
zp = vp[vb == 0]
allpay = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
print('VIP押注0', len(z), '其中储值>0', int((zp > 0).sum()), '储值中位', round(zp[zp > 0].median()), '占全体储值', round(zp.sum() / allpay[allpay > 0].sum() * 100, 2))
print('输赢', pd.to_numeric(z['游戏总输赢'], errors='coerce').fillna(0).abs().sum())
