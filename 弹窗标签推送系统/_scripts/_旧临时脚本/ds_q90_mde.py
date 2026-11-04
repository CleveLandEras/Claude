"""设计者试算（Q90 设计卡用）：只读。看在场付费者 R 的离散程度与粗略可检测幅度，用来定方法（截尾、分层、分组比例），不作结论。"""
import math
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, '/Users/decheng.huang/claude/弹窗标签推送系统/_scripts')
from an_q76_perf import load  # noqa: E402

g, U = load()
a = g['a'].copy()
m = (a['tenure'] / 30.44).clip(lower=1)
a['R'] = (a['dep'].clip(lower=0) / m).where(a['tenure'].notna())
a['cg'] = np.where(a['卡别'] == 1, '普卡', np.where(a['卡别'] == 2, '银卡', '金卡以上'))
a['r07'] = a['days'] <= 7
o1 = a[a.r07 & (a.dep > 0) & a['nov']]
k = math.ceil(len(o1) * 0.01)
top = o1.nlargest(k, 'R')
rest = o1[~o1['会员编号'].isin(top['会员编号'])]
hi = o1[o1.cg == '金卡以上']
hi_rest = hi[~hi['会员编号'].isin(top['会员编号'])]
Z = 1.96 + 0.84


def show(df, name):
    r = df['R'].dropna()
    n = len(r)
    mu, sd = r.mean(), r.std()
    p99 = r.quantile(0.99)
    rw = r.clip(upper=p99)
    lr = np.log1p(r)
    out = []
    for split in (0.5, 0.2):
        n1, n2 = n * split, n * (1 - split)
        se = math.sqrt(1 / n1 + 1 / n2)
        out.append(f'分组 {int(split*100)}/{int((1-split)*100)}：MDE 原值 {Z*sd*se/mu*100:.1f}%｜P99 截尾 {Z*rw.std()*se/rw.mean()*100:.1f}%')
    print(f'{name}: n={n:,} 均值 {mu:,.0f} 中位 {r.median():,.0f} sd {sd:,.0f} CV {sd/mu:.2f}｜截尾后 CV {rw.std()/rw.mean():.2f}｜log sd {lr.std():.2f}')
    print('   ' + '；'.join(out))
    # 按卡别×注册时长分层后的残差 CV（分层能降多少方差）
    tb = pd.cut(df['tenure'], [-1, 365, 1095, 1e6], labels=['≤1y', '1–3y', '>3y']).astype(str)
    grp = df['卡别'].clip(upper=6).astype(str) + tb
    resid = (df['R'] - df.groupby(grp)['R'].transform('mean')).dropna()
    print(f'   分层（卡别×注册三档）后残差 sd / 均值 = {resid.std()/mu:.2f}（原 CV {sd/mu:.2f}）')


show(rest, 'O1 其余')
show(hi_rest, 'O1 金卡以上去大户')
show(hi, 'O1 金卡以上全部')
show(top, 'O1 R 前 1%')
# 二元指标：D1 待再来回来率 / O4 付费率 粗算（p 未知取 0.5 最坏）
for n, p, name in [(755, 0.5, 'D1 待再来（p=0.5 最坏）'), (927, 0.5, 'D1 全部（p=0.5）'), (8022, 0.20, 'O4 付费率（p=0.20）')]:
    se = math.sqrt(p * (1 - p) * (1 / (n / 2) + 1 / (n / 2)))
    print(f'{name}: n={n}，50/50 分组 MDE 绝对 {Z*se*100:.1f} 个百分点')
