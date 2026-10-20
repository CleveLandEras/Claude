"""Q14：首储与储值位（D4a、D4b）。照设计卡 Q14 S1–S4。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']
NOV = ['VIP', '黑名單']

d = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
d = d[~d['身份'].isin(EX)].copy()
d['last'] = pd.to_datetime(d['最後登入時間']).dt.normalize()
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
d['days'] = (T0 - d['last']).dt.days
d['tenure'] = (T0 - d['reg']).dt.days
d['dep'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
d['bon'] = pd.to_numeric(d['充值赠点'], errors='coerce').fillna(0)
d['hk'] = pd.to_numeric(d['储值回馈比'], errors='coerce')
d['nov'] = ~d['身份'].isin(NOV)
d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
d['pp'] = (d['dep'] <= 0) & (d['bet'] > 10000)
print('活跃', len(d))

pay = d[d['dep'] > 0]
print('\n===== S1')
print(f'  从未储值 {int((d["dep"] <= 0).sum()):,}（主数 {int(((d["dep"] <= 0) & d["nov"]).sum()):,}）；潜在付费上限 {int(d["pp"].sum()):,}；有储值 {len(pay):,}')


def desc(g, name):
    q = g['dep']
    print(f'  {name}: {len(g):,} 人｜卡组 普/银/金 {int((g.cg == "普卡").sum())}/{int((g.cg == "银卡").sum())}/{int((g.cg == "金卡以上").sum())}（普卡 {(g.cg == "普卡").mean() * 100:.2f}%）'
          f'｜身份 持續/回流/新增/VIP/黑 {"/".join(str(int((g["身份"] == k).sum())) for k in ["持續", "回流", "新增", "VIP", "黑名單"])}'
          f'｜储值 中位 {q.median():,.0f} P75 {q.quantile(.75):,.0f} 最高 {q.max():,.0f}｜0–7 天 {int((g.days <= 7).sum()):,}｜回馈比<100 {int((g.hk < 100).sum())}')


print('\n===== S2 D4a 下界：有储值且充值赠点 < 15,000')
lb = pay[pay['bon'] < 15000]
desc(lb, '全部（含VIP）')
desc(lb[lb['nov']], '主数')
lb16 = pay[pay['bon'] < 16800]
print(f'  对照 < 16,800：{len(lb16):,}（主数 {int(lb16["nov"].sum()):,}）')
new6 = pay[pay['reg'] >= '2026-06-01']
lb6 = new6[new6['bon'] < 15000]
print(f'  2026-06 以后注册的有储值者 {len(new6):,}，其中 < 15,000 {len(lb6):,}')
desc(lb6, '2026-06 以后注册子集')
lb['fp'] = lb['dep'].round(0).astype(int).astype(str) + '@' + lb['hk'].round(0).astype('Int64').astype(str)
print('  档位指纹前 12：', lb['fp'].value_counts().head(12).to_dict())
for fp in ['70@200', '30@333', '33@303', '30@100', '30@108', '50@100']:
    print(f'    {fp}: {int((lb["fp"] == fp).sum())}')
print(f'  储值分布：≤50 {int((lb.dep <= 50).sum())}，51–100 {int(((lb.dep > 50) & (lb.dep <= 100)).sum())}，>100 {int((lb.dep > 100).sum())}')
print(f'  与 D1 重叠（金卡以上主数）{int(((lb.cg == "金卡以上") & lb.nov).sum())}')

print('\n===== S3 D4a 错位上界：充值赠点 ≥ 15,000，扣去 50@336 的 129 人（组合 17 人未扣）')
ub = pay[(pay['bon'] >= 15000) & ~((pay['dep'] == 50) & (pay['bon'] == 16800))]
for cg in ['金卡以上', '银卡', '普卡']:
    x = ub[ub.cg == cg]
    xn = x[x.nov]
    print(f'  {cg}: {len(x):,}（主数 {len(xn):,}），0–7 天 {int((xn.days <= 7).sum()):,}，储值中位 {xn.dep.median():,.0f}')
print(f'  合计 {len(ub):,}（主数 {int(ub.nov.sum()):,}）；50@336 人数 {int(((pay.dep == 50) & (pay.bon == 16800)).sum())}')

print('\n===== S4 D4b：从未储值、0–7 天登录（主数）')
nb = d[(d['dep'] <= 0) & d['nov'] & (d['days'] <= 7)].copy()
bins = [-1, 29, 90, 365, 1095, 100000]
labs = ['<30 天', '30–90 天', '91–365 天', '1–3 年', '3 年以上']
nb['tb'] = pd.cut(nb['tenure'], bins, labels=labs).astype(str)
tab = pd.crosstab(nb['tb'], nb['身份'], margins=True).reindex(labs + ['nan', 'All'])
print(tab.to_string())
pt = nb.groupby('tb')['pp'].sum().reindex(labs)
print('  潜在付费代理（押注>1万）', pt.to_dict(), '合计', int(nb['pp'].sum()))
tot = len(nb)
ge1y = int(nb['tenure'].ge(366).sum())
print(f'  合计 {tot:,}；注册 1 年以上（>365 天）{ge1y:,}（{ge1y / tot * 100:.2f}%）；<30 天 {int((nb.tenure <= 29).sum()):,}；注册缺值 {int(nb.reg.isna().sum())}')

print('\n===== 新增付费参照（完整注册队列，按注册天数）')
nw = d[d['身份'] == '新增'].copy()
nw['tb'] = pd.cut(nw['tenure'], [-1, 0, 7, 14, 21, 29], labels=['0 天', '1–7', '8–14', '15–21', '22–29']).astype(str)
for k, g in nw.groupby('tb'):
    print(f'  注册 {k}: {len(g):,} 人，有储值 {int((g.dep > 0).sum())}（{(g.dep > 0).mean() * 100:.2f}%）')
np_ = nw[nw.dep > 0]
print(f'  新增有储值 {len(np_):,}（{len(np_) / len(nw) * 100:.2f}%）；储值恰 50 元 {int((np_.dep == 50).sum())}（{(np_.dep == 50).mean() * 100:.2f}%），其中 16,800 点 {int(((np_.dep == 50) & (np_.bon == 16800)).sum())}、15,000 点 {int(((np_.dep == 50) & (np_.bon == 15000)).sum())}')
print(f'  新增有储值者中充值赠点 ≥ 15,000 {int((np_.bon >= 15000).sum())}')
