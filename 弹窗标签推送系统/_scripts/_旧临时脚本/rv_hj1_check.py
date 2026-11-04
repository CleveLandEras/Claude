import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['id3'] = d['身份'].replace({'VIP': '持續', '黑名單': '持續'})
amt = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
d['amt'] = amt
d['bet'] = bet
base = pd.Timestamp('2026-09-16')
rt = pd.to_datetime(d['注册时间'], errors='coerce')
days = (base - rt).dt.days
d['days'] = days
print('reg null', rt.isna().sum())
for k, s in d.groupby('id3'):
    dd = s['days']
    print(k, len(s), 'null', dd.isna().sum(), '<0', (dd < 0).sum(), '0-30', ((dd >= 0) & (dd <= 30)).sum(),
          '31-90', ((dd > 30) & (dd <= 90)).sum(), 'min', dd.min(), 'max', dd.max())
    print('   days desc of 新增-like', dd.describe().to_dict() if k == '新增' else '')
nw = d[d['id3'] == '新增']
print('新增 reg date range', rt[nw.index].min(), rt[nw.index].max())
print('新增 days value counts top', nw['days'].value_counts().sort_index().tail(8).to_dict())
lg = pd.to_datetime(d['最後登入時間'], errors='coerce')
ld = (base.normalize() + pd.Timedelta(days=1) - lg).dt.days
for k, s in d.groupby('id3'):
    print(k, 'bet>=1w', round((s['bet'] >= 10000).mean() * 100, 2), 'rtp med', pd.to_numeric(s['RTP'], errors='coerce').median())
nz = d[d['amt'] <= 0]
print('never', len(nz), 'bet>1w', (nz['bet'] > 10000).sum(), (nz['bet'] >= 10000).sum())
print('bet>1w all', round((d['bet'] > 10000).mean() * 100, 2), round((d['bet'] >= 10000).mean() * 100, 2))
