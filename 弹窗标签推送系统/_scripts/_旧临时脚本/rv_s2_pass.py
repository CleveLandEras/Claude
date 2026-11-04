import pandas as pd
b = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(b + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])]
print('活跃', len(a))
print(a['身份'].value_counts().to_dict())
a['last'] = pd.to_datetime(a['最後登入時間'])
a['reg'] = pd.to_datetime(a['注册时间'])
ref = pd.Timestamp('2026-09-16')
a['gap'] = (ref.normalize() - a['last'].dt.normalize()).dt.days
a['regd'] = (ref.normalize() - a['reg'].dt.normalize()).dt.days
inf = a['gap'] <= 7
print('在场', inf.sum(), '离线>=8', (a['gap'] >= 8).sum(), '>=15', (a['gap'] >= 15).sum())
print('8-14', ((a['gap'] >= 8) & (a['gap'] <= 14)).sum(), '15-31', ((a['gap'] >= 15) & (a['gap'] <= 31)).sum())
c = '总充值金额'
bet = '游戏总押注'
print('有储值', (a[c] > 0).sum(), '累计储值', a[c].sum())
print('潜在付费甲', ((a[c] <= 0) & (a[bet] > 10000)).sum())
pp = (a[c] <= 0) & (a[bet] > 10000)
print('甲 注册<=120', (pp & (a['regd'] <= 120)).sum(), '普卡占', (pp & (a['卡别'] == 1)).sum() / pp.sum())
print('新增', (a['身份'] == '新增').sum(), 'regd<=29', (a['regd'] <= 29).sum())
print('回流在场', ((a['身份'] == '回流') & inf).sum(), '回流>=8', ((a['身份'] == '回流') & (a['gap'] >= 8)).sum())
print('新增∩甲', ((a['身份'] == '新增') & pp).sum(), '回流∩甲', ((a['身份'] == '回流') & pp).sum())
hv = a[c] > 0
print('有储值在场', (hv & inf).sum())
g = a[a['卡别'] >= 3][c].sum() / a[c].sum()
print('金卡以上占储值(卡别>=3)', g)
d = pd.read_csv(b + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
print('流失名单', len(d), '不在活跃里', (~d['会员编号'].isin(a['会员编号'])).sum())
print('---- extra')
new = a['身份'] == '新增'; ret = a['身份'] == '回流'
print('新增在场', (new & inf).sum(), '新增∩甲∩在场', (new & pp & inf).sum())
print('回流∩甲∩在场', (ret & pp & inf).sum(), '回流在场', (ret & inf).sum())
print('新增∩有储值', (new & hv).sum(), '新增∩有储值∩在场', (new & hv & inf).sum())
print('回流∩有储值', (ret & hv).sum(), '回流∩有储值∩在场', (ret & hv & inf).sum())
# 宽口径并集: 新增|回流|甲|有储值
wide = new | ret | pp | hv
print('宽并集', wide.sum(), '未覆盖', (~wide).sum(), '在场未覆盖', ((~wide) & inf).sum())
# 窄: 新增|回流在场|甲可核实(regd<=120)|空
nar = new | (ret & inf) | (pp & (a['regd'] <= 120))
print('窄并集', nar.sum(), '未覆盖', (~nar).sum(), '在场未覆盖', ((~nar) & inf).sum())
nov = (~wide)
print('宽未覆盖储值', a.loc[nov, c].sum())
print('持續有储值在场', ((a['身份'] == '持續') & hv & inf).sum(), '占储值', a.loc[(a['身份'] == '持續') & hv & inf, c].sum() / a[c].sum())
print('离线>=8 卡1占', (a.loc[a['gap'] >= 8, '卡别'] == 1).mean(), '推播App', 'n/a')
print('平台', a.loc[a['gap'] >= 8, '登入平台'].value_counts().to_dict())
