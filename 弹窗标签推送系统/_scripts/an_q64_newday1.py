"""Q64：新增只来注册当天（D2）。照设计卡 Q64 S1–S3。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']
APP = {'android', 'ios', 'apk'}
BRW = {'mweb', 'web', 'h5', 'mh5'}


def prep(x):
    x = x.copy()
    x['lastts'] = pd.to_datetime(x['最後登入時間'])
    x['regts'] = pd.to_datetime(x['注册时间'], errors='coerce')
    x['last'] = x['lastts'].dt.normalize()
    x['reg'] = x['regts'].dt.normalize()
    x['tenure'] = (T0 - x['reg']).dt.days
    x['plat'] = x['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
    x['pcls'] = np.where(x['plat'].isin(APP), 'App', np.where(x['plat'].isin(BRW), '浏览器', '缺值'))
    x['dep'] = pd.to_numeric(x['总充值金额'], errors='coerce').fillna(0)
    x['bet'] = pd.to_numeric(x['游戏总押注'], errors='coerce').fillna(0)
    x['act'] = pd.to_numeric(x['活动赠点'], errors='coerce').fillna(0)
    x['bon'] = pd.to_numeric(x['充值赠点'], errors='coerce').fillna(0)
    x['cal'] = x['last'] == x['reg']
    x['h24'] = (x['lastts'] - x['regts']) < pd.Timedelta(hours=24)
    x['h48'] = (x['lastts'] - x['regts']) < pd.Timedelta(hours=48)
    return x


ra = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = prep(ra[~ra['身份'].isin(EX)])
N = a[(a['reg'] >= '2026-08-18') & (a['reg'] <= '2026-09-08')].copy()
print('满 8 天注册队列', len(N), '；身份', N['身份'].value_counts().to_dict())

print('\n===== S1 三个口径 × 注册周')
N['wk'] = pd.cut(N['tenure'], [7, 14, 21, 29], labels=['8–14', '15–21', '22–29']).astype(str)
for w in ['全部', '8–14', '15–21', '22–29']:
    x = N if w == '全部' else N[N.wk == w]
    print(f'  {w}: n={len(x):,}｜日历 {int(x.cal.sum()):,}（{x.cal.mean() * 100:.2f}%）｜24h {int(x.h24.sum()):,}（{x.h24.mean() * 100:.2f}%）｜48h {int(x.h48.sum()):,}（{x.h48.mean() * 100:.2f}%）')

S = N[N.cal].copy()
Rt = N[~N.cal].copy()
bins = [-1, 0, 1000, 10000, 100000, 1e18]
labs = ['0', '1–1,000', '1,001–1 万', '1 万–10 万', '10 万以上']
for x in (S, Rt):
    x['bb'] = pd.cut(x['bet'], bins, labels=labs).astype(str)


def seg(x, name):
    print(f'  {name}（n={len(x):,}）')
    for b in labs:
        g = x[x.bb == b]
        if len(g) == 0:
            print(f'    {b}: 0')
            continue
        print(f'    {b}: {len(g):,}（{len(g) / len(x) * 100:.2f}%）｜赠点=1,000 {(g.act == 1000).mean() * 100:.2f}%｜有储值 {int((g.dep > 0).sum())}｜储值=50 {int((g.dep == 50).sum())}')
    z = x[x.bb.isin(['0', '1–1,000'])]
    print(f'    押注 0 与 1–1,000 合计 {len(z):,}（{len(z) / len(x) * 100:.2f}%）')


print('\n===== S2 只来当天者走到哪一步（日历口径 3,893 内部）')
seg(S, '全部')
seg(S[S.pcls == 'App'], 'App 类')
seg(S[S.pcls == '浏览器'], '浏览器类')
p = S[S.dep > 0]
print(f'  有储值 {len(p)}，储值中位 {p.dep.median():,.0f}；储值=50 {int((p.dep == 50).sum())}（16,800 点 {int(((p.dep == 50) & (p.bon == 16800)).sum())}、15,000 点 {int(((p.dep == 50) & (p.bon == 15000)).sum())}）')
for k, nm in [(N[N.h24], '24h 口径'), (N[N.h48], '48h 口径')]:
    k = k.copy()
    k['bb'] = pd.cut(k['bet'], bins, labels=labs).astype(str)
    zz = k[k.bb.isin(['0', '1–1,000'])]
    print(f'  敏感性 {nm}: n={len(k):,}，押注 0 与 1–1,000 合计 {len(zz) / len(k) * 100:.2f}%')
print('  背景（回来过的 3,821 人，不能比）：', {b: int((Rt.bb == b).sum()) for b in labs})

print('\n===== S3 注册前就定下的因素')
p0 = N.cal.mean()
day = N.groupby('reg').agg(n=('cal', 'size'), r=('cal', 'mean'), wk=('wk', 'first'))
for w in ['8–14', '15–21', '22–29']:
    x = day[day.wk == w]
    exp = np.sqrt(p0 * (1 - p0) / x.n.mean()) * 100
    sd = x.r.std() * 100
    print(f'  周 {w}: 天数 {len(x)}，日比例 {x.r.min() * 100:.1f}%–{x.r.max() * 100:.1f}%，标准差 {sd:.2f} pp，期望波动 {exp:.2f} pp，倍数 {sd / exp:.2f}，日均 {x.n.mean():.0f}；周内相关（人数 vs 比例）{x.n.corr(x.r):.2f}')
print(f'  全部日：标准差 {day.r.std() * 100:.2f} pp，人数与比例相关 {day.n.corr(day.r):.2f}')
print('  逐日（注册日, 人数, 比例）:', [(str(i.date())[5:], int(r.n), round(r.r * 100, 1)) for i, r in day.iterrows()])
N['wd'] = N['reg'].dt.dayofweek
wd = N.groupby('wd')['cal'].agg(['size', 'mean'])
print('  星期（0=一）:', {int(i): (int(r['size']), round(r['mean'] * 100, 2)) for i, r in wd.iterrows()})
N['hb'] = pd.cut(N['regts'].dt.hour, [-1, 5, 11, 17, 23], labels=['0–5', '6–11', '12–17', '18–23']).astype(str)
hb = N.groupby('hb').agg(n=('h24', 'size'), h24=('h24', 'mean'), cal=('cal', 'mean'))
print('  时段（24h 口径 / 日历对照）:', {i: (int(r.n), round(r.h24 * 100, 2), round(r.cal * 100, 2)) for i, r in hb.iterrows()})
pc = N.groupby('pcls').agg(n=('cal', 'size'), cal=('cal', 'mean'), h24=('h24', 'mean'))
print('  平台类:', {i: (int(r.n), round(r.cal * 100, 2), round(r.h24 * 100, 2)) for i, r in pc.iterrows()})
pl = N.groupby('plat').agg(n=('cal', 'size'), cal=('cal', 'mean'))
print('  平台:', {i: (int(r.n), round(r.cal * 100, 2) if r.n >= 30 else '—') for i, r in pl.iterrows()})

print('\n===== 第二批复核：8/1–8/15 注册队列（合并口径）')
rc = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
c = prep(rc[~rc['身份'].isin(EX)])
L = c[~c['会员编号'].isin(a['会员编号'])]
U = pd.concat([a, L], ignore_index=True)
Q = U[(U['reg'] >= '2026-08-01') & (U['reg'] <= '2026-08-15')]
print(f'  队列 {len(Q):,}，只来当天 {int(Q.cal.sum()):,}（{Q.cal.mean() * 100:.2f}%）')
q = Q.groupby('pcls')['cal'].agg(['size', 'mean'])
print('  平台类:', {i: (int(r['size']), round(r['mean'] * 100, 2)) for i, r in q.iterrows()})
