"""Q93：N1 的前提与分档（A30）。照设计卡 Q93 S1–S4 与判读规则 1–6。只读，不带参数。
人群定义照 an_q77_opp.py（o1、top、rest、R、g0 写法），import an_q76_perf.load，不另定义。
R = max(累计储值,0) ÷ max(账号月龄,1)，是「历史月均」，不是月储值，也不是单次付费。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import math
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, _ROOT + '/_scripts')
import contextlib  # noqa: E402
import io  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    from an_q76_perf import load  # noqa: E402
    g, U = load()
a = g['a'].copy()
m = (a['tenure'] / 30.44).clip(lower=1)
a['R'] = (a['dep'].clip(lower=0) / m).where(a['tenure'].notna())
a['cg'] = np.where(a['卡别'] == 1, '普卡', np.where(a['卡别'] == 2, '银卡', '金卡以上'))
a['r07'] = a['days'] <= 7
a['g0'] = pd.to_numeric(a['充值赠点'], errors='coerce').fillna(0).round(0)
a['a0'] = a['dep'].round(2)

o1 = a[a.r07 & (a.dep > 0) & a['nov']]
k = math.ceil(len(o1) * 0.01)
top = o1.nlargest(k, 'R')
rest = o1[~o1['会员编号'].isin(top['会员编号'])]
hi = rest[rest.cg == '金卡以上'].copy()
print('===== S1 口径复现')
print(f'O1 {len(o1):,}（应 13,368）｜大户 {len(top)}（应 134）｜O1 其余 {len(rest):,}（应 13,234）｜高卡去大户 {len(hi):,}（应 5,146）')
ok = (len(o1), len(top), len(rest), len(hi)) == (13368, 134, 13234, 5146)
print('复现', '通过' if ok else '不通过')

hi['tier'] = np.where(hi['卡别'] >= 6, '卡6+7', '卡' + hi['卡别'].astype(int).astype(str))
TIERS = ['卡3', '卡4', '卡5', '卡6+7']


def s1(x, name):
    lo = int((x.g0 < 15000).sum())
    fp = int(((x.a0 == 50) & x.g0.isin([16800, 15000])).sum())
    up = len(x) - fp
    print(f'  {name}: n {len(x):,}｜下界（赠点 < 15,000，确定没买过首储）{lo}（{lo / len(x) * 100:.2f}%）｜确定买过首储（累计 50 且赠点 16,800 / 15,000）{fp}｜上界 {up:,}（{up / len(x) * 100:.2f}%）')
    return lo, fp, up


print('\n===== S1 前提上下界')
s1(hi, '高卡去大户')
for t in TIERS:
    s1(hi[hi.tier == t], t)
s1(top, '大户 134')

print('\n===== S2 各档 R 分布（按历史月均）')
Q = {}
for t in TIERS:
    x = hi[hi.tier == t]
    r = x['R'].dropna()
    q = r.quantile([.1, .25, .5, .75, .9])
    Q[t] = q
    print(f'  {t}: n {len(x):,}｜R P10 {q[.1]:,.1f} P25 {q[.25]:,.1f} 中位 {q[.5]:,.1f} P75 {q[.75]:,.1f} P90 {q[.9]:,.1f}｜均值 {r.mean():,.1f}（均值/中位 {r.mean() / q[.5]:.2f}）'
          f'｜累计储值中位 {x.dep.median():,.0f}｜注册月龄中位 {(x.tenure / 30.44).median():.1f}')
print('  相邻档重叠（低一档中 R 高于上一档 R 中位的比例）：')
for lo_, up_ in [('卡3', '卡4'), ('卡4', '卡5'), ('卡5', '卡6+7')]:
    x = hi[hi.tier == lo_]['R'].dropna()
    print(f'    {lo_} 对 {up_}：{(x > Q[up_][.5]).mean() * 100:.2f}%')
print(f'  卡3 中位 / 卡6+7 中位 倍数（全部人）：{Q["卡6+7"][.5] / Q["卡3"][.5]:.2f}')

print('\n===== S2 注册时长控制（各档 × 注册三档 R 中位）')
hi['tb'] = pd.cut(hi['tenure'], [-1, 365, 1095, 1e7], labels=['≤365', '366–1,095', '>1,095']).astype(str)
MED = {}
for t in TIERS:
    cells = []
    for b in ['≤365', '366–1,095', '>1,095']:
        x = hi[(hi.tier == t) & (hi.tb == b)]['R'].dropna()
        if len(x) < 30:
            cells.append(f'{b}: n {len(x)}（小格）')
        else:
            MED[(t, b)] = x.median()
            cells.append(f'{b}: n {len(x):,} 中位 {x.median():,.1f}')
    print(f'  {t}｜' + '｜'.join(cells))
if ('卡3', '>1,095') in MED and ('卡6+7', '>1,095') in MED:
    print(f'  注册 > 1,095 天口径：卡6+7 中位 / 卡3 中位 = {MED[("卡6+7", ">1,095")] / MED[("卡3", ">1,095")]:.2f}')
for b in ['≤365', '366–1,095']:
    if ('卡3', b) in MED and ('卡6+7', b) in MED:
        print(f'  注册 {b} 口径：卡6+7 / 卡3 = {MED[("卡6+7", b)] / MED[("卡3", b)]:.2f}')

print('\n===== S3 价格对照（P 为价格带锚点，不是任何礼包的实际价格）')
PS = [50, 300, 1000, 3000]
J = {}
for t in TIERS:
    row = []
    for P in PS:
        p25, med = Q[t][.25], Q[t][.5]
        j = '偏低' if P < p25 else ('不偏低' if P > med else '不定')
        J[(t, P)] = j
        row.append(f'P={P}: {j}')
    print(f'  {t}（P25 {Q[t][.25]:,.1f}，中位 {Q[t][.5]:,.1f}）｜' + '｜'.join(row))
# 同一判断在注册 > 1,095 天口径下（反例检查 ②）
print('  反例检查：注册 > 1,095 天口径下的 P25 / 中位')
for t in TIERS:
    x = hi[(hi.tier == t) & (hi.tb == '>1,095')]['R'].dropna()
    if len(x) >= 30:
        print(f'    {t}: n {len(x):,} P25 {x.quantile(.25):,.1f} 中位 {x.median():,.1f}｜' + '｜'.join(
            f'P={P}: ' + ('偏低' if P < x.quantile(.25) else ('不偏低' if P > x.median() else '不定')) for P in PS))

print('\n===== S4 量级')
TR = hi['R'].sum()
for t in TIERS:
    x = hi[hi.tier == t]
    print(f'  {t}: 人数 {len(x):,}（{len(x) / len(hi) * 100:.2f}%）｜R 合计 {x.R.sum():,.0f}（{x.R.sum() / TR * 100:.2f}%）')
for P in [300, 1000]:
    ts = [t for t in TIERS if J[(t, P)] == '偏低']
    x = hi[hi.tier.isin(ts)]
    print(f'  P={P}：判「偏低」的档 {ts}｜人数 {len(x):,}（{len(x) / len(hi) * 100:.2f}%）｜R {x.R.sum() / TR * 100:.2f}%')
    tsn = [t for t in TIERS if J[(t, P)] == '不定']
    print(f'         判「不定」的档 {tsn}；判「不偏低」的档 {[t for t in TIERS if J[(t, P)] == "不偏低"]}')

print('\n===== 大户 134')
r = top['R']
print(f'  R 中位 {r.median():,.1f}，P25 {r.quantile(.25):,.1f}，均值 {r.mean():,.1f}；卡别 {top["卡别"].value_counts().sort_index().to_dict()}')
