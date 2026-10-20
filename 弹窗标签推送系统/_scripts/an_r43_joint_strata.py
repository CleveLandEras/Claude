"""R43：押注段 × 储值段双重分层，比较卡组之间的 0–7 天登录比例（A8 表 3c）。不带参数运行，只读。
口径与 an_r40_card_bet_recency.py 相同：剔除機器人、測試帳號；最后登录按日期相减、9/16 为第 0 天；
押注段、储值段切分与 A8 表 3 一致。门槛：比较的两组各不少于 30 人才报差距。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
for c in ['总充值金额', '游戏总押注', '卡别']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['总充值金额'] = df['总充值金额'].fillna(0)
df['游戏总押注'] = df['游戏总押注'].fillna(0)
df['卡组'] = np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上'))
df['距末登'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(df['最後登入時間'].astype(str).str[:10])).dt.days
df['近'] = df['距末登'] <= 7
print('剔除后', len(df))

bet_bins = [-np.inf, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000, np.inf]
bet_lab = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
pay_bins = [-np.inf, 0, 1_000, 10_000, 100_000, np.inf]
pay_lab = ['≤0', '1–1千', '1千–1万', '1万–10万', '>10万']
df['押注段'] = pd.cut(df['游戏总押注'], bins=bet_bins, labels=bet_lab)
df['储值段'] = pd.cut(df['总充值金额'], bins=pay_bins, labels=pay_lab)

print('\n== 储值分段内各卡组的押注（说明储值分段未控制押注）==')
for p in pay_lab[:3]:
    s = df[df['储值段'] == p]
    for g in ['普卡', '金卡以上']:
        t = s[s['卡组'] == g]
        print(f'  [{p}] {g} {len(t)} 人，押注中位 {t["游戏总押注"].median():,.0f}，押注 > 1 千万 {(t["游戏总押注"] > 1e7).mean()*100:.2f}%')

MIN = 30


def cmp(a, b):
    print(f'\n== 双重分层：{a} 对 {b}（两边都 ≥ {MIN} 人才列）==')
    rows = []
    for bl in bet_lab:
        for pl in pay_lab:
            s = df[(df['押注段'] == bl) & (df['储值段'] == pl)]
            x, y = s[s['卡组'] == a], s[s['卡组'] == b]
            if len(x) >= MIN and len(y) >= MIN:
                ra, rb = x['近'].mean() * 100, y['近'].mean() * 100
                rows.append((bl, pl, ra, int(x['近'].sum()), len(x), rb, int(y['近'].sum()), len(y), rb - ra))
                print(f'  [{bl} × {pl}] {a} {ra:.2f}%（{int(x["近"].sum())}/{len(x)}） {b} {rb:.2f}%（{int(y["近"].sum())}/{len(y)}） 差 {rb - ra:.2f}')
    if rows:
        # 按两边人数的调和权重合并的加权平均差（Mantel-Haenszel 风险差）
        num = sum((r[5] / 100 - r[2] / 100) * r[4] * r[7] / (r[4] + r[7]) for r in rows)
        den = sum(r[4] * r[7] / (r[4] + r[7]) for r in rows)
        print(f'  合并（MH 加权风险差，{len(rows)} 格）：{num / den * 100:.2f} 个百分点')
        keep = [r for r in rows if r[0] not in ('1千万–1亿', '>1亿')]
        if keep and len(keep) < len(rows):
            num = sum((r[5] / 100 - r[2] / 100) * r[4] * r[7] / (r[4] + r[7]) for r in keep)
            den = sum(r[4] * r[7] / (r[4] + r[7]) for r in keep)
            print(f'  去掉普卡押注过千万的格后（{len(keep)} 格）：{num / den * 100:.2f} 个百分点')


cmp('普卡', '金卡以上')
cmp('普卡', '银卡')
cmp('银卡', '金卡以上')
