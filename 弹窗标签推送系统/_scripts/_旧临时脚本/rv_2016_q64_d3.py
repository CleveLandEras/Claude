"""审查 2026-09-28 20:16：独立复算 Q64（A17）关键数与环节2 D3 节新写入的数。只读，不带参数。"""
import numpy as np
import pandas as pd

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']

r = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = r[~r['身份'].isin(EX)].copy()
print('活跃剔除后', len(a))
a['lt'] = pd.to_datetime(a['最後登入時間'])
a['rt'] = pd.to_datetime(a['注册时间'], errors='coerce')
a['ld'] = a['lt'].dt.normalize()
a['rd'] = a['rt'].dt.normalize()
a['bet'] = pd.to_numeric(a['游戏总押注'], errors='coerce').fillna(0)
a['dep'] = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
a['card'] = pd.to_numeric(a['卡别'], errors='coerce')
a['days'] = (T0 - a['ld']).dt.days
print('注册时间缺值', int(a['rt'].isna().sum()))

N = a[(a.rd >= '2026-08-18') & (a.rd <= '2026-09-08')].copy()
N['cal'] = N.ld == N.rd
N['h24'] = (N['lt'] - N['rt']) < pd.Timedelta(hours=24)
N['h48'] = (N['lt'] - N['rt']) < pd.Timedelta(hours=48)
print('队列', len(N), '日历', int(N.cal.sum()), round(N.cal.mean() * 100, 2),
      '24h', int(N.h24.sum()), round(N.h24.mean() * 100, 2), '48h', int(N.h48.sum()), round(N.h48.mean() * 100, 2))
# 24h 口径下是否有人 cal=False 但 h24=True（跨零点）以及 cal=True 但 h24=False（不应有）
print('cal 真但 h24 假', int((N.cal & ~N.h24).sum()), '；h24 真但 cal 假', int((~N.cal & N.h24).sum()))
N['ten'] = (T0 - N.rd).dt.days
for lo, hi in [(8, 14), (15, 21), (22, 29)]:
    x = N[(N.ten >= lo) & (N.ten <= hi)]
    print(f'周 {lo}-{hi}: n={len(x)} cal {x.cal.mean()*100:.2f} h24 {x.h24.mean()*100:.2f} h48 {x.h48.mean()*100:.2f}')


def segs(x, nm):
    b = x.bet
    s = {'0': (b == 0), '1-1000': (b > 0) & (b <= 1000), '1001-1w': (b > 1000) & (b <= 10000),
         '1w-10w': (b > 10000) & (b <= 100000), '>10w': b > 100000}
    out = {k: (int(v.sum()), round(v.mean() * 100, 2)) for k, v in s.items()}
    low = (s['0'] | s['1-1000']).mean() * 100
    print(nm, len(x), out, '低两段合计', round(low, 2))


S = N[N.cal]
segs(S, '日历')
segs(N[N.h24], '24h')
segs(N[N.h48], '48h')
app = S['登入平台'].astype(str).str.strip().str.lower().isin(['android', 'ios', 'apk'])
segs(S[app], 'App')
segs(S[~app], '浏览器')
p = S[S.dep > 0]
print('有储值', len(p), '中位', p.dep.median(), '恰 50', int((p.dep == 50).sum()))

# 平台
Napp = N['登入平台'].astype(str).str.strip().str.lower().isin(['android', 'ios', 'apk'])
print('平台 App', int(Napp.sum()), round(N[Napp].cal.mean() * 100, 2), '浏览器', int((~Napp).sum()), round(N[~Napp].cal.mean() * 100, 2))

# 时段 24h
h = N.rt.dt.hour
for lo, hi in [(0, 5), (6, 11), (12, 17), (18, 23)]:
    x = N[(h >= lo) & (h <= hi)]
    print(f'时段 {lo}-{hi}: n={len(x)} 24h {x.h24.mean()*100:.2f} 日历 {x.cal.mean()*100:.2f}')

# 日期：原法 + 去掉随访梯度后的残差
day = N.groupby('rd').agg(n=('cal', 'size'), r=('cal', 'mean'), ten=('ten', 'first'))
p0 = N.cal.mean()
for lo, hi in [(8, 14), (15, 21), (22, 29)]:
    x = day[(day.ten >= lo) & (day.ten <= hi)]
    exp = np.sqrt(p0 * (1 - p0) / x.n.mean()) * 100
    print(f'周 {lo}-{hi}: sd {x.r.std()*100:.2f} exp {exp:.2f} 倍 {x.r.std()*100/exp:.2f} corr {x.n.corr(x.r):.2f}')
# 线性去随访梯度（全部 22 天，按人数加权）
w = day.n.values
X = np.vstack([np.ones(len(day)), day.ten.values]).T
W = np.diag(w)
beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ day.r.values)
res = day.r.values - X @ beta
exp_each = np.sqrt(p0 * (1 - p0) / day.n.values)
z = res / exp_each
print('随访梯度斜率（每天 pp）', round(beta[1] * 100, 3), '；残差 z 的标准差', round(z.std(ddof=2), 2), '；|z|>2 的日子',
      [(str(i.date())[5:], round(v, 2)) for i, v in zip(day.index, z) if abs(v) > 2])
# 偏高日子多出的人数（相对本周均值）
tot = 0
for d in ['2026-09-05', '2026-09-06', '2026-09-07', '2026-09-08', '2026-08-24']:
    row = day.loc[pd.Timestamp(d)]
    wk = day[(day.ten >= (8 if row.ten <= 14 else 22)) & (day.ten <= (14 if row.ten <= 14 else 29))]
    wm = (wk.r * wk.n).sum() / wk.n.sum()
    ex = row.n * (row.r - wm)
    tot += ex
    print(d[5:], int(row.n), round(row.r * 100, 1), '本周均值', round(wm * 100, 2), '多出', round(ex, 1))
print('偏高日子合计多出', round(tot, 1), '占 3,893', round(tot / 3893 * 100, 2), '%')

# 星期
wd = N.groupby(N.rd.dt.dayofweek).cal.agg(['size', 'mean'])
print('星期', {int(i): (int(v['size']), round(v['mean'] * 100, 2)) for i, v in wd.iterrows()})

# 第二批：8/1–8/15 合并口径
rc = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
c = rc[~rc['身份'].isin(EX)].copy()
c = c[~c['会员编号'].isin(a['会员编号'])]
U = pd.concat([r[~r['身份'].isin(EX)], c], ignore_index=True)
U['rd'] = pd.to_datetime(U['注册时间'], errors='coerce').dt.normalize()
U['ld'] = pd.to_datetime(U['最後登入時間']).dt.normalize()
Q = U[(U.rd >= '2026-08-01') & (U.rd <= '2026-08-15')]
Qa = Q['登入平台'].astype(str).str.strip().str.lower().isin(['android', 'ios', 'apk'])
Qc = Q.ld == Q.rd
print('第二批', len(Q), int(Qc.sum()), round(Qc.mean() * 100, 2), 'App', int(Qa.sum()), round(Qc[Qa].mean() * 100, 2),
      '浏览器', int((~Qa).sum()), round(Qc[~Qa].mean() * 100, 2))

# D3 回流数字
R = a[a['身份'] == '回流']
R8 = R.days >= 8
g = np.where(R.card >= 3, '金+', np.where(R.card == 2, '银', '普'))
print('回流', len(R), '≥8', int(R8.sum()))
for k in ['普', '银', '金+']:
    m = g == k
    print(k, int(m.sum()), int((R8 & m).sum()), round((R8 & m).sum() / m.sum() * 100, 2), '储值占回流',
          round(R.dep[m].sum() / R.dep.sum() * 100, 2))
C = a[a['身份'] == '持續']
print('持續普卡 ≥8', round((C[C.card == 1].days >= 8).mean() * 100, 2))
zz = R[(g == '普') & (R.dep == 0) & (R.bet == 0)]
print('普卡回流 从未储值 押注 0', len(zz), round((zz.days >= 8).mean() * 100, 2))
