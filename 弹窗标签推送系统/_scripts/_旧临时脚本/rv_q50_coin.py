# 审查者只读复算：Q50 的 542 / 330 / 83.8%、「押注 10 万以下为 0」、530 名银卡以上的押注是否都够 500 万、对照组
import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
print('columns', list(d.columns))
print('卡别', d['卡别'].value_counts().to_dict())
d['loss'] = -d['游戏总输赢']
d['excess'] = d['loss'] - d['活动赠点']
never = d[d['总充值金额'] <= 0].copy()
pot = never[never['游戏总押注'] > 10000]
big = pot[pot['excess'] > 100000]
print('never', len(never), 'pot', len(pot), 'big', len(big), 'share', round(len(big) / len(pot) * 100, 2))
print('big by card', big['卡别'].value_counts().to_dict())
print('big min bet', big['游戏总押注'].min(), 'big bet<=1e5', (big['游戏总押注'] <= 1e5).sum(), 'big bet<=1e6', (big['游戏总押注'] <= 1e6).sum())
g1 = never[never['游戏总押注'] > 1e8]
print('bet>1e8', len(g1), 'big among', (g1['excess'] > 100000).sum(), round((g1['excess'] > 100000).mean() * 100, 1))
b1m = never[never['游戏总押注'] > 1e6]
print('never bet>1e6', len(b1m), 'by card', b1m['卡别'].value_counts().to_dict(), 'big among', (b1m['excess'] > 100000).sum())
# 530 名银卡以上从未储值者：押注分布，是否都够 500 万
hi = never[never['卡别'] > 1]
print('never non-普卡', len(hi), hi['卡别'].value_counts().to_dict())
print('non-普卡 bet<5e6', (hi['游戏总押注'] < 5e6).sum(), 'bet<1e6', (hi['游戏总押注'] < 1e6).sum(), 'min', hi['游戏总押注'].min())
print('non-普卡 big excess', (hi['excess'] > 100000).sum())
# 对照：有储值者用同一方法（把自己的储值点数算进来源），看方法本身的假阳性
pay = d[d['总充值金额'] > 0].copy()
pay['excess_pay'] = pay['loss'] - pay['活动赠点'] - pay['总充值金额'] * 100 - pay['充值赠点']
print('pay n', len(pay), 'excess_pay>100k', (pay['excess_pay'] > 100000).sum(), round((pay['excess_pay'] > 100000).mean() * 100, 2))
pay_b = pay[pay['游戏总押注'] > 1e6]
print('pay bet>1e6', len(pay_b), 'excess_pay>100k', (pay_b['excess_pay'] > 100000).sum(), round((pay_b['excess_pay'] > 100000).mean() * 100, 2))
nb = never[never['游戏总押注'] > 1e6]
print('never bet>1e6 excess>100k rate', round((nb['excess'] > 100000).mean() * 100, 2))
# 充值赠点在从未储值者中是否为 0
print('never 充值赠点>0', (never['充值赠点'] > 0).sum())
