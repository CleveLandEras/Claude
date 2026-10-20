"""Q90：上线后怎么评估（A29）。照设计卡 Q90 S2 平衡核对、S3 可检测幅度、S4 情景对表。只读，不带参数。
人群定义复用 an_q86_lift.py（内部 an_q77_opp → an_q76_perf → an_q66_push）：O1 其余 rest、高卡去大户、大户 top、D1、D8 独有 UQ、O4（回流 0–7 天）。不另定义。
R = max(累计,0) ÷ max(月龄,1)，是「历史月均」，代替月储值：本地 MDE 为乐观口径（真实只会更大）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import contextlib
import io
import math
import runpy

import numpy as np
import pandas as pd

SC = _ROOT + '/_scripts/'
with contextlib.redirect_stdout(io.StringIO()):
    G = runpy.run_path(SC + 'an_q86_lift.py')
U, g, a = G['U'], G['g'], G['a'] if 'a' in G else None
o1, top, rest, O1_hi_nt = G['o1'], G['top'], G['rest'], G['O1_hi_nt']
D1, D1a, D1l = G['D1'], G['D1a'], G['D1l']
UQ = g['UQ']
Uv = U.set_index('会员编号')
A = g['a'].copy()
A['r07'] = A['days'] <= 7
O4 = A[(A['身份'] == '回流') & A['r07']]
Z = 1.96 + 0.84  # 双侧 5%、把握度 80%


def pick(x):
    return Uv.loc[list(x['会员编号'])].copy()


POP = {'O1 其余（主行）': pick(rest), '高卡去大户': pick(O1_hi_nt), '大户（R 前 1%）': pick(top),
       'D1 全部': pick(D1), 'D1 待再来': pick(D1a), 'D1 离开': pick(D1l), 'D8 独有': pick(UQ), 'O4 回流在场': pick(O4)}


def cells(df):
    """卡别（6、7 合并）× 注册三档；每个卡别内 < 30 人的注册档并入相邻档。返回每人所属格标签。"""
    ck = np.where(df['卡别'] >= 6, '6–7', df['卡别'].astype(int).astype(str))
    tb = pd.cut(df['tenure'], [-1, 365, 1095, 1e7], labels=['≤365', '366–1,095', '>1,095']).astype(str)
    lab = pd.Series(index=df.index, dtype=object)
    merged = []
    TB = ['≤365', '366–1,095', '>1,095']
    for c in sorted(set(ck)):
        m = ck == c
        groups = [[t] for t in TB]
        while True:
            sizes = [int((m & tb.isin(gp)).sum()) for gp in groups]
            small = [i for i, s in enumerate(sizes) if s < 30]
            if not small or len(groups) == 1:
                break
            i = small[0]
            j = 1 if i == 0 else (i - 1 if i == len(groups) - 1 else (i - 1 if sizes[i - 1] <= sizes[i + 1] else i + 1))
            p, q = sorted([i, j])
            groups[p] = groups[p] + groups[q]
            del groups[q]
        for gp in groups:
            if len(gp) > 1:
                merged.append(f'{c}:{"+".join(gp)}')
            lab[m & tb.isin(gp)] = f'{c}|{"+".join(gp)}'
    return lab, merged


def mde(sd, mu, n, split):
    n1, n2 = n * split, n * (1 - split)
    return Z * sd * math.sqrt(1 / n1 + 1 / n2) / mu * 100


RES = {}
print('===== S3 连续指标（R 代替人均月储值；MDE 为相对均值的 %，乐观口径）')
for nm, df in POP.items():
    d = df[df['R'].notna()].copy()
    r = d['R']
    n, mu, med, sd = len(r), r.mean(), r.median(), r.std()
    p99 = r.quantile(0.99)
    rw = r.clip(upper=p99)
    lab, merged = cells(d)
    res = (r - r.groupby(lab).transform('mean'))
    resw = (rw - rw.groupby(lab).transform('mean'))
    out = {}
    for sp in (0.5, 0.2):
        out[sp] = (mde(sd, mu, n, sp), mde(rw.std(), rw.mean(), n, sp), mde(res.std(), mu, n, sp), mde(resw.std(), rw.mean(), n, sp))
    RES[nm] = dict(n=n, mu=mu, med=med, sd=sd, cv=sd / mu, p99=p99, out=out, mu_w=rw.mean())
    print(f'{nm}: n {n:,}（R 缺 {len(df) - n}）｜均值 {mu:,.1f} 中位 {med:,.1f} sd {sd:,.1f} CV {sd / mu:.2f}｜P99 截尾值 {p99:,.0f}，截尾后均值 {rw.mean():,.1f} CV {rw.std() / rw.mean():.2f}'
          f'｜分层残差 sd/均值 {res.std() / mu:.2f}｜格数 {lab.nunique()}；合并 {merged if merged else "无"}')
    for sp in (0.5, 0.2):
        o = out[sp]
        print(f'   {int(sp * 100)}/{int((1 - sp) * 100)}：原值 {o[0]:.1f}%｜截尾 {o[1]:.1f}%｜分层 {o[2]:.1f}%｜分层+截尾 {o[3]:.1f}%'
              f'｜k=3 合并区间（分层+截尾）{o[3] / math.sqrt(3):.1f}%–{o[3]:.1f}%')

print('\n===== S3 二元指标（绝对百分点）')
BIN = {}
for nm, n, p, note in [('D1 全部 · 回来 / 储值', len(D1), 0.5, 'p 未知取 0.5（最坏）'), ('D1 待再来 · 回来 / 储值', len(D1a), 0.5, '同上'),
                       ('D1 离开 · 回来 / 储值', len(D1l), 0.5, '同上'), ('D8 独有 · 回来 / 储值', len(UQ), 0.5, '同上'),
                       ('O4 · 付费率', len(O4), (O4['dep'] > 0).mean(), '本快照')]:
    m50 = Z * math.sqrt(p * (1 - p) * (2 / n + 2 / n)) * 100
    m20 = Z * math.sqrt(p * (1 - p) * (1 / (0.2 * n) + 1 / (0.8 * n))) * 100
    BIN[nm] = (n, p, m50, m20)
    print(f'{nm}: n {n:,} p {p:.4f}（{note}）｜50/50 {m50:.2f} 个百分点｜20/80 {m20:.2f}｜k=3 区间（50/50）{m50 / math.sqrt(3):.2f}–{m50:.2f}')

print('\n===== S4 在场一面情景对表（判档用分层+截尾、50/50）')


def band(x, m):
    return '理论上可测' if x >= m else ('边缘' if x >= m / 2 else '测不出')


def need(x, m):
    k = (m / x) ** 2
    return k, ('现有人数够' if k <= 1 else ('合并约三期可能够' if k <= 3 else '现有规模下测不出'))


for nm in ['O1 其余（主行）', '高卡去大户', '大户（R 前 1%）']:
    o = RES[nm]['out']
    m = o[0.5][3]
    for x in [1, 3, 5, 10]:
        k, kk = need(x, m)
        print(f'  {nm} x={x}%：MDE 原值 50/50 {o[0.5][0]:.1f}% 20/80 {o[0.2][0]:.1f}%｜分层+截尾 50/50 {m:.1f}% 20/80 {o[0.2][3]:.1f}%｜判档 {band(x, m)}｜所需人数 {k:.1f} 倍（{kk}）')

print('\n===== S4 不来一面情景对表（回来率提高 N ÷ 格人数；判档用 50/50 二元 MDE，p = 0.5）')
for nm, key in [('D1 全部', 'D1 全部 · 回来 / 储值'), ('D1 待再来', 'D1 待再来 · 回来 / 储值'), ('D1 离开', 'D1 离开 · 回来 / 储值')]:
    n, p, m50, m20 = BIN[key]
    for N in [9, 28, 46, 93]:
        x = N / n * 100
        k, kk = need(x, m50)
        print(f'  {nm}（{n}）N={N}：提高 {x:.2f} 个百分点｜MDE 50/50 {m50:.2f}｜20/80 {m20:.2f}｜判档 {band(x, m50)}｜所需人数 {k:.1f} 倍（{kk}）')

print('\n===== S2 路 B 编号末位奇偶平衡核对')
print('会员编号 dtype', U['会员编号'].dtype, '样例', list(U['会员编号'].astype(str).head(3)))
for nm in ['O1 其余（主行）', '高卡去大户', 'D1 全部']:
    df = POP[nm].reset_index()
    s = df['会员编号'].astype(str).str.strip()
    isnum = s.str.fullmatch(r'\d+')
    last = s.str[-1]
    grp = np.where(last.str.isdigit(), last.fillna('0').apply(lambda c: int(c) % 2 if c.isdigit() else ord(c) % 2), last.apply(lambda c: ord(c) % 2))
    df['bk'] = grp
    n0, n1 = int((df.bk == 0).sum()), int((df.bk == 1).sum())
    ndiff = abs(n0 - n1) / ((n0 + n1) / 2) * 100
    cg = np.where(df['卡别'] >= 3, '金卡以上', np.where(df['卡别'] == 2, '银卡', '普卡'))
    shares = pd.crosstab(df['bk'], cg, normalize='index') * 100
    sd_ = (shares.loc[0] - shares.loc[1]).abs().max() if len(shares) == 2 else np.nan
    r0, r1 = df.loc[df.bk == 0, 'R'], df.loc[df.bk == 1, 'R']
    mdiff = abs(r0.mean() - r1.mean()) / RES[nm]['mu'] * 100
    half = RES[nm]['out'][0.5][0] / 2
    verdict = '不平衡' if (ndiff > 2 or sd_ > 1 or mdiff > half) else '本快照下平衡'
    print(f'  {nm}: 纯数字编号 {isnum.mean() * 100:.1f}%｜偶 {n0:,} 奇 {n1:,}（差 {ndiff:.2f}%）｜卡组占比最大差 {sd_:.2f} 个百分点'
          f'｜R 均值 偶 {r0.mean():,.1f} 奇 {r1.mean():,.1f}（差 {mdiff:.2f}% ，门槛 {half:.2f}%）｜R 中位 偶 {r0.median():,.1f} 奇 {r1.median():,.1f}｜{verdict}')

print('\n===== 附：O4 付费率本快照', f'{(O4["dep"] > 0).mean() * 100:.2f}%', '；O4 人数', len(O4))
