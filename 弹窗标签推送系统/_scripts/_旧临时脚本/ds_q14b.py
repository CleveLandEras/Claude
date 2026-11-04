# 设计者试算（只读）：Q14 「付过费但确定没买首储」下界是否可行；Q64 时间戳口径；Q65 回流离开者
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(BASE + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
a['reg'] = pd.to_datetime(a['注册时间'], errors='coerce')
a['last'] = pd.to_datetime(a['最後登入時間'], errors='coerce')
a['regd'] = (ref - a['reg'].dt.normalize()).dt.days
a['lastd'] = (ref - a['last'].dt.normalize()).dt.days
a['pay'] = a['总充值金额'].fillna(0)
a['cz'] = a['充值赠点'].fillna(0)
a['bet'] = a['游戏总押注'].fillna(0)
a['grp'] = np.select([a['卡别'] == 1, a['卡别'] == 2], ['普', '银'], '金+')
print('时间戳样例', a['最後登入時間'].head(3).tolist(), a['注册时间'].head(3).tolist())

p = a[a['pay'] > 0].copy()
p['lt15000'] = p['cz'] < 15000
p['lt16800'] = p['cz'] < 16800
print('有储值', len(p))
print('充值赠点<15000', int(p['lt15000'].sum()), '<16800', int(p['lt16800'].sum()))
print(pd.crosstab(p['grp'], p['lt15000'], margins=True).to_string())
print('<15000 且 0-7天', int((p['lt15000'] & (p['lastd'] <= 7)).sum()))
print('<15000 按身份', p[p['lt15000']]['身份'].value_counts().to_dict())
print('<15000 储值分布', p[p['lt15000']]['pay'].describe().round(0).to_dict())
print('<15000 回馈比<100', int((p['lt15000'] & (p['储值回馈比'] < 100)).sum()))
# 注册 2026-06 起的有储值者
p6 = p[p['reg'] >= '2026-06-01']
print('6月起注册有储值', len(p6), '<15000', int(p6['lt15000'].sum()))
# 金卡以上 有储值 充值赠点分布
g = p[p['grp'] == '金+']
print('金+ 充值赠点分位', g['cz'].quantile([.01, .05, .1, .25, .5]).round(0).to_dict())
print('金+ 有储值 0-7天', int((g['lastd'] <= 7).sum()))

# 从未储值 0-7 天：按身份 × 注册时长
z = a[(a['pay'] <= 0) & (a['lastd'] <= 7)].copy()
z['regb'] = pd.cut(z['regd'], [-1, 29, 90, 365, 1095, 1e6], labels=['<30', '30-90', '91-365', '1-3y', '>3y'])
print(pd.crosstab(z['regb'], z['身份'], margins=True).to_string())
print('押注>1万', pd.crosstab(z['regb'], z['bet'] > 10000).to_string())

# Q64：时间戳口径（注册后 24h 内最后登录）
n = a[(a['身份'] == '新增') & (a['regd'] >= 8)].copy()
n['cal'] = n['reg'].dt.normalize() == n['last'].dt.normalize()
h = (n['last'] - n['reg']).dt.total_seconds() / 3600
n['h24'] = h < 24
n['h48'] = h < 48
print('日历口径', int(n['cal'].sum()), '24h', int(n['h24'].sum()), '48h', int(n['h48'].sum()), '负间隔', int((h < 0).sum()))
n['hr'] = n['reg'].dt.hour
print(n.groupby(pd.cut(n['hr'], [-1, 5, 11, 17, 23]), observed=False)[['cal', 'h24']].mean().round(3).to_string())
n['wk'] = pd.cut(n['regd'], [7, 14, 21, 29])
print(n.groupby('wk', observed=False)[['cal', 'h24']].agg(['size', 'mean']).round(3).to_string())

# 离开者里的回流
l = pd.read_csv(BASE + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
l = l[~l['身份'].isin(['機器人', '測試帳號'])]
l = l[~l['会员编号'].isin(a['会员编号'])]
print('离开者', len(l), l['身份'].value_counts().to_dict())
