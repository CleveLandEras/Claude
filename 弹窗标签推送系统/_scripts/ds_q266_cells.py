import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
print(list(d.columns))
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('n', len(d))
d['last'] = pd.to_datetime(d['最後登入時間'])
d['days'] = (pd.Timestamp('2026-09-16') - d['last'].dt.normalize()).dt.days
d['在场'] = d['days'] <= 7
d['高卡'] = d['卡别'] >= 3
d['有储值'] = d['总充值金额'] > 0
print(d['身份'].value_counts())
print(pd.crosstab(d['身份'], d['在场'], margins=True))
print(pd.crosstab(d['身份'], d['高卡'], margins=True))
print(pd.crosstab([d['身份'], d['在场']], d['有储值'], margins=True))
print(d['卡别'].value_counts().sort_index())
