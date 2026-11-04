import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
v = d[d['身份'] == 'VIP']
pay = v['总充值金额']
bet = v['游戏总押注']
print('VIP', len(v), 'pay>0', (pay > 0).sum(), 'pay<=0', (pay <= 0).sum(), 'pay na', pay.isna().sum())
print('pay median', pay.median(), 'pay>0 median', pay[pay > 0].median())
print('bet0', (bet == 0).sum(), 'bet0 & pay>0', ((bet == 0) & (pay > 0)).sum(), 'bet>0 & pay>0', ((bet > 0) & (pay > 0)).sum())
print('ratio notna', v['储值回馈比'].notna().sum())
print(pay.describe())
print('pay<=0 & bet', v.loc[pay <= 0, '游戏总押注'].describe())
print('VIP pay<=0 & bet>1w', ((pay <= 0) & (bet > 10000)).sum(), 'VIP pay<=0 card', v.loc[pay <= 0, '卡别'].value_counts().to_dict())
# identity-level payer counts
p = d[d['总充值金额'] > 0]
print(p['身份'].value_counts().to_dict())
