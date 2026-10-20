"""Q16：高卡流失风险（D1）。照设计卡 Q16 S1–S4 与推进计划提醒 25。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']
NOV = ['VIP', '黑名單']
APP = {'android', 'ios', 'apk'}


def prep(d):
    d = d.copy()
    d['last'] = pd.to_datetime(d['最後登入時間']).dt.normalize()
    d['days'] = (T0 - d['last']).dt.days
    d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
    d['app'] = d['plat'].isin(APP)
    d['dep'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
    d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
    d['nov'] = ~d['身份'].isin(NOV)
    d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
    return d


ra = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
rc = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
a = prep(ra[~ra['身份'].isin(EX)])
c = prep(rc[~rc['身份'].isin(EX)])
L = c[~c['会员编号'].isin(a['会员编号'])].copy()
TA = a['dep'].sum()
TU = TA + L['dep'].sum()
a['tier'] = pd.cut(a['days'], [-1, 0, 3, 7, 14, 31], labels=['0', '1–3', '4–7', '8–14', '15–31']).astype(str)
L['tier'] = '32–46'
a['src'], L['src'] = '活跃', '离开'
U = pd.concat([a, L], ignore_index=True)
TIERS = ['0', '1–3', '4–7', '8–14', '15–31', '32–46']
WID = {'0': 1, '1–3': 3, '4–7': 4, '8–14': 7, '15–31': 17, '32–46': 15}


def pct(x, d):
    return f'{x / d * 100:.2f}%'


print('===== S1 暴露')
g_all = a[a['cg'] == '金卡以上']
g = g_all[g_all['nov']]
print(f'  含VIP {len(g_all):,} / 储值占活跃 {pct(g_all["dep"].sum(), TA)}；主数 {len(g):,} / {pct(g["dep"].sum(), TA)}；占不含VIP总额 {pct(g["dep"].sum(), a.loc[a["nov"], "dep"].sum())}')
G = U[(U['cg'] == '金卡以上') & U['nov']]
print(f'  合并口径金卡以上主数 {len(G):,}，储值 {G["dep"].sum():,.0f}（占合并 {pct(G["dep"].sum(), TU)}）')

print('\n===== S2 六档')
rows = []
for t in TIERS:
    x = G[G['tier'] == t]
    p = x[x['dep'] > 0]
    s = x['dep'].sum()
    rows.append({
        '档': t, '人数': len(x), '日均': round(len(x) / WID[t], 1),
        '储值占活跃': pct(s, TA) if t != '32–46' else '—', '储值占合并': pct(s, TU),
        '有储值者中位': round(p['dep'].median(), 1) if len(p) else None,
        '前10占本档': f'{x["dep"].nlargest(10).sum() / s * 100:.2f}%' if s > 0 else '-',
        '卡3/4/5/6/7': '/'.join(str(int((x['卡别'] == k).sum())) for k in range(3, 8)),
        '持續/回流/新增': '/'.join(str(int((x['身份'] == k).sum())) for k in ['持續', '回流', '新增']),
        'App%': f'{x["app"].mean() * 100:.2f}%',
    })
print(pd.DataFrame(rows).to_string(index=False))

R = G[G['tier'].isin(['8–14', '15–31', '32–46'])]
Rs = R['dep'].sum()
print(f'\n风险层 {len(R):,} 人，储值 {Rs:,.0f}（占合并 {pct(Rs, TU)}；占金卡以上合并储值 {pct(Rs, G["dep"].sum())}）')
srt = R['dep'].sort_values(ascending=False).values
for k in (10, 50, 100, 200):
    print(f'  前 {k} 人占风险层储值 {srt[:k].sum() / Rs * 100:.2f}%')
print(f'  去掉前 10 人后 {Rs - srt[:10].sum():,.0f}（占合并 {pct(Rs - srt[:10].sum(), TU)}）')
cum = np.cumsum(srt) / Rs
for q in (0.5, 0.8, 0.9):
    print(f'  占风险层储值 {int(q * 100)}% 需要 {int(np.searchsorted(cum, q) + 1)} 人')
print(f'  风险层有储值 {int((R["dep"] > 0).sum())}，储值 ≥ 1 万 {int((R["dep"] >= 10000).sum())}，≥ 10 万 {int((R["dep"] >= 100000).sum())}')
print(f'  离开者占风险层人数 {pct(int((R["src"] == "离开").sum()), len(R))}，占风险层储值 {pct(R.loc[R["src"] == "离开", "dep"].sum(), Rs)}')
pR = R[R['dep'] > 0]['dep'].median()
p0 = G[(G['tier'].isin(['0', '1–3', '4–7'])) & (G['dep'] > 0)]['dep'].median()
print(f'  有储值者中位：风险层 {pR:,.1f}；0–7 天 {p0:,.1f}；差 {(pR / p0 - 1) * 100:.1f}%')

print('\n===== 卡别内风险率（分母 = 该卡别在合并口径主数中的人数）')
for k in range(3, 8):
    x = G[G['卡别'] == k]
    r = x['tier'].isin(['8–14', '15–31', '32–46'])
    rn = int(r.sum())
    ex_share = len(x) / len(G) * 100
    rk_share = rn / len(R) * 100
    print(f'  卡别 {k}: 人数 {len(x):,}｜风险 {rn}｜风险率 {rn / len(x) * 100:.2f}%｜占风险层人数 {rk_share:.2f}% vs 占金卡以上 {ex_share:.2f}%（差 {rk_share - ex_share:+.2f}）｜占风险层储值 {pct(x.loc[r, "dep"].sum(), Rs)}')
for cg in ['普卡', '银卡']:
    x = U[(U['cg'] == cg) & U['nov']]
    r = x['tier'].isin(['8–14', '15–31', '32–46'])
    print(f'  对照 {cg}: 人数 {len(x):,}｜风险 {int(r.sum()):,}｜风险率 {r.mean() * 100:.2f}%')
print(f'  金卡以上合计风险率 {len(R) / len(G) * 100:.2f}%')

print('\n===== S3 储值衰退上限')
print(f'  有储值的金卡以上（主数）{int((g["dep"] > 0).sum()):,}（含VIP {int((g_all["dep"] > 0).sum()):,}）')

print('\n===== S4 够得着')
act = R[R['src'] == '活跃']
print(f'  弹窗（活跃部分）{len(act):,}；推播上界 App 类 {int(R["app"].sum())}（{pct(int(R["app"].sum()), len(R))}）；离开者 App {int(L.loc[L.index.isin(R.index) & False, "app"].sum()) if False else int(R.loc[R["src"] == "离开", "app"].sum())}/{int((R["src"] == "离开").sum())}')
top100 = R.sort_values('dep', ascending=False).head(100)
print(f'  储值前 100 人：离开 {int((top100["src"] == "离开").sum())}，App {int(top100["app"].sum())}，卡别', top100['卡别'].value_counts().sort_index().to_dict(), '，档', top100['tier'].value_counts().to_dict())

print('\n===== 重叠')
print(f'  回流 {int((R["身份"] == "回流").sum())}，新增 {int((R["身份"] == "新增").sum())}')
