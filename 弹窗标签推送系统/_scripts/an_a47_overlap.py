# A47 人群重叠与未覆盖：读 an_a45_members.load()，宽/窄/在场三套口径
import itertools
import numpy as np
import pandas as pd
from an_a45_members import load

df, m = load()
pay, bet, idn, card, dep = m['pay'], m['bet'], m['idn'], m['card'], m['dep']
N = len(df)
TOT = df[pay].sum()
df['tier'] = np.where(df[card] == 1, '普卡', np.where(df[card] == 2, '银卡', '金卡以上'))
pr = df['present']
empty = pd.Series(False, index=df.index)

SETS = {
    '宽': {'新增': df['is_new'], '回流': df['is_back'], '潜在付费': df['pp_wide'], '潜在流失': df['churn_ub']},
    '窄': {'新增': df['is_new'], '回流': df['back_present'], '潜在付费': df['pp_verified'], '潜在流失': empty},
    '在场': {'新增': df['is_new'] & pr, '回流': df['back_present'], '潜在付费': df['pp_wide'] & pr, '潜在流失': df['churn_alt_a']},
}
names = ['新增', '回流', '潜在付费', '潜在流失']

for sc, S in SETS.items():
    print(f'\n######## {sc}口径 ########')
    print('各类规模', {k: int(v.sum()) for k, v in S.items()})
    print('--- 两两交集（人数｜占 62,292｜占行类｜占列类｜交集储值占总储值）---')
    for a, b in itertools.combinations(names, 2):
        x = S[a] & S[b]
        k = int(x.sum())
        sa, sb = int(S[a].sum()), int(S[b].sum())
        ps = df[x][pay].sum()
        print(f'{a}∩{b}: {k:,}  {k / N * 100:.2f}%  占{a} {k / sa * 100 if sa else 0:.2f}%  占{b} {k / sb * 100 if sb else 0:.2f}%  交集储值 {int(ps):,}（占总 {ps / TOT * 100:.2f}%）  卡别 {df[x]["tier"].value_counts().to_dict()}')
    cnt = sum(S[n].astype(int) for n in names)
    print('命中类数分布', {int(i): int((cnt == i).sum()) for i in range(0, 5)})
    # 覆盖核对
    un = cnt == 0
    uni = cnt > 0
    print(f'并集 {int(uni.sum()):,} + 未覆盖 {int(un.sum()):,} = {int(uni.sum() + un.sum()):,}  (N={N:,})')
    # 被压损失
    print('--- 互斥+优先级：若 A 优先，被压住的 B 人数｜占 B｜占 B 储值 ---')
    for a, b in itertools.permutations(names, 2):
        x = S[a] & S[b]
        sb = S[b]
        if x.sum() == 0:
            continue
        pb = df[sb][pay].sum()
        pxb = df[x][pay].sum()
        print(f'  {a}优先 → 被压的{b}: {int(x.sum()):,}｜占{b} {x.sum() / sb.sum() * 100:.2f}%｜占{b}储值 {pxb / pb * 100 if pb else 0:.2f}%')
    # 未覆盖拆解
    u = df[un]
    print(f'--- 未覆盖拆解（n={len(u):,}，占 {len(u) / N * 100:.2f}%，占累计储值 {u[pay].sum() / TOT * 100:.2f}%）---')
    print('身份', u[idn].value_counts().to_dict())
    print('卡别', u['tier'].value_counts().to_dict())
    print('有储值', int((u[pay] > 0).sum()), '在场', int(u['present'].sum()), '押注>10,000', int((u[bet] > 10000).sum()))
    print('有储值且在场', int(((u[pay] > 0) & u['present']).sum()), '其中金卡以上', int(((u[pay] > 0) & u['present'] & (u['tier'] == '金卡以上')).sum()))
    print('无储值且押注≤10,000', int(((u[pay] <= 0) & (u[bet] <= 10000)).sum()), '其中在场', int(((u[pay] <= 0) & (u[bet] <= 10000) & u['present']).sum()))
    print('有储值且不在场', int(((u[pay] > 0) & ~u['present']).sum()))
    # 分组表：身份×(有储值 / 在场)
    g = u.assign(有储值=u[pay] > 0, 在场=u['present']).groupby([idn, '有储值', '在场']).agg(人数=(pay, 'size'), 储值=(pay, 'sum'))
    g['占储值%'] = (g['储值'] / TOT * 100).round(2)
    print(g.to_string())
    print('金卡以上 未覆盖', int((u['tier'] == '金卡以上').sum()), '储值占', round(u[u['tier'] == '金卡以上'][pay].sum() / TOT * 100, 2))

print('\n######## 读法乙 ########')
sure = df['has_paid'] & (df[dep] < 15000)
print('确定付过费且没买首储（充值赠点<15,000）', int(sure.sum()), '身份', df[sure][idn].value_counts().to_dict(), '卡别', df[sure]['tier'].value_counts().to_dict())
print('其与宽口径潜在流失的交集', int((sure & df['churn_ub']).sum()), '与在场口径潜在流失', int((sure & df['churn_alt_a']).sum()), '与新增', int((sure & df['is_new']).sum()), '与回流', int((sure & df['is_back']).sum()))
print('乙上界（有储值 18,265）与新增', int((df['has_paid'] & df['is_new']).sum()), '与回流', int((df['has_paid'] & df['is_back']).sum()))
print('读法甲 ∩ 有储值', int((df['pp_wide'] & df['has_paid']).sum()))

print('\n######## 破产暴露范围在五类中的分布（宽口径）########')
bk = df['bk_ub_bet']
S = SETS['宽']
print('破产暴露（在场且押注>0）', int(bk.sum()))
for k in names:
    x = bk & S[k]
    print(f'  ∩{k}: {int(x.sum()):,}  占暴露 {x.sum() / bk.sum() * 100:.2f}%')
cnt = sum(S[n].astype(int) for n in names)
print('  不属于任何类', int((bk & (cnt == 0)).sum()))

print('\n######## 身份基础表 ########')
print(df.groupby(idn).agg(人数=(pay, 'size'), 储值=(pay, 'sum')).assign(占储值=lambda t: (t['储值'] / TOT * 100).round(2)))
