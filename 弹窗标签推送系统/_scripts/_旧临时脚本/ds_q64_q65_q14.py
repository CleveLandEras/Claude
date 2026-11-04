# 设计者试算（只读）：为 Q64、Q65、Q14 设计切分方式，不产出结论
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(BASE + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
print('活跃', len(a))
print(list(a.columns))

ref = pd.Timestamp('2026-09-16')
a['reg'] = pd.to_datetime(a['注册时间'], errors='coerce')
a['last'] = pd.to_datetime(a['最後登入時間'], errors='coerce')
a['regd'] = (ref - a['reg'].dt.normalize()).dt.days
a['lastd'] = (ref - a['last'].dt.normalize()).dt.days
plat = a['登入平台'].astype(str).str.lower()
a['app'] = plat.isin(['android', 'ios', 'apk'])
a['pay'] = a['总充值金额'].fillna(0)
a['bet'] = a['游戏总押注'].fillna(0)
a['gift'] = a['活动赠点'].fillna(0)
a['cz'] = a['充值赠点'].fillna(0)

print('\n===== Q64 新增 =====')
n = a[(a['身份'] == '新增')].copy()
n8 = n[n['regd'] >= 8].copy()
n8['day1'] = n8['reg'].dt.normalize() == n8['last'].dt.normalize()
print('满8天', len(n8), '只来当天', n8['day1'].sum(), round(n8['day1'].mean() * 100, 2))
# 按注册日
g = n8.groupby(n8['reg'].dt.date).agg(n=('day1', 'size'), d1=('day1', 'mean'))
g['d1'] = (g['d1'] * 100).round(1)
print(g.to_string())
print('按日只来当天率 min/max/std', g['d1'].min(), g['d1'].max(), round(g['d1'].std(), 2))
print('注册人数与只来当天率相关', round(np.corrcoef(g['n'], g['d1'])[0, 1], 3))
n8['wd'] = n8['reg'].dt.dayofweek
print(n8.groupby('wd')['day1'].agg(['size', 'mean']).round(3).to_string())
# 注册小时
n8['hr'] = n8['reg'].dt.hour
print('按注册小时', n8.groupby(pd.cut(n8['hr'], [-1, 5, 11, 17, 23]))['day1'].agg(['size', 'mean']).round(3).to_string())
# 平台
print(n8.groupby('app')['day1'].agg(['size', 'mean']).round(3).to_string())
print(n8.groupby(plat[n8.index])['day1'].agg(['size', 'mean']).round(3).to_string())
# 押注
for name, d in [('只来当天', n8[n8['day1']]), ('回来过', n8[~n8['day1']])]:
    print(name, len(d), '押注0', round((d['bet'] == 0).mean() * 100, 2),
          '押注<=1000', round((d['bet'] <= 1000).mean() * 100, 2),
          '押注中位', d['bet'].median(), '有储值', round((d['pay'] > 0).mean() * 100, 2),
          '储值=50', int((d['pay'] == 50).sum()), '卡别>1', int((d['卡别'] > 1).sum()),
          '赠点=1000', round((d['gift'] == 1000).mean() * 100, 2),
          '赠点>2000', round((d['gift'] > 2000).mean() * 100, 2))
# 只来当天且有储值
d1p = n8[n8['day1'] & (n8['pay'] > 0)]
print('只来当天有储值', len(d1p), '储值分布', d1p['pay'].describe().round(0).to_dict())
# 注册-最后登录间隔分布 for returners
gap = (n8['last'].dt.normalize() - n8['reg'].dt.normalize()).dt.days
print('间隔', gap.value_counts().sort_index().head(15).to_dict())
# 押注分档 × 只来当天
n8['betb'] = pd.cut(n8['bet'], [-1, 0, 1000, 10000, 100000, 1e18], labels=['0', '1-1k', '1k-1w', '1w-10w', '>10w'])
print(pd.crosstab(n8['betb'], n8['day1'], margins=True).to_string())

print('\n===== Q65 回流 =====')
b = a.copy()
b['grp'] = np.select([b['卡别'] == 1, b['卡别'] == 2], ['普', '银'], '金+')
b['lb'] = pd.cut(b['lastd'], [-1, 0, 3, 7, 14, 31], labels=['0', '1-3', '4-7', '8-14', '15-31'])
for idn in ['回流', '持續']:
    s = b[b['身份'] == idn]
    print(idn, len(s))
    print((pd.crosstab(s['grp'], s['lb'], normalize='index') * 100).round(2).to_string())
    print(s.groupby('grp').size().to_dict())
# 注册时长控制：回流 vs 持續 同卡组、同注册时长
b['regb'] = pd.cut(b['regd'], [-1, 29, 90, 365, 1095, 1e6], labels=['<30', '30-90', '91-365', '1-3y', '>3y'])
b['ge8'] = b['lastd'] >= 8
t = b[b['身份'].isin(['回流', '持續'])].groupby(['grp', 'regb', '身份'])['ge8'].agg(['size', 'mean']).round(3)
print(t.to_string())
# 回流 付过费 vs 从未
r = b[b['身份'] == '回流']
print('回流有储值 ge8', round(r[r['pay'] > 0]['ge8'].mean() * 100, 2), '从未', round(r[r['pay'] <= 0]['ge8'].mean() * 100, 2))
print('回流 押注0 比例', round((r['bet'] == 0).mean() * 100, 2), 'ge8中押注0', round((r[r['ge8']]['bet'] == 0).mean() * 100, 2))
print('回流 赠点500-599', int(((r['gift'] >= 500) & (r['gift'] < 600)).sum()))
# 回流 金卡以上 储值集中
rg = r[r['grp'] == '金+']
print('回流金+', len(rg), 'ge8', int(rg['ge8'].sum()), '储值', rg['pay'].sum(), '回流总储值', r['pay'].sum())
print('回流金+ ge8 储值', rg[rg['ge8']]['pay'].sum())

print('\n===== Q14 首储 =====')
p = a[a['pay'] > 0].copy()
p['fp16800'] = (p['pay'] == 50) & (p['cz'] == 16800)
p['fp15000'] = (p['pay'] == 50) & (p['cz'] == 15000)
print('有储值', len(p), '16800', int(p['fp16800'].sum()), '15000', int(p['fp15000'].sum()))
p['grp'] = np.select([p['卡别'] == 1, p['卡别'] == 2], ['普', '银'], '金+')
print(p.groupby('grp').size().to_dict())
p['payb'] = pd.cut(p['pay'], [0, 50, 100, 500, 1000, 10000, 1e12], labels=['1-50', '51-100', '101-500', '501-1k', '1k-1w', '>1w'])
print(pd.crosstab(p['payb'], p['grp'], margins=True).to_string())
p['r7'] = p['lastd'] <= 7
print('有储值 0-7天', int(p['r7'].sum()), '按卡组', p.groupby('grp')['r7'].sum().to_dict())
print('储值>50 且 0-7天', int(((p['pay'] > 50) & p['r7']).sum()))
# 储值 <= 50 中非首储
print('储值<=50 人数', int((p['pay'] <= 50).sum()), '其中50元', int((p['pay'] == 50).sum()))
# 新增有储值 首储 vs 非
nn = p[p['身份'] == '新增']
print('新增有储值', len(nn), '储值=50', int((nn['pay'] == 50).sum()), '16800', int(nn['fp16800'].sum()), '15000', int(nn['fp15000'].sum()))
print('新增有储值 储值分档', nn['payb'].value_counts().sort_index().to_dict())
# 回馈比 >=150 小额
# 从未储值
z = a[a['pay'] <= 0]
print('从未储值', len(z), '0-7天', int((z['lastd'] <= 7).sum()))
print('从未储值 0-7天 按身份', z[z['lastd'] <= 7]['身份'].value_counts().to_dict())
print('从未储值 0-7天 押注>1万', int(((z['lastd'] <= 7) & (z['bet'] > 10000)).sum()))
# 新增转化：新增 注册满8天 有储值率 by 押注
print('新增满8天有储值率', round((n8['pay'] > 0).mean() * 100, 2), '新增全部', round((n['pay'] > 0).mean() * 100, 2))
# 新增 按注册天数 有储值率
n['regb2'] = pd.cut(n['regd'], [-1, 0, 3, 7, 14, 21, 29])
print(n.groupby('regb2')['pay'].apply(lambda x: round((x > 0).mean() * 100, 2)).to_string())
