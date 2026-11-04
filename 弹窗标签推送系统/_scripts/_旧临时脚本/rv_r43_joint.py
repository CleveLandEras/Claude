"""审查复算：储值分段内各卡组的押注中位数；押注段 × 储值段双重分层下普卡与金卡以上的 0–7 天比例。只读。"""
import os
import pandas as pd

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
card = pd.to_numeric(df['卡别'], errors='coerce')
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
pay = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
d = pd.to_datetime(df['最後登入時間'].astype(str).str[:10], errors='coerce')
near = (pd.Timestamp('2026-09-16') - d).dt.days <= 7
grp = pd.Series('金卡以上', index=df.index)
grp[card == 1] = '普卡'
grp[card == 2] = '银卡'


def bband(x):
    if x <= 1e4: return '1≤1万'
    if x <= 1e5: return '21万-10万'
    if x <= 1e6: return '310万-1百万'
    if x <= 1e7: return '41百万-1千万'
    if x <= 1e8: return '51千万-1亿'
    return '6>1亿'


def pband(x):
    if x <= 0: return '1≤0'
    if x <= 1e3: return '21-1千'
    if x <= 1e4: return '31千-1万'
    if x <= 1e5: return '41万-10万'
    return '5>10万'


t = pd.DataFrame({'g': grp, 'near': near, 'b': bet.map(bband), 'p': pay.map(pband), 'bet': bet})
print('== 储值段内各卡组押注中位数与押注超过 1 千万占比 ==')
for p, s in t.groupby('p'):
    for g in ['普卡', '银卡', '金卡以上']:
        u = s[s.g == g]
        if len(u):
            print(f'  {p} {g} n={len(u)} 押注中位={u.bet.median():,.0f} 押注>1千万占比={(u.bet > 1e7).mean()*100:.2f}%')

print('\n== 押注段 × 储值段，普卡与金卡以上都 ≥ 30 人的格 ==')
for (b, p), s in t.groupby(['b', 'p']):
    a = s[s.g == '普卡']
    c = s[s.g == '金卡以上']
    if len(a) >= 30 and len(c) >= 30:
        print(f'  {b} × {p}：普卡 {int(a.near.sum())}/{len(a)}={a.near.mean()*100:.2f}%；金卡以上 {int(c.near.sum())}/{len(c)}={c.near.mean()*100:.2f}%；差 {(c.near.mean()-a.near.mean())*100:.2f}')

print('\n== 押注段 × 储值段，普卡与银卡都 ≥ 30 人的格 ==')
for (b, p), s in t.groupby(['b', 'p']):
    a = s[s.g == '普卡']
    c = s[s.g == '银卡']
    if len(a) >= 30 and len(c) >= 30:
        print(f'  {b} × {p}：普卡 {a.near.mean()*100:.2f}%（{len(a)}）；银卡 {c.near.mean()*100:.2f}%（{len(c)}）；差 {(c.near.mean()-a.near.mean())*100:.2f}')
