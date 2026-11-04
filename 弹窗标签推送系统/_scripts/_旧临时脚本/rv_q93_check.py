"""审查复算 A30（Q93）。只读，不带参数。独立从原始 CSV 起算，不 import 执行者脚本。"""
import math

import numpy as np
import pandas as pd

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
T0 = pd.Timestamp('2026-09-16')
ra = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = ra[~ra['身份'].isin(['機器人', '測試帳號'])].copy()
a['last'] = pd.to_datetime(a['最後登入時間']).dt.normalize()
a['reg'] = pd.to_datetime(a['注册时间'], errors='coerce').dt.normalize()
a['days'] = (T0 - a['last']).dt.days
a['tenure'] = (T0 - a['reg']).dt.days
a['dep'] = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
a['nov'] = ~a['身份'].isin(['VIP', '黑名單'])
a['g0'] = pd.to_numeric(a['充值赠点'], errors='coerce').fillna(0).round(0)
m = (a['tenure'] / 30.44).clip(lower=1)
a['R'] = (a['dep'].clip(lower=0) / m).where(a['tenure'].notna())
o1 = a[(a['days'] <= 7) & (a['dep'] > 0) & a['nov']]
k = math.ceil(len(o1) * 0.01)
top = o1.nlargest(k, 'R')
rest = o1[~o1['会员编号'].isin(top['会员编号'])]
hi = rest[rest['卡别'] >= 3].copy()
print('O1', len(o1), '大户', len(top), '其余', len(rest), '高卡去大户', len(hi), '大户卡别', top['卡别'].value_counts().sort_index().to_dict())
print('R 缺值（高卡去大户）', int(hi['R'].isna().sum()))
print('S1 下界 赠点<15000', int((hi.g0 < 15000).sum()), '确定买过首储', int(((hi.dep.round(2) == 50) & hi.g0.isin([16800, 15000])).sum()))
hi['t'] = np.where(hi['卡别'] >= 6, '卡6+7', '卡' + hi['卡别'].astype(int).astype(str))
T = ['卡3', '卡4', '卡5', '卡6+7']
TR = hi['R'].sum()
for t in T:
    r = hi.loc[hi.t == t, 'R'].dropna()
    print(t, len(r), 'P25 %.2f 中位 %.2f' % (r.quantile(.25), r.median()), 'R 占 %.2f%%' % (r.sum() / TR * 100))
    # 价格阈值：P < P25 偏低；P > 中位 不偏低
old = hi[hi['tenure'] > 1095]
for t in T:
    r = old.loc[old.t == t, 'R'].dropna()
    print('老账号', t, len(r), 'P25 %.2f 中位 %.2f' % (r.quantile(.25), r.median()))
print('中位倍数 %.2f' % (hi.loc[hi.t == '卡6+7', 'R'].median() / hi.loc[hi.t == '卡3', 'R'].median()))
print('老账号中位倍数 %.2f' % (old.loc[old.t == '卡6+7', 'R'].median() / old.loc[old.t == '卡3', 'R'].median()))
# 锚点敏感性：几百元范围内，判「偏低」的档与人数、R 占比
for P in [100, 200, 250, 299, 300, 301, 350, 400, 500, 600, 700, 800, 1000, 1400]:
    ts = []
    und = []
    for t in T:
        r = hi.loc[hi.t == t, 'R'].dropna()
        if P < r.quantile(.25):
            ts.append(t)
        elif P <= r.median():
            und.append(t)
    x = hi[hi.t.isin(ts)]
    print(f'P={P}: 偏低 {ts} 人数 {len(x):,} R {x.R.sum() / TR * 100:.2f}%｜不定 {und}')
# 卡5 中 R 在 [299, 301] 附近的人数（锚点贴边程度）
r5 = hi.loc[hi.t == '卡5', 'R']
print('卡5 R<300 比例 %.4f' % (r5 < 300).mean())
