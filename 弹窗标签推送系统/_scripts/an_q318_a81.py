# Q318 / A81 更新：按答复登记第 173、174 行定稿口径复算
# 潜在付费＝从未储值，且近 14 天押注 >= 20,000（无登录条件）
# 潜在流失＝近 7 天内有登录；第 15–28 天登录 >= 4 天；近 14 天登录 < 4 天；按近 14 天登录 2–3 天、1 天分两档
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

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
print('分母 N =', N, '；注册时间缺失', df['reg'].isna().sum(), '；总充值<0 的行', (df['总充值金额'] < 0).sum(), '；从未储值', never.sum(), f'{never.mean():.2%}')
print('身份分布', df['身份'].value_counts().to_dict())

print('\n== 一、潜在付费：从未储值 且 近 14 天押注 >= 门槛（无登录条件）==')
for thr in [10000, 20000, 40000]:
    allbet = never & (bet >= thr)
    low13 = allbet & (df['regd'] <= 13)
    low14 = allbet & (df['regd'] <= 14)
    up14 = allbet & (df['lastd'] <= 14)
    up7 = allbet & (df['lastd'] <= 7)
    print(f'门槛 {thr:>6,}: 累计押注达标且从未储值 {allbet.sum()}；下界(注册<=13天) {low13.sum()}；注册<=14天 {low14.sum()}；上界(最后登录<=14天) {up14.sum()} ({up14.sum()/N:.2%})；其中最后登录<=7天 {up7.sum()}')
thr = 20000
U = never & (bet >= thr) & (df['lastd'] <= 14)
L = never & (bet >= thr) & (df['regd'] <= 13)
print('\n下界 L =', L.sum(), f'({L.sum()/N:.2%})', '；其中最后登录距今 >14 天（应为 0）', (L & (df['lastd'] > 14)).sum(), '；L 是否都在 U 内', (L & ~U).sum() == 0)
print('L 的 最后登录<=7天', (L & (df['lastd'] <= 7)).sum(), '；身份', df.loc[L, '身份'].value_counts().to_dict())
print('注册时间缺失者（regd 为空）中 从未储值且押注>=20000 且最后登录<=14天', (df['regd'].isna() & U).sum())
print('上界 U =', U.sum(), f'({U.sum()/N:.2%})', '；其中近7天登录', (U & (df['lastd'] <= 7)).sum())
print('U 身份', df.loc[U, '身份'].value_counts().to_dict())

print('\n== 二、V2 依据复算（注册 7–13 天、从未储值）==')
for lo, hi in [(7, 13), (7, 14)]:
    s = (df['regd'] >= lo) & (df['regd'] <= hi) & never
    b = bet[s]
    print(f'注册{lo}-{hi}天未付费 {s.sum()}：中位数 {b.median():.0f}，P75 {b.quantile(.75):.0f}，>=20,000 {(b>=20000).sum()} ({(b>=20000).mean():.2%})，>=140,000 {(b>=140000).sum()} ({(b>=140000).mean():.2%})')

print('\n== 三、画像：上界 U 对比近一月活跃其余人 ==')
R = ~U
print('卡别构成（U / 其余）'); print(pd.crosstab(df['卡别'], U, normalize='columns').round(4))
print('身份构成（U / 其余）'); print(pd.crosstab(df['身份'], U, normalize='columns').round(4))
print('注册天数中位数 U', df.loc[U, 'regd'].median(), '其余', df.loc[R, 'regd'].median(), '；满一年 U', f'{(df.loc[U,"regd"]>365).mean():.2%}', '其余', f'{(df.loc[R,"regd"]>365).mean():.2%}')

print('\n== 四、潜在流失候选池（必要条件）==')
last7 = df['lastd'] <= 7
print('近7天有登录', last7.sum(), f'({last7.mean():.2%})')
# 第 15–28 天登录 >= 4 天 需要账号在第 15–28 天窗口内至少有 4 个自然日：注册日距今 >= 17 天
for k in [17, 28]:
    pool = last7 & (df['regd'] >= k)
    print(f'候选池：近7天有登录 且 注册距今>={k}天 = {pool.sum()} ({pool.sum()/N:.2%})；身份 {df.loc[pool,"身份"].value_counts().to_dict()}；从未储值 {(pool&never).sum()}，有储值 {(pool&pay).sum()}')
pool = last7 & (df['regd'] >= 17)
print('近7天有登录但注册<17天（按定义不可能命中）', (last7 & (df['regd'] < 17)).sum(), '；注册缺失', (last7 & df['regd'].isna()).sum())
print('新增身份总', (df['身份'] == '新增').sum(), '其中 注册>=17天', ((df['身份'] == '新增') & (df['regd'] >= 17)).sum(), '其中候选池', ((df['身份'] == '新增') & pool).sum())
print('回流身份总', (df['身份'] == '回流').sum(), '其中候选池', ((df['身份'] == '回流') & pool).sum())
print('注册距今 17-27 天且近7天登录', (last7 & (df['regd'] >= 17) & (df['regd'] < 28)).sum())

print('\n== 五、重叠（上界口径）==')
print('U ∩ 新增', (U & (df['身份'] == '新增')).sum(), f'占新增 {(U & (df["身份"]=="新增")).sum()/(df["身份"]=="新增").sum():.2%}', '；U ∩ 回流', (U & (df['身份'] == '回流')).sum(), f'占回流 {(U & (df["身份"]=="回流")).sum()/(df["身份"]=="回流").sum():.2%}')
print('U ∩ 候选池(17天)', (U & pool).sum(), f'占U {(U & pool).sum()/U.sum():.2%}', '；U ∩ 候选池(28天)', (U & last7 & (df['regd'] >= 28)).sum())
print('L(下界) ∩ 候选池(17天)', (L & pool).sum())
print('回流 ∩ U ∩ 候选池(17天)', ((df['身份'] == '回流') & U & pool).sum(), '；新增 ∩ U ∩ 候选池', ((df['身份'] == '新增') & U & pool).sum())
print('新增 ∩ 候选池', ((df['身份'] == '新增') & pool).sum(), '；回流 ∩ 候选池', ((df['身份'] == '回流') & pool).sum())
old = never & (bet > 10000)
print('\n旧口径复核：从未储值且累计押注>10,000（全部）', old.sum(), '；其中近7天登录', (old & last7).sum())
