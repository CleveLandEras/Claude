import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
b = d['游戏总押注']
frac = d[(b > 0) & (b < 10)]
print('0<bet<10 n', len(frac))
print(frac['卡别'].value_counts().sort_index().to_dict())
print(frac['身份'].value_counts().to_dict())
print('recharge>0', (frac['总充值金额'] > 0).sum())
nonint = d[(b % 1) != 0]
print('non-integer bet n', len(nonint), 'of which bet<10', (nonint['游戏总押注'] < 10).sum())
