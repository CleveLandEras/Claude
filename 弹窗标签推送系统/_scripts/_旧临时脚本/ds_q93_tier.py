"""设计者试算（Q93 设计卡用，只读，不作结论）：在场高卡去大户 5,146 人按卡别的 R 分布、赠点 < 15,000 人数、R 相对价位锚点。"""
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
a['g0'] = pd.to_numeric(a['充值赠点'], errors='coerce').fillna(0).round(0)
a['r07'] = a['days'] <= 7
o1 = a[a.r07 & (a.dep > 0) & a['nov']]
k = math.ceil(len(o1) * 0.01)
top = o1.nlargest(k, 'R')
rest = o1[~o1['会员编号'].isin(top['会员编号'])]
hi = rest[rest['卡别'] >= 3].copy()
print('O1', len(o1), '前1%', k, '其余', len(rest), '高卡去大户', len(hi), 'R缺值', int(hi.R.isna().sum()))
print('大户卡别', top['卡别'].value_counts().sort_index().to_dict())
q = [0.1, 0.25, 0.5, 0.75, 0.9]
for c in [3, 4, 5, 6, 7, '6+7', '全部']:
    x = hi if c == '全部' else (hi[hi['卡别'] >= 6] if c == '6+7' else hi[hi['卡别'] == c])
    if len(x) == 0:
        print(c, 0); continue
    rq = x.R.quantile(q).round(0).tolist()
    sq = x.dep.quantile([0.5]).round(0).tolist()
    anc = {p: round((x.R >= p).mean() * 100, 1) for p in [50, 300, 1000, 3000]}
    print(f'卡{c}: n={len(x)}｜R P10/25/50/75/90={rq}｜S中位={sq}｜赠点<15000={int((x.g0 < 15000).sum())}｜R≥锚点%={anc}｜注册月龄中位={round(x.tenure.median() / 30.44, 1)}')
# 相邻卡别重叠：低一级卡 R > 高一级卡 R 中位 的比例
for c in [3, 4, 5, 6]:
    lo, up = hi[hi['卡别'] == c], hi[hi['卡别'] == c + 1]
    if len(lo) and len(up):
        print(f'卡{c} 中 R > 卡{c + 1} R中位 的比例 {round((lo.R > up.R.median()).mean() * 100, 1)}%（n {len(lo)} / {len(up)}）')
# 单次档位代理：累计储值为 50 的整倍数、回馈比分布
hi['hk'] = pd.to_numeric(hi['储值回馈比'], errors='coerce')
print('回馈比 P10/50/90', hi.hk.quantile([0.1, 0.5, 0.9]).round(0).tolist(), '≥150 占比', round((hi.hk >= 150).mean() * 100, 2))
print('累计储值 < 3000 的高卡', int((hi.dep < 3000).sum()))
