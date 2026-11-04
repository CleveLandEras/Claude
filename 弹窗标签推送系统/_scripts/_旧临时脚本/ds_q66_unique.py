# 设计者试算（只读）：Q66 D8 独有部分的分布，用于定切分方式，不出结论
import pandas as pd

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
act = pd.read_csv(BASE + '近一月活跃_20260916.csv', encoding='utf-8-sig')
chn = pd.read_csv(BASE + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
bad = ['機器人', '測試帳號']
act = act[~act['身份'].isin(bad)].copy()
chn = chn[~chn['身份'].isin(bad)].copy()
left = chn[~chn['会员编号'].isin(act['会员编号'])].copy()
act['src'] = 'act'
left['src'] = 'left'
m = pd.concat([act, left], ignore_index=True)
print('act', len(act), 'left', len(left), 'merged', len(m))

ref = pd.Timestamp('2026-09-16')
m['ll'] = pd.to_datetime(m['最後登入時間'], errors='coerce').dt.normalize()
m['rg'] = pd.to_datetime(m['注册时间'], errors='coerce').dt.normalize()
m['days'] = (ref - m['ll']).dt.days
m['regdays'] = (ref - m['rg']).dt.days
card = m['卡别']
vipb = m['身份'].isin(['VIP', '黑名單'])
d8 = m['days'] >= 8
d1 = d8 & card.between(3, 7) & ~vipb
d2 = m['rg'].between(pd.Timestamp('2026-08-18'), pd.Timestamp('2026-09-08')) & (m['ll'] == m['rg'])
d3 = (m['src'] == 'act') & (m['身份'] == '回流') & d8
print('D8', d8.sum(), 'D1', d1.sum(), 'D2', d2.sum(), 'D3', d3.sum())
uniq = d8 & ~(d1 | d2 | d3)
u = m[uniq].copy()
print('unique', len(u))

app = ['android', 'ios', 'apk']
def desc(df, name):
    n = len(df)
    if n == 0:
        print(name, 0); return
    bet = df['游戏总押注']
    pay = df['总充值金额']
    print('---', name, n)
    print(' src left share', round((df['src'] == 'left').mean() * 100, 2))
    print(' card1 share', round((df['卡别'] == 1).mean() * 100, 2))
    print(' paid share', round((pay > 0).mean() * 100, 2))
    print(' bet q10/25/50/75/90', [round(x) for x in bet.quantile([.1, .25, .5, .75, .9])])
    print(' bet==0', round((bet <= 0).mean() * 100, 2))
    for t in [1e4, 1e5, 1e6]:
        print('  bet>=', int(t), round((bet >= t).mean() * 100, 2))
    print(' potpay(pay<=0&bet>1e4)', round(((pay <= 0) & (bet > 1e4)).mean() * 100, 2))
    rd = df['regdays']
    print(' reg<60', round((rd < 60).mean() * 100, 2), 'reg>=365', round((rd >= 365).mean() * 100, 2))
    print(' level median', df['会员等级'].median())
    plat = df['登入平台'].astype(str).str.lower()
    print(' app share', round(plat.isin(app).mean() * 100, 2))
    lvl = df['会员等级']
    print(' bet per regday median', round((bet / rd.clip(lower=1)).median()))

desc(u, 'unique')
desc(u[u['src'] == 'act'], 'unique act 8-31')
desc(u[u['src'] == 'left'], 'unique left')
ref07 = m[(m['days'] <= 7) & (m['卡别'] == 1) & ~vipb]
desc(ref07, 'ref: act 0-7 card1')
desc(m[d8 & (m['卡别'] == 1) & (d2 | d3)], 'ref: overlap card1 (D2/D3)')
# 身份
print(u['身份'].value_counts())
# 注册时段拆分
oneday = u['ll'] == u['rg']
print('uniq reg 8/1-8/15 & oneday', (u['rg'].between(pd.Timestamp('2026-08-01'), pd.Timestamp('2026-08-15')) & oneday).sum())
print('uniq reg>=2026-08-01 all', (u['rg'] >= pd.Timestamp('2026-08-01')).sum())
print('uniq reg 8/18-9/8 (not oneday)', u['rg'].between(pd.Timestamp('2026-08-18'), pd.Timestamp('2026-09-08')).sum())
print('uniq reg 9/9-9/16', (u['rg'] >= pd.Timestamp('2026-09-09')).sum())
print('uniq oneday any reg', oneday.sum())
old = u[u['rg'] < pd.Timestamp('2026-08-01')]
print('uniq reg<8/1', len(old))
refb = ref07['游戏总押注']
p25, p50 = refb.quantile(.25), refb.quantile(.5)
print('ref07 bet p25 p50', round(p25), round(p50))
for name, df in [('uniq', u), ('uniq old', old)]:
    b = df['游戏总押注']
    print(name, 'low<p25', (b < p25).sum(), 'mid', ((b >= p25) & (b < p50)).sum(), 'high>=p50', (b >= p50).sum())
# 按注册时长分层的高投入比例
for lo, hi in [(0, 60), (60, 365), (365, 99999)]:
    s = u[(u['regdays'] >= lo) & (u['regdays'] < hi)]
    r = ref07[(ref07['regdays'] >= lo) & (ref07['regdays'] < hi)]
    print('regdays', lo, hi, 'uniq n', len(s), 'high share', round((s['游戏总押注'] >= p50).mean() * 100, 2), 'ref high share', round((r['游戏总押注'] >= p50).mean() * 100, 2))
# 回流 identity stock
print('回流 in act', (act['身份'] == '回流').sum(), 'of which 0-7', ((m['src'] == 'act') & (m['身份'] == '回流') & (m['days'] <= 7)).sum())
