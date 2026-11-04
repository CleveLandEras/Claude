"""审查复算 A29（Q90）。只读。独立写 MDE 公式与编号末位分布，人群定义复用 an_q86_lift（不另定义）。"""
import contextlib
import io
import math
import runpy

import numpy as np
import pandas as pd

SC = '/Users/decheng.huang/claude/弹窗标签推送系统/_scripts/'
DD = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
with contextlib.redirect_stdout(io.StringIO()):
    G = runpy.run_path(SC + 'an_q86_lift.py')
U, g = G['U'], G['g']
o1, top, rest, hi_nt, hi = G['o1'], G['top'], G['rest'], G['O1_hi_nt'], G['O1_hi']
D1, D1a, D1l = G['D1'], G['D1a'], G['D1l']
UQ = g['UQ']
Uv = U.set_index('会员编号')

print('== 人群人数')
print('O1', len(o1), 'top', len(top), 'rest', len(rest), 'O1 高卡', len(hi), '高卡去大户', len(hi_nt), 'D1', len(D1), len(D1a), len(D1l), 'UQ', len(UQ))
print('top 卡组', top['cg'].value_counts().to_dict())
print('若按「高卡内前 1%」去大户应去', math.ceil(len(hi) * 0.01), '人；实际去', len(hi) - len(hi_nt))
print('D1 卡别', D1['卡别'].value_counts().sort_index().to_dict(), '身份', D1['身份'].value_counts().to_dict())
print('D1 有储值率', round((Uv.loc[list(D1['会员编号']), 'dep'] > 0).mean() * 100, 2))
print('D1 tier', D1['tier'].value_counts().to_dict())

Z = 2.8


def mde_raw(v, sp=0.5):
    v = v.dropna()
    n = len(v)
    return Z * v.std() * math.sqrt(1 / (n * sp) + 1 / (n * (1 - sp))) / v.mean() * 100


def strat_trunc(df, sp=0.5):
    d = df[df['R'].notna()].copy()
    rw = d['R'].clip(upper=d['R'].quantile(0.99))
    ck = np.where(d['卡别'] >= 6, 67, d['卡别'])
    tb = pd.cut(d['tenure'], [-1, 365, 1095, 1e7], labels=False)
    key = pd.Series(ck, index=d.index).astype(str) + '_' + pd.Series(tb, index=d.index).astype(str)
    # 不做小格合并，作为对照（合并只影响极少数格）
    res = rw - rw.groupby(key).transform('mean')
    n = len(d)
    return Z * res.std() * math.sqrt(1 / (n * sp) + 1 / (n * (1 - sp))) / rw.mean() * 100


for nm, x in [('主行', rest), ('高卡去大户', hi_nt), ('大户', top), ('D1', D1), ('UQ', UQ)]:
    y = Uv.loc[list(x['会员编号'])]
    print(f'{nm}: n {y.R.notna().sum()} 均值 {y.R.mean():.1f} sd {y.R.std():.1f} 原值 MDE {mde_raw(y.R):.2f}% 分层+截尾（不合并小格）{strat_trunc(y):.2f}%')

print('\n== 二元 MDE 与 p 的敏感性（D1 927，50/50）')
n = len(D1)
for p in [0.5, 0.3, 0.2, 0.12, 0.1, 0.05]:
    m = Z * math.sqrt(p * (1 - p) * 4 / n) * 100
    print(f'  p={p}: MDE {m:.2f} pp（≈ {m / 100 * n:.0f} 人）；N=9 → {9 / n * 100:.2f}pp {"测不出" if 9 / n * 100 < m / 2 else "边缘+"}；N=28 → {28 / n * 100:.2f}pp {"测不出" if 28 / n * 100 < m / 2 else ("边缘" if 28 / n * 100 < m else "可测")}；N=46 → {"测不出" if 46 / n * 100 < m / 2 else ("边缘" if 46 / n * 100 < m else "可测")}')
# p 使 N=28 恰落边缘的上限
lo, hi_ = 0.0001, 0.5
for _ in range(60):
    mid = (lo + hi_) / 2
    m = Z * math.sqrt(mid * (1 - mid) * 4 / n) * 100
    if 28 / n * 100 >= m / 2:
        lo = mid
    else:
        hi_ = mid
print(f'  N=28 落「边缘」所需 p ≤ {lo:.3f}')
lo, hi_ = 0.0001, 0.5
for _ in range(60):
    mid = (lo + hi_) / 2
    m = Z * math.sqrt(mid * (1 - mid) * 4 / n) * 100
    if 9 / n * 100 >= m / 2:
        lo = mid
    else:
        hi_ = mid
print(f'  N=9 落「边缘」所需 p ≤ {lo:.4f}')

print('\n== 编号末位（原始 CSV 按字符串读）')
for f in ['近一月活跃_20260916.csv', '八月登录流失名单_20260916.csv']:
    raw = pd.read_csv(DD + f, encoding='utf-8-sig', dtype=str)
    raw = raw[~raw['身份'].isin(['機器人', '測試帳號'])]
    s = raw['会员编号'].str.strip()
    L = s.str.len()
    print(f, '行', len(s), '含非数字字符', int((~s.str.fullmatch(r'\d+')).sum()), '含 E/小数点', int(s.str.contains(r'[eE\.]').sum()))
    print('  位数分布', L.value_counts().sort_index().to_dict())
    long_ = s[L >= 8]
    print('  ≥8 位末位分布', long_.str[-1].value_counts().sort_index().to_dict())
    print('  ≥8 位末两位分布前 10', long_.str[-2:].value_counts().head(10).to_dict())
    print('  样例（只看位数结构，不输出完整编号）前缀 4 位分布', long_.str[:4].value_counts().head(5).to_dict())

print('\n== 高卡去大户：末位奇偶两组 R 均值与中位比')
y = Uv.loc[list(hi_nt['会员编号'])].reset_index()
par = y['会员编号'].astype(str).str.strip().str[-1].astype(int) % 2
for k in [0, 1]:
    print('  ', '偶' if k == 0 else '奇', int((par == k).sum()), 'R 均值', round(y.R[par == k].mean(), 1), '中位', round(y.R[par == k].median(), 1))
