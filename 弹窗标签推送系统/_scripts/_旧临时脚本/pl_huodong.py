import pandas as pd
import numpy as np

p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
print(d.columns.tolist())
a = d['活动赠点']
print('活动赠点 describe', a.describe())
print('null', a.isna().sum(), '==0', (a == 0).sum(), '<0', (a < 0).sum(), '>0', (a > 0).sum())
d['has_act'] = a > 0
d['pay'] = d['总充值金额'] > 0
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce')
d['last'] = pd.to_datetime(d['最後登入時間'], errors='coerce')
d['regdays'] = (pd.Timestamp('2026-09-16') - d['reg'].dt.normalize()).dt.days
d['lastdays'] = (pd.Timestamp('2026-09-16') - d['last'].dt.normalize()).dt.days
for k, g in d.groupby('身份'):
    print(k, len(g), 'act>0 %.2f' % (g['has_act'].mean() * 100), 'median act', g['活动赠点'].median(),
          'P75', g['活动赠点'].quantile(.75))
print('--- by pay')
for k, g in d.groupby('pay'):
    print(k, len(g), 'act>0 %.2f' % (g['has_act'].mean() * 100), 'median', g['活动赠点'].median())
print('--- value counts top 20 活动赠点')
print(a.value_counts().head(20))
print('--- 新增 by regdays bucket')
x = d[d['身份'] == '新增']
print(x['regdays'].describe())
for lo, hi in [(0, 0), (1, 3), (4, 7), (8, 14), (15, 29), (30, 999)]:
    g = x[(x['regdays'] >= lo) & (x['regdays'] <= hi)]
    if len(g):
        print(lo, hi, len(g), 'act>0 %.2f' % (g['has_act'].mean() * 100), 'median', g['活动赠点'].median())
print('--- 活动咬分比')
b = d['活动咬分比']
print(b.describe())
print('null', b.isna().sum())
# check relation: 咬分比 vs 活动赠点/押注
m = d[(d['游戏总押注'] > 0) & b.notna()]
r1 = (m['活动赠点'] / m['游戏总押注'])
print('corr 咬分比 vs 活动赠点/押注', np.corrcoef(m['活动咬分比'], r1)[0, 1])
r2 = (m['活动赠点'] / (m['充值赠点'] + m['活动赠点']).replace(0, np.nan))
mm = m[r2.notna()]
print('corr 咬分比 vs 活动赠点/(充值+活动)', np.corrcoef(mm['活动咬分比'], r2[r2.notna()])[0, 1])
print(m[['活动赠点', '充值赠点', '游戏总押注', '游戏总输赢', '活动咬分比']].head(15))
print('--- 卡别 x act')
for k, g in d.groupby('卡别'):
    print(k, len(g), 'act>0 %.2f' % (g['has_act'].mean() * 100), 'median', g['活动赠点'].median())
print('--- act>0 by lastdays')
for lo, hi in [(0, 0), (1, 7), (8, 14), (15, 31)]:
    g = d[(d['lastdays'] >= lo) & (d['lastdays'] <= hi)]
    print(lo, hi, len(g), 'act>0 %.2f' % (g['has_act'].mean() * 100), 'median', g['活动赠点'].median())
