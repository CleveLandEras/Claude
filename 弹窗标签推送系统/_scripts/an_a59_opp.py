# A59 机会：基线卡、结构天花板、本地基准差、敏感度。只给人数与累计单位，不给预测，不给月度金额，不给客单价
# 口径复用 an_a45_members.load()（近一月活跃，剔除機器人、測試帳號后 62,292）+ 八月流失名单独有 12,188 = 合并 74,480
# 只读；不输出会员编号；不带参数运行
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from an_a45_members import load, _read

act, m = load()
pay, bet, card = m['pay'], m['bet'], m['card']
dfa, ma = _read('八月登录流失名单_20260916.csv')
only = dfa[~dfa[ma['id']].isin(set(act[m['id']]))].copy()

A = pd.DataFrame({'dsl': act['dsl'].values, 'pay': act[pay].values, 'bet': act[bet].values, 'card': act[card].values,
                  'new': act['is_new'].values, 'back': act['is_back'].values, 'pp': act['pp_wide'].values,
                  'in_active': True})
O = pd.DataFrame({'dsl': only['dsl'].values, 'pay': only[ma['pay']].values, 'bet': only[ma['bet']].values,
                  'card': only[ma['card']].values, 'new': False, 'back': False, 'pp': False, 'in_active': False})
df = pd.concat([A, O], ignore_index=True)
df['present'] = df['dsl'] <= 7
df['off8'] = df['dsl'] >= 8
df['off15'] = df['dsl'] >= 15
df['paid'] = df['pay'] > 0
df['cb'] = df['card'].map(lambda c: '普卡' if c == 1 else ('银卡' if c == 2 else '金卡以上'))
act_df = df[df['in_active']].copy()
NA, NM = len(act_df), len(df)
print('活跃', NA, '合并', NM, '在场', int(df.present.sum()), '离线≥8', int(df.off8.sum()), '离线≥15', int(df.off15.sum()))

def base(name, g):
    n = len(g); pr = int(g.present.sum()); pd_ = int(g.paid.sum()); s = g.loc[g.paid, 'pay'].sum()
    avg = s / pd_ if pd_ else float('nan')
    print(f'{name}｜人数 {n:,}｜在场 {pr:,}（{pr/n*100:.2f}%）｜有储值 {pd_:,}（{pd_/n*100:.2f}%）｜有储值者累计储值合计 {int(s):,}｜人均 {avg:,.0f}')
    return n, pr / n, pd_ / n, avg

print('\n=== 一 基线卡 ===')
G = {}
G['全体(活跃)'] = act_df
G['新增'] = act_df[act_df.new]
G['回流存量'] = act_df[act_df.back]
G['潜在付费(宽)'] = act_df[act_df.pp]
G['潜在流失(上界:有储值)'] = act_df[act_df.paid]
G['潜在流失(替代:有储值且在场)'] = act_df[act_df.paid & act_df.present]
G['破产暴露上界(在场全体)'] = act_df[act_df.present]
G['离线≥8(合并)'] = df[df.off8]
G['全体(合并)'] = df
B = {}
for k, g in G.items():
    B[k] = base(k, g)

print('\n=== 二 结构天花板（人数；理论上限，非估计）===')
nv = df['pay'] <= 0
print('活跃：离线≥8', int(df.off8.sum()), ' 离线≥15', int(df.off15.sum()), ' 召回名单 28,894（见 A57）')
for k in ['新增', '回流存量', '潜在付费(宽)']:
    g = G[k]
    print(f'付费率：{k} 中无储值者', int((g.pay <= 0).sum()), '（其中在场', int(((g.pay <= 0) & g.present).sum()), '）')
print('付费率：活跃全体无储值者', int((act_df.pay <= 0).sum()), ' 合并全体无储值者', int(nv.sum()))
print('付费率：在场无储值者', int((df.present & nv).sum()), ' 离线≥8无储值者', int((df.off8 & nv).sum()))

print('\n=== 三 本地基准差 ===')
tot = act_df
w = tot['cb'].value_counts(normalize=True).to_dict()
print('全体 卡别权重', {k: round(v, 4) for k, v in w.items()})
rate_all = tot.paid.mean(); pres_all = tot.present.mean()
print(f'全体 有储值率 {rate_all*100:.2f}%  在场率 {pres_all*100:.2f}%')
avg_all_paid = tot.loc[tot.paid, 'pay'].mean()
print('全体有储值者人均累计储值', int(avg_all_paid))
def std_rate(g, col):
    s = 0.0
    for c, wt in w.items():
        gg = g[g.cb == c]
        s += wt * (gg[col].mean() if len(gg) else 0.0)
    return s
for name in ['新增', '回流存量']:
    g = G[name]; n = len(g)
    for col, label, ref in [('paid', '付费率', rate_all), ('present', '在场率', pres_all)]:
        raw = g[col].mean()
        st = std_rate(g, col)
        d_raw = (ref - raw); d_std = (ref - st)
        print(f'{name} {label}：本类 {raw*100:.2f}%｜全体 {ref*100:.2f}%｜未标准化差(全体-本类) {d_raw*100:.2f} pp｜卡别标准化后本类 {st*100:.2f}%，差 {d_std*100:.2f} pp｜折人数 未标准化 {d_raw*n:,.0f} 标准化 {d_std*n:,.0f}')
        if col == 'paid':
            avg = g.loc[g.paid, 'pay'].mean() if g.paid.any() else avg_all_paid
            print(f'    折累计单位（人均累计储值取本类有储值者 {avg:,.0f}，非月度、非客单价）：未标准化 {d_raw*n*avg:,.0f}  标准化 {d_std*n*avg:,.0f}')
    # 卡别构成
    print('   卡别构成', g.cb.value_counts(normalize=True).round(4).to_dict())
print('说明：卡别由累计储值或累计押注决定，标准化会吸收一部分真实差异（偏小）；未标准化含新账号尚无时间储值等选择效应（偏大）。')

print('\n=== 四 敏感度（1/0.5/2/5 个百分点对应人数；单位换算）===')
rows = [('新增', G['新增']), ('回流存量', G['回流存量']), ('潜在付费(宽)', G['潜在付费(宽)']),
        ('潜在流失(上界:有储值)', G['潜在流失(上界:有储值)']), ('破产暴露上界(在场)', G['破产暴露上界(在场全体)'])]
for name, g in rows:
    n = len(g)
    avg = g.loc[g.paid, 'pay'].mean() if g.paid.any() else avg_all_paid
    src = '本类有储值者' if g.paid.any() else '全体有储值者(替代)'
    cells = []
    for pp in [0.5, 1, 2, 5]:
        k = n * pp / 100
        cells.append(f'{pp}pp={k:,.0f}人')
    print(f'{name} n={n:,}｜' + '｜'.join(cells) + f'｜付费率每1pp折累计单位 {n*0.01*avg:,.0f}（人均 {avg:,.0f}，取{src}）')
# 在场率敏感度只给人数：离线≥8 / 全体合并
for name, n in [('离线≥8', int(df.off8.sum())), ('合并全体', NM)]:
    print(f'在场率 {name} n={n:,}｜' + '｜'.join(f'{pp}pp={n*pp/100:,.0f}人' for pp in [0.5, 1, 2, 5]))

print('\n=== 五 自查 ===')
print('(iv) 抽查：新增有储值', int(G['新增'].paid.sum()), '（A51: 10,749-9,648=1,101）｜回流存量有储值', int(G['回流存量'].paid.sum()), '（16,564-14,027=2,537）｜离线≥8 有储值', int(df[df.off8].paid.sum()), '（A48: 6,688）')
print('全体活跃有储值率', f'{rate_all*100:.2f}%', '（卡: 29.32%）')
print('离线≥8 累计储值', int(df.loc[df.off8, 'pay'].sum()), '（A48: 28,342,430）')
