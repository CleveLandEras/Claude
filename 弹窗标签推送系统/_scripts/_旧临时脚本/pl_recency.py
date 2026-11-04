import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(p, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
print('rows', len(df))
t = pd.to_datetime(df['最後登入時間'], errors='coerce')
print('last login min/max', t.min(), t.max())
ref = pd.Timestamp('2026-09-17')
df['gap'] = (ref.normalize() - t.dt.normalize()).dt.days
df['grp'] = df['卡别'].apply(lambda c: '普卡' if c == 1 else ('银卡' if c == 2 else '金卡以上'))
amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
df['amt'] = amt
tot = amt.sum()
bins = [0, 3, 7, 14, 21, 40]
labels = ['1-3', '4-7', '8-14', '15-21', '22+']
df['gb'] = pd.cut(df['gap'], bins=bins, labels=labels)
for g, sub in df.groupby('grp'):
    print('==', g, len(sub))
    c = sub.groupby('gb', observed=False).agg(n=('gap', 'size'), amt=('amt', 'sum'))
    c['pct_n'] = (c['n'] / len(sub) * 100).round(2)
    c['pct_amt_all'] = (c['amt'] / tot * 100).round(2)
    print(c[['n', 'pct_n', 'pct_amt_all']])
# gold+ with gap >7
g = df[df['grp'] == '金卡以上']
print('gold gap>7', (g['gap'] > 7).sum(), round(g.loc[g['gap'] > 7, 'amt'].sum() / tot * 100, 2))
print('gold gap>14', (g['gap'] > 14).sum(), round(g.loc[g['gap'] > 14, 'amt'].sum() / tot * 100, 2))
print('gold identity', g['身份'].value_counts().to_dict())
