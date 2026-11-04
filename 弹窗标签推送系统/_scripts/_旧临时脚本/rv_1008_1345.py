import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
pay = '总充值金额'; bet = '游戏总押注'
d['last'] = pd.to_datetime(d['最後登入時間'], errors='coerce')
d['gap'] = (pd.Timestamp('2026-09-16') - d['last'].dt.normalize()).dt.days
print('> 10000', ((d[pay] == 0) & (d[bet] > 10000)).sum())
print('>=10000', ((d[pay] == 0) & (d[bet] >= 10000)).sum())
print('pay<=0 >10000', ((d[pay] <= 0) & (d[bet] > 10000)).sum())
pp = d[(d[pay] <= 0) & (d[bet] > 10000)]
print('<=0 overlap', pp['身份'].isin(['新增', '回流']).sum(), len(pp))
print('pay<0', (d[pay] < 0).sum(), 'pay isna', d[pay].isna().sum(), 'bet na', d[bet].isna().sum())
dd = d[~d['身份'].isin(['VIP', '黑名單'])]
print('近一周 pay==0', ((dd[pay] == 0) & (dd['gap'] <= 7)).sum(), 'pay<=0', ((dd[pay] <= 0) & (dd['gap'] <= 7)).sum())
print('含VIP pay<=0', ((d[pay] <= 0) & (d['gap'] <= 7)).sum())
print('gap<=7 by floor', ((dd[pay] == 0) & (((pd.Timestamp('2026-09-16 23:59:59') - dd['last']).dt.days) <= 7)).sum())
