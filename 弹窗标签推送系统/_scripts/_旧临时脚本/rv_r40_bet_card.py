"""审查复算：A8 表 3（卡组 × 押注段 × 0–7 天登录），独立写法：日期取字符串前 10 位，分段用显式比较。
另算：两种标准化（全体权重、金卡以上权重）、各段两两差距、储值分段全表。只读。"""
import os
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
print('剔除后', len(df))
card = pd.to_numeric(df['卡别'], errors='coerce')
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
pay = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
d = pd.to_datetime(df['最後登入時間'].astype(str).str[:10], errors='coerce')
gap = (pd.Timestamp('2026-09-16') - d).dt.days
near = gap <= 7
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
G = ['普卡', '银卡', '金卡以上']
for col, name in [('b', '押注段'), ('p', '储值段')]:
    print(f'\n== {name} ==')
    for k, s in t.groupby(col):
        row = [f'{k} n={len(s)} 全体 {s.near.mean()*100:.2f}%']
        for g in G:
            u = s[s.g == g]
            row.append(f'{g} {int(u.near.sum())}/{len(u)}' + (f'={u.near.mean()*100:.2f}%' if len(u) else ''))
        print('  ' + '；'.join(row))

print('\n全体 0-7:', {g: f'{t[t.g==g].near.mean()*100:.2f}%' for g in G})
print('押注中位:', t.groupby('g').bet.median().to_dict())
for g in G:
    print(g, '押注段分布', (t[t.g == g].b.value_counts(normalize=True).sort_index() * 100).round(2).to_dict())

rate = t.groupby(['g', 'b']).near.mean().unstack()
cnt = t.groupby(['g', 'b']).size().unstack().fillna(0)
for wname, w in [('全体', t.b.value_counts(normalize=True)), ('金卡以上', t[t.g == '金卡以上'].b.value_counts(normalize=True))]:
    out = {}
    for g in G:
        r = rate.loc[g]
        ok = r.notna() & w.reindex(r.index).fillna(0).gt(0)
        ww = w.reindex(r.index)[ok]
        out[g] = f'{(r[ok]*ww).sum()/ww.sum()*100:.2f}%'
    print(f'标准化（权重={wname}）', out)
print('\n格人数\n', cnt)
