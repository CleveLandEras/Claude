# 设计者试算（Q314）：只读，只用来确定切分方式与可复算性，不出结论
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
print('行数', len(df))
print(df.columns.tolist())
print(df[['注册时间', '最後登入時間']].head(3))
snap = pd.Timestamp('2026-09-16 23:59:59')
df['reg'] = pd.to_datetime(df['注册时间'], errors='coerce')
df['last'] = pd.to_datetime(df['最後登入時間'], errors='coerce')
df['regd'] = (snap.normalize() - df['reg'].dt.normalize()).dt.days
df['lastd'] = (snap.normalize() - df['last'].dt.normalize()).dt.days
pay = df['总充值金额'] > 0
bet = df['游戏总押注']
for k in [13, 14]:
    r = df['regd'] <= k
    n_unpaid = (r & ~pay).sum(); n_paid = (r & pay).sum()
    print(f'注册距快照<= {k} 天: 未付费 {n_unpaid}, 其中押注>140000 {(r & ~pay & (bet > 140000)).sum()}; '
          f'付费 {n_paid}, 其中押注>140000 {(r & pay & (bet > 140000)).sum()}')
    # 日均押注口径：押注 / max(注册天数,1)
    days = df['regd'].clip(lower=1)
    print('   日均>1万: 未付费', (r & ~pay & (bet / days > 10000)).sum(), ' 付费', (r & pay & (bet / days > 10000)).sum())
r = df['regd'] <= 13
d1 = df['regd'] + 1
print('日均口径(注册天数+1): 未付费', (r & ~pay & (bet / d1 > 10000)).sum(), '/', (r & ~pay).sum(),
      ' 付费', (r & pay & (bet / d1 > 10000)).sum(), '/', (r & pay).sum())
for name, dd in [('快照-注册(小数天)', (snap - df['reg']).dt.total_seconds() / 86400),
                 ('最后登录-注册(小数天,下限1)', ((df['last'] - df['reg']).dt.total_seconds() / 86400).clip(lower=1)),
                 ('注册天数(下限1)', df['regd'].clip(lower=1)), ('固定14天', 14)]:
    m = bet / dd > 10000
    print(name, '未付费', (r & ~pay & m).sum(), ' 付费', (r & pay & m).sum())
up = (~pay) & (bet > 140000)
for w in [7, 14]:
    print(f'从未储值且累计押注>140000 且最后登录<= {w} 天:', (up & (df['lastd'] <= w)).sum())
print('从未储值且累计押注>140000（全部）:', up.sum())
print('注册<=14天 且 从未储值 且押注>140000（精确部分）:', (up & (df['regd'] <= 14)).sum())
print('近7天登录（lastd<=7）:', (df['lastd'] <= 7).sum())
print('近7天登录且注册>=28天:', ((df['lastd'] <= 7) & (df['regd'] >= 28)).sum())
print(pd.crosstab(up & (df['lastd'] <= 14), df['身份']))
