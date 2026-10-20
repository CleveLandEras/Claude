"""R40 反例检查：卡别与最后登录的相关，有多少来自「玩得多（押注大）」本身？
做法：按累计押注分段（同 A3 表 8b / R35 的段），在同一押注段内比较卡组三档的 0–7 天登录比例；
反过来，在同一卡组内比较押注段之间的 0–7 天比例。再按累计储值分段做一遍（卡别部分按储值定级）。
最后登录按日期相减、9/16 记第 0 天（与 A8 一致）。不带参数运行，只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
for c in ['总充值金额', '游戏总押注', '卡别']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['总充值金额'] = df['总充值金额'].fillna(0)
df['游戏总押注'] = df['游戏总押注'].fillna(0)
df['卡组'] = np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上'))
ref = pd.Timestamp('2026-09-16')
df['距末登'] = (ref - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
df['近'] = df['距末登'] <= 7
print('剔除后', N, '0–7 天', int(df['近'].sum()), f'{df["近"].mean()*100:.2f}%')
print('押注空值', int(pd.to_numeric(pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'),
                                              encoding='utf-8-sig')['游戏总押注'], errors='coerce').isna().sum()))

bet_bins = [-np.inf, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000, np.inf]
bet_lab = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
df['押注段'] = pd.cut(df['游戏总押注'], bins=bet_bins, labels=bet_lab, right=True)
pay_bins = [-np.inf, 0, 1_000, 10_000, 100_000, np.inf]
pay_lab = ['≤0', '1–1千', '1千–1万', '1万–10万', '>10万']
df['储值段'] = pd.cut(df['总充值金额'], bins=pay_bins, labels=pay_lab, right=True)
groups = ['普卡', '银卡', '金卡以上']


def table(seg, labs, title):
    print(f'\n== {title}：同一段内，卡组三档的 0–7 天比例（人数） ==')
    for l in labs:
        s = df[df[seg] == l]
        parts = []
        for g in groups:
            t = s[s['卡组'] == g]
            if len(t):
                parts.append(f'{g} {t["近"].mean()*100:.2f}%（{int(t["近"].sum())}/{len(t)}）')
            else:
                parts.append(f'{g} -（0）')
        print(f'  [{l}] 段内 {len(s)} 人，段内全体 {s["近"].mean()*100:.2f}%；' + '；'.join(parts))
    print(f'\n== {title}：同一卡组内，各段的 0–7 天比例 ==')
    for g in groups:
        s = df[df['卡组'] == g]
        parts = []
        for l in labs:
            t = s[s[seg] == l]
            if len(t):
                parts.append(f'{l} {t["近"].mean()*100:.2f}%（{int(t["近"].sum())}/{len(t)}）')
        print(f'  [{g}] ' + '；'.join(parts))


table('押注段', bet_lab, '按累计押注分段')
table('储值段', pay_lab, '按累计储值分段')

# 直接标准化：用全部人的押注段分布为权重，算各卡组「押注构成拉平后」的 0–7 天比例
print('\n== 直接标准化（权重 = 全部 62,292 人的押注段分布；卡组某段为空时该段不计并重归一）==')
w_all = df['押注段'].value_counts(normalize=True).reindex(bet_lab)
for g in groups:
    s = df[df['卡组'] == g]
    r = s.groupby('押注段', observed=False)['近'].mean().reindex(bet_lab)
    ok = r.notna()
    std = (r[ok] * w_all[ok]).sum() / w_all[ok].sum()
    print(f'  {g}：原始 {s["近"].mean()*100:.2f}%，按全体押注构成标准化 {std*100:.2f}%（有效段 {int(ok.sum())}）')
# 以金卡以上的押注构成为权重，看普卡、银卡若押注构成与金卡以上相同时的比例
print('\n== 反向标准化（权重 = 金卡以上 6,366 人的押注段分布）==')
w_hi = df[df['卡组'] == '金卡以上']['押注段'].value_counts(normalize=True).reindex(bet_lab)
print('  金卡以上押注段分布', {k: f'{v*100:.2f}%' for k, v in w_hi.items()})
for g in groups:
    s = df[df['卡组'] == g]
    r = s.groupby('押注段', observed=False)['近'].mean().reindex(bet_lab)
    ok = r.notna() & (w_hi > 0)
    std = (r[ok] * w_hi[ok]).sum() / w_hi[ok].sum()
    print(f'  {g}：按金卡以上押注构成标准化 {std*100:.2f}%')

# 金卡以上内部，押注段与 0–7 天
print('\n== 各卡组押注中位数 ==')
print(df.groupby('卡组')['游戏总押注'].median().reindex(groups).round(0).to_dict())
