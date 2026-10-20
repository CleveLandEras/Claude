"""Q90 附：编号末位奇偶不平衡的来源诊断，及两种替代分桶（倒数第二位奇偶、编号 ÷ 10 取整后奇偶等价于倒数第二位；另试 编号 mod 7 分 0–3 / 4–6 不均，故只试倒数第二位与 mod 97 奇偶）。只读，不带参数。
规则 5 同 Q90 卡：人数差 > 2%、卡组占比差 > 1 个百分点、R 均值差 > 该人群 50/50 原值 MDE 的一半 → 不平衡。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

SC = _ROOT + '/_scripts/'
with contextlib.redirect_stdout(io.StringIO()):
    G = runpy.run_path(SC + 'an_q86_lift.py')
U = G['U']
Uv = U.set_index('会员编号')
POP = {'O1 其余（主行）': (G['rest'], 12.3), '高卡去大户': (G['O1_hi_nt'], 12.7), 'D1 全部': (G['D1'], 72.8)}

allid = U['会员编号'].astype('int64')
L = allid.astype(str).str.len()
print('全体（合并）编号位数分布：', L.value_counts().sort_index().to_dict())
print('全体末位分布：', (allid % 10).value_counts().sort_index().to_dict())
for ln in sorted(L.unique()):
    x = U[L == ln]
    print(f'  位数 {ln}: n {len(x):,}｜偶数占 {(x["会员编号"] % 2 == 0).mean() * 100:.1f}%｜有储值率 {(x["dep"] > 0).mean() * 100:.1f}%｜R 均值 {x["R"].mean():,.1f}｜平台 {x["plat"].value_counts().head(3).to_dict()}')


def check(df, half, key, name):
    b = key(df['会员编号'].astype('int64'))
    n0, n1 = int((b == 0).sum()), int((b == 1).sum())
    nd = abs(n0 - n1) / ((n0 + n1) / 2) * 100
    cg = np.where(df['卡别'] >= 3, '金卡以上', np.where(df['卡别'] == 2, '银卡', '普卡'))
    sh = pd.crosstab(b, cg, normalize='index') * 100
    sd = (sh.iloc[0] - sh.iloc[1]).abs().max()
    r0, r1 = df.loc[b == 0, 'R'], df.loc[b == 1, 'R']
    md = abs(r0.mean() - r1.mean()) / df['R'].mean() * 100
    v = '不平衡' if (nd > 2 or sd > 1 or md > half) else '本快照下平衡'
    print(f'    {name}: {n0:,} / {n1:,}（差 {nd:.2f}%）｜卡组差 {sd:.2f}｜R 均值差 {md:.2f}%（门槛 {half:.2f}%）｜中位 {r0.median():,.1f} / {r1.median():,.1f}｜{v}')


for nm, (x, m) in POP.items():
    df = Uv.loc[list(x['会员编号'])].reset_index()
    ln = df['会员编号'].astype(str).str.len()
    print(f'\n{nm}（n {len(df):,}）：位数分布 {ln.value_counts().sort_index().to_dict()}')
    check(df, m / 2, lambda s: s % 2, '末位奇偶（原）')
    check(df, m / 2, lambda s: (s // 10) % 2, '倒数第二位奇偶')
    check(df, m / 2, lambda s: (s % 97) % 2, '编号 mod 97 奇偶')
    short = df[ln <= 8]
    if len(short) > 100:
        check(short, m / 2, lambda s: s % 2, f'只看 ≤ 8 位编号（{len(short):,} 人）末位奇偶')
