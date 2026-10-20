import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['last'] = pd.to_datetime(d['最後登入時間'])
d['days'] = (pd.Timestamp('2026-09-16') - d['last'].dt.normalize()).dt.days
d['在场'] = d['days'] <= 7
d['高卡'] = d['卡别'] >= 3
d['有储值'] = d['总充值金额'] > 0
d['无储值'] = d['总充值金额'] <= 0
d['潜付甲'] = d['无储值'] & (d['游戏总押注'] > 10000)
d['普银'] = d['卡别'].isin([1, 2])
print('n', len(d), '在场', int(d['在场'].sum()), '离线(活跃内)', int((~d['在场']).sum()))
print('身份三格(新增/回流/其余=持續+VIP+黑名單):')
for k, g in [('新增', d['身份'] == '新增'), ('回流', d['身份'] == '回流'), ('其余', ~d['身份'].isin(['新增', '回流']))]:
    s = d[g]
    print(k, len(s), '在场', int(s['在场'].sum()), '离线', int((~s['在场']).sum()))
print('其余内:', d[~d['身份'].isin(['新增', '回流'])]['身份'].value_counts().to_dict())
print('高卡', int(d['高卡'].sum()), '高卡有储值', int((d['高卡'] & d['有储值']).sum()))
print('高卡按身份', d[d['高卡']]['身份'].value_counts().to_dict())
print('有储值', int(d['有储值'].sum()), '有储值在场', int((d['有储值'] & d['在场']).sum()))
print('普银有储值', int((d['普银'] & d['有储值']).sum()), '普银有储值在场', int((d['普银'] & d['有储值'] & d['在场']).sum()))
print('金卡以上有储值', int((d['高卡'] & d['有储值']).sum()), '金卡以上有储值在场', int((d['高卡'] & d['有储值'] & d['在场']).sum()))
print('--- 在场口径两两交集 ---')
z = d[d['在场']]
print('新增∩潜付甲', int(((z['身份'] == '新增') & z['潜付甲']).sum()))
print('新增∩潜流(有储值)', int(((z['身份'] == '新增') & z['有储值']).sum()))
print('回流∩潜付甲', int(((z['身份'] == '回流') & z['潜付甲']).sum()))
print('回流∩潜流(有储值)', int(((z['身份'] == '回流') & z['有储值']).sum()))
print('潜付甲∩有储值', int((z['潜付甲'] & z['有储值']).sum()))
print('--- 五类之外在场 ---')
other = z[(z['身份'] == '持續') & z['有储值']]
print('持續有储值在场', len(other))
low = z[(z['身份'] == '持續') & z['无储值'] & (z['游戏总押注'] <= 10000)]
print('持續无储值押注<=10000在场', len(low), '卡别分布', low['卡别'].value_counts().to_dict())
print('--- 离线(活跃内) 身份 ---')
print(d[~d['在场']]['身份'].value_counts().to_dict())
print('离线 + 仅名单12,188(沿用阶段2): 27,929+12,188 =', 27929 + 12188)
print('VIP/黑名單 在场', int(z['身份'].isin(['VIP', '黑名單']).sum()), '总', int(d['身份'].isin(['VIP', '黑名單']).sum()))
# 活动位套二：身份三格 x 下滑上界(普银有储值)
print('--- 套二六格上界(下滑=普银有储值,上界) ---')
d['格'] = d['身份'].map(lambda x: x if x in ('新增', '回流') else '其余')
d['下滑上界'] = d['普银'] & d['有储值']
print(pd.crosstab(d['格'], d['下滑上界'], margins=True))
zz = d[d['在场']]
print(pd.crosstab(zz['格'], zz['下滑上界'], margins=True))
