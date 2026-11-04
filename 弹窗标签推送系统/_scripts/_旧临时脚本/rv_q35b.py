"""审查复算 Q35 补充（只读，不带参数）：60 名银卡押注取值；表 3b 共同支撑标准化；押注部分漏记的候选。"""
import numpy as np
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['a'] = d['days'] <= 7
d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
d['pcls'] = np.where(d['plat'].isin(['android', 'ios', 'apk']), 'App', np.where(d['plat'] == '缺值', '缺值', '浏览器'))
bl = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
d['bs'] = pd.cut(d['游戏总押注'], [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf], labels=bl)
nov = d[d['身份'] != 'VIP']
s = nov[(nov['bs'] == '≤1万') & (nov['cg'] == '银卡')]
print('60 名银卡押注>0 的取值', s.loc[s['游戏总押注'] > 0, '游戏总押注'].value_counts().to_dict())
print('全体押注恰为 6000 的', (d['游戏总押注'] == 6000).sum(), '其中银卡', ((d['游戏总押注'] == 6000) & (d['cg'] == '银卡')).sum())

rate = nov.groupby(['bs', 'cg'], observed=False)['a'].mean().unstack()
cnt = nov.groupby(['bs', 'cg'], observed=False)['a'].size().unstack()
w = nov['bs'].value_counts().reindex(bl)
common = [b for b in bl if cnt.loc[b].min() > 0]
print('三组都有人的押注段', common)
wc = w[common] / w[common].sum()
std = {g: round(float((rate.loc[common, g] * wc).sum() * 100), 2) for g in ['普卡', '银卡', '金卡以上']}
print('共同支撑（不含 VIP，全体权重）', std, '金卡以上减普卡', round(std['金卡以上'] - std['普卡'], 2), ' 共同支撑占不含 VIP 人数 %.2f%%' % (w[common].sum() / w.sum() * 100))
# 含 VIP 的原口径在同一共同支撑上
rate0 = d.groupby(['bs', 'cg'], observed=False)['a'].mean().unstack()
w0 = d['bs'].value_counts().reindex(bl)
wc0 = w0[common] / w0[common].sum()
std0 = {g: round(float((rate0.loc[common, g] * wc0).sum() * 100), 2) for g in ['普卡', '银卡', '金卡以上']}
print('同一共同支撑（含 VIP）', std0, '差', round(std0['金卡以上'] - std0['普卡'], 2))

never = d['总充值金额'] <= 0
lowb = never & (d['游戏总押注'] > 0) & (d['游戏总押注'] <= 1e4)
for thr in [100, 500]:
    x = d[lowb & (d['会员等级'] > thr)]
    print('从未储值、押注 0–1 万、等级>%d：%d 人' % (thr, len(x)), x['pcls'].value_counts().to_dict(), x['身份'].value_counts().to_dict())
print('从未储值、押注 0–1 万 按平台人数', d[lowb]['pcls'].value_counts().to_dict())
z = d[never & (d['游戏总押注'] == 0) & (d['会员等级'] > 100)]
print('从未储值、押注=0、等级>100：%d' % len(z), z['身份'].value_counts().to_dict(), z['pcls'].value_counts().to_dict())
# 押注与会员等级：按平台看同押注段的等级中位（押注若漏记网页，网页用户等级相对押注偏高）
pay = d[d['总充值金额'] > 0]
print('有储值者：押注段 × 平台类 的会员等级中位')
print(pay.groupby(['bs', 'pcls'], observed=False)['会员等级'].median().unstack().round(0).to_string())
print('全体：押注段 × 平台类 的会员等级中位')
print(d.groupby(['bs', 'pcls'], observed=False)['会员等级'].median().unstack().round(0).to_string())
