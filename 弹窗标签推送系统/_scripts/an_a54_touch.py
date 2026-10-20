# A54 人群触达现状：五类人群按现有配置，进大厅 / 破产时最多弹几个、命中哪些规则的人数
# 读 an_a45_members.load() 的口径（分母 62,292，剔除機器人、測試帳號）；不带参数运行
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from an_a45_members import load

df, m = load()
card, idn, pay, bet = m['card'], m['idn'], m['pay'], m['bet']
N = len(df)
vip_bl = df[idn].isin(['VIP', 'VIP玩家', '黑名單'])
df['pb'] = df[card].isin([1, 2])          # 普卡、银卡：无月月抽权益，且 ID10/11 只覆盖这两档
df['gold'] = df[card] >= 3                # 金卡以上

groups = {
    '新增': df['is_new'],
    '回流（存量）': df['is_back'],
    '回流（在场）': df['back_present'],
    '潜在付费（读法甲，上界）': df['pp_wide'],
    '潜在付费（可核实）': df['pp_verified'],
    '潜在流失（替代：有储值且在场）': df['churn_alt_a'],
    '潜在流失（上界：有储值）': df['churn_ub'],
    '全体': pd.Series(True, index=df.index),
}

print('分母 N =', N)
print('卡别分布（1 普卡 2 银卡 3+ 金卡以上）', df[card].value_counts().sort_index().to_dict())
rows = []
for name, mask in groups.items():
    g = df[mask]
    n = len(g)
    pb = int(g['pb'].sum())
    gold = int(g['gold'].sum())
    never = int(g['never_paid'].sum())
    rows.append((name, n, pb, gold, never))
    print(f'{name}: 人数 {n:,}  普卡银卡 {pb:,}（{pb/n*100:.2f}%）  金卡以上 {gold:,}（{gold/n*100:.2f}%）  从未储值 {never:,}（{never/n*100:.2f}%）')

print('\n=== ID10/11 命中上界（卡别 × 有储值；当月储值低于上月 50% 本地算不出）===')
has = df['has_paid']
for label, mk in [('全部', pd.Series(True, index=df.index)), ('剔除 VIP、黑名單', ~vip_bl)]:
    a = int((has & df['pb'] & mk).sum())
    b = int((has & df['pb'] & df['present'] & mk).sum())
    c = int((has & df['gold'] & mk).sum())
    d = int((has & df['gold'] & df['present'] & mk).sum())
    print(f'{label}: 普银有储值 {a:,}（在场 {b:,}）  金卡以上有储值 {c:,}（在场 {d:,}）')

print('\n=== 首储礼包排第 1 位（ID6、ID7）的确定对象：从未储值 ===')
nv = df['never_paid']
print('从未储值', int(nv.sum()), f'占全体 {nv.mean()*100:.2f}%')
for name, mask in [('新增', df['is_new']), ('回流存量', df['is_back']), ('潜在付费上界', df['pp_wide'])]:
    k = int((mask & nv).sum())
    print(f'  {name} 中从未储值 {k:,}（{k/int(mask.sum())*100:.2f}%）')

print('\n=== 破产位暴露 ===')
print('在场全体', int(df['present'].sum()), '在场且累计押注>0', int((df['present'] & (df[bet] > 0)).sum()))
