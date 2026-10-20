"""Q66：推送诊断（D8 拆分与 U2 画像）。照设计卡 Q66 S1–S2、S5。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']
NOV = ['VIP', '黑名單']
APP = {'android', 'ios', 'apk'}


def prep(x):
    x = x.copy()
    x['last'] = pd.to_datetime(x['最後登入時間']).dt.normalize()
    x['reg'] = pd.to_datetime(x['注册时间'], errors='coerce').dt.normalize()
    x['days'] = (T0 - x['last']).dt.days
    x['tenure'] = (T0 - x['reg']).dt.days
    x['plat'] = x['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
    x['app'] = x['plat'].isin(APP)
    x['dep'] = pd.to_numeric(x['总充值金额'], errors='coerce').fillna(0)
    x['bet'] = pd.to_numeric(x['游戏总押注'], errors='coerce').fillna(0)
    x['lv'] = pd.to_numeric(x['会员等级'], errors='coerce')
    x['nov'] = ~x['身份'].isin(NOV)
    x['pp'] = (x['dep'] <= 0) & (x['bet'] > 10000)
    return x


ra = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
rc = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
a = prep(ra[~ra['身份'].isin(EX)])
c = prep(rc[~rc['身份'].isin(EX)])
L = c[~c['会员编号'].isin(a['会员编号'])].copy()
a['src'], L['src'] = '活跃', '离开'
U = pd.concat([a, L], ignore_index=True)
TU = U['dep'].sum()
U['tier'] = np.where(U['src'] == '离开', '离开', np.where(U['days'] >= 15, '15–31', np.where(U['days'] >= 8, '8–14', '0–7')))
D8 = U[U['tier'] != '0–7']
D1 = D8[(D8['卡别'] >= 3) & D8['nov']]
D2 = D8[(D8['src'] == '活跃') & (D8['reg'] >= '2026-08-18') & (D8['reg'] <= '2026-09-08') & (D8['last'] == D8['reg'])]
D3 = D8[(D8['src'] == '活跃') & (D8['身份'] == '回流')]
ov = set(D1['会员编号']) | set(D2['会员编号']) | set(D3['会员编号'])
UQ = D8[~D8['会员编号'].isin(ov)].copy()
print(f'D8 {len(D8):,}；D1 {len(D1)}；D2 {len(D2):,}；D3 {len(D3):,}；并集 {len(ov):,}；独有 {len(UQ):,}；合并储值 {TU:,.0f}')


def row(g, name):
    n = len(g)
    t = g['tier'].value_counts()
    print(f'  {name}: {n:,}｜8–14 {int(t.get("8–14", 0)):,}｜15–31 {int(t.get("15–31", 0)):,}｜离开 {int(t.get("离开", 0)):,}｜储值占合并 {g["dep"].sum() / TU * 100:.2f}%｜App {g["app"].mean() * 100 if n else 0:.2f}%')


print('\n===== S1 拆分')
row(D1, 'D1'); row(D2, 'D2'); row(D3, 'D3')
cal = UQ['last'] == UQ['reg']
U1a = UQ[(UQ['reg'] >= '2026-08-01') & (UQ['reg'] <= '2026-08-15') & cal]
U1b = UQ[(UQ['reg'] >= '2026-08-18') & (UQ['reg'] <= '2026-09-08') & ~cal]
new8 = UQ[UQ['reg'] >= '2026-08-01']
U1c = new8[~new8['会员编号'].isin(set(U1a['会员编号']) | set(U1b['会员编号']))]
U2 = UQ[UQ['reg'] < '2026-08-01'].copy()
UM = UQ[UQ['reg'].isna()]
for g, nm in [(U1a, 'U1a 8/1–8/15 注册只来当天'), (U1b, 'U1b 8/18–9/8 注册来过不止当天'), (U1c, 'U1c 其余 8/1 后注册'), (U2, 'U2 8/1 前注册'), (UM, '注册缺值'), (UQ, '独有合计')]:
    row(g, nm)
u1 = len(U1a) + len(U1b) + len(U1c)
print(f'  U1 合计 {u1:,}（占独有 {u1 / len(UQ) * 100:.2f}%）；8/1 后注册 {len(new8):,}')
print('  U1c 注册日范围', U1c['reg'].min(), U1c['reg'].max(), '；U1c 身份', U1c['身份'].value_counts().to_dict())
print('  U2 身份', U2['身份'].value_counts().to_dict(), '卡别', U2['卡别'].value_counts().sort_index().to_dict())

print('\n===== S2 U2 画像')
ref = a[(a['days'] <= 7) & (a['卡别'] == 1) & a['nov']].copy()
p25, p50 = ref['bet'].quantile(0.25), ref['bet'].quantile(0.5)
print(f'  参照组（0–7 天普卡非VIP）{len(ref):,}；押注 P25 {p25:,.0f}，P50 {p50:,.0f}')


def segs(g):
    return np.where(g['bet'] >= p50, '高', np.where(g['bet'] >= p25, '中', '低'))


U2['seg'] = segs(U2)
ref['seg'] = segs(ref)
for s in ['低', '中', '高']:
    x = U2[U2.seg == s]
    t = x['tier'].value_counts()
    print(f'  {s}: {len(x):,}（{len(x) / len(U2) * 100:.2f}%）｜8–14 {int(t.get("8–14", 0)):,} 15–31 {int(t.get("15–31", 0)):,} 离开 {int(t.get("离开", 0)):,}｜有储值率 {(x.dep > 0).mean() * 100:.2f}%｜潜在付费代理 {int(x.pp.sum()):,}｜App {x.app.mean() * 100:.2f}%')
print(f'  U2 押注中位 {U2.bet.median():,.0f}；独有全体押注中位 {UQ.bet.median():,.0f}')
for g in (U2, ref):
    g['tl'] = np.where(g['tenure'] > 365, '365 天以上', np.where(g['tenure'] >= 60, '60–365', '<60'))
for tl in ['365 天以上', '60–365', '<60']:
    x, r = U2[U2.tl == tl], ref[ref.tl == tl]
    hx = (x.seg == '高').mean() * 100 if len(x) else np.nan
    hr = (r.seg == '高').mean() * 100 if len(r) else np.nan
    print(f'  层 {tl}: U2 {len(x):,} 高段 {hx:.2f}%｜参照 {len(r):,} 高段 {hr:.2f}%｜差 {hx - hr:+.2f}')
print(f'  会员等级中位：U2 {U2.lv.median():.0f}，参照 {ref.lv.median():.0f}')
bpd = lambda g: (g['bet'] / g['tenure'].clip(lower=1)).median()
print(f'  押注÷注册天数 中位：U2 {bpd(U2):,.1f}，参照 {bpd(ref):,.1f}')

print('\n===== S5 回流存量（存在性迹象）')
rf = a[a['身份'] == '回流']
print(f'  回流 {len(rf):,}，其中 0–7 天 {int((rf.days <= 7).sum()):,}')
print(f'\n规则 4：D1 储值占 D8 储值 {D1["dep"].sum() / D8["dep"].sum() * 100:.2f}%')
