import pandas as pd
base = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(base + '近一月活跃_20260916.csv', encoding='utf-8-sig')
b = pd.read_csv(base + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
b = b[~b['身份'].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
for d in (a, b):
    d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce')
    d['last'] = pd.to_datetime(d['最後登入時間'], errors='coerce')
    d['regd'] = (ref - d['reg'].dt.normalize()).dt.days
    d['lastd'] = (ref - d['last'].dt.normalize()).dt.days
print('lapsed rows', len(b))
print(b['身份'].value_counts().to_string())
print(b['lastd'].describe().to_string())
only = b[~b['会员编号'].isin(a['会员编号'])]
print('lapsed only', len(only))
print(only['身份'].value_counts().to_string())
print('active 身份 x lastd bucket')
a['lb'] = pd.cut(a['lastd'], [-1, 0, 7, 14, 31], labels=['0', '1-7', '8-14', '15-31'])
print(pd.crosstab(a['身份'], a['lb']).to_string())
print('regd missing', a['regd'].isna().sum(), 'neg', (a['regd'] < 0).sum())
for k, g in a.groupby('身份'):
    print(k, 'regd<30', (g['regd'] < 30).sum(), 'regd<=29 share', round((g['regd'] < 30).mean(), 4), 'regd<=120', (g['regd'] <= 120).sum())
never = a[a['总充值金额'] <= 0]
for t in (1000, 5000, 10000, 50000, 100000):
    s = never[never['游戏总押注'] > t]
    print('never-paid bet>', t, len(s), 'reg<=120d', int((s['regd'] <= 120).sum()), 'reg>120d', int((s['regd'] > 120).sum()), 'last0-7', int((s['lastd'] <= 7).sum()))
s = never[never['游戏总押注'] > 10000]
print('by identity', s['身份'].value_counts().to_string())
print('bet>1e6 among them', int((s['游戏总押注'] > 1e6).sum()))
paid = a[a['总充值金额'] > 0]
print('paid', len(paid), 'paid last0-7', int((paid['lastd'] <= 7).sum()), 'paid last>=8', int((paid['lastd'] >= 8).sum()))
print('paid by card', paid['卡别'].clip(upper=3).value_counts().sort_index().to_string())
# cumulative-storage share by identity
tot = a['总充值金额'].sum()
print('total', tot)
print((a.groupby('身份')['总充值金额'].sum() / tot).round(4).to_string())
# 回流 zero-bet
r = a[a['身份'] == '回流']
print('回流 bet0', int((r['游戏总押注'] <= 0).sum()), 'regd quantiles', r['regd'].quantile([.05, .25, .5, .75]).tolist())
# 新增 regd
n = a[a['身份'] == '新增']
print('新增 regd', n['regd'].describe().to_string())
# 活动赠点 negative count
print('act pts neg', int((a['活动赠点'] < 0).sum()), 'RTP missing', int(a['RTP'].isna().sum()), 'bet0', int((a['游戏总押注'] <= 0).sum()))
