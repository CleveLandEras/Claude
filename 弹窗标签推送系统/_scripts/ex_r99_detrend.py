"""R99 复算：注册日期偏高日子相对本周均值多出的人数；按人数加权去随访梯度后的标准化残差。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']

ra = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = ra[~ra['身份'].isin(EX)].copy()
a['last'] = pd.to_datetime(a['最後登入時間']).dt.normalize()
a['reg'] = pd.to_datetime(a['注册时间'], errors='coerce').dt.normalize()
a['tenure'] = (T0 - a['reg']).dt.days
N = a[(a['reg'] >= '2026-08-18') & (a['reg'] <= '2026-09-08')].copy()
N['cal'] = N['last'] == N['reg']
N['wk'] = pd.cut(N['tenure'], [7, 14, 21, 29], labels=['8–14', '15–21', '22–29']).astype(str)
print('队列', len(N), '只来当天', int(N.cal.sum()))

day = N.groupby('reg').agg(n=('cal', 'size'), k=('cal', 'sum'), r=('cal', 'mean'), wk=('wk', 'first'), t=('tenure', 'first'))
wkmean = N.groupby('wk')['cal'].mean()
day['wkm'] = day['wk'].map(wkmean)
day['excess'] = day['k'] - day['n'] * day['wkm']
high = ['2026-09-05', '2026-09-06', '2026-09-07', '2026-09-08', '2026-08-24']
print('\n周均值', {k: round(v * 100, 2) for k, v in wkmean.items()})
tot = 0
for d in high:
    r = day.loc[pd.Timestamp(d)]
    tot += r.excess
    print(f'  {d[5:]} n={int(r.n)} 比例 {r.r * 100:.1f}% 周均 {r.wkm * 100:.2f}% 多出 {r.excess:.1f}')
print(f'  合计多出 {tot:.1f} 人，占 3,893 的 {tot / N.cal.sum() * 100:.2f}%')
print(f'  对照（旧写法）：比全队列均值 {N.cal.mean() * 100:.2f}% 高', [round((day.loc[pd.Timestamp(d)].r - N.cal.mean()) * 100, 1) for d in high])

# 按人数加权线性去梯度
w = day['n'].values
x = day['t'].values.astype(float)
y = day['r'].values
X = np.vstack([np.ones_like(x), x]).T
W = np.diag(w)
beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
fit = X @ beta
se = np.sqrt(fit * (1 - fit) / w)
z = (y - fit) / se
day['fit'] = fit
day['z'] = z
day['excess_dt'] = day['k'] - day['n'] * fit
print(f'\n加权回归：截距 {beta[0] * 100:.2f}%，斜率 {beta[1] * 100:.3f} pp / 天（注册距今每多 1 天）')
print(f'  标准化残差标准差 {np.std(z, ddof=1):.2f}；|z|>2：', [(str(i.date())[5:], round(v, 2)) for i, v in day['z'].items() if abs(v) > 2])
print('  偏高五日 z：', [(d[5:], round(day.loc[pd.Timestamp(d)].z, 2)) for d in high])
print(f'  偏高五日去梯度后多出合计 {sum(day.loc[pd.Timestamp(d)].excess_dt for d in high):.1f} 人')
print('  z 最大三日：', [(str(i.date())[5:], round(v, 2)) for i, v in day['z'].sort_values(ascending=False).head(3).items()])
