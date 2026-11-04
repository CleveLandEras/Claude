"""审查复算 A12、Q35（只读，不带参数）。"""
import numpy as np
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
reg = pd.to_datetime(d['注册时间'])
d['rd'] = reg.dt.normalize()
d['ten'] = (pd.Timestamp('2026-09-16') - d['rd']).dt.days
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
d['pcls'] = np.where(d['plat'].isin(['android', 'ios', 'apk']), 'App', np.where(d['plat'] == '缺值', '缺值', '浏览器'))
H = d['活动赠点']; B = d['游戏总押注']; Y = d['总充值金额']; L = d['会员等级']
new = d[d['身份'] == '新增']
print('\n[完整名单] 新增', len(new), '注册天数', new['ten'].min(), new['ten'].max())
print('注册日 >= 8/18 的各身份', d.loc[d['rd'] >= '2026-08-18', '身份'].value_counts().to_dict())
print('注册日 8/16–8/17 的各身份', d.loc[(d['rd'] >= '2026-08-16') & (d['rd'] < '2026-08-18'), '身份'].value_counts().to_dict())
print('最后登录早于注册日的人数', (d['days'] > d['ten']).sum())
same = new['ten'] == new['days']
m8 = new['ten'] >= 8
print('\n满 8 天', m8.sum(), '只来注册当天', (m8 & same).sum(), '%.2f%%' % ((m8 & same).sum() / m8.sum() * 100))
e = new['活动赠点'] == 1000
print('=1000', e.sum(), '%.2f%%' % (e.mean() * 100), '押注中位', new.loc[e, '游戏总押注'].median(),
      '只来当天', (e & same).sum(), '%.2f%%' % ((e & same).sum() / e.sum() * 100))
print('=1000 且满 8 天', (e & m8).sum(), '其中只来当天', (e & m8 & same).sum(), '%.2f%%' % ((e & m8 & same).sum() / (e & m8).sum() * 100))
print('=1000 注册 1–7 天', (e & (new['ten'] >= 1) & (new['ten'] <= 7)).sum(), '注册 0 天', (e & (new['ten'] == 0)).sum())
print('满 8 天只来当天：=1000 %d，>1000 %d，<1000 %d' % ((e & m8 & same).sum(), ((new['活动赠点'] > 1000) & m8 & same).sum(), ((new['活动赠点'] < 1000) & m8 & same).sum()))
print('满 8 天来过不止一天', (m8 & ~same).sum(), '其中 =1000', (m8 & ~same & e).sum())
z = new[new['ten'] == 0]
print('注册当天', len(z), '>0 %.2f%%' % ((z['活动赠点'] > 0).mean() * 100), '=1000', (z['活动赠点'] == 1000).sum())
for lab, g in [('<1000', new['活动赠点'] < 1000), ('>1000', new['活动赠点'] > 1000), ('=1000', e)]:
    x = new[g]
    print(lab, len(x), '押注中位', x['游戏总押注'].median(), '押注0 %.2f' % ((x['游戏总押注'] == 0).mean() * 100),
          '浏览器 %.2f' % ((x['pcls'] == '浏览器').mean() * 100), '有储值 %.2f' % ((x['总充值金额'] > 0).mean() * 100),
          '0–7 %.2f' % ((x['days'] <= 7).mean() * 100))
for c in ['浏览器', 'App']:
    x = new[new['pcls'] == c]
    print('新增', c, len(x), '<1000 %.2f' % ((x['活动赠点'] < 1000).mean() * 100), '=0 %.2f' % ((x['活动赠点'] == 0).mean() * 100))
x = new[new['plat'] == 'web']; print('新增 web', len(x), '<1000 %.2f' % ((x['活动赠点'] < 1000).mean() * 100))

print('\n[门槛] 表口径')
grp = {'新增': d['身份'] == '新增', '回流': d['身份'] == '回流', '持续表口径': d['身份'].isin(['持續', 'VIP', '黑名單'])}
for k, g in grp.items():
    x = d[g]
    print(k, len(x), '>0 %.2f >1000 %.2f >2000 %.2f' % ((x['活动赠点'] > 0).mean() * 100, (x['活动赠点'] > 1000).mean() * 100, (x['活动赠点'] > 2000).mean() * 100))
# 口径混用检查：6 月前注册的账号没有新手礼包 1,000 点，按 A12 自己的推断，扣掉新手礼包应为 >0
for k, g in grp.items():
    x = d[g]
    old = x['rd'] < '2026-06-01'
    alt = np.where(old, x['活动赠点'] > 0, x['活动赠点'] > 1000)
    print(k, '6 月前注册占 %.2f%%' % (old.mean() * 100), '按注册时间分口径（6 月前 >0，之后 >1000）%.2f%%' % (alt.mean() * 100),
          '6 月前注册者 >0 %.2f，>1000 %.2f' % ((x.loc[old, '活动赠点'] > 0).mean() * 100, (x.loc[old, '活动赠点'] > 1000).mean() * 100))
r = d[d['身份'] == '回流']
print('回流 ≤1000', (r['活动赠点'] <= 1000).sum(), '押注中位', r.loc[r['活动赠点'] <= 1000, '游戏总押注'].median(),
      '0–7 %.2f' % ((r.loc[r['活动赠点'] <= 1000, 'days'] <= 7).mean() * 100), '回流全体 0–7 %.2f' % ((r['days'] <= 7).mean() * 100))
f5 = d['活动赠点'] == 500
print('=500', f5.sum(), d.loc[f5, '身份'].value_counts().to_dict())
d['m'] = d['rd'].dt.to_period('M')
t = d[d['rd'] >= '2026-03-01'].groupby('m').apply(lambda x: pd.Series({'n': len(x), 'eq1000': round((x['活动赠点'] == 1000).mean() * 100, 2), 'eq0': round((x['活动赠点'] == 0).mean() * 100, 2)}))
print(t.to_string())

print('\n[押注、储值字段]')
b0 = B == 0
print('押注=0', b0.sum(), d.loc[b0, '身份'].value_counts().to_dict())
both = b0 & (Y <= 0)
print('两列=0', both.sum(), d.loc[both, '身份'].value_counts().to_dict())
nv = ~d['身份'].isin(['新增', 'VIP'])
print('非新增非VIP 两列=0', (both & nv).sum(), '其中等级>100', (both & nv & (L > 100)).sum())
print('非新增非VIP 押注=0', (b0 & nv).sum(), '全零且等级<=1', (b0 & nv & (H == 0) & (Y <= 0) & (L <= 1)).sum(),
      '有储值或等级>100', (b0 & nv & ((Y > 0) | (L > 100))).sum())
pre = d['rd'] < '2025-01-01'
print('2025 前注册、押注0、非新增', (pre & b0 & (d['身份'] != '新增')).sum(), d.loc[pre & b0 & (d['身份'] != '新增'), '身份'].value_counts().to_dict())
pp = (Y <= 0) & (B > 1e4)
print('潜在付费', pp.sum())
# 部分漏记检查：从未储值、押注 0<B<=1万，但会员等级明显高（等级主要随押注累积）
lowb = (Y <= 0) & (B > 0) & (B <= 1e4)
ref = d[(B > 1e4) & (B <= 2e4)]
print('参照：押注 1–2 万者会员等级 p50/p90', ref['会员等级'].median(), ref['会员等级'].quantile(0.9))
for thr in [100, 200, 500]:
    print('从未储值、押注 0–1 万、等级>%d' % thr, (lowb & (L > thr)).sum(), '  押注=0、从未储值、等级>%d' % thr, ((Y <= 0) & b0 & (L > thr)).sum())
print('从未储值、押注 0–1 万 按平台 等级>200 占比', d[lowb].groupby('pcls').apply(lambda x: round((x['会员等级'] > 200).mean() * 100, 2)).to_dict())

print('\n[A8 不含 VIP]')
nov = d[d['身份'] != 'VIP'].copy()
def cg(c):
    return np.where(c == 1, '普卡', np.where(c == 2, '银卡', '金卡以上'))
print('卡别取值', sorted(d['卡别'].dropna().unique().tolist()))
nov['cg'] = cg(nov['卡别'])
bins = [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf]
labs = ['≤1万', '1–10万', '10–100万', '1百万–1千万', '1千万–1亿', '>1亿']
nov['bs'] = pd.cut(nov['游戏总押注'], bins, labels=labs)
nov['a'] = nov['days'] <= 7
tab = nov.groupby(['bs', 'cg'])['a'].agg(['sum', 'size'])
print(tab.to_string())
w = nov['bs'].value_counts()
w = w.drop('≤1万'); w = w / w.sum()
res = {}
for g in ['普卡', '银卡', '金卡以上']:
    rate = nov[nov['cg'] == g].groupby('bs')['a'].mean().drop('≤1万')
    res[g] = (rate * w).sum() * 100
print('全体权重（不含 VIP，三组都去掉 ≤1万 重归一）', {k: round(v, 2) for k, v in res.items()}, '差', round(res['金卡以上'] - res['普卡'], 2))
w2 = nov['bs'].value_counts(normalize=True)
res2 = {}
for g in ['普卡', '银卡']:
    rate = nov[nov['cg'] == g].groupby('bs')['a'].mean()
    res2[g] = (rate * w2).sum() * 100
print('普卡、银卡含 ≤1万 全权重（an_q35 的做法：只对缺格的组重归一）', {k: round(v, 2) for k, v in res2.items()}, '金卡以上减普卡', round(res['金卡以上'] - res2['普卡'], 2))
s60 = nov[(nov['bs'] == '≤1万') & (nov['cg'] == '银卡')]
print('≤1万 银卡不含VIP', len(s60), '押注0', (s60['游戏总押注'] == 0).sum(), '=6000', (s60['游戏总押注'] == 6000).sum(),
      '2025前且押注0', ((s60['rd'] < '2025-01-01') & (s60['游戏总押注'] == 0)).sum(), '浏览器', (s60['pcls'] == '浏览器').sum(),
      '有储值', (s60['总充值金额'] > 0).sum())
