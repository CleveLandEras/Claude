"""Q13 / A3 回流与潜在付费画像。不带参数运行，只读。
① 回流画像：卡别构成、储值率、有储值者储值额分布、注册年限、最后登录间隔，并与持续（含 VIP、黑名单）、新增对照；
② 从未储值者按累计押注 >1 千、>1 万、>5 万、>10 万分身份计数，并按最后登录间隔拆分（弹窗只在登录时出现）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
raw = len(df)
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
print('原始', raw, '剔除后', N)

pay = '总充值金额'
bet = '游戏总押注'
df[pay] = pd.to_numeric(df[pay], errors='coerce').fillna(0)
df[bet] = pd.to_numeric(df[bet], errors='coerce').fillna(0)
df['身份3'] = df['身份'].replace({'VIP': '持續', '黑名單': '持續'})
card = {1: '普卡', 2: '银卡', 3: '金卡', 4: '白金卡', 5: '钻石卡', 6: '黑卡', 7: '至尊卡'}
df['卡别名'] = df['卡别'].map(card)
df['卡组'] = np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上'))
df['付费'] = df[pay] > 0
ref = pd.Timestamp('2026-09-16')
df['注册天数'] = (ref - pd.to_datetime(df['注册时间'], errors='coerce').dt.normalize()).dt.days
df['距末登'] = (ref - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
TOTAL = df[pay].sum()
ids = ['回流', '持續', '新增']


def pct(a, b):
    return f'{a / b * 100:.2f}%' if b else '—'


print('\n== ① 回流画像 ==')
for k in ids:
    s = df[df['身份3'] == k]
    print(f'\n-- {k}：{len(s)} 人，储值率 {pct(s["付费"].sum(), len(s))}（{int(s["付费"].sum())}），'
          f'累计储值占比 {pct(s[pay].sum(), TOTAL)}，人均 {s[pay].sum() / len(s):.1f}')
    vc = s['卡组'].value_counts()
    print('卡组构成（分母该身份人数）：', {c: f'{vc.get(c, 0)}（{pct(vc.get(c, 0), len(s))}）' for c in ['普卡', '银卡', '金卡以上']})
    # 各卡组储值率与储值占比（占该身份总额）
    for c in ['普卡', '银卡', '金卡以上']:
        g = s[s['卡组'] == c]
        print(f'   {c}：储值率 {pct(g["付费"].sum(), len(g))}，占该身份储值 {pct(g[pay].sum(), s[pay].sum())}')

print('\n== 有储值者储值额档（分母：该身份有储值人数） ==')
bins = [0, 50, 200, 1000, 10000, float('inf')]
labs = ['1–50', '51–199', '200–999', '1,000–9,999', '≥10,000']
p = df[df['付费']].copy()
p['档'] = pd.cut(p[pay], bins=[0, 50.0001, 199.9999, 999.9999, 9999.9999, float('inf')], labels=labs)
for k in ids:
    s = p[p['身份3'] == k]
    vc = s['档'].value_counts().reindex(labs, fill_value=0)
    print(k, len(s), {l: f'{vc[l]}（{pct(vc[l], len(s))}）' for l in labs},
          '中位', round(s[pay].median()), 'P75', round(s[pay].quantile(.75)), 'P90', round(s[pay].quantile(.9)))

print('\n== 注册年限（分母：该身份注册时间非空人数） ==')
tb = [-1, 29, 90, 365, 1095, 1e6]
tl = ['30天内', '30–90天', '91–365天', '1–3年', '>3年']
df['注册档'] = pd.cut(df['注册天数'], bins=tb, labels=tl)
for k in ids:
    s = df[(df['身份3'] == k) & df['注册天数'].notna()]
    vc = s['注册档'].value_counts().reindex(tl, fill_value=0)
    print(k, len(s), {l: f'{vc[l]}（{pct(vc[l], len(s))}）' for l in tl})

print('\n== 最后登录间隔（分母：该身份人数；0 = 9/16 当天） ==')
rb = [-1, 0, 3, 7, 14, 31]
rl = ['当天', '1–3天', '4–7天', '8–14天', '15–31天']
df['末登档'] = pd.cut(df['距末登'], bins=rb, labels=rl)
for k in ids:
    s = df[df['身份3'] == k]
    vc = s['末登档'].value_counts().reindex(rl, fill_value=0)
    print(k, len(s), {l: f'{vc[l]}（{pct(vc[l], len(s))}）' for l in rl}, '空', int(s['距末登'].isna().sum()))

print('\n== 回流：储值与否 × 最后登录（分母：回流中该组人数） ==')
r = df[df['身份3'] == '回流']
for f, name in [(True, '有储值'), (False, '从未储值')]:
    s = r[r['付费'] == f]
    vc = s['末登档'].value_counts().reindex(rl, fill_value=0)
    print(name, len(s), {l: f'{vc[l]}（{pct(vc[l], len(s))}）' for l in rl})

print('\n== 回流：押注分布（分母：回流人数） ==')
for th in [0, 1000, 10000, 50000, 100000]:
    print(f'押注>{th}', int((r[bet] > th).sum()), pct((r[bet] > th).sum(), len(r)))
print('回流 押注中位', round(r[bet].median()), '持续', round(df[df['身份3'] == '持續'][bet].median()),
      '新增', round(df[df['身份3'] == '新增'][bet].median()))
print('活动赠点>0 比例', {k: pct((df[df['身份3'] == k]['活动赠点'] > 0).sum(), (df['身份3'] == k).sum()) for k in ids})

print('\n== 回流 × 注册年限：储值率（分母：该格人数） ==')
for l in tl:
    s = r[r['注册档'] == l]
    print(l, len(s), pct(s['付费'].sum(), len(s)), '人均', round(s[pay].sum() / len(s), 1) if len(s) else '—')

print('\n== ② 从未储值 × 累计押注（分母：该身份从未储值人数） ==')
np_ = df[~df['付费']]
print('从未储值合计', len(np_), {k: int((np_['身份3'] == k).sum()) for k in ids})
for th in [1000, 10000, 50000, 100000]:
    row = {}
    for k in ids:
        s = np_[np_['身份3'] == k]
        row[k] = f'{int((s[bet] > th).sum())}（{pct((s[bet] > th).sum(), len(s))}）'
    tot = int((np_[bet] > th).sum())
    print(f'押注>{th:,}', row, '合计', tot, pct(tot, len(np_)))

print('\n== ② 从未储值且押注>1万：卡组与最后登录（分母：该组人数） ==')
q = np_[np_[bet] > 10000]
print('人数', len(q), '卡组', q['卡组'].value_counts().to_dict())
vc = q['末登档'].value_counts().reindex(rl, fill_value=0)
print({l: f'{vc[l]}（{pct(vc[l], len(q))}）' for l in rl})
print('7 天内登录', int((q['距末登'] <= 7).sum()), pct((q['距末登'] <= 7).sum(), len(q)))
for k in ids:
    s = q[q['身份3'] == k]
    print(k, len(s), '7 天内登录', int((s['距末登'] <= 7).sum()), pct((s['距末登'] <= 7).sum(), len(s)))
print('押注中位（从未储值且>1万）', round(q[bet].median()))
print('\n== 对照：有储值者押注中位 / 从未储值押注中位 ==', round(p[bet].median()), round(np_[bet].median()))
print('从未储值且押注>1万 的 RTP 中位', round(q['RTP'].median(), 4) if 'RTP' in q else '—',
      '活动赠点>0', pct((q['活动赠点'] > 0).sum(), len(q)))
