"""审查 20:44：独立复算 A23（Q76）、A22（Q69）、A21（Q68）的关键数字。只读。"""
import pandas as pd
import numpy as np

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
T0 = pd.Timestamp('2026-09-16')

act = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
lost = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
act = act[~act['身份'].isin(['機器人', '測試帳號'])].copy()
lost = lost[~lost['身份'].isin(['機器人', '測試帳號'])].copy()
lost = lost[~lost['会员编号'].isin(set(act['会员编号']))].copy()
act['is_left'] = False
lost['is_left'] = True
m = pd.concat([act, lost], ignore_index=True)
m['lastd'] = pd.to_datetime(m['最後登入時間']).dt.normalize()
m['regd'] = pd.to_datetime(m['注册时间'], errors='coerce').dt.normalize()
m['gap'] = (T0 - m['lastd']).dt.days
m['age'] = (T0 - m['regd']).dt.days
m['money'] = pd.to_numeric(m['总充值金额'], errors='coerce').fillna(0)
m['wager'] = pd.to_numeric(m['游戏总押注'], errors='coerce').fillna(0)
m['bonus'] = pd.to_numeric(m['充值赠点'], errors='coerce').fillna(0)
m['vipbl'] = m['身份'].isin(['VIP', '黑名單'])
m['R'] = m['money'].clip(lower=0) / np.maximum(m['age'] / 30.44, 1)
m.loc[m['regd'].isna(), 'R'] = np.nan
S_tot = m['money'].sum()
R_tot = m['R'].sum()
print('合并', len(m), 'S总额', round(S_tot), 'R总额', round(R_tot), 'R缺值', int(m['R'].isna().sum()))
print('VIP黑名单占 S %.2f%% R %.2f%%' % (m.loc[m.vipbl, 'money'].sum() / S_tot * 100, m.loc[m.vipbl, 'R'].sum() / R_tot * 100))

silent = m[m['is_left'] | (m['gap'] >= 8)]
d1 = silent[(silent['卡别'] >= 3) & (~silent['vipbl'])]
d2 = silent[(~silent['is_left']) & (silent['regd'] >= pd.Timestamp('2026-08-18')) & (silent['regd'] <= pd.Timestamp('2026-09-08')) & (silent['lastd'] == silent['regd'])]
d3 = silent[(~silent['is_left']) & (silent['身份'] == '回流')]
ids = set(d1['会员编号']) | set(d2['会员编号']) | set(d3['会员编号'])
only = silent[~silent['会员编号'].isin(ids)]
old = only[only['regd'] < pd.Timestamp('2026-08-01')]
young = only[only['regd'] >= pd.Timestamp('2026-08-01')]
refg = m[(~m['is_left']) & (m['gap'] <= 7) & (m['卡别'] == 1) & (~m['vipbl'])]
q50 = refg['wager'].quantile(0.5)
top = old[old['wager'] >= q50]
topp = top[top['卡别'] == 1]


def exp(g, nm):
    s, r = g['money'].sum(), g['R'].sum()
    s10 = g['money'].nlargest(10).sum()
    r10 = g['R'].nlargest(10).sum()
    print('%s n=%d S=%d (%.2f%%) R=%d (%.2f%%) 有储值率 %.2f%% 前10 S %.2f%% R %.2f%% 去前10 S %.2f%% R %.2f%%' % (
        nm, len(g), round(s), s / S_tot * 100, round(r), r / R_tot * 100, (g['money'] > 0).mean() * 100,
        s10 / s * 100, r10 / r * 100, (s - s10) / S_tot * 100, (r - r10) / R_tot * 100))
    return s, r


res = {}
for g, nm in [(d1, 'D1'), (d3, 'D3'), (only, 'D8独有'), (young, 'U1'), (old, 'U2'), (top, 'U2高段'), (topp, 'U2高段普卡')]:
    res[nm] = exp(g, nm)


def cells(g, nm):
    out = []
    for lab, mk in [('0-7', (~g.is_left) & (g.gap <= 7)), ('8-14', (~g.is_left) & (g.gap.between(8, 14))),
                    ('15-31', (~g.is_left) & (g.gap >= 15)), ('离开', g.is_left)]:
        x = g[mk]
        out.append('%s %d S%.2f%% R%.2f%%' % (lab, len(x), x.money.sum() / S_tot * 100, x.R.sum() / R_tot * 100))
    x = g[g.is_left]
    out.append('离开占暴露 S %.2f%% R %.2f%%' % (x.money.sum() / g.money.sum() * 100, x.R.sum() / g.R.sum() * 100))
    print(nm, ' | '.join(out))


for g, nm in [(d1, 'D1'), (d3, 'D3'), (only, 'D8独有')]:
    cells(g, nm)

# D2
coh = m[(~m['is_left']) & (m['regd'] >= pd.Timestamp('2026-08-18')) & (m['regd'] <= pd.Timestamp('2026-09-08'))]
one = coh[coh['lastd'] == coh['regd']]
more = coh[coh['lastd'] != coh['regd']]
for g, nm in [(more, '来过不止当天'), (one, '只来当天')]:
    p = g[g.money > 0]
    print(nm, len(g), '人均 %.1f' % g.money.mean(), '付费率 %.2f%%' % ((g.money > 0).mean() * 100),
          '付费者均值 %.1f 中位 %.0f' % (p.money.mean(), p.money.median()))
v_mean = more.money.mean() - one.money.mean()
pm, pn = more[more.money > 0], one[one.money > 0]
v_med = (more.money > 0).mean() * pm.money.median() - (one.money > 0).mean() * pn.money.median()
d2_1 = len(one) * 0.01 * v_mean
d2_1m = len(one) * 0.01 * v_med
print('D2 每人价值 均值差 %.1f 拆解差 %.1f；1%% 弹性 %.0f / %.0f；占S %.4f%% R %.4f%%' % (v_mean, v_med, d2_1, d2_1m, d2_1 / S_tot * 100, d2_1 / R_tot * 100))

# D4b
a = m[~m['is_left']]
d4b = a[(a.money <= 0) & (a.gap <= 7) & (~a.vipbl)]
ref = m[(m.age <= 30) & (m.money > 0)]
print('D4b', len(d4b), '参照新增付费者', len(ref), '均值 %.1f 中位 %.0f' % (ref.money.mean(), ref.money.median()))
d4_1 = len(d4b) * 0.01 * ref.money.mean()
d4_1m = len(d4b) * 0.01 * ref.money.median()
print('D4b 1%% 弹性 %.0f (S %.3f%% R %.3f%%) 中位 %.0f' % (d4_1, d4_1 / S_tot * 100, d4_1 / R_tot * 100, d4_1m))

# 新增队列占比
nc = m[m.regd >= pd.Timestamp('2026-08-18')]
print('新增队列(8/18起)', len(nc), 'S %.2f%% R %.2f%%' % (nc.money.sum() / S_tot * 100, nc.R.sum() / R_tot * 100))
# 偏向检查
pay = m[m.money > 0]
bins = [(0, 30), (31, 90), (91, 365), (366, 1095), (1096, 999999)]
for lo, hi in bins:
    x = pay[pay.age.between(lo, hi)]
    print('注册 %d-%d 天' % (lo, hi), len(x), 'R均 %.0f 中 %.0f S均 %.0f 中 %.0f' % (x.R.mean(), x.R.median(), x.money.mean(), x.money.median()))

# 比较
S1, R1 = res['D1']; S3, R3 = res['D3']; S8, R8 = res['D8独有']
print('D1/D3 S %.2f R %.2f' % (S1 / S3, R1 / R3))
print('D1/D8 S %.2f R %.2f' % (S1 / S8, R1 / R8))
print('D8/D3 S %.2f R %.2f' % (S8 / S3, R8 / R3))
print('D1/D2 S %.1f R %.2f' % (S1 * .01 / d2_1, R1 * .01 / d2_1))
print('D8/D2 S %.2f R %.2f' % (S8 * .01 / d2_1, R8 * .01 / d2_1))
print('D3/D2 S %.2f R %.2f' % (S3 * .01 / d2_1, R3 * .01 / d2_1))
print('D1/D4b S %.2f R %.2f' % (S1 * .01 / d4_1, R1 * .01 / d4_1))
print('D4b/D2 %.1f' % (d4_1 / d2_1))

# A22
am = a[~a.vipbl]
paid = am[am.money > 0]
g2 = paid[paid.bonus >= 15000]
print('A22 有储值主数', len(paid), '一定没买', int((paid.bonus < 15000).sum()), 'G2上界', len(g2), '0-7天', int((g2.gap <= 7).sum()))
for lab, mk in [('普卡', g2['卡别'] == 1), ('银卡', g2['卡别'] == 2), ('金卡以上', g2['卡别'] >= 3)]:
    print('  ', lab, int(mk.sum()), '占有储值总额 %.2f%%' % (g2.loc[mk, 'money'].sum() / paid.money.sum() * 100))
print('从未储值主数', int((am.money <= 0).sum()), '0-7', int(((am.money <= 0) & (am.gap <= 7)).sum()))
gold = paid[paid['卡别'] >= 3]
print('A21 金卡以上有储值主数', len(gold), '0-7', int((gold.gap <= 7).sum()), '普银有储值主数', int((paid['卡别'] <= 2).sum()))
# D4a 高卡上界 5,968 的 S/R
print('D4a 高卡上界 S %.2f%% R %.2f%%' % (g2.loc[g2['卡别'] >= 3, 'money'].sum() / S_tot * 100, g2.loc[g2['卡别'] >= 3, 'R'].sum() / R_tot * 100))
