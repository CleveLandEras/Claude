"""Q86：改善幅度怎么估（A25）。照设计卡 Q86 S1–S5。只读，不带参数。
人群定义复用 an_q77_opp.py（o1、top、rest，内部 import an_q76_perf 的 load / unit_S / unit_R）与 an_q66_push.py（D1）。不另定义。
S = 累计储值（合并口径）；R = max(累计,0) ÷ max(月龄,1)，月龄 = 注册距 9/16 天数 ÷ 30.44；注册缺值不计入 R。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

SC = _ROOT + '/_scripts/'
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    G = runpy.run_path(SC + 'an_q77_opp.py')
U, g, TS, TR = G['U'], G['g'], G['TS'], G['TR']
o1, top, rest = G['o1'], G['top'], G['rest']

ids = lambda x: set(x['会员编号'])
Uv = U.set_index('会员编号')


def pick(s):
    return Uv.loc[list(s)]


O1_hi = o1[o1['cg'] == '金卡以上']
O1_hi_nt = O1_hi[~O1_hi['会员编号'].isin(ids(top))]
D1 = g['D1']
D1a = D1[D1['tier'] != '离开']
D1l = D1[D1['tier'] == '离开']

print('===== S1 核对')
print(f'合并 {len(U):,}；S 总额 {TS:,.0f}；R 总额 {TR:,.0f}')
print(f'O1 全部 {len(o1):,}；O1 金卡以上 {len(O1_hi):,}；R 前 1% {len(top)}（卡组 {top["cg"].value_counts().to_dict()}）；O1 其余 {len(rest):,}；金卡以上去大户 {len(O1_hi_nt):,}')
print(f'O1 其余卡组 {rest["cg"].value_counts().to_dict()}')
print(f'D1 {len(D1)}；分档 {D1["tier"].value_counts().to_dict()}；待再来 {len(D1a)}；离开 {len(D1l)}；D1 身份 {D1["身份"].value_counts().to_dict()}')
print(f'O1 ∩ D1 = {len(ids(o1) & ids(D1))}；O1 金卡以上 ∩ D1 = {len(ids(O1_hi) & ids(D1))}')
for nm, x in [('O1 其余', rest), ('O1 金卡以上去大户', O1_hi_nt), ('O1 金卡以上', O1_hi), ('R 前 1%', top), ('D1', D1), ('D1 待再来', D1a), ('D1 离开', D1l)]:
    y = pick(ids(x))
    print(f'  {nm}: n {len(y):,}｜S {y.S.sum():,.0f}（{y.S.sum() / TS * 100:.2f}%）｜R {y.R.sum():,.0f}（{y.R.sum() / TR * 100:.2f}%）｜R 缺 {int(y.R.isna().sum())}'
          f'｜R 中位 {y.R.median():,.1f} 均值 {y.R.mean():,.1f} P90 {y.R.quantile(.9):,.0f} P99 {y.R.quantile(.99):,.0f}｜S 中位 {y.S.median():,.0f} 均值 {y.S.mean():,.0f}')

print('\n===== S2 在场一面情景')
ROWS = {'主行 O1 其余': pick(ids(rest)), '高卡去大户': pick(ids(O1_hi_nt)), '高卡全部': pick(ids(O1_hi))}
XS = [1, 3, 5, 10]
for nm, y in ROWS.items():
    bs, br, n = y.S.sum(), y.R.sum(), len(y)
    med, mean = y.R.median(), y.R.mean()
    print(f'  {nm}（{n:,} 人；底盘 S {bs:,.0f} / R {br:,.0f}；R 中位 {med:,.1f} 均值 {mean:,.1f}）')
    for x in XS:
        s, r = bs * x / 100, br * x / 100
        pp = r / n
        print(f'    x={x}%：S {s:,.0f}（{s / TS * 100:.3f}%）｜R {r:,.0f}（{r / TR * 100:.3f}%）｜人均每月 {pp:,.1f}（= R 中位 {pp / med * 100:.1f}%，R 均值 {x}%）')

print('\n===== S3 同条件差距（O1 金卡以上）')
H = pick(ids(O1_hi)).copy()
H['cgk'] = np.where(H['卡别'] >= 6, '6–7', H['卡别'].astype(int).astype(str))
H['tb3'] = pd.cut(H['tenure'], [-1, 365, 1095, 1e7], labels=['≤365', '366–1,095', '>1,095']).astype(str)
q1, q2 = H['bet'].quantile([1 / 3, 2 / 3])
H['bt3'] = np.where(H['bet'] <= q1, '押注低', np.where(H['bet'] <= q2, '押注中', '押注高'))
print(f'  R 缺（注册缺值）{int(H.R.isna().sum())}；tenure 缺 {int(H.tenure.isna().sum())}；押注三分位 {q1:,.0f} / {q2:,.0f}')
TB = ['≤365', '366–1,095', '>1,095']


def gap(v):
    v = v.dropna()
    m = v.median()
    return m, (m - v[v < m]).sum()


def split(outer, col, order_outer):
    out = {'R': 0.0, 'S': 0.0}
    rows = []
    for o in order_outer:
        x = H[H[outer] == o]
        groups = [[t] for t in TB]
        # 合并 < 30 人的格到相邻注册档
        while True:
            sizes = [int(x['tb3'].isin(gp).sum()) for gp in groups]
            small = [i for i, s in enumerate(sizes) if s < 30]
            if not small or len(groups) == 1:
                break
            i = small[0]
            if i == 0:
                j = 1
            elif i == len(groups) - 1:
                j = i - 1
            else:
                j = i - 1 if sizes[i - 1] <= sizes[i + 1] else i + 1
            a_, b_ = sorted([i, j])
            groups[a_] = groups[a_] + groups[b_]
            del groups[b_]
        for gp in groups:
            y = x[x['tb3'].isin(gp)]
            if len(y) < 30:
                rows.append((o, '+'.join(gp), len(y), None, None, None, None))
                continue
            mr, gr = gap(y['R'])
            ms, gs = gap(y['S'])
            out['R'] += gr
            out['S'] += gs
            rows.append((o, '+'.join(gp), len(y), mr, gr, ms, gs))
    return out, rows


for nm, outer, order in [('切分 A 卡组 × 注册时长', 'cgk', ['3', '4', '5', '6–7']), ('切分 B 押注三分位 × 注册时长', 'bt3', ['押注低', '押注中', '押注高'])]:
    out, rows = split(outer, 'tb3', order)
    print(f'  {nm}')
    for r in rows:
        if r[3] is None:
            print(f'    {r[0]} {r[1]}: n {r[2]}（小格，只列人数）')
        else:
            print(f'    {r[0]} {r[1]}: n {r[2]:,}｜R 中位 {r[3]:,.1f} 缺口 {r[4]:,.0f}｜S 中位 {r[5]:,.0f} 缺口 {r[6]:,.0f}')
    print(f'    G：R {out["R"]:,.0f}（占高卡 R 底盘 {out["R"] / H.R.sum() * 100:.2f}%）｜S {out["S"]:,.0f}（占高卡 S 底盘 {out["S"] / H.S.sum() * 100:.2f}%）')
# 不分注册时长的对照（陷阱 3）
for nm, outer in [('只按卡组（不分注册时长）', 'cgk')]:
    tr = ts = 0
    for o in ['3', '4', '5', '6–7']:
        y = H[H[outer] == o]
        tr += gap(y['R'])[1]
        ts += gap(y['S'])[1]
    print(f'  对照 {nm}：G R {tr / H.R.sum() * 100:.2f}%｜S {ts / H.S.sum() * 100:.2f}%')

print('\n===== S4 不来一面情景')
NS = [9, 28, 46, 93]
DROWS = {'D1 927': pick(ids(D1)), 'D1 待再来 755': pick(ids(D1a)), 'D1 离开 172': pick(ids(D1l))}


def kq(v, q):
    v = v.dropna().sort_values(ascending=False)
    c = v.cumsum() / v.sum()
    return int((c < q).sum() + 1)


for nm, y in DROWS.items():
    r, s = y.R.dropna(), y.S
    print(f'  {nm}：R 均值 {r.mean():,.1f} 中位 {r.median():,.1f} P99 {r.quantile(.99):,.0f}｜均值/中位 {r.mean() / r.median():.2f}｜S 均值 {s.mean():,.0f} 中位 {s.median():,.0f}（{s.mean() / s.median():.2f}）')
    print(f'    R 口径 K50 {kq(r, .5)} K80 {kq(r, .8)} K90 {kq(r, .9)}｜S 口径 K50 {kq(s, .5)} K80 {kq(s, .8)} K90 {kq(s, .9)}｜R 前 10 占 {r.nlargest(10).sum() / r.sum() * 100:.2f}%')
    for N in NS:
        print(f'    N={N}：R 甲 {N * r.mean():,.0f} 乙 {N * r.median():,.0f} 丙 {r.nlargest(N).sum():,.0f}｜S 甲 {N * s.mean():,.0f} 乙 {N * s.median():,.0f} 丙 {s.nlargest(N).sum():,.0f}')

print('\n===== S5 等价表')
Dm = DROWS['D1 927']


def topk(v, amt):
    v = v.dropna().sort_values(ascending=False).cumsum()
    return int((v < amt).sum() + 1) if amt <= v.iloc[-1] else None


for unit in ['R', 'S']:
    v = Dm[unit].dropna()
    mean, med = v.mean(), v.median()
    print(f'  {unit}：D1 每人 甲 {mean:,.1f} 乙 {med:,.1f}')
    for nm in ['主行 O1 其余', '高卡去大户']:
        base = ROWS[nm][unit].sum()
        for x in [1, 3, 5]:
            amt = base * x / 100
            print(f'    {nm} x={x}%（{amt:,.0f}）≈ 甲 {amt / mean:,.1f} 人｜乙 {amt / med:,.1f} 人（乙/甲 {mean / med:.2f}）｜丙 前 {topk(v, amt)} 人')
        for dn, dv in [('D1 927', v), ('D1 待再来 755', DROWS['D1 待再来 755'][unit].dropna())]:
            k80 = kq(dv, .8)
            avg = dv.nlargest(k80).mean()
            print(f'    {nm} × {dn} 名单：K80 {k80} 人，人均 {avg:,.1f}；在场 1% ≈ 前 K80 中留住 {base * 0.01 / avg:.1f} 人；3% ≈ {base * 0.03 / avg:.1f} 人')
        rev = 9 * mean / base * 100
        full = v.sum() / base * 100
        print(f'    反向：D1 额外留住 9 人（甲）≈ {nm} 多付 {rev:.2f}%｜乙 {9 * med / base * 100:.3f}%｜丙（前 9 人）{v.nlargest(9).sum() / base * 100:.2f}%｜与 D1 全部暴露持平需 {full:.2f}%')
    print(f'    参照：与 D1 全部暴露持平，对高卡全部需 {v.sum() / ROWS["高卡全部"][unit].sum() * 100:.2f}%')
