"""Q130 大户：S1 复现、S2 对照集合、S3 落位、S4 缺席大户级高卡、反例检查。只读。
口径：O1 = 最后登录 0–7 天、累计储值 > 0、身份非 VIP 与黑名單（剔除機器人、測試帳號）；R = 累计储值（负按 0）÷ 月龄（注册距 2026-09-16 天数 ÷ 30.44，最少 1）。
D1 = 高卡（卡别 ≥ 3）去 VIP、黑名單，最后登录 ≥ 8 天（活跃里）+ 八月流失名单里不在活跃里的（已离开）。
"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd, numpy as np
B = _ROOT + '/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
col = {k: [x for x in a.columns if k in x][0] for k in ['会员编号', '注册', '最後登入', '卡别', '总充值', '身份']}
ID, CARD, IDN = col['会员编号'], col['卡别'], col['身份']
for d in (a, c):
    d.drop(d[d[IDN].isin(['機器人', '測試帳號'])].index, inplace=True)
print('活跃', len(a), '流失名单', len(c))
ref = pd.Timestamp('2026-09-16')

def prep(d):
    d = d.copy()
    d['days'] = (ref - pd.to_datetime(d[col['最後登入']]).dt.normalize()).dt.days
    d['age'] = (ref - pd.to_datetime(d[col['注册']], errors='coerce').dt.normalize()).dt.days
    d['S'] = d[col['总充值']]
    d['R'] = d['S'].clip(lower=0) / (d['age'] / 30.44).clip(lower=1)
    return d
a = prep(a); c = prep(c)
leave = c[~c[ID].isin(a[ID])]
notvb = lambda d: ~d[IDN].isin(['VIP', '黑名單'])
O1 = a[(a.days <= 7) & (a.S > 0) & notvb(a)]
O1 = O1[O1.R.notna()].copy()
print('O1', len(O1), 'S 合计', int(O1.S.sum()), 'R 合计', round(O1.R.sum(), 0))
tot_S = a.S.clip(lower=0).sum(); tot_R = a.R.sum()
print('全平台（62,292 人）S 合计', int(tot_S), 'R 合计', round(tot_R, 0))

def dist(t, name):
    print('---', name, '人数', len(t))
    print(' 卡别', t[CARD].value_counts().sort_index().to_dict())
    print(' 身份', t[IDN].value_counts().to_dict())
    print(' 注册天数', pd.cut(t.age, [-1, 30, 90, 365, 1095, 99999]).value_counts().sort_index().to_dict())
    print(' 最后登录天数', pd.cut(t.days, [-1, 0, 1, 3, 7]).value_counts().sort_index().to_dict())
    print(' S 占 O1 %.2f%% 占全平台 %.2f%%；R 占 O1 %.2f%% 占全平台 %.2f%%' % (
        t.S.sum() / O1.S.sum() * 100, t.S.sum() / tot_S * 100, t.R.sum() / O1.R.sum() * 100, t.R.sum() / tot_R * 100))

topR = O1.nlargest(134, 'R'); TR = topR.R.min()
topS = O1.nlargest(134, 'S'); TS = topS.S.min()
print('门槛 R', round(TR, 1), '门槛 S', round(TS, 1))
dist(topR, 'R 集合')
dist(topS, 'S 集合')
ov = set(topR[ID]) & set(topS[ID])
print('两集合重叠', len(ov))

# 落位：身份 × 集合
for nm, t in [('R 集合', topR), ('S 集合', topS)]:
    print(nm, '身份×卡别')
    print(pd.crosstab(t[IDN], t[CARD]))

# S4 缺席的大户级高卡
hi = lambda d: d[CARD] >= 3
D1a = a[hi(a) & notvb(a) & (a.days >= 8)]
D1b = leave[hi(leave) & notvb(leave)]
D1 = pd.concat([D1a, D1b]).copy()
D1['grp'] = np.where(D1[ID].isin(D1a[ID]), '活跃里 8 天以上没来', '已离开')
print('D1', len(D1), D1.grp.value_counts().to_dict(), 'R 合计', round(D1.R.sum(), 0), 'S 合计', int(D1.S.clip(lower=0).sum()))
D1s = D1.sort_values('R', ascending=False)
k80 = int((D1s.R.cumsum() / D1s.R.sum() < 0.8).sum()) + 1
top168 = set(D1s.head(k80)[ID])
print('D1 R 前 80% 人数（前 N 人）', k80)
D1s_S = D1.sort_values('S', ascending=False)
k80S = int((D1s_S.S.clip(lower=0).cumsum() / D1s_S.S.clip(lower=0).sum() < 0.8).sum()) + 1
print('D1 S 前 80% 人数', k80S)
for nm, thr, key in [('R 门槛', TR, 'R'), ('S 门槛', TS, 'S')]:
    x = D1[D1[key] >= thr]
    print(nm, '达标人数', len(x), x.grp.value_counts().to_dict(),
          '全部在 R 前80%名单内？', bool(set(x[ID]) <= top168), '不在人数', len(set(x[ID]) - top168),
          '其 R 占 D1 R %.2f%% 占全平台 R %.2f%%；S 占 D1 S %.2f%% 占全平台 S %.2f%%' % (
              x.R.sum() / D1.R.sum() * 100, x.R.sum() / tot_R * 100,
              x.S.clip(lower=0).sum() / D1.S.clip(lower=0).sum() * 100, x.S.clip(lower=0).sum() / tot_S * 100))
    if len(x):
        print('   最后登录天数', x.days.describe().round(1).to_dict(), ' 卡别', x[CARD].value_counts().sort_index().to_dict(), ' 身份', x[IDN].value_counts().to_dict())
# 在 S 前 80% 名单内（按 S 排）
xs = D1[D1.S >= TS]
print('S 门槛达标者是否都在 D1 按 S 排前 80% 内', bool(set(xs[ID]) <= set(D1s_S.head(k80S)[ID])), '不在人数', len(set(xs[ID]) - set(D1s_S.head(k80S)[ID])))
print('S 门槛达标者是否都在 R 前 168（前 80%）名单内', bool(set(xs[ID]) <= top168), '不在人数', len(set(xs[ID]) - top168))

# 反例 ①：门槛敏感性（0.5%、2%）
for pct, n in [('0.5%', int(round(len(O1) * 0.005))), ('1%', 134), ('2%', int(round(len(O1) * 0.02)))]:
    t = O1.nlargest(n, 'R'); th = t.R.min()
    x = D1[D1.R >= th]
    print('门槛', pct, '人数', n, 'R 门槛', round(th, 1), '身份', t[IDN].value_counts().to_dict(), '卡别', t[CARD].value_counts().sort_index().to_dict(),
          '| D1 达标', len(x), '不在前 80% 名单', len(set(x[ID]) - top168),
          '| 占 O1 S %.1f%% R %.1f%%' % (t.S.sum() / O1.S.sum() * 100, t.R.sum() / O1.R.sum() * 100))
# 反例 ②：活跃里达到门槛的 VIP
v = a[(a[IDN] == 'VIP') & (a.R >= TR)]
print('活跃里 VIP 且 R>=门槛', len(v), v[CARD].value_counts().sort_index().to_dict(), '最后登录', v.days.describe().round(1).to_dict())
b = a[(a[IDN] == '黑名單') & (a.R >= TR)]
print('黑名單 R>=门槛', len(b))
# 注册不满 1 年、R 放大
print('R 集合中注册 <365 天', int((topR.age < 365).sum()), '<=90 天', int((topR.age <= 90).sum()))
print('S 集合中注册 <365 天', int((topS.age < 365).sum()))
# 在场大户中，身份与新增/回流活动位：新增、回流者
print('R 集合 新增/回流', int((topR[IDN] == '新增').sum()), int((topR[IDN] == '回流').sum()))
print('S 集合 新增/回流', int((topS[IDN] == '新增').sum()), int((topS[IDN] == '回流').sum()))
# 最后登录 0 天占比（碰到上限的上界）
print('R 集合 最后登录=0 天', int((topR.days == 0).sum()), ' <=1 天', int((topR.days <= 1).sum()))
