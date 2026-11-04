import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
pay = d[d['总充值金额'] > 0].copy()
r = pay['储值回馈比']
print('top values', r.round(0).value_counts().head(20))
print('share <=100.5', (r <= 100.5).mean(), ' >150', (r > 150).mean(), ' >=200', (r >= 200).mean())
pay['amt'] = pd.cut(pay['总充值金额'], [0, 100, 500, 1000, 5000, 20000, 1e9])
print(pay.groupby('amt', observed=True)['储值回馈比'].describe(percentiles=[.25, .5, .75, .9]))
print(pay.groupby('身份')['储值回馈比'].describe(percentiles=[.25, .5, .75, .9]))
pay['bonus_hi'] = pay['储值回馈比'] >= 150
print(pd.crosstab(pay['amt'], pay['bonus_hi'], normalize='index'))
print('amt dist of payers', pay['amt'].value_counts().sort_index())
print('top deposit values', pay['总充值金额'].round(0).value_counts().head(15))
