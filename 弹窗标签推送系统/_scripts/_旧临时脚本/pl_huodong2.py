import pandas as pd
import numpy as np

p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
a = d['活动赠点']
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce')
d['regdays'] = (pd.Timestamp('2026-09-16') - d['reg'].dt.normalize()).dt.days
x = d[(d['身份'] == '新增') & (d['regdays'] == 0)]
print('day0 new', len(x))
print(x['活动赠点'].value_counts().head(10))
print('day0 new bet median', x['游戏总押注'].median())
for k, g in d.groupby('身份'):
    n = len(g)
    print(k, n,
          'act==1000 %.2f' % ((g['活动赠点'] == 1000).mean() * 100),
          '<=1000 %.2f' % ((g['活动赠点'] <= 1000).mean() * 100),
          '>2000 %.2f' % ((g['活动赠点'] > 2000).mean() * 100),
          '>10000 %.2f' % ((g['活动赠点'] > 10000).mean() * 100))
# 活动赠点 exactly 1000 people: bet
y = d[d['活动赠点'] == 1000]
print('act==1000 n', len(y), 'identity', y['身份'].value_counts().to_dict(), 'bet median', y['游戏总押注'].median(),
      'pay>0', (y['总充值金额'] > 0).sum())
# 咬分比 check formula
m = d[(d['游戏总输赢'] != 0) & d['活动咬分比'].notna()]
calc = m['活动赠点'] / (-m['游戏总输赢']) * 100
print('咬分比 == 活动赠点/(-输赢)*100 within 0.01:', (abs(calc - m['活动咬分比']) < 0.01).mean(), len(m))
calc2 = m['活动赠点'] / (-(m['游戏总输赢'])) * 100
print(pd.concat([m['活动咬分比'].head(8), calc2.head(8)], axis=1))
