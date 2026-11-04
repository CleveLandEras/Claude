import pandas as pd
base = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(base + '近一月活跃_20260916.csv', encoding='utf-8-sig')
b = pd.read_csv(base + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
for n, d in (('active', a), ('lapsed', b)):
    d = d[~d['身份'].isin(['機器人', '測試帳號'])]
    print(n, len(d))
    print(d.dtypes.to_string())
    print(d['身份'].value_counts().to_string())
    print(d.describe(include='all').T.to_string())
    print(d.head(3).T.to_string())
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
for c in ['总充值金额', '游戏总押注', '游戏总输赢', 'RTP', '活动赠点', '充值赠点', '储值回馈比', '活动咬分比']:
    s = pd.to_numeric(a[c], errors='coerce')
    print(c, 'null', s.isna().sum(), 'zero', (s == 0).sum(), 'neg', (s < 0).sum(), s.quantile([.1, .5, .9, .99]).tolist())
print(a['会员等级'].value_counts().sort_index().to_string())
print(a['卡别'].value_counts().sort_index().to_string())
print(a['登入平台'].value_counts().to_string())
# 回流 注册时间 / 最后登录 分布
a['reg'] = pd.to_datetime(a['注册时间'], errors='coerce')
a['last'] = pd.to_datetime(a['最後登入時間'], errors='coerce')
a['regd'] = (pd.Timestamp('2026-09-16') - a['reg'].dt.normalize()).dt.days
a['lastd'] = (pd.Timestamp('2026-09-16') - a['last'].dt.normalize()).dt.days
print(a.groupby('身份')['regd'].describe().to_string())
print(a.groupby('身份')['lastd'].describe().to_string())
print(a.groupby('身份')['regd'].apply(lambda s: (s < 30).mean()).to_string())
