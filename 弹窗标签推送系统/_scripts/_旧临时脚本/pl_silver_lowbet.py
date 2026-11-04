import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
print('card counts', d['卡别'].value_counts().sort_index().to_dict())
s = d[(d['卡别'] == 2) & (d['身份'] != 'VIP') & (d['游戏总押注'] <= 10000)]
print('silver nonVIP bet<=1万 n', len(s))
print('bet value counts:\n', s['游戏总押注'].value_counts().sort_index())
s2 = d[(d['卡别'] == 2) & (d['游戏总押注'] <= 10000)]
print('silver incl VIP bet<=1万 n', len(s2), 'VIP', (s2['身份'] == 'VIP').sum())
print('bet<10000 strict silver nonVIP', ((d['卡别'] == 2) & (d['身份'] != 'VIP') & (d['游戏总押注'] < 10000)).sum())
