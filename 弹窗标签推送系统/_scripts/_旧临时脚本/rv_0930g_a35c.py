# 审查 2026-09-30：检查 A35 储值占比是否把负储值截为 0（只读）
import pandas as pd
P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
neg = d[d['总充值金额'] < 0]
print('负储值 11 人：卡别', neg['卡别'].value_counts().to_dict(), '身份', neg['身份'].value_counts().to_dict(), '合计', neg['总充值金额'].sum())
d['pay0'] = d['总充值金额'].clip(lower=0)
S0 = d.pay0.sum()
print('截0后储值合计', S0, '原合计', d['总充值金额'].sum())
g = d.groupby('卡别').pay0.sum() / S0 * 100
print(g.round(3).to_dict())
m = d[(d['卡别'] == 1) & (d['身份'] == '持續')]
print('普卡持續 pay0 share %.3f' % (m.pay0.sum() / S0 * 100))
print('名义 18.10 用截0: %.3f' % (d['活动赠点'].clip(lower=0).sum() / 100 / S0 * 100))
print('有储值(>0)', (d['总充值金额'] > 0).sum(), '储值<=0', (d['总充值金额'] <= 0).sum())
