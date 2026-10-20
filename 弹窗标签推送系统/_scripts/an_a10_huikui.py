"""Q31 / A10：储值回馈比的口径验证与礼包指纹。
数据：数据/近一月活跃_20260916.csv；剔除機器人、測試帳號后 62,292 人。
只描述，不评价礼包好坏。
"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N 全体', len(d))
d['amt'] = d['总充值金额']
d['r'] = d['储值回馈比']
pay = d[d['amt'] > 0].copy()
print('N 有储值 (>0)', len(pay))

print('\n==== ① 口径验证 ====')
print('回馈比缺值（全体）', d['r'].isna().sum(), ' 有储值者中缺值', pay['r'].isna().sum())
print('从未储值者回馈比取值 top', d[d['amt'] <= 0]['r'].round(2).value_counts(dropna=False).head(5).to_dict())
pay['calc'] = pay['充值赠点'] / pay['amt']
k = (pay['r'] / pay['calc']).replace([np.inf, -np.inf], np.nan)
print('r / (充值赠点/总充值) 分位数', k.quantile([0, .01, .05, .5, .95, .99, 1]).round(4).to_dict())
print('相关系数 r vs 充值赠点/总充值', round(pay[['r', 'calc']].corr().iloc[0, 1], 6))
kk = k.median()
resid = (pay['r'] - pay['calc'] * kk).abs()
print('按中位比例换算后 |残差| ≤ 0.5 的占比', round((resid <= 0.5).mean(), 4), ' 分母', resid.notna().sum())
print('充值赠点 = 0 的有储值者', int((pay['充值赠点'] == 0).sum()), ' 这些人的 r top', pay[pay['充值赠点'] == 0]['r'].round(1).value_counts().head(5).to_dict())
# 活动赠点是否混入
pay['calc2'] = (pay['充值赠点'] + pay['活动赠点']) / pay['amt']
print('相关系数 r vs (充值+活动赠点)/总充值', round(pay[['r', 'calc2']].corr().iloc[0, 1], 6))
print('r 描述（有储值者）', pay['r'].describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).round(2).to_dict())
print('r < 99.5 的人数', int((pay['r'] < 99.5).sum()), ' r 在 [99.5,100.5] 的人数', int(pay['r'].between(99.5, 100.5).sum()),
      ' 占比', round(pay['r'].between(99.5, 100.5).mean() * 100, 2))
print('r 恰好 100（round 2）', int((pay['r'].round(2) == 100).sum()))
low = pay[pay['r'] < 99.5]
print('r<99.5 的储值额 top', low['amt'].round(0).value_counts().head(8).to_dict(), ' 身份', low['身份'].value_counts().to_dict())
print('r<99.5 的 r 分位', low['r'].quantile([0, .25, .5, .75, 1]).round(2).to_dict())

print('\n==== ② 固定档位指纹：总充值金额 × 回馈比（round 0）人数最多的组合 ====')
pay['a0'] = pay['amt'].round(2)
pay['r0'] = pay['r'].round(0)
combo = pay.groupby(['a0', 'r0']).size().sort_values(ascending=False)
print(combo.head(40).to_string())
print('\n储值额（精确）人数 top 20')
print(pay['a0'].value_counts().head(20).to_string())
for v in [30, 50, 70, 100, 150, 200, 300, 500, 1000]:
    s = pay[pay['a0'] == v]
    if len(s):
        vc = s['r0'].value_counts()
        print(f'储值 {v}: n={len(s)}  回馈比 top', vc.head(6).to_dict(), ' 该额最常见回馈比占比', round(vc.iloc[0] / len(s) * 100, 2))
for rv in [300, 336, 333, 200, 250, 150]:
    s = pay[pay['r0'] == rv]
    print(f'回馈比≈{rv}: n={len(s)}  储值额 top', s['a0'].value_counts().head(6).to_dict())
# 回馈比恰好 300 的精确值
s300 = pay[pay['r'].round(2) == 300]
print('回馈比 = 300.00（round 2）人数', len(s300), ' 储值额', s300['a0'].value_counts().to_dict())
s50 = pay[pay['a0'] == 50]
print('储值=50 的 回馈比（round 2）top', s50['r'].round(2).value_counts().head(10).to_dict())
s70 = pay[pay['a0'] == 70]
print('储值=70 的 回馈比（round 2）top', s70['r'].round(2).value_counts().head(8).to_dict())
s30 = pay[pay['a0'] == 30]
print('储值=30 的 回馈比（round 2）top', s30['r'].round(2).value_counts().head(8).to_dict())
# 组合 50 + x 的推测：储值=50 回馈比 336：赠点 = 336*50/100 = 168 NT 等值？ 检查 50=?
# 储值额是 50 的倍数且回馈比一致的档位检查
print('\n储值 ≤ 200 的精确储值额分布（人数≥30）')
vc = pay[pay['a0'] <= 200]['a0'].value_counts()
print(vc[vc >= 30].sort_index().to_string())

print('\n==== ③ 只买过首储礼包的下界：储值=50 且 回馈比=300 ====')
fb = pay[(pay['a0'] == 50) & (pay['r'].round(0) == 300)].copy()
N = len(d); NP = len(pay)
print('下界人数', len(fb), ' 占全体', round(len(fb) / N * 100, 2), ' 占有储值者', round(len(fb) / NP * 100, 2),
      ' 占累计储值', round(fb['amt'].sum() / pay['amt'].sum() * 100, 4))

ref = pd.Timestamp('2026-09-16')
d['last'] = pd.to_datetime(d['最後登入時間'], errors='coerce')
d['days'] = (ref.normalize() - d['last'].dt.normalize()).dt.days
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce')
d['regdays'] = (ref.normalize() - d['reg'].dt.normalize()).dt.days
d['cardg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
plat = d['登入平台'].astype(str).str.lower()
d['platg'] = np.where(plat.isin(['android', 'ios', 'apk']), 'App类', np.where(plat.isin(['web', 'mweb', 'mh5', 'h5']), '浏览器类', '缺值'))  # 与 A9 口径一致：浏览器类 = web/Web、mweb、mh5、h5
d['dayg'] = pd.cut(d['days'], [-1, 7, 14, 31, 10000], labels=['0–7天', '8–14天', '15–31天', '>31天'])
d['regg'] = pd.cut(d['regdays'], [-1, 29, 90, 365, 1e6], labels=['≤29天', '30–90天', '91–365天', '>1年'])

d['grp'] = '其他有储值'
d.loc[d['amt'] <= 0, 'grp'] = '从未储值（其余）'
d.loc[(d['amt'] <= 0) & (d['游戏总押注'] > 10000), 'grp'] = '潜在付费代理'
d.loc[d.index.isin(fb.index), 'grp'] = '只买首储（下界）'
print('分组人数', d['grp'].value_counts().to_dict())
print('平台原值（全体）', d['登入平台'].value_counts(dropna=False).to_dict())

def dist(col):
    t = pd.crosstab(d['grp'], d[col], normalize='index').mul(100).round(2)
    n = d['grp'].value_counts()
    t['分母'] = n
    print(f'\n-- {col} 分布（行 %）--')
    print(t.to_string())

for c in ['身份', 'cardg', 'platg', 'dayg', 'regg']:
    dist(c)

print('\n-- 押注、赠点、会员等级（中位数 / 分位）--')
g = d.groupby('grp')
print(g['游戏总押注'].describe(percentiles=[.25, .5, .75]).round(0).to_string())
print(g['会员等级'].median().to_string())
print('押注 > 1万 占比', g.apply(lambda x: round((x['游戏总押注'] > 10000).mean() * 100, 2)).to_dict())
print('押注 > 10万 占比', g.apply(lambda x: round((x['游戏总押注'] > 100000).mean() * 100, 2)).to_dict())
print('活动赠点中位', g['活动赠点'].median().round(0).to_dict())
# 首储下界的注册日 与 最后登录 关系：新增是否买完就走
fbd = d[d['grp'] == '只买首储（下界）']
print('下界内 新增者 0–7天占比', round((fbd[fbd['身份'] == '新增']['days'] <= 7).mean() * 100, 2), ' n', int((fbd['身份'] == '新增').sum()))

print('\n==== 敏感度：储值=50 各回馈比的结构 ====')
d['a0'] = d['amt'].round(2); d['r0'] = d['r'].round(0)
s50all = d[d['a0'] == 50]
for rv, s in s50all.groupby('r0'):
    if len(s) >= 20:
        print(f'储值50 回馈比{rv}: n={len(s)} 身份', s['身份'].value_counts().to_dict(), ' 普卡%', round((s['卡别'] == 1).mean() * 100, 1),
              ' 押注中位', int(s['游戏总押注'].median()))

print('\n==== ④ 按储值额分段的回馈比 ====')
pay = d[d['amt'] > 0].copy()
pay['seg'] = pd.cut(pay['amt'], [0, 100, 500, 1000, 5000, 20000, 1e12], labels=['1–100', '101–500', '501–1千', '1千–5千', '5千–2万', '>2万'])
t = pay.groupby('seg', observed=True).agg(n=('r', 'size'), 中位数=('r', 'median'),
                                          p25=('r', lambda x: x.quantile(.25)), p75=('r', lambda x: x.quantile(.75)),
                                          ge150=('r', lambda x: round((x >= 150).mean() * 100, 2)),
                                          le100=('r', lambda x: round((x <= 100.5).mean() * 100, 2)))
print(t.round(2).to_string())
t2 = pay.groupby('身份').agg(n=('r', 'size'), 中位数=('r', 'median'), p25=('r', lambda x: x.quantile(.25)), p75=('r', lambda x: x.quantile(.75)),
                             mn=('r', 'min'), mx=('r', 'max'),
                             ge150=('r', lambda x: round((x >= 150).mean() * 100, 2)),
                             le100=('r', lambda x: round((x <= 100.5).mean() * 100, 2)))
print(t2.round(2).to_string())
t3 = pay.groupby('cardg').agg(n=('r', 'size'), 中位数=('r', 'median'),
                              ge150=('r', lambda x: round((x >= 150).mean() * 100, 2)),
                              le100=('r', lambda x: round((x <= 100.5).mean() * 100, 2)))
print(t3.round(2).to_string())
print('全体有储值 ≥150 占比', round((pay['r'] >= 150).mean() * 100, 2), ' ≤100.5 占比', round((pay['r'] <= 100.5).mean() * 100, 2), ' 中位', pay['r'].median())
# 新增内部：按储值分段
nw = pay[pay['身份'] == '新增']
print('新增有储值中储值恰为 50 的占比', round((nw['a0'] == 50).mean() * 100, 2), ' 50&300 占比', round(((nw['a0'] == 50) & (nw['r0'] == 300)).mean() * 100, 2))

print('\n==== ⑤ 固定档位的平台、身份结构 ====')
tiers = {'50@300': (50, 300), '70@200': (70, 200), '30@333': (30, 333), '33@303': (33, 303), '50@336': (50, 336),
         '30@100': (30, 100), '30@108': (30, 108), '50@100': (50, 100), '60@104': (60, 104)}
for name, (a, rv) in tiers.items():
    s = pay[(pay['a0'] == a) & (pay['r0'] == rv)]
    pl = s['登入平台'].astype(str).str.lower().value_counts()
    print(f'{name}: n={len(s)} 浏览器类%', round((s['platg'] == '浏览器类').mean() * 100, 1), ' 平台', pl.head(6).to_dict(), ' 身份', s['身份'].value_counts().to_dict(),
          ' 普卡%', round((s['卡别'] == 1).mean() * 100, 1), ' 押注中位', int(s['游戏总押注'].median()),
          ' 0–7天%', round((s['days'] <= 7).mean() * 100, 1))

print('\n==== ⑥ 组合解码：若回馈比 = 各档赠送倍数按金额加权，则组合的回馈比可预测 ====')
# 单位检验：赠点 / (储值 × 100) 与 r 的关系
pay['unit'] = pay['充值赠点'] / (pay['amt'] * 100) * 100
print('充值赠点/(储值×100)×100 的中位 / r 中位（50@300 组）',
      pay[(pay['a0'] == 50) & (pay['r0'] == 300)]['unit'].median(), pay[(pay['a0'] == 50) & (pay['r0'] == 300)]['r'].median())
print('50@300 组 充值赠点 取值 top', pay[(pay['a0'] == 50) & (pay['r0'] == 300)]['充值赠点'].value_counts().head(3).to_dict())
print('70@200 组 充值赠点 取值 top', pay[(pay['a0'] == 70) & (pay['r0'] == 200)]['充值赠点'].value_counts().head(3).to_dict())
print('30@333 组 充值赠点 取值 top', pay[(pay['a0'] == 30) & (pay['r0'] == 333)]['充值赠点'].value_counts().head(3).to_dict())
print('33@303 组 充值赠点 取值 top', pay[(pay['a0'] == 33) & (pay['r0'] == 303)]['充值赠点'].value_counts().head(3).to_dict())
print('30@100 组 充值赠点 取值 top', pay[(pay['a0'] == 30) & (pay['r0'] == 100)]['充值赠点'].value_counts().head(3).to_dict())
print('30@108 组 充值赠点 取值 top', pay[(pay['a0'] == 30) & (pay['r0'] == 108)]['充值赠点'].value_counts().head(3).to_dict())
print('50@100 组 充值赠点 取值 top', pay[(pay['a0'] == 50) & (pay['r0'] == 100)]['充值赠点'].value_counts().head(3).to_dict())
print('50@336 组 充值赠点 取值 top', pay[(pay['a0'] == 50) & (pay['r0'] == 336)]['充值赠点'].value_counts().head(3).to_dict())
combos = {'50@300+70@200': (120, (50 * 300 + 70 * 200) / 120),
          '50@300+30@333': (80, (50 * 300 + 30 * 333.33) / 80),
          '30@333+70@200': (100, (30 * 333.33 + 70 * 200) / 100),
          '50@300+70@200+30@333': (150, (50 * 300 + 70 * 200 + 30 * 333.33) / 150),
          '50@300+33@303': (83, (50 * 300 + 33 * 303) / 83)}
for name, (a, rexp) in combos.items():
    s = pay[pay['a0'] == a]
    hit = s[(s['r'] - rexp).abs() <= 1.5]
    print(f'{name}: 储值={a} 预测回馈比 {rexp:.2f}  该储值额 n={len(s)}  命中（±1.5）{len(hit)}  命中者 r 取值',
          hit['r'].round(1).value_counts().head(4).to_dict())
# 首储下界 + 可解码组合 合计
dec = pay[((pay['a0'] == 120) & ((pay['r'] - 241.67).abs() <= 1.5)) | ((pay['a0'] == 80) & ((pay['r'] - 312.5).abs() <= 1.5)) |
          ((pay['a0'] == 150) & ((pay['r'] - 260).abs() <= 1.5)) | ((pay['a0'] == 83) & ((pay['r'] - 301.2).abs() <= 1.5))]
print('含首储的可解码组合合计', len(dec), ' 加下界后', len(dec) + 523)
print('\n==== ⑦ 回馈比是否 = floor(充值赠点 / 储值)（整数，向下取整）====')
fl = np.floor(pay['充值赠点'] / pay['amt'] + 1e-9)
print('r == floor(赠点/储值) 的占比', round((pay['r'] == fl).mean() * 100, 3), ' 分母', len(pay),
      ' r 为整数的占比', round((pay['r'] == pay['r'].round(0)).mean() * 100, 3))
print('不相等者 r - floor 的取值 top', (pay['r'] - fl)[pay['r'] != fl].round(2).value_counts().head(5).to_dict())
# 按精确赠点（老币）解码：首储（50 元、15,000）+ 一个已知固定档位
known = {'70@200（70 元、14,000）': (70, 14000), '30@333（30 元、10,000）': (30, 10000), '33@303（33 元、10,000）': (33, 10000),
         '30@100（30 元、3,000）': (30, 3000), '30@108（30 元、3,240）': (30, 3240)}
tot = 0
for name, (a, c) in known.items():
    s = pay[(pay['amt'].round(2) == 50 + a) & (pay['充值赠点'].round(0) == 15000 + c)]
    tot += len(s)
    print(f'首储 + {name}: 储值 {50 + a}、赠点 {15000 + c}  命中 {len(s)}')
s3 = pay[(pay['amt'].round(2) == 150) & (pay['充值赠点'].round(0) == 39000)]
print('首储 + 70@200 + 30@333: 命中', len(s3))
print('首储 + 一个已知档位 合计（精确赠点）', tot, ' 下界 523 + 该合计 =', 523 + tot)
# 同样方法看不含首储的组合，作为方法对照：70@200 + 30@333
s4 = pay[(pay['amt'].round(2) == 100) & (pay['充值赠点'].round(0) == 24000)]
print('对照：70@200 + 30@333（100 元、24,000）命中', len(s4))
# 首储档位在「储值恰为 50」之外是否可能以其他形式出现：赠点恰为 15,000 的人的储值额
print('充值赠点恰为 15,000 的人的储值额 top', pay[pay['充值赠点'].round(0) == 15000]['amt'].round(0).value_counts().head(6).to_dict())

# 储值≤100 且 回馈比 ≥ 150：高赠送的小额储值者规模
sm = pay[(pay['amt'] <= 100)]
print('储值≤100 人数', len(sm), ' 其中 r≥150', int((sm['r'] >= 150).sum()), ' 其中落在 50@300/70@200/30@333/33@303 四档',
      int(sum(((sm['a0'] == a) & (sm['r0'] == rv)).sum() for a, rv in [(50, 300), (70, 200), (30, 333), (33, 303)])))
print('新增有储值', len(nw), ' 其中储值=50', int((nw['a0'] == 50).sum()), ' 储值=50&r=300', int(((nw['a0'] == 50) & (nw['r0'] == 300)).sum()))
