# A49 自查补充：宽、窄口径未覆盖的差额由哪一类的圈法造成（只读，用 an_a45_members.load）
import pandas as pd
from an_a45_members import load

df, m = load()
pay = m['pay']
pr = df['present']
empty = pd.Series(False, index=df.index)

W = {'新增': df['is_new'], '回流': df['is_back'], '潜在付费': df['pp_wide'], '潜在流失': df['churn_ub']}
Nn = {'新增': df['is_new'], '回流': df['back_present'], '潜在付费': df['pp_verified'], '潜在流失': empty}
names = list(W)

cw = sum(W[n].astype(int) for n in names)
cn = sum(Nn[n].astype(int) for n in names)
gap = (cn == 0) & (cw > 0)  # 窄口径未覆盖、宽口径已覆盖
print('窄未覆盖', int((cn == 0).sum()), '宽未覆盖', int((cw == 0).sum()), '差额（窄未覆盖且宽覆盖）', int(gap.sum()))
print('宽未覆盖是否为窄未覆盖的子集', int(((cw == 0) & (cn != 0)).sum()), '（应为 0）')


def split(label, base):
    g = gap & base
    print(f'\n=== {label}：差额 {int(g.sum()):,} ===')
    for n in ['回流', '潜在付费', '潜在流失']:
        print(f'  宽口径下被「{n}」覆盖（可重叠）', int((g & W[n]).sum()))
    only = {n: int((g & W[n] & ~sum([W[k] for k in ['回流', '潜在付费', '潜在流失'] if k != n])).sum()) for n in ['回流', '潜在付费', '潜在流失']}
    print('  只被一类覆盖（独占）', only)
    print('  被不止一类覆盖', int((g & (sum(W[k].astype(int) for k in ['回流', '潜在付费', '潜在流失']) >= 2)).sum()))
    print('  差额里 有储值', int((g & (df[pay] > 0)).sum()), '无储值', int((g & (df[pay] <= 0)).sum()))


split('全体', pd.Series(True, index=df.index))
split('在场用户', pr)

# 只放宽潜在流失（其余窄）时的未覆盖，只放宽潜在付费，只放宽回流
for nm in ['回流', '潜在付费', '潜在流失']:
    S = dict(Nn)
    S[nm] = W[nm]
    c = sum(S[n].astype(int) for n in names)
    print(f'\n只把「{nm}」放宽到宽口径、其余取窄：未覆盖 全体 {int((c == 0).sum()):,}，在场 {int(((c == 0) & pr).sum()):,}')
