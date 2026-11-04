# 审查复核：96.68%、金卡以上合并差倍数、普卡内部差倍数；只读
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
pay = '总充值金额'
print('N', len(df), '金卡以上', (df['卡别'] >= 3).sum())
tot = df[pay].sum()
print('金卡以上占累计储值(含VIP黑名单)', round(df[df['卡别'] >= 3][pay].sum() / tot * 100, 2))
main = df[~df['身份'].isin(['VIP', '黑名單'])]
print('剔除VIP黑名单后', len(main), round(main[main['卡别'] >= 3][pay].sum() / main[pay].sum() * 100, 2))
hp = main[main[pay] > 0]
for lab, s in [('金卡以上', hp[hp['卡别'] >= 3][pay]), ('普卡', hp[hp['卡别'] == 1][pay])]:
    p25, p90 = s.quantile(.25), s.quantile(.90)
    print(lab, 'P25', p25, 'P90', p90, '倍', round(p90 / p25, 1), 'P10', s.quantile(.1), 'P75', s.quantile(.75), round(s.quantile(.75) / s.quantile(.25), 1))
for lab, s in [('金卡以上', df[df['卡别'] >= 3][pay]), ('普卡', df[(df['卡别'] == 1) & (df[pay] > 0)][pay])]:
    print('含VIP', lab, round(s.quantile(.90) / s.quantile(.25), 1))
