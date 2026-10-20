"""审查 20:54：独立复算 A24（Q77）关键数字。只读。定义沿用 rv_2044_q76.py（审查者自写）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import math
import pandas as pd
import numpy as np

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')

act = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
lost = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
print('活跃列', list(act.columns))
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
m['bonus'] = pd.to_numeric(m['充值赠点'], errors='coerce').fillna(0)
m['vipbl'] = m['身份'].isin(['VIP', '黑名單'])
m['R'] = m['money'].clip(lower=0) / np.maximum(m['age'] / 30.44, 1)
m.loc[m['regd'].isna(), 'R'] = np.nan
lvcol = [c for c in m.columns if '等级' in c or '等級' in c]
print('等级列', lvcol)
S_tot, R_tot = m['money'].sum(), m['R'].sum()

silent = m[m['is_left'] | (m['gap'] >= 8)]
d1 = silent[(silent['卡别'] >= 3) & (~silent['vipbl'])]
d3 = silent[(~silent['is_left']) & (silent['身份'] == '回流')]
S1, R1 = d1.money.sum(), d1.R.sum()
S3, R3 = d3.money.sum(), d3.R.sum()
print('D1 S %.2f%% R %.2f%%；D3 S %.2f%% R %.2f%%' % (S1 / S_tot * 100, R1 / R_tot * 100, S3 / S_tot * 100, R3 / R_tot * 100))

a = m[(~m.is_left)]
pres = a[(a.gap <= 7) & (~a.vipbl)]


def show(g, nm):
    s, r = g.money.sum(), g.R.sum()
    print('%s n=%d S %.2f%% R %.2f%% | 与D1持平 S %.1f%% R %.1f%% | 与D3 S %.1f%% R %.1f%% | 每1%%是D1每1%%的 S %.2f 倍 R %.2f 倍' % (
        nm, len(g), s / S_tot * 100, r / R_tot * 100, S1 / s * 100, R1 / r * 100, S3 / s * 100, R3 / r * 100, s / S1, r / R1))


o1 = pres[pres.money > 0]
show(o1, 'O1')
for lab, mk in [('普卡', o1['卡别'] == 1), ('银卡', o1['卡别'] == 2), ('金卡以上', o1['卡别'] >= 3)]:
    show(o1[mk], 'O1 ' + lab)
k = math.ceil(len(o1) * 0.01)
top = o1.nlargest(k, 'R')
rest = o1.drop(top.index)
show(top, 'O1 前1%% (%d)' % k)
show(rest, 'O1 其余')
print('前1% 卡别>=3', int((top['卡别'] >= 3).sum()))
g2 = a[(~a.vipbl) & (a.money > 0) & (a.bonus >= 15000) & (a['卡别'] >= 3)]
print('D4a高卡上界', len(g2), '与 O1 金卡以上重叠', len(set(g2['会员编号']) & set(o1.loc[o1['卡别'] >= 3, '会员编号'])))
# 普卡 / 银卡翻倍是否及 D1
for lab, mk in [('普卡', o1['卡别'] == 1), ('银卡', o1['卡别'] == 2)]:
    x = o1[mk]
    print(lab, '翻倍后 S 占 D1 %.1f%% R %.1f%%' % (x.money.sum() / S1 * 100, x.R.sum() / R1 * 100))

# O4
ids = a[(a.gap <= 7)]
o4 = ids[ids['身份'] == '回流']
cont = ids[ids['身份'] == '持續']
show(o4, 'O4')
print('O4 付费率 %.2f%% 持續 %.2f%%' % ((o4.money > 0).mean() * 100, (cont.money > 0).mean() * 100))
print('O4 卡别分布', o4['卡别'].value_counts().sort_index().to_dict())
bins = [-1, 29, 90, 365, 1095, 1e7]
labs = ['<30', '30-90', '91-365', '1-3y', '3y+']
for df in (o4, cont):
    df['tb'] = pd.cut(df['age'], bins, labels=labs).astype(str)
    df['cg'] = np.where(df['卡别'] == 1, '普', np.where(df['卡别'] == 2, '银', '金+'))
for c in ['普', '银', '金+']:
    for t in labs:
        r_, q_ = o4[(o4.cg == c) & (o4.tb == t)], cont[(cont.cg == c) & (cont.tb == t)]
        if len(r_) == 0 and len(q_) == 0:
            continue
        print('  %s %s 回流 %d %.2f%% 持續 %d %.2f%% 差 %+.2f' % (c, t, len(r_), (r_.money > 0).mean() * 100 if len(r_) else np.nan,
                                                         len(q_), (q_.money > 0).mean() * 100 if len(q_) else np.nan,
                                                         ((q_.money > 0).mean() - (r_.money > 0).mean()) * 100 if len(r_) and len(q_) else np.nan))

# O2
o2 = pres[(pres.money > 0) & (pres.money <= 100)]
show(o2, 'O2')
print('O2 中位', o2.money.median())

# O3
T = {2: 1000, 3: 3000, 4: 8000, 5: 20000, 6: 50000, 7: 100000}
LV = {5: 750, 6: 5000, 7: 10000}
tot = past = 0
up = []
for c in range(1, 7):
    x = pres[pres['卡别'] == c]
    cond = x.money >= 0.8 * T[c + 1]
    if c + 1 in LV and lvcol:
        cond &= pd.to_numeric(x[lvcol[0]], errors='coerce').fillna(0) >= LV[c + 1]
    y = x[cond]
    p = y[y.money >= T[c + 1]]
    tot += len(y); past += len(p); up.append(y)
    print('  O3 %d→%d 上界 %d 已过 %d' % (c, c + 1, len(y), len(p)))
print('O3 合计', tot, past)
show(pd.concat(up), 'O3 上界人群')
