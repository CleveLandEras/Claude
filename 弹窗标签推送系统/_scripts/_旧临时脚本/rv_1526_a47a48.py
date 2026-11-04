import sys
sys.path.insert(0, '/Users/decheng.huang/claude/弹窗标签推送系统/_scripts')
import pandas as pd
from an_a45_members import load, _read

df, m = load()
pay, bet, idn, card = m['pay'], m['bet'], m['idn'], m['card']
N = len(df)
P = df['present']
new, back = df['is_new'], df['is_back']
pp, ch = df['pp_wide'], df['churn_ub']
ppv = df['pp_verified']
bp = df['back_present']
print('N', N, 'present', P.sum())
# overlaps wide
for nm, a, b in [('新∩回', new, back), ('新∩付', new, pp), ('新∩流', new, ch), ('回∩付', back, pp), ('回∩流', back, ch), ('付∩流', pp, ch)]:
    print(nm, '宽', (a & b).sum(), '在场', (a & b & P).sum())
print('窄 新∩付可核实', (new & ppv).sum(), '回在场∩付可核实', (bp & ppv).sum(), '回(存量)∩付可核实', (back & ppv).sum())
# 窄口径: 新增10749, 回流在场8022, 付可核实5976, 流=0
nar = new | bp | ppv
print('窄并集', nar.sum(), '未覆盖', N - nar.sum())
wide = new | back | pp | ch
print('宽并集', wide.sum(), '未覆盖', N - wide.sum())
pres_u = (new | back | pp | ch) & P
print('在场并集(宽∩在场)', pres_u.sum(), '未覆盖', N - pres_u.sum(), '在场内未覆盖', (P & ~(new | back | pp | ch)).sum())
# 命中类数
cnt = new.astype(int) + back.astype(int) + pp.astype(int) + ch.astype(int)
print('宽 命中分布', cnt.value_counts().to_dict())
cntn = new.astype(int) + bp.astype(int) + ppv.astype(int)
print('窄 命中分布', cntn.value_counts().to_dict())
cntp = (new & P).astype(int) + (back & P).astype(int) + (pp & P).astype(int) + (ch & P).astype(int)
print('在场口径 命中', cntp.value_counts().to_dict())
tot = df[pay].sum()
print('累计储值', tot)
print('窄口径未覆盖储值占比', df[~nar][pay].sum() / tot)
print('宽口径未覆盖储值', df[~wide][pay].sum(), df[~wide][pay].sum() / tot)
print('在场口径未覆盖储值占比', df[~pres_u][pay].sum() / tot)
# 窄口径未覆盖中 持续有储值在场
cont = ~new & ~back & ~df[idn].isin(['VIP', 'VIP玩家', '黑名單'])
x = df[~nar & df['has_paid'] & P & (df[idn] == '持續')]
print('持續有储值在场 窄未覆盖', len(x), x[pay].sum() / tot)
print('VIP', (df[idn].isin(['VIP', 'VIP玩家'])).sum(), '黑名單', (df[idn] == '黑名單').sum(), 'VIP储值占', df[df[idn].isin(['VIP', 'VIP玩家'])][pay].sum() / tot)
# 破产暴露内分布
bk = df['bk_ub_bet']
print('bk', bk.sum(), 'new', (bk & new).sum(), 'back', (bk & back).sum(), 'pp', (bk & pp).sum(), 'ch', (bk & ch).sum(), 'none', (bk & ~(new | back | pp | ch)).sum())
# 离线分档
dfa, ma = _read('八月登录流失名单_20260916.csv')
only = dfa[~dfa[ma['id']].isin(set(df[m['id']]))]
print('only', len(only), 'dsl range', only['dsl'].min(), only['dsl'].max())
off = df[df['dsl'] >= 8]
print('活跃内离线', len(off), '≥15', (df['dsl'] >= 15).sum(), '合并离线', len(off) + len(only), '合并≥15', (df['dsl'] >= 15).sum() + (only['dsl'] >= 15).sum())
print('合并总', N + len(only), '离线占', (len(off) + len(only)) / (N + len(only)))
print('离线储值', off[pay].sum() + only[pay].sum(), (off[pay].sum() + only[pay].sum()) / (tot + only[pay].sum()))
print('only >=15', (only['dsl'] >= 15).sum(), 'only dsl 8-14', ((only['dsl'] >= 8) & (only['dsl'] <= 14)).sum())
# 8-14 layer composition merged
al = pd.concat([df, only])
for a, b in [(8, 14), (15, 31), (32, 99)]:
    x = al[(al['dsl'] >= a) & (al['dsl'] <= b)]
    print(a, b, len(x), (x[pay] > 0).sum(), x[pay].sum(), x[idn].value_counts().to_dict())
# 持續 在场无储值 押注<=10000
print('在场无储值押注≤1万持續', (P & ~df['has_paid'] & (df[bet] <= 10000) & (df[idn] == '持續')).sum())
# 离线 非1/新/回 构成
print('离线 回流', (off['is_back']).sum(), '新增', off['is_new'].sum())
# 持續在场 有储值 & 其它
print('持續有储值在场', ((df[idn] == '持續') & P & df['has_paid']).sum())
print('读法乙子集3677', (df['has_paid'] & (df[m['dep']] < 15000)).sum())
