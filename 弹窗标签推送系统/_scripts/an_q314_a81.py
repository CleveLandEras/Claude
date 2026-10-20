# Q314 / A81：潜在付费、潜在流失新定义下的本地规模、画像、重叠；V2 依据复算
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
import numpy as np

P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
snap = pd.Timestamp('2026-09-16 23:59:59')
df['reg'] = pd.to_datetime(df['注册时间'], errors='coerce')
df['last'] = pd.to_datetime(df['最後登入時間'], errors='coerce')
df['regd'] = (snap.normalize() - df['reg'].dt.normalize()).dt.days
df['lastd'] = (snap.normalize() - df['last'].dt.normalize()).dt.days
bet = df['游戏总押注']
never = df['总充值金额'] <= 0
pay = ~never
N = len(df)
print('分母 N =', N, '；注册时间缺失', df['reg'].isna().sum(), '；总充值<0 的行', (df['总充值金额'] < 0).sum())
print('身份分布', df['身份'].value_counts().to_dict())
print('从未储值（总充值<=0）', never.sum(), f'{never.mean():.2%}')

print('\n== 一、潜在付费：V2 当前版（近14天登录>=4天且近14天押注>=20,000）与上午版（>140,000）==')
for thr in [20000, 70000, 140000, 280000]:
    up14 = never & (bet >= thr) & (df['lastd'] <= 14)
    up7 = never & (bet >= thr) & (df['lastd'] <= 7)
    low13 = never & (bet >= thr) & (df['regd'] <= 13)
    low14 = never & (bet >= thr) & (df['regd'] <= 14)
    # 登录>=4 天：注册 regd 天（含当日 regd+1 个自然日）至少要 >=4 日才可能
    low13_l = low13 & (df['regd'] >= 3)
    allbet = never & (bet >= thr)
    print(f'门槛 {thr:>7,}: 从未储值且累计押注达标 {allbet.sum()}；上界(最后登录<=14天) {up14.sum()}；其中<=7天 {up7.sum()}；'
          f'注册<=13天(押注精确) {low13.sum()}，其中注册>=3天(才可能登录>=4天) {low13_l.sum()}；注册<=14天 {low14.sum()}')

print('\n条件(c)：注册<=13天 从未储值 押注>140,000 与 日均>1万 两写法')
r13 = df['regd'] <= 13
for name, d in [('注册天数+1', df['regd'] + 1), ('注册天数(下限1)', df['regd'].clip(lower=1))]:
    a = (r13 & never & (bet > 140000)).sum()
    b = (r13 & never & (bet / d > 10000)).sum()
    print(f'  日均口径={name}: 14天合计>140,000 {a}；日均>1万 {b}')

print('\n== 二、V2 依据复算 ==')
# 7-14天
for lo, hi in [(7, 14), (7, 13)]:
    s = (df['regd'] >= lo) & (df['regd'] <= hi) & never
    b = bet[s]
    print(f'注册{lo}-{hi}天未付费 {s.sum()}：押注中位数 {b.median():.0f}，P75 {b.quantile(.75):.0f}，>=20,000 {(b>=20000).sum()} ({(b>=20000).mean():.2%})，>=140,000 {(b>=140000).sum()} ({(b>=140000).mean():.2%})，>140,000 {(b>140000).sum()}')
# 14天内 付费 vs 未付费，日均>1万
snapf = pd.Timestamp('2026-09-16 23:59:59')
frac = (snapf - df['reg']).dt.total_seconds() / 86400
r = df['regd'] <= 13
print('注册<=13天：未付费', (r & never).sum(), '付费', (r & pay).sum())
print('  注册>=7且<=13天', ((df['regd'] >= 7) & r & never).sum())
for name, d in [('快照-注册小数天', frac), ('注册天数(下限1)', df['regd'].clip(lower=1)), ('注册天数+1', df['regd'] + 1)]:
    m = bet / d > 10000
    print(f'  日均>1万[{name}]: 未付费 {(r & never & m).sum()}/{(r & never).sum()} = {(r & never & m).sum()/(r & never).sum():.2%}；付费 {(r & pay & m).sum()}/{(r & pay).sum()} = {(r & pay & m).sum()/(r & pay).sum():.2%}')
print('  押注>140,000 占比：未付费', f'{(r & never & (bet>140000)).sum()}/{(r&never).sum()}', f'{(r & never & (bet>140000)).sum()/(r&never).sum():.2%}',
      '付费', f'{(r & pay & (bet>140000)).sum()}/{(r&pay).sum()}', f'{(r & pay & (bet>140000)).sum()/(r&pay).sum():.2%}')
print('  押注>=20,000 占比：未付费', f'{(r & never & (bet>=20000)).sum()}/{(r&never).sum()}', f'{(r & never & (bet>=20000)).sum()/(r&never).sum():.2%}',
      '付费', f'{(r & pay & (bet>=20000)).sum()}/{(r&pay).sum()}', f'{(r & pay & (bet>=20000)).sum()/(r&pay).sum():.2%}')
s714 = (df['regd'] >= 7) & (df['regd'] <= 14) & never
print('  注册7–14天未付费中押注>=140,000 占比（V2 说 4.88%）', f'{(bet[s714]>=140000).sum()}/{s714.sum()} = {(bet[s714]>=140000).mean():.2%}；>140,000: {(bet[s714]>140000).mean():.2%}')

print('\n== 三、画像：以 V2 当前版上界(从未储值、押注>=20,000、最后登录<=14天) 对比 近一月活跃其余人 ==')
U = never & (bet >= 20000) & (df['lastd'] <= 14)
R = ~U
print('U =', U.sum(), f'{U.mean():.2%}')
print('卡别构成（U / 其余）')
ct = pd.crosstab(df['卡别'], U, normalize='columns').round(4)
print(ct)
print('身份构成（U / 其余）')
print(pd.crosstab(df['身份'], U, normalize='columns').round(4))
print('身份计数 U', df.loc[U, '身份'].value_counts().to_dict())
print('注册天数 分档 U / 其余')
bins = [-1, 7, 14, 28, 90, 365, 10 ** 6]
lab = ['<=7', '8-14', '15-28', '29-90', '91-365', '>365']
print(pd.crosstab(pd.cut(df['regd'], bins, labels=lab), U, normalize='columns').round(4))
print('注册天数中位数 U', df.loc[U, 'regd'].median(), '其余', df.loc[R, 'regd'].median())
print('近7天登录率 U', f'{(df.loc[U,"lastd"]<=7).mean():.2%}', '其余', f'{(df.loc[R,"lastd"]<=7).mean():.2%}')
for c in ['活动赠点', '充值赠点', '游戏总输赢', 'RTP']:
    print(f'中位数 {c}: U {df.loc[U,c].median():.2f} 其余 {df.loc[R,c].median():.2f}')
# 同口径：140,000 版
U140 = never & (bet > 140000) & (df['lastd'] <= 14)
print('\nU140 =', U140.sum(), '身份', df.loc[U140, '身份'].value_counts().to_dict(), '卡别', df.loc[U140, '卡别'].value_counts().to_dict())

print('\n== 四、潜在流失候选池 ==')
pool = (df['lastd'] <= 7) & (df['regd'] >= 28)
print('近7天有登录', (df['lastd'] <= 7).sum(), '；候选池(近7天有登录且注册>=28天)', pool.sum(), f'{pool.sum()/N:.2%} of {N}')
print('候选池身份', df.loc[pool, '身份'].value_counts().to_dict())
print('候选池中 从未储值', (pool & never).sum(), '有储值', (pool & pay).sum())
print('近7天有登录但注册<28天（按定义不可能命中）', ((df['lastd'] <= 7) & (df['regd'] < 28)).sum())
print('近7天有登录且注册>=28 的 身份=新增', ((df['身份'] == '新增') & pool).sum(), '回流', ((df['身份'] == '回流') & pool).sum())
print('新增 总', (df['身份'] == '新增').sum(), '其中注册>=28天', ((df['身份'] == '新增') & (df['regd'] >= 28)).sum())
print('回流 总', (df['身份'] == '回流').sum(), '其中候选池', ((df['身份'] == '回流') & pool).sum())
print('\n== 五、重叠 ==')
for name, m in [('U(V2当前版上界)', U), ('U140(140k版上界)', U140)]:
    print(name, '∩ 新增', (m & (df['身份'] == '新增')).sum(), '∩ 回流', (m & (df['身份'] == '回流')).sum(),
          '∩ 持續', (m & (df['身份'] == '持續')).sum(), '∩ 近7天登录', (m & (df['lastd'] <= 7)).sum(),
          '∩ 流失候选池', (m & pool).sum(), '∩ 流失候选池且近7天登录(同)', (m & pool & (df['lastd'] <= 7)).sum())
# 旧定义对照（近4个月押注>10,000 的上界在阶段2：25,972，用同分母复核）
old = never & (bet > 10000)
print('旧口径复核：从未储值且累计押注>10,000（全部）', old.sum(), '；其中近7天登录', (old & (df['lastd'] <= 7)).sum())
print('旧上界(从未储值押注>10000)：', old.sum())
# 注册天数低于28 的 U
print('U 中 注册<28天', (U & (df['regd'] < 28)).sum(), '；>=28天', (U & (df['regd'] >= 28)).sum())
