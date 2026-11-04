# 审查 2026-09-30：A35 卡组占比精确值（只读）
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 20)
P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('卡别取值', d['卡别'].value_counts(dropna=False).sort_index().to_dict())
for c in ['总充值金额', '游戏总押注', '活动赠点', '充值赠点']:
    d[c] = pd.to_numeric(d[c], errors='coerce')
    print(c, '缺值', d[c].isna().sum(), '负值', (d[c] < 0).sum())
    d[c] = d[c].fillna(0)
d['act0'] = d['活动赠点'].clip(lower=0)
d['pay0'] = d['总充值金额'].clip(lower=0)
A = d.act0.sum(); S = d['总充值金额'].sum(); S0 = d.pay0.sum()
g = d.groupby('卡别').agg(n=('act0', 'size'), act=('act0', 'sum'), pay=('总充值金额', 'sum'), bet=('游戏总押注', 'sum'))
g['act%'] = g.act / A * 100; g['pay%'] = g.pay / S * 100; g['a/b%'] = g.act / g.bet * 100
print(g.round(4))
pk = g.loc[1]
print('普卡 pay share 精确 %.4f  act share %.4f' % (pk.pay / S * 100, pk.act / A * 100))
bk = g.loc[[6, 7]].sum()
print('黑卡至尊 act/bet %.4f pay share %.4f act share %.4f' % (bk.act / bk.bet * 100, bk.pay / S * 100, bk.act / A * 100))
print('倍数 %.3f' % ((pk.act / pk.bet) / (bk.act / bk.bet)))
# 普卡持續
m = d[(d['卡别'] == 1) & (d['身份'] == '持續')]
print('普卡持續', len(m), 'act %.2f pay %.2f' % (m.act0.sum() / A * 100, m['总充值金额'].sum() / S * 100))
