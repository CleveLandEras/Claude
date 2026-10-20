import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
sys.path.insert(0, _ROOT + '/_scripts')
import pandas as pd
from an_a45_members import load

df, m = load()
pay, bet, idn, act = m['pay'], m['bet'], m['idn'], m['act']
N = len(df)
P = df['present']
new, back = df['is_new'], df['is_back']
pp, ppv, ch, bp = df['pp_wide'], df['pp_verified'], df['churn_ub'], df['back_present']

# R295：在场用户里不属于任何一类，宽口径 vs 窄口径
wide = new | back | pp | ch
nar = new | bp | ppv
print('在场', P.sum())
print('在场内未覆盖 宽口径', (P & ~wide).sum(), '窄口径', (P & ~nar).sum(), '其中有储值', (P & ~nar & df['has_paid']).sum())
print('窄口径在场未覆盖占在场', (P & ~nar).sum() / P.sum())
print('宽口径未覆盖 离线', (~P & ~wide).sum(), '在场', (P & ~wide).sum())
# 在场口径未覆盖 28,988 中，属于五类成员（新增/回流）的离线人数
pres_u = wide & P
unc_pres = ~pres_u
print('在场口径未覆盖', unc_pres.sum(), '其中 新增/回流成员', (unc_pres & (new | back)).sum(),
      '其余（非新非回）', (unc_pres & ~(new | back)).sum())

# R296：新增∩潜在付费 占比两种分母
x = (new & pp).sum()
print('新∩付', x, '占付 上界', x / pp.sum(), '占付 可核实', x / ppv.sum(), '上界分母', pp.sum(), '可核实分母', ppv.sum())
print('新∩付 全部落在可核实内', (new & pp & ppv).sum())

# R299：新增账龄对照
z = df[new & (df[bet] == 0)]
print('新增押注0', len(z), '赠点=1000', (z[act] == 1000).sum(), '占比', (z[act] == 1000).mean(), '注册>=7天', (z['age'] >= 7).sum(), (z['age'] >= 7).mean())
nw = df[new]
print('新增在场率', nw['present'].mean(), '全体', P.mean())
for a, b in [(0, 7), (8, 29), (30, 59), (60, 119)]:
    g = df[(df['age'] >= a) & (df['age'] <= b)]
    print('注册', a, b, len(g), '在场率', g['present'].mean())
print('新增 age>=8 在场率', nw[nw['age'] >= 8]['present'].mean(), (nw['age'] >= 8).sum())
