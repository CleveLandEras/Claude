import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
snap = pd.Timestamp('2026-09-16')
df['regd'] = (snap - pd.to_datetime(df['注册时间'], errors='coerce').dt.normalize()).dt.days
df['lastd'] = (snap - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
N = len(df)
never = df['总充值金额'] <= 0
bet = df['游戏总押注']
near7 = df['lastd'] <= 7
print('N', N, 'near7', near7.sum())
for k in [17, 18, 28]:
    pool = near7 & (df['regd'] >= k)
    print(f'注册>={k}: 候选池 {pool.sum()} ({pool.sum()/N:.2%})；新增∩ {(pool & (df["身份"]=="新增")).sum()}；回流∩ {(pool & (df["身份"]=="回流")).sum()}；'
          f'近7天登录但注册<{k} {(near7 & (df["regd"]<k)).sum()}；与潜在付费上界重叠 {(pool & never & (bet>=20000) & (df["lastd"]<=14)).sum()}')
# 下界检查：注册<=13天 从未储值 押注>=20000
low = never & (bet >= 20000) & (df['regd'] <= 13)
print('潜在付费下界(注册<=13天) ', low.sum(), f'{low.sum()/N:.2%}')
up = never & (bet >= 20000) & (df['lastd'] <= 14)
print('上界', up.sum(), '近7天', (up & near7).sum())
