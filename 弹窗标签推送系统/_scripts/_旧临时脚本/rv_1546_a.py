import sys
sys.path.insert(0, '/Users/decheng.huang/claude/弹窗标签推送系统/_scripts')
import pandas as pd
from an_a45_members import load

df, m = load()
P = df['present']
new, back, bp = df['is_new'], df['is_back'], df['back_present']
pp, ppv, ch = df['pp_wide'], df['pp_verified'], df['churn_ub']
wide = new | back | pp | ch
nar = new | bp | ppv
print('N', len(df), '宽未覆盖', (~wide).sum(), '窄未覆盖', (~nar).sum(), '差', (~nar).sum() - (~wide).sum())
gap = ~nar & wide
print('gap', gap.sum(), 'gap∩在场', (gap & P).sum())
for n, s in [('付', pp), ('流', ch), ('回', back)]:
    print(n, '全体', (gap & s).sum(), '在场', (gap & P & s).sum())
g = gap & P
print('在场差额 流 %.4f 付 %.4f' % ((g & ch).sum() / g.sum(), (g & pp & ~ch).sum() / g.sum()))
print('在场差额 同时 付&流', (g & pp & ch).sum(), '回', (g & back).sum())
# 单类放宽
for nm, extra in [('流', ch), ('付', pp), ('回', back)]:
    c = new | (bp if nm != '回' else back) | (ppv if nm != '付' else pp) | (ch if nm == '流' else False)
    print('放宽', nm, '全体未覆盖', (~c).sum(), '在场', (~c & P).sum())
# 重叠
cw = new.astype(int) + back.astype(int) + pp.astype(int) + ch.astype(int)
print('宽 命中2', (cw == 2).sum(), (cw == 2).mean())
cnn = new.astype(int) + bp.astype(int) + ppv.astype(int)
print('窄 命中2', (cnn == 2).sum(), (cnn == 2).mean())
cp = (new & P).astype(int) + (back & P).astype(int) + (pp & P).astype(int) + (ch & P).astype(int)
print('在场 命中2', (cp == 2).sum(), (cp == 2).sum() / len(df), (cp == 2).sum() / P.sum())
# 新增押注0
nw = df[new]
b0 = nw[nw[m['bet']] <= 0]
print('新增押注0', len(b0), 'gift1000', (b0[m['gift']] == 1000).sum() if 'gift' in m else 'nogift')
print('b0 age>=7', (b0['age'] >= 7).sum(), (b0['age'] >= 7).mean())
# 8-14天档 星期分布
x = df[(df['dsl'] >= 8) & (df['dsl'] <= 14)]
print('8-14', len(x), x['ld'].dt.dayofweek.value_counts().sort_index().to_dict())
print('逐日', x['dsl'].value_counts().sort_index().to_dict())
print('≥8', (df['dsl'] >= 8).sum(), '≥15', (df['dsl'] >= 15).sum())
