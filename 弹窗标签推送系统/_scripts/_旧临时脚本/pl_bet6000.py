import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
print('total', len(d))
b = d['游戏总押注']
vc = b.value_counts().head(15)
print('top bet values:\n', vc)
s = d[b == 6000]
print('bet==6000 n', len(s))
print(s['卡别'].value_counts().sort_index())
print(s['身份'].value_counts())
print(s['登入平台'].value_counts())
print('recharge>0', (s['总充值金额'] > 0).sum(), 'median recharge', s['总充值金额'].median())
print('活动赠点 describe', s['活动赠点'].describe())
print('会员等级 describe', s['会员等级'].describe())
# near 6000 values
for v in [5000, 6000, 7000, 10000]:
    print(v, (b == v).sum())
# potential payer proxy: 从未储值 and bet>1万 ; how many never-paid with bet==6000
print('never paid & bet==6000', ((d['总充值金额'] <= 0) & (b == 6000)).sum())
