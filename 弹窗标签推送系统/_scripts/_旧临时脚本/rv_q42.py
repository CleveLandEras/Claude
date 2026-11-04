# 审查者只读复算：A13 八月离开的用户（Q42）
import pandas as pd
import numpy as np

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
act = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
chu = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
print('cols', list(act.columns))
print('raw', len(act), len(chu))
bad = ['機器人', '測試帳號']
act = act[~act['身份'].isin(bad)].copy()
chu = chu[~chu['身份'].isin(bad)].copy()
print('clean', len(act), len(chu))
print('dup', act['会员编号'].duplicated().sum(), chu['会员编号'].duplicated().sum())

REF = pd.Timestamp('2026-09-16')
for d in (act, chu):
    d['ll'] = pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()
    d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
    d['days'] = (REF - d['ll']).dt.days
    d['regdays'] = (REF - d['reg']).dt.days
    d['dep'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
    d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
    d['card'] = pd.to_numeric(d['卡别'], errors='coerce')
    d['cg'] = np.where(d['card'] == 1, '普', np.where(d['card'] == 2, '银', '金'))
    p = d['登入平台'].astype(str).str.lower()
    d['app'] = p.isin(['android', 'ios', 'apk'])
    d['brw'] = p.isin(['mweb', 'web', 'h5', 'mh5'])
    d['pp'] = (d['dep'] <= 0) & (d['bet'] > 10000)

lv = chu[~chu['会员编号'].isin(act['会员编号'])].copy()
ov = chu[chu['会员编号'].isin(act['会员编号'])]
print('leavers', len(lv), 'overlap', len(ov))
print('leaver days range', lv['days'].min(), lv['days'].max())
print('leaver ll range', lv['ll'].min(), lv['ll'].max())

def band(x):
    if x <= 7: return 'a0-7'
    if x <= 14: return 'b8-14'
    return 'c15-31'
act['band'] = act['days'].apply(band)
lv['band'] = 'd32-46'
allp = pd.concat([act, lv], ignore_index=True)
print('merged', len(allp))
tot = allp['dep'].sum()
print('tot dep merged', tot, 'act', act['dep'].sum(), 'lv', lv['dep'].sum(), 'ratio lv/act %.4f' % (lv['dep'].sum() / act['dep'].sum()))

def prof(g, name):
    n = len(g)
    pay = g[g['dep'] > 0]
    r = dict(n=n,
             pu=(g.cg == '普').mean() * 100, yin=(g.cg == '银').mean() * 100, jin=(g.cg == '金').mean() * 100, njin=(g.cg == '金').sum(),
             pay=(g.dep > 0).mean() * 100, paymed=pay.dep.median(), depshare=g.dep.sum() / tot * 100,
             betmed=g.bet.median(), bet0=(g.bet == 0).mean() * 100, pp=g.pp.mean() * 100,
             aug=(g.reg >= pd.Timestamp('2026-08-01')).mean() * 100,
             y1=(g.regdays > 365).mean() * 100,
             app=g.app.mean() * 100, brw=g.brw.mean() * 100)
    print(name, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})

for b, g in allp.groupby('band'):
    prof(g, b)
print('--- pre-Aug reg only')
pre = allp[allp['reg'] < pd.Timestamp('2026-08-01')]
for b, g in pre.groupby('band'):
    prof(g, b)

print('--- table2 by cardgroup share in leaver band')
for cg, g in allp.groupby('cg'):
    print(cg, len(g), (g.band == 'd32-46').mean() * 100, (g.band == 'd32-46').sum())
for th in (10000, 100000):
    g = allp[allp.dep >= th]
    print('dep>=', th, len(g), (g.band == 'd32-46').mean() * 100, (g.band == 'd32-46').sum())

print('--- concentration')
s = lv['dep'].sort_values(ascending=False)
print('top10 share', s.head(10).sum() / s.sum() * 100, 'top1% n', int(len(lv) * 0.01), s.head(int(round(len(lv) * 0.01))).sum() / s.sum() * 100)
print('ex top10 / act', (s.sum() - s.head(10).sum()) / act['dep'].sum() * 100)
print('lv by cg share', lv.groupby('cg').dep.sum() / lv.dep.sum() * 100)
lj = lv[lv.cg == '金']
print('lv jin n', len(lj), 'dep', lj.dep.sum(), 'share of act', lj.dep.sum() / act.dep.sum() * 100, 'paymed', lj[lj.dep > 0].dep.median())
print('lv jin top10 share', lj.dep.sort_values(ascending=False).head(10).sum() / lj.dep.sum() * 100)
z = lv[(lv.bet == 0) & (lv.dep > 0)]
print('lv bet0 dep>0', len(z), z.dep.sum(), z.dep.sum() / lv.dep.sum() * 100)
za = act[(act.bet == 0) & (act.dep > 0)]
print('act bet0 dep>0', len(za), za.dep.sum(), 'ratio ex', (lv.dep.sum() - z.dep.sum()) / (act.dep.sum() - za.dep.sum()) * 100)

print('--- S4')
aj = act[act.cg == '金'].dep
p25, p50 = aj.quantile(0.25), aj.median()
print('p25', p25, 'p50', p50)
for b, g in allp.groupby('band'):
    nj = g[g.cg != '金']
    h = nj[nj.dep >= p25]; h2 = nj[nj.dep >= p50]
    print(b, len(nj), len(h), round(len(h) / len(nj) * 100, 3), (h.cg == '普').sum(), (h.cg == '银').sum(), len(h2), round(len(h2) / len(nj) * 100, 3))

print('--- S5 cohort')
co = allp[(allp.reg >= pd.Timestamp('2026-08-01')) & (allp.reg <= pd.Timestamp('2026-08-15'))]
print('cohort', len(co), 'daily', len(co) / 15)
print('left', (co.band == 'd32-46').sum(), (co.band == 'd32-46').mean() * 100)
one = co[co.ll == co.reg]
print('oneday', len(one), len(one) / len(co) * 100)
g1000 = co[pd.to_numeric(co['活动赠点'], errors='coerce') == 1000]
print('gift1000', len(g1000), len(g1000) / len(co) * 100, 'oneday among', (g1000.ll == g1000.reg).mean() * 100)
print('oneday share of leavers', len(one[one.band == 'd32-46']) / len(lv) * 100, len(one[one.band == 'd32-46']))
a12 = act[(act.reg >= pd.Timestamp('2026-08-18')) & (act.reg <= pd.Timestamp('2026-09-08'))]
print('a12 cohort 8/18-9/8', len(a12), len(a12) / 22, 'oneday', (a12.ll == a12.reg).mean() * 100)
print('leaver aug reg', (lv.reg >= pd.Timestamp('2026-08-01')).sum())
