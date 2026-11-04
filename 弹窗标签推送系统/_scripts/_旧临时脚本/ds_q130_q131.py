"""设计者试算（只读）：Q130 大户、Q131 成本的切分方式。只用于设计方法，不作结论。"""
import pandas as pd, numpy as np, os
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
print('列：', list(a.columns))
col = {k: [x for x in a.columns if k in x][0] for k in ['会员编号', '注册', '最後登入', '卡别', '总充值', '押注', '输赢', 'RTP', '活动赠点', '充值赠点', '回馈', '咬分', '身份']}
for d in (a, c):
    d.drop(d[d[col['身份']].isin(['機器人', '測試帳號'])].index, inplace=True)
print('活跃', len(a), '流失', len(c))
ref = pd.Timestamp('2026-09-16')
def prep(d):
    d = d.copy()
    d['days'] = (ref - pd.to_datetime(d[col['最後登入']]).dt.normalize()).dt.days
    d['age'] = (ref - pd.to_datetime(d[col['注册']], errors='coerce').dt.normalize()).dt.days
    d['S'] = d[col['总充值']]
    d['R'] = d['S'].clip(lower=0) / (d['age'] / 30.44).clip(lower=1)
    return d
a = prep(a); c = prep(c)
leave = c[~c[col['会员编号']].isin(a[col['会员编号']])]
notvb = lambda d: ~d[col['身份']].isin(['VIP', '黑名單'])
O1 = a[(a.days <= 7) & (a.S > 0) & notvb(a)]
O1 = O1[O1.R.notna()]
print('O1', len(O1))
top = O1.nlargest(134, 'R'); T = top.R.min()
print('大户', len(top), '门槛 R', round(T, 1), '卡别', top[col['卡别']].value_counts().sort_index().to_dict())
print('身份', top[col['身份']].value_counts().to_dict())
print('注册天数分档', pd.cut(top.age, [0, 30, 90, 365, 1095, 99999]).value_counts().sort_index().to_dict())
print('最后登录天数', top.days.value_counts().sort_index().to_dict())
print('S 占 O1', round(top.S.sum() / O1.S.sum() * 100, 2), 'R 占 O1', round(top.R.sum() / O1.R.sum() * 100, 2))
topS = O1.nlargest(134, 'S')
print('按 S 前 134 与按 R 前 134 重叠', len(set(topS[col['会员编号']]) & set(top[col['会员编号']])))
# D1
hi = lambda d: d[col['卡别']] >= 3
D1a = a[hi(a) & notvb(a) & (a.days >= 8)]
D1b = leave[hi(leave) & notvb(leave)]
D1 = pd.concat([D1a, D1b])
print('D1', len(D1), '其中 R>=门槛', int((D1.R >= T).sum()), '（活跃里', int((D1a.R >= T).sum()), '离开', int((D1b.R >= T).sum()), '）')
D1s = D1.sort_values('R', ascending=False)
cum = D1s.R.cumsum() / D1s.R.sum()
k80 = int((cum < 0.8).sum()) + 1
print('D1 R 前 80% 人数', k80, 'R>=门槛者都在其中？', int((D1s.head(k80).R >= T).sum()))
print('D1 R>=门槛者 最后登录天数', D1[D1.R >= T].days.describe().round(1).to_dict())
# 全体活跃里 R>=门槛但不在 O1（VIP 等）
print('活跃里 R>=门槛 按身份', a[a.R >= T][col['身份']].value_counts().to_dict())
# Q131
print('---- 成本 ----')
for k in ['活动赠点', '充值赠点', '押注', 'RTP', '咬分', '回馈']:
    s = a[col[k]]
    print(k, '缺值', int(s.isna().sum()), '<0', int((s < 0).sum()), '=0', int((s == 0).sum()), '分位', s.quantile([.5, .9, .99]).round(2).to_dict(), '合计', round(float(s.sum()), 0))
ev = a[col['活动赠点']].clip(lower=0)
es = ev.sort_values(ascending=False)
print('活动赠点 前1%人数占比', round(es.head(len(es) // 100).sum() / es.sum() * 100, 1), '前10%', round(es.head(len(es) // 10).sum() / es.sum() * 100, 1))
bonus = a[col['充值赠点']] - 100 * a.S
pay = a[a.S > 0]
bp = (pay[col['充值赠点']] - 100 * pay.S)
print('有储值者 加赠点(充值赠点-100×储值) <0', int((bp < 0).sum()), '合计', round(bp.clip(lower=0).sum(), 0), '占充值赠点', round(bp.clip(lower=0).sum() / pay[col['充值赠点']].sum() * 100, 2))
print('活动赠点合计 / 押注合计 %', round(ev.sum() / a[col['押注']].sum() * 100, 3))
print('活动赠点合计 / (100×储值合计) %', round(ev.sum() / (100 * a.S.clip(lower=0).sum()) * 100, 2))
a['cg'] = np.where(a[col['卡别']] >= 3, '高', np.where(a[col['卡别']] == 2, '银', '普'))
g = a.groupby(['cg', col['身份']]).agg(n=(col['会员编号'], 'size'), ev=(col['活动赠点'], lambda x: x.clip(lower=0).sum()), S=('S', lambda x: x.clip(lower=0).sum()))
g['ev%'] = (g.ev / g.ev.sum() * 100).round(2); g['S%'] = (g.S / g.S.sum() * 100).round(2)
print(g)
r = a[a[col['押注']] > 0]
chk = 100 + r[col['输赢']] / r[col['押注']] * 100
print('RTP 与 100+输赢/押注 差绝对值中位', round(float((r[col['RTP']] - chk).abs().median()), 3))
print('大户 活动赠点占全体', round(a[a[col['会员编号']].isin(top[col['会员编号']])][col['活动赠点']].clip(lower=0).sum() / ev.sum() * 100, 2))
