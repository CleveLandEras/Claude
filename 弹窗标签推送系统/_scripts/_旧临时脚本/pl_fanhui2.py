import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
pay = d[d['总充值金额'] > 0].copy()
for v in [30, 50, 70, 100]:
    s = pay[pay['总充值金额'].round(0) == v]
    print('deposit', v, 'n', len(s), 'ratio top', s['储值回馈比'].round(0).value_counts().head(5).to_dict())
r300 = pay[pay['储值回馈比'].round(0) == 300]
print('ratio300 deposit top', r300['总充值金额'].round(0).value_counts().head(8).to_dict())
r200 = pay[pay['储值回馈比'].round(0) == 200]
print('ratio200 deposit top', r200['总充值金额'].round(0).value_counts().head(8).to_dict())
print('ratio300 身份', r300['身份'].value_counts().to_dict(), '卡别', r300['卡别'].value_counts().to_dict())
