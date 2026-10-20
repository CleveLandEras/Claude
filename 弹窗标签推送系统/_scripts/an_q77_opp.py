"""Q77：机会扫描（A24）。照设计卡 Q77。只读，不带参数。单位、分母、函数复用 an_q76_perf.py。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import math
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, _ROOT + '/_scripts')
from an_q76_perf import load, expose  # noqa: E402

g, U = load()
TS, TR = U['S'].sum(), U['R'].sum()
a = g['a'].copy()
a['S'] = a['dep']
m = (a['tenure'] / 30.44).clip(lower=1)
a['R'] = (a['dep'].clip(lower=0) / m).where(a['tenure'].notna())
a['cg'] = np.where(a['卡别'] == 1, '普卡', np.where(a['卡别'] == 2, '银卡', '金卡以上'))
a['r07'] = a['days'] <= 7
a['g0'] = pd.to_numeric(a['充值赠点'], errors='coerce').fillna(0).round(0)
a['a0'] = a['dep'].round(2)

# 问题暴露（A23，合并口径）
PROB = {}
for k, ids in {'D1': set(g['D1']['会员编号']), 'D3': set(g['D3']['会员编号']), 'D8 独有': set(g['UQ']['会员编号'])}.items():
    e = expose(U, ids, TS, TR)
    PROB[k] = (e['S'], e['R'])
print('问题暴露', {k: (round(v[0]), round(v[1])) for k, v in PROB.items()})


def base(ids, name):
    e = expose(U, ids, TS, TR)
    print(f'  {name}: n={e["n"]:,}｜S {e["S"]:,.0f}（{e["S%"]:.2f}%）｜R {e["R"]:,.0f}（{e["R%"]:.2f}%）｜前10 占 S {e["前10占S"]:.2f}% R {e["前10占R"]:.2f}%'
          f'｜去前10 S {e["去前10 S%"]:.2f}% R {e["去前10 R%"]:.2f}%')
    be = '；'.join(f'{k}: S {PROB[k][0] / e["S"] * 100:.1f}% R {PROB[k][1] / e["R"] * 100:.1f}%' for k in PROB)
    print(f'     持平（问题暴露 ÷ 底盘）：{be}')
    return e


print('\n===== O1 在场付费者（0–7 天、有储值、剔除 VIP、黑名单）')
o1 = a[a.r07 & (a.dep > 0) & a['nov']]
base(set(o1['会员编号']), 'O1 全部')
for c in ['普卡', '银卡', '金卡以上']:
    base(set(o1.loc[o1.cg == c, '会员编号']), f'O1 {c}')
k = math.ceil(len(o1) * 0.01)
top = o1.nlargest(k, 'R')
rest = o1[~o1['会员编号'].isin(top['会员编号'])]
base(set(top['会员编号']), f'O1 R 前 1%（{k} 人）')
base(set(rest['会员编号']), 'O1 其余')
print('  前 1% 卡组', top['cg'].value_counts().to_dict())
d4a_up = a[(a['卡别'] >= 3) & a['nov'] & (a.dep > 0) & (a.g0 >= 15000)]
ov = len(set(o1.loc[o1.cg == '金卡以上', '会员编号']) & set(d4a_up['会员编号']))
print(f'  O1 金卡以上 {int((o1.cg == "金卡以上").sum()):,} ∩ D4a 高卡上界 {len(d4a_up):,} = {ov:,}')
print(f'  O1 中赠点 < 15,000（一定没买首储，储值位先看 NT$50）{int((o1.g0 < 15000).sum()):,}，其中金卡以上 {int(((o1.g0 < 15000) & (o1.cg == "金卡以上")).sum())}')

print('\n===== O4 回流在场者')
tb = lambda t: pd.cut(t, [-1, 29, 90, 365, 1095, 1e6], labels=['<30', '30–90', '91–365', '1–3 年', '3 年以上']).astype(str)
a['tb'] = tb(a['tenure'])
o4 = a[(a['身份'] == '回流') & a.r07]
cont = a[(a['身份'] == '持續') & a.r07]
base(set(o4['会员编号']), 'O4 回流 0–7 天')
print(f'  付费率：回流在场 {(o4.dep > 0).mean() * 100:.2f}%；持續在场 {(cont.dep > 0).mean() * 100:.2f}%')
rows, big = [], 0
for c in ['普卡', '银卡', '金卡以上']:
    for t in ['<30', '30–90', '91–365', '1–3 年', '3 年以上']:
        r, q = o4[(o4.cg == c) & (o4.tb == t)], cont[(cont.cg == c) & (cont.tb == t)]
        ok = len(r) >= 30 and len(q) >= 30
        judged = ok and t not in ('30–90', '<30')
        pr, pq = (r.dep > 0).mean() * 100 if len(r) else np.nan, (q.dep > 0).mean() * 100 if len(q) else np.nan
        print(f'  {c} {t}: 回流 {len(r):,} {pr:.2f}%｜持續 {len(q):,} {pq:.2f}%｜持續−回流 {pq - pr:+.2f}｜{"判读" if judged else ("不判读" if ok else "小格")}')
        if judged and c == '普卡':
            rows.append(pq - pr)
print(f'  普卡判读格 {len(rows)}；差 ≥ 5 的格 {sum(1 for x in rows if x >= 5)}；差 < 5 的格 {sum(1 for x in rows if x < 5)}')

print('\n===== O2 小额付费者（0–7 天、储值 1–100、剔除 VIP、黑名单）')
o2 = a[a.r07 & (a.dep > 0) & (a.dep <= 100) & a['nov']]
e = base(set(o2['会员编号']), 'O2')
only16800 = (a.a0 == 50) & (a.g0 == 16800)
only15000 = (a.a0 == 50) & (a.g0 == 15000)
print(f'  子行：只买首储 16,800 点（129 口径）全体 {int(only16800.sum())}，其中 O2 内 {int((only16800 & a["会员编号"].isin(o2["会员编号"])).sum())}')
print(f'  子行：+ 50 元 15,000 点（652 口径）全体 {int((only16800 | only15000).sum())}，其中 O2 内 {int(((only16800 | only15000) & a["会员编号"].isin(o2["会员编号"])).sum())}')
again = o2.dep.sum()
print(f'  全部人再付一次同额：{again:,.0f}（占 S {again / TS * 100:.3f}%，占 R {again / TR * 100:.3f}%，假设）；储值中位 {o2.dep.median():,.0f}')

print('\n===== O3 接近升卡门槛（上界；只看储值路线）')
T = {2: 1000, 3: 3000, 4: 8000, 5: 20000, 6: 50000, 7: 100000}
LV = {5: 750, 6: 5000, 7: 10000}
act = a[a.r07 & a['nov']].copy()
tot = past = 0
upS = []
for c in range(1, 7):
    nx = c + 1
    x = act[act['卡别'] == c]
    cond = x.dep >= 0.8 * T[nx]
    if nx in LV:
        cond &= x['lv'] >= LV[nx]
    y = x[cond]
    p = y[y.dep >= T[nx]]
    tot += len(y)
    past += len(p)
    upS.extend(y['会员编号'])
    print(f'  卡别 {c} → {nx}（门槛 {T[nx]:,}{"，等级 " + str(LV[nx]) if nx in LV else ""}）：上界 {len(y):,}，其中累计已过门槛 {len(p):,}')
print(f'  合计上界 {tot:,}，其中累计已过门槛却没升 {past:,}')
base(set(upS), 'O3 上界人群')

print('\n===== O5、O6（已含在 D8 独有 / D4b）')
hi = g['U2'][g['U2'].seg == '高']
e5 = expose(U, set(hi['会员编号']), TS, TR)
print(f'  O5 U2 高段 {e5["n"]:,}：占 D8 独有暴露 S {e5["S"] / PROB["D8 独有"][0] * 100:.1f}%、R {e5["R"] / PROB["D8 独有"][1] * 100:.1f}%；普卡 {int((hi["卡别"] == 1).sum()):,}')
d4b = a[(a.dep <= 0) & a['nov'] & a.r07]
o6 = d4b[d4b['bet'] > 10000]
print(f'  O6 D4b 中押注 > 1 万：{len(o6):,}（占 D4b {len(o6) / len(d4b) * 100:.2f}%）')
