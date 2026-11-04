import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
print(len(d))
print(d['登入平台'].value_counts(dropna=False))
d['卡组'] = pd.cut(d['卡别'], [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上'])
print(pd.crosstab(d['登入平台'], d['卡组'], margins=True))
print(pd.crosstab(d['登入平台'], d['身份'], margins=True))
g = d.groupby('登入平台')['总充值金额'].sum()
print((g / g.sum()).round(4))
print(d['会员等级'].describe())
