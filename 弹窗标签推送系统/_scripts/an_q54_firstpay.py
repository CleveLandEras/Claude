"""Q54 / A10 纠错：首储礼包 = NT$50、16,800 点（Dk 既有资料 ①，产品体验报告 P30、P59）。
按 A10 原方法（an_a10_huikui.py）重算「只买过首储」与「首储 + 一个已知固定档位」的下界，并重出画像。
数据：数据/近一月活跃_20260916.csv；剔除機器人、測試帳號后 62,292 人。只读，不带参数。
"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(d)
d['amt'] = d['总充值金额']
d['r'] = d['储值回馈比']
d['a0'] = d['amt'].round(2)
d['g0'] = d['充值赠点'].round(0)
pay = d[d['amt'] > 0]
NP = len(pay)
print('N 全体', N, ' 有储值', NP)

FA, FG = 50, 16800  # 首储：50 元、16,800 点

print('\n==== ① 首储指纹 50 元 @ 16,800 点 ====')
s50 = pay[pay['a0'] == 50]
print('储值恰为 50 的人数', len(s50), ' 充值赠点分布', s50['g0'].value_counts().head(8).to_dict())
print('充值赠点恰为 16,800 的人的储值额', pay[pay['g0'] == FG]['a0'].value_counts().head(6).to_dict())
print('回馈比 336 的人的储值额', pay[pay['r'].round(0) == 336]['a0'].value_counts().head(6).to_dict())
fb = pay[(pay['a0'] == FA) & (pay['g0'] == FG)]
print('下界 1（只买过首储）', len(fb), ' 占全体 %.2f%%' % (len(fb) / N * 100), ' 占有储值 %.2f%%' % (len(fb) / NP * 100),
      ' 储值合计', fb['amt'].sum(), ' 占全部累计储值 %.4f%%' % (fb['amt'].sum() / pay['amt'].sum() * 100))

print('\n==== ② 首储 + 一个已知固定档位（精确储值额 + 精确充值赠点）====')
# 已知固定档位：取 A10 表 2 各档的充值赠点众数（本脚本重取）
tiers = {'70@200': (70, 200), '30@333': (30, 333), '33@303': (33, 303), '30@100': (30, 100), '30@108': (30, 108),
         '50@100': (50, 100), '60@104': (60, 104), '50@300（15,000 点，档位未知）': (50, 300)}
known = {}
for name, (a, rv) in tiers.items():
    s = pay[(pay['a0'] == a) & (pay['r'].round(0) == rv)]
    vc = s['g0'].value_counts()
    known[name] = (a, int(vc.index[0]), len(s), int(vc.iloc[0]))
    print(f'{name}: n={len(s)}  充值赠点众数 {int(vc.index[0])}（{int(vc.iloc[0])} 人）')
tot = 0
for name, (a, g, n, _) in known.items():
    s = pay[(pay['a0'] == FA + a) & (pay['g0'] == FG + g)]
    tot += len(s)
    print(f'首储 + {name}: 储值 {FA + a}、赠点 {FG + g}  命中 {len(s)}')
print('首储 + 一个已知档位 合计', tot, ' 下界 2 =', len(fb) + tot)
# 方法对照（不含首储）
for name, (a, g) in {'70@200 + 30@333': (100, 24000), '50@300 + 70@200': (120, 29000), '50@300 + 30@108': (80, 18240)}.items():
    print(f'对照 {name}（{a} 元、{g} 点）命中', len(pay[(pay['a0'] == a) & (pay['g0'] == g)]))

print('\n==== ③ 画像（行内占比；分母为各组人数）====')
ref = pd.Timestamp('2026-09-16')
d['last'] = pd.to_datetime(d['最後登入時間'], errors='coerce')
d['days'] = (ref.normalize() - d['last'].dt.normalize()).dt.days
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce')
d['regdays'] = (ref.normalize() - d['reg'].dt.normalize()).dt.days
d['cardg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
plat = d['登入平台'].astype(str).str.lower()
d['platg'] = np.where(plat.isin(['android', 'ios', 'apk']), 'App类', np.where(plat.isin(['web', 'mweb', 'mh5', 'h5']), '浏览器类', '缺值'))
d['dayg'] = pd.cut(d['days'], [-1, 7, 14, 31, 10000], labels=['0–7天', '8–14天', '15–31天', '>31天'])
d['regg'] = pd.cut(d['regdays'], [-1, 29, 90, 365, 1e6], labels=['≤29天', '30–90天', '91–365天', '>1年'])
f15 = pay[(pay['a0'] == 50) & (pay['g0'] == 15000)].index
d['grp'] = '其他有储值'
d.loc[d['amt'] <= 0, 'grp'] = '从未储值其余'
d.loc[(d['amt'] <= 0) & (d['游戏总押注'] > 10000), 'grp'] = '潜在付费代理'
d.loc[d.index.isin(f15), 'grp'] = '50元15000点（档位未知）'
d.loc[d.index.isin(fb.index), 'grp'] = '只买首储16800'
print('分组人数', d['grp'].value_counts().to_dict())
for c in ['身份', 'cardg', 'platg', 'dayg', 'regg']:
    t = pd.crosstab(d['grp'], d[c], normalize='index').mul(100).round(2)
    t['分母'] = d['grp'].value_counts()
    print(f'\n-- {c} --')
    print(t.to_string())
g = d.groupby('grp')
print('\n押注中位', g['游戏总押注'].median().round(0).to_dict())
print('押注 > 1万 %', g.apply(lambda x: round((x['游戏总押注'] > 10000).mean() * 100, 2)).to_dict())
print('押注 > 10万 %', g.apply(lambda x: round((x['游戏总押注'] > 100000).mean() * 100, 2)).to_dict())
print('会员等级中位', g['会员等级'].median().to_dict())
print('活动赠点中位', g['活动赠点'].median().round(0).to_dict())
fbd = d[d['grp'] == '只买首储16800']
print('只买首储 16,800 平台原值', fbd['登入平台'].value_counts().to_dict())
print('只买首储 16,800 注册 ≤ 90 天 %', round((fbd['regdays'] <= 90).mean() * 100, 2), ' 新增者 n', int((fbd['身份'] == '新增').sum()))
nw = d[(d['身份'] == '新增') & (d['amt'] > 0)]
print('新增有储值', len(nw), ' 其中 50 元', int((nw['a0'] == 50).sum()), ' 50@16800', int(((nw['a0'] == 50) & (nw['g0'] == FG)).sum()),
      ' 50@15000', int(((nw['a0'] == 50) & (nw['g0'] == 15000)).sum()))
