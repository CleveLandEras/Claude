"""Q11：环节2 问题清单的三层规模（暴露 / 风险 / 够得着）与初排。照设计卡 Q11 S2、S3。只读，不带参数。"""
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
    d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
    d['days'] = (T0 - d['last']).dt.days
    d['tenure'] = (T0 - d['reg']).dt.days
    d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
    d['app'] = d['plat'].isin(APP)
    d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
    d['dep'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
    d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
    d['pp'] = (d['dep'] <= 0) & (d['bet'] > 10000)
    d['nov'] = ~d['身份'].isin(NOV)
    return d


ra = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
rc = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
a = prep(ra[~ra['身份'].isin(EX)])
c = prep(rc[~rc['身份'].isin(EX)])
L = c[~c['会员编号'].isin(a['会员编号'])].copy()
a['src'] = '活跃'
L['src'] = '离开'
U = pd.concat([a, L], ignore_index=True)
TA = a['dep'].sum()
TU = U['dep'].sum()
TA_nov = a.loc[a['nov'], 'dep'].sum()
print('活跃', len(a), '离开者', len(L), '合并', len(U))
print(f'储值合计 活跃 {TA:,.0f}  合并 {TU:,.0f}  活跃不含VIP黑名单 {TA_nov:,.0f}')
print('VIP+黑名单 活跃', int((~a['nov']).sum()), '离开者', int((~L['nov']).sum()), '离开者身份', L['身份'].value_counts().to_dict())


def pct(x, d):
    return f'{x / d * 100:.2f}%'


def layer(name, g, tot=TA, totname='活跃'):
    n = len(g)
    s = g['dep'].sum()
    act = int((g['src'] == '活跃').sum())
    app = g['app'].mean() * 100 if n else 0
    top10 = g['dep'].nlargest(10).sum() / s * 100 if s > 0 else 0
    print(f'  {name}: 人数 {n:,}｜储值 {s:,.0f}（占{totname} {pct(s, tot)}）｜弹窗够得着(活跃部分) {act:,}（{pct(act, n) if n else "-"}）｜推播上界 App 类 {app:.2f}%（{int(g["app"].sum()):,} 人）｜前10人占本层储值 {top10:.2f}%')
    return dict(n=n, s=s, act=act, app=app)


R = {}
print('\n===== D1 高卡流失（金卡以上，主数剔除 VIP、黑名单）')
e1 = a[(a['cg'] == '金卡以上') & a['nov']]
e1v = a[a['cg'] == '金卡以上']
print(f'  暴露 主数 {len(e1):,}（占 62,292 {pct(len(e1), len(a))}），储值占活跃 {pct(e1["dep"].sum(), TA)}；含VIP {len(e1v):,} / {pct(e1v["dep"].sum(), TA)}')
r1a = a[(a['cg'] == '金卡以上') & a['nov'] & (a['days'] >= 8)]
r1L = L[(L['cg'] == '金卡以上') & L['nov']]
r1 = pd.concat([r1a, r1L])
print(f'  活跃 ≥8 天 {len(r1a):,}（含VIP {int(((a["cg"] == "金卡以上") & (a["days"] >= 8)).sum()):,}），离开者 {len(r1L):,}（含VIP {int((L["cg"] == "金卡以上").sum()):,}）')
R['D1'] = layer('风险层（活跃≥8天+离开者）', r1, TU, '合并')
print(f'  其中活跃部分储值占活跃 {pct(r1a["dep"].sum(), TA)}；离开者部分储值占合并 {pct(r1L["dep"].sum(), TU)}')
r1v = pd.concat([a[(a['cg'] == '金卡以上') & (a['days'] >= 8)], L[L['cg'] == '金卡以上']])
print(f'  含VIP对照：人数 {len(r1v):,}，储值占合并 {pct(r1v["dep"].sum(), TU)}')

print('\n===== D2 新增只来注册当天')
nw = a[a['身份'] == '新增']
print(f'  暴露 新增 {len(nw):,}（{pct(len(nw), len(a))}），储值占活跃 {pct(nw["dep"].sum(), TA)}')
n8 = nw[nw['tenure'] >= 8]
r2 = n8[n8['last'] == n8['reg']]
print(f'  注册满 8 天 {len(n8):,}，只来当天 {len(r2):,}（{pct(len(r2), len(n8))}）；最后登录天数最小 {r2["days"].min()}')
R['D2'] = layer('风险层', r2)

print('\n===== D3 回流 ≥8 天未登录')
rf = a[a['身份'] == '回流']
print(f'  暴露 回流 {len(rf):,}（{pct(len(rf), len(a))}），储值占活跃 {pct(rf["dep"].sum(), TA)}')
r3 = rf[rf['days'] >= 8]
R['D3'] = layer('风险层', r3)
print(f'  占回流 {pct(len(r3), len(rf))}；对照：持續（同为活跃文件）≥8 天占持續 {pct(int(((a["身份"] == "持續") & (a["days"] >= 8)).sum()), int((a["身份"] == "持續").sum()))}')

print('\n===== D4a 有储值、不在首储买家下界里（上界）')
pay = a[a['dep'] > 0]
payn = pay[pay['nov']]
print(f'  有储值 {len(pay):,}（主数剔除VIP黑名单 {len(payn):,}）；上界 {len(pay) - 129:,} / {len(pay) - 652:,}；剔除后 {len(payn) - 129:,} / {len(payn) - 652:,}（129、652 未按 VIP 拆，按原数减）')
print(f'  储值占活跃（仅体量参照）{pct(pay["dep"].sum(), TA)}；剔除VIP {pct(payn["dep"].sum(), TA)}')

print('\n===== D4b 从未储值中 0–7 天登录')
nev = a[(a['dep'] <= 0) & a['nov']]
nevv = a[a['dep'] <= 0]
print(f'  暴露 从未储值 主数 {len(nev):,}（含VIP {len(nevv):,}，{pct(len(nevv), len(a))}）')
r4b = nev[nev['days'] <= 7]
R['D4b'] = layer('风险层', r4b)
print(f'  其中潜在付费代理 {int(r4b["pp"].sum()):,}；全体潜在付费上限 {int(a["pp"].sum()):,}')

print('\n===== D5 条件式：普卡、银卡 0–7 天登录')
r5 = a[a['cg'].isin(['普卡', '银卡']) & a['nov'] & (a['days'] <= 7)]
e5 = a[a['cg'].isin(['普卡', '银卡']) & a['nov']]
print(f'  暴露 普银 主数 {len(e5):,}（{pct(len(e5), len(a))}）；若不跳过 风险层 {len(r5):,}；若跳过 0')

print('\n===== D8 沉默与离开（合并口径 74,480，含 VIP）')
r8a = a[a['days'] >= 8]
r8 = pd.concat([r8a, L])
print(f'  活跃≥8天 {len(r8a):,} + 离开者 {len(L):,}')
R['D8'] = layer('风险层', r8, TU, '合并')
r8p = r8[r8['dep'] > 0]
print(f'  有储值部分 {len(r8p):,} 人，储值占合并 {pct(r8p["dep"].sum(), TU)}')
r8n = r8[r8['nov']]
print(f'  剔除VIP黑名单对照 {len(r8n):,}，储值占合并 {pct(r8n["dep"].sum(), TU)}')

print('\n===== 重叠（人数）')
ids = {k: set(v['会员编号']) for k, v in {'D1': r1, 'D2': r2, 'D3': r3, 'D4b': r4b, 'D8': r8}.items()}
ks = list(ids)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        x = len(ids[ks[i]] & ids[ks[j]])
        if x:
            print(f'  {ks[i]} ∩ {ks[j]} = {x:,}')

uni = ids['D1'] | ids['D2'] | ids['D3']
only8 = r8[~r8['会员编号'].isin(uni)]
print(f'  D1∪D2∪D3 = {len(uni):,}；D8 独有 {len(only8):,}')
print('  D8 独有 身份', only8['身份'].value_counts().to_dict())
print('  D8 独有 卡组', only8['cg'].value_counts().to_dict(), '来源', only8['src'].value_counts().to_dict())
print(f'  D8 独有 储值占合并 {pct(only8["dep"].sum(), TU)}')

print('\n===== 初排（判读规则 1–7）')
people = {'D1': R['D1']['n'], 'D2': R['D2']['n'], 'D3': R['D3']['n'], 'D4b': R['D4b']['n'], 'D8': R['D8']['n']}
money = {'D1': R['D1']['s'] / TU, 'D8': R['D8']['s'] / TU}  # R91：两项同为全体口径（含负值行）
pr = sorted(people, key=lambda k: -people[k])
mr = sorted(money, key=lambda k: -money[k])
print('  人数榜', [(k, people[k]) for k in pr])
print('  储值榜（合并口径分母）', [(k, f'{money[k] * 100:.2f}%') for k in mr])
for top in (2, 3, 4):
    first = sorted({k for k in pr[:top]} | {k for k in mr[:top]})
    print(f'  前 {top} 为第一档：', first)
