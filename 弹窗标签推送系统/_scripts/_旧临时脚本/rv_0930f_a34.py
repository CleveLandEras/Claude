"""审查 A34 复算（只读）。独立重写口径，不导入执行者脚本。"""
import pandas as pd, numpy as np
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
cols = list(a.columns)
def fc(k):
    return [x for x in cols if k in x][0]
ID, REG, LAST, CARD, S_, IDN = fc('会员编号'), fc('注册'), fc('最後登入'), fc('卡别'), fc('总充值'), fc('身份')
a = a[~a[IDN].isin(['機器人', '測試帳號'])].copy()
c = c[~c[IDN].isin(['機器人', '測試帳號'])].copy()
print('活跃', len(a), '流失名单', len(c))
ref = pd.Timestamp('2026-09-16')
for d in (a, c):
    d['days'] = (ref - pd.to_datetime(d[LAST]).dt.normalize()).dt.days
    d['age'] = (ref - pd.to_datetime(d[REG], errors='coerce').dt.normalize()).dt.days
    d['S'] = d[S_]
    d['R'] = d['S'].clip(lower=0) / (d['age'] / 30.44).clip(lower=1)
vb = ['VIP', '黑名單']
O1 = a[(a.days <= 7) & (a.S > 0) & (~a[IDN].isin(vb)) & a.R.notna()]
print('O1', len(O1))
topR = O1.sort_values('R', ascending=False).head(134)
topS = O1.sort_values('S', ascending=False).head(134)
print('R 门槛', round(topR.R.min(), 1), 'S 门槛', topS.S.min())
print('R 集合 身份', topR[IDN].value_counts().to_dict())
print('R 集合 新增 卡别', topR[topR[IDN] == '新增'][CARD].value_counts().to_dict())
print('R 集合 回流 卡别', topR[topR[IDN] == '回流'][CARD].value_counts().to_dict())
print('S 集合 身份', topS[IDN].value_counts().to_dict())
print('重叠', len(set(topR[ID]) & set(topS[ID])))
print('R 集合 注册<365', int((topR.age < 365).sum()))
# 新增金卡以上
nw = a[a[IDN] == '新增']
g = nw[nw[CARD] >= 3]
print('新增', len(nw), '金卡以上', len(g), '%.2f%%' % (len(g) / len(nw) * 100), g[CARD].value_counts().sort_index().to_dict())
print('  其中 有储值且 0-7 天', int(((g.S > 0) & (g.days <= 7)).sum()))
print('  新增金卡以上 注册天数分布', g.age.describe().round(1).to_dict())
# D1
leave = c[~c[ID].isin(a[ID])]
D1a = a[(a[CARD] >= 3) & (~a[IDN].isin(vb)) & (a.days >= 8)].copy(); D1a['grp'] = 'wait'
D1b = leave[(leave[CARD] >= 3) & (~leave[IDN].isin(vb))].copy(); D1b['grp'] = 'left'
D1 = pd.concat([D1a, D1b])
print('D1', len(D1), len(D1a), len(D1b))
def k80(d, key):
    s = d.sort_values(key, ascending=False)
    v = s[key].clip(lower=0)
    k = int((v.cumsum() / v.sum() < 0.8).sum()) + 1
    return s.head(k)
pooled = k80(D1, 'R')
print('合并排序 R 前80% 人数', len(pooled), pooled.grp.value_counts().to_dict())
cw = k80(D1a, 'R'); cl = k80(D1b, 'R')
print('分格 R 前80%：待再来', len(cw), '已离开', len(cl), '合计', len(cw) + len(cl))
percell = set(cw[ID]) | set(cl[ID])
print('合并名单与分格名单重合', len(set(pooled[ID]) & percell))
thr = topR.R.min()
x = D1[D1.R >= thr]
print('R 门槛达标', len(x), x.grp.value_counts().to_dict(), '不在合并名单', len(set(x[ID]) - set(pooled[ID])), '不在分格名单', len(set(x[ID]) - percell))
xs = D1[D1.S >= topS.S.min()]
print('S 门槛达标', len(xs), xs.grp.value_counts().to_dict(), '不在合并名单', len(set(xs[ID]) - set(pooled[ID])), '不在分格名单', len(set(xs[ID]) - percell))
print('D1 R 占合并口径', 'S 份额计算略')
