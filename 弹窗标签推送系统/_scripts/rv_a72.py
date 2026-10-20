import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
d = pd.read_csv(_ROOT + '/数据/近一月活跃_20260916.csv', encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
z = d['days'] <= 7
cs = d['总充值金额'] > 0
print(len(d), int(z.sum()), int((~z).sum()))
print('新增在场', int(((d['身份']=='新增')&z).sum()))
print('有储值在场', int((cs&z).sum()), '普银有储值在场', int((cs&z&d['卡别'].isin([1,2])).sum()))
print('高卡', int((d['卡别']>=3).sum()))
print('持續无储值低押注在场', int(((d['身份']=='持續')&z&~cs&(d['游戏总押注']<=10000)).sum()))
print('持續有储值在场', int(((d['身份']=='持續')&z&cs).sum()))
print('有储值在场剔VIP黑名單', int((cs&z&~d['身份'].isin(['VIP','黑名單'])).sum()))
print('VIP/黑在场/总', int((z&d['身份'].isin(['VIP','黑名單'])).sum()), int(d['身份'].isin(['VIP','黑名單']).sum()))
sub = d[z & (d['身份'].isin(['新增','回流']))]
print('新增∪回流 在场且有储值', int((cs[sub.index]).sum()))
print('身份 value_counts 在场', d[z]['身份'].value_counts().to_dict())
print('同时命中: 新增∩有储值在场', int(((d['身份']=='新增')&z&cs).sum()), '回流∩有储值在场', int(((d['身份']=='回流')&z&cs).sum()))
