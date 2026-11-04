import pandas as pd
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])]
v = a[a['身份'] == 'VIP'].copy()
v['bet'] = pd.to_numeric(v['游戏总押注'], errors='coerce').fillna(0)
v['pay'] = pd.to_numeric(v['总充值金额'], errors='coerce').fillna(0)
z = v[(v['bet'] == 0) & (v['pay'] > 0)]
print('n', len(z))
print(z['pay'].describe(percentiles=[.1, .25, .5, .75, .9]).round())
print('卡别', z['卡别'].value_counts().to_dict())
print('平台', z['登入平台'].value_counts().to_dict())
print('等级中位', z['会员等级'].median())
nz = v[v['bet'] > 0]
print('VIP押注>0', len(nz), '储值中位', nz['pay'].median())
