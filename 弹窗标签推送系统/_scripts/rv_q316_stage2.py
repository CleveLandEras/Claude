import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(df))
snap = pd.Timestamp('2026-09-16')
reg = pd.to_datetime(df['注册时间'], errors='coerce').dt.normalize()
ll = pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()
df['regd'] = (snap - reg).dt.days
df['lld'] = (snap - ll).dt.days
dep = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
print('reg missing', df['regd'].isna().sum(), 'll missing', df['lld'].isna().sum())

new = df['身份'] == '新增'
ret = df['身份'] == '回流'
n7 = df['lld'] <= 7
print('near7', n7.sum(), 'new', new.sum(), 'ret', ret.sum(), 'ret&n7', (ret & n7).sum())

for th in [10000, 20000, 40000]:
    up = (dep <= 0) & (bet >= th) & (df['lld'] <= 14)
    lo = (dep <= 0) & (bet >= th) & (df['regd'] <= 13)
    print('th', th, 'upper', up.sum(), 'lower', lo.sum(), 'up&n7', (up & n7).sum())

up = (dep <= 0) & (bet >= 20000) & (df['lld'] <= 14)
lo = (dep <= 0) & (bet >= 20000) & (df['regd'] <= 13)
print('lo subset up', (lo & ~up).sum(), 'lo all new', (lo & ~new).sum())
for k in [16, 17, 18, 28]:
    print('pool reg>=', k, (n7 & (df['regd'] >= k)).sum())
pool = n7 & (df['regd'] >= 17)

card = pd.to_numeric(df['卡别'], errors='coerce')
print('up 普卡 share', round((up & (card == 1)).sum() / up.sum() * 100, 2))
print('up 普卡+银卡', round((up & card.isin([1, 2])).sum() / up.sum() * 100, 2))
print('old acc 持續 reg>=365 n7 in up', (up & (df['身份'] == '持續') & (df['regd'] >= 365) & n7).sum())

def r(a, b):
    return f'{a.sum()} ({a.sum()/b.sum()*100:.2f}%)'

print('--- wide')
print('new&up', r(new & up, new), 'ret&up', r(ret & up, ret), 'new&pool', r(new & pool, new), 'ret&pool', r(ret & pool, ret), 'up&pool', r(up & pool, up))
print('--- near7')
print('new&up', r(new & up & n7, new & n7), 'ret&up', r(ret & up & n7, ret & n7), 'new&pool', r(new & pool, new & n7), 'ret&pool', r(ret & pool, ret & n7), 'up&pool', r(up & pool, up & n7))
cnt_w = new.astype(int) + ret.astype(int) + up.astype(int) + pool.astype(int)
print('wide exactly2', (cnt_w == 2).sum(), 'ge3', (cnt_w >= 3).sum(), 'near7 exactly2', ((cnt_w == 2) & n7).sum(), 'near7 ge3', ((cnt_w >= 3) & n7).sum())
cnt_n = new.astype(int) + (ret & n7).astype(int) + lo.astype(int)
print('narrow exactly2', (cnt_n == 2).sum())
wu = new | ret | up | pool
nu = new | (ret & n7) | lo
print('wide union', wu.sum(), 'uncov', (~wu).sum(), 'uncov n7', (~wu & n7).sum())
print('narrow union', nu.sum(), 'uncov', (~nu).sum(), 'uncov n7', (~nu & n7).sum(), 'uncov n7 dep>0', (~nu & n7 & (dep > 0)).sum())
cont = df['身份'] == '持續'
g1 = n7 & (dep <= 0) & (bet < 20000) & cont
print('group1', g1.sum(), 'g1 wide uncovered', (g1 & ~wu).sum())
b = n7 & (bet > 0)
print('bankrupt range', b.sum(), 'up', round((b & up).sum()/b.sum()*100, 2), 'pool', round((b & pool).sum()/b.sum()*100, 2))
print('new-first PL lost', (new & pool).sum(), 'new|ret & pool', ((new | ret) & pool).sum(), round(((new | ret) & pool).sum()/pool.sum()*100, 2))
print('ret&up&pool', (ret & up & pool).sum(), 'new&up&pool', (new & up & pool).sum())
