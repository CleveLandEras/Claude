# A57 缺口规模：阶段 3 判为不可实现的 10 个场景的"暴露面"（三层）、去重合并、缺口 × 五类
# 口径复用 an_a45_members.load()（近一月活跃，剔除機器人、測試帳號后 62,292）+ 八月流失名单中不在前者的 12,188 = 合并 74,480
# 只读；不输出会员编号；不带参数运行
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from an_a45_members import load, _read

act, m = load()
pay, bet, card, idn = m['pay'], m['bet'], m['card'], m['idn']
dfa, ma = _read('八月登录流失名单_20260916.csv')
only = dfa[~dfa[ma['id']].isin(set(act[m['id']]))].copy()
LIST_N = len(dfa)

# ---- 合并表：只保留算数需要的列 ----
def slim(d, mm, in_active):
    o = pd.DataFrame({
        'dsl': d['dsl'].values, 'pay': d[mm['pay']].values, 'bet': d[mm['bet']].values,
        'card': d[mm['card']].values, 'in_active': in_active,
    })
    return o
a = slim(act, m, True)
o = slim(only, ma, False)
df = pd.concat([a, o], ignore_index=True)
nA, nO = len(a), len(o)
N = len(df)
# 五类与派生口径只对近一月活跃内定义（与 A45、A48 一致），名单独有者不属于任何一类
def pad(series):
    return pd.concat([pd.Series(series.values), pd.Series([False] * nO)], ignore_index=True)
df['is_new'] = pad(act['is_new'])
df['is_back'] = pad(act['is_back'])
df['pp_wide'] = pad(act['pp_wide'])
df['churn_ub'] = pad(act['churn_ub'])
df['churn_alt_a'] = pad(act['churn_alt_a'])
df['present'] = df['dsl'] <= 7
df['off8'] = df['dsl'] >= 8
df['off15'] = df['dsl'] >= 15
df['has_paid'] = df['pay'] > 0
df['pb'] = df['card'].isin([1, 2])
df['decline_ub'] = df['in_active'] & df['pb'] & df['has_paid']       # 储值下滑规则命中上界（A54）
df['ltd_ub'] = df['bet'] >= 10000                                     # 限时加码资格上界（累计押注 ≥ 10,000，本地算不出其余条件）
# 召回名单：八月流失名单全部行（剔除后）= 独有 12,188 + 与活跃重叠部分
list_ids = set(dfa[ma['id']])
df['recall'] = pd.concat([act[m['id']].isin(list_ids).reset_index(drop=True), pd.Series([True] * nO)], ignore_index=True)
ALL = pd.Series(True, index=df.index)

PAY_ALL = df['pay'].sum()
PAY_ACT = df.loc[df['in_active'], 'pay'].sum()

print('=== 一 原子人群与恒等式 ===')
print('活跃', nA, '名单独有', nO, '合并', N, '名单剔除后总行', LIST_N, '其中与活跃重叠', int(df.loc[df["in_active"], "recall"].sum()))
print('在场', int(df['present'].sum()), '离线≥8', int(df['off8'].sum()), '离线≥15', int(df['off15'].sum()))
print('在场+离线 =', int(df['present'].sum() + df['off8'].sum()), '（应等于合并）')
print('累计储值 活跃', int(PAY_ACT), '合并', int(PAY_ALL), '名单独有', int(PAY_ALL - PAY_ACT))
for k in ['is_new', 'is_back', 'pp_wide', 'churn_ub', 'churn_alt_a', 'decline_ub', 'ltd_ub', 'recall']:
    s = df[k]
    print(f'{k}: {int(s.sum()):,}  在场 {int((s & df.present).sum()):,}  离线≥8 {int((s & df.off8).sum()):,}')
print('decline_ub 在场', int((df.decline_ub & df.present).sum()), '（A54: 12,201 / 8,104）')
print('ltd_ub ∩ 在场', int((df.ltd_ub & df.present).sum()), ' ltd_ub ∩ 活跃', int((df.ltd_ub & df.in_active).sum()))
print('new ∩ 在场', int((df.is_new & df.present).sum()))
print('recall 与 off8 交集', int((df.recall & df.off8).sum()), ' recall 与 在场 交集', int((df.recall & df.present).sum()))

# ---- 逐场景三层 ----
PUSH_UP = ALL                                   # 推送可达上端 = 合并全体（A48 区间上端含义；在场走快显等）
S = {}
# 场景: (状态, L1, L2 or None, 备注)
S[7]  = ('推断', df.present, df.decline_ub & df.present)
S[16] = ('推断', df.present, df.decline_ub & df.present)
S[19] = ('推断', df.present, df.present & df.ltd_ub)
S[13] = ('推断', PUSH_UP, df.present & df.ltd_ub)
S[22] = ('推断', PUSH_UP, None)
S[23] = ('推断', df.present, df.present & df.ltd_ub)
S[17] = ('出处明写', df.is_new, df.is_new & df.present)
S[14] = ('推断', PUSH_UP, df.present & df.ltd_ub)
S[25] = ('推断', df.off8, df.recall)
S[11] = ('出处明写', None, None)   # 不单独计人数

def stat(mask):
    n = int(mask.sum())
    p = df.loc[mask, 'pay'].sum()
    return n, n / N * 100, n / nA * 100 if False else n / nA * 100, int(p), p / PAY_ALL * 100
def row(name, mask):
    n = int(mask.sum()); p = df.loc[mask, 'pay'].sum()
    inA = int((mask & df.in_active).sum()); pA = df.loc[mask & df.in_active, 'pay'].sum()
    print(f'{name}｜人数 {n:,}｜占合并 {n/N*100:.2f}%｜占活跃 {inA/nA*100:.2f}%（活跃内 {inA:,}）｜累计储值 {int(p):,}｜占合并储值 {p/PAY_ALL*100:.2f}%｜活跃内储值占活跃 {pA/PAY_ACT*100:.2f}%')

print('\n=== 二 逐场景暴露面 ===')
for k in [7, 16, 19, 13, 22, 23, 17, 14, 25]:
    st, l1, l2 = S[k]
    print(f'--- 场景 {k}（{st}）')
    row('  第一层', l1)
    if l2 is None:
        print('  第二层 不可知')
    else:
        row('  第二层', l2)
print('--- 场景 11：不单独计人数；规模取 13、22、23、25 的第一层并集')
u11 = S[13][1] | S[22][1] | S[23][1] | S[25][1]
row('  11 的并集', u11)

print('\n=== 三 去重合并 ===')
stated_only_17 = S[17][1]
row('(a1) 仅出处明写：17（11 无独立规模）', stated_only_17)
row('(a2) 仅出处明写：17 ∪ 11（11 取 13/22/23/25 第一层并集）', stated_only_17 | u11)
L1u = ALL.copy() & False
for k in [7, 16, 19, 13, 22, 23, 17, 14, 25]:
    L1u = L1u | S[k][1]
row('(b) 含推断：第一层并集', L1u)
print('   第一层并集与合并全体之差', N - int(L1u.sum()), '；撑满的场景（第一层=合并全体）：13、22、14')
L1u_no_push = ALL.copy() & False
for k in [7, 16, 19, 23, 17, 25]:
    L1u_no_push = L1u_no_push | S[k][1]
row('(b\') 第一层并集（不含推送可达上端的 13、22、14）', L1u_no_push)
L2u = ALL.copy() & False
for k in [7, 16, 19, 13, 23, 17, 14, 25]:
    L2u = L2u | S[k][2]
row('(c) 含推断：第二层并集（22 不可知，未计）', L2u)
# 第二层并集的构成：去掉 25 召回名单后
L2u_no_recall = ALL.copy() & False
for k in [7, 16, 19, 13, 23, 17, 14]:
    L2u_no_recall = L2u_no_recall | S[k][2]
row('(c\') 第二层并集（不含 25 的召回名单）', L2u_no_recall)
print('出处明写 17 的第二层', int(S[17][2].sum()))

print('\n=== 缺口 × 五类（分母＝各类自身人数；同人属多类不去重；五类只在活跃内定义）===')
cls = {'新增': df.is_new, '回流存量': df.is_back, '潜在付费(宽)': df.pp_wide, '潜在流失(上界:有储值)': df.churn_ub}
print('类大小', {k: int(v.sum()) for k, v in cls.items()})
sets = {
    '17 第一层': S[17][1], '7/16 第一层(在场)': S[7][1], '7/16 第二层(下滑上界∩在场)': S[7][2],
    '19/23 第二层(限时加码资格上界∩在场)': S[19][2], '13/22/14 第一层(推送上端)': S[13][1],
    '25 第一层(离线≥8)': S[25][1], '25 第二层(召回名单)': S[25][2],
    '(b) 第一层并集': L1u, '(c) 第二层并集': L2u,
}
for nm, mk in sets.items():
    cells = []
    for cn, cm in cls.items():
        k = int((mk & cm).sum()); cells.append(f'{cn} {k:,}（{k/int(cm.sum())*100:.2f}%）')
    print(nm, '｜', '｜'.join(cells))
print('破产：暴露上界 = 在场全体', int(df.present.sum()), '（是触发时刻，不进矩阵）')

print('\n=== 反例检查 ===')
print('(i) 并集 ≤ 合并：', int(L1u.sum()) <= N, ' 第二层并集 ≤ 在场∪召回∪新增...：', int(L2u.sum()))
print('(ii) 新增', int(df.is_new.sum()), '（A51: 10,749）')
print('(iii) 储值分母同为累计口径：活跃', int(PAY_ACT), ' 合并', int(PAY_ALL))
# (v) 暴露面大但机制上不太可能影响的例子：S19 第一层（在场）里没有任何已知推送用例对象的人
no_push_case = df.present & ~df.ltd_ub
print('(v) 场景 19：在场但不属于限时加码资格上界者（已知推送用例之外）', int(no_push_case.sum()), f'占在场 {no_push_case.sum()/df.present.sum()*100:.2f}%')
# 第二层的比例
print('第二层并集占合并', f'{L2u.sum()/N*100:.2f}%', ' 在场内的第二层并集', int((L2u & df.present).sum()))
