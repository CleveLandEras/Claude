"""Q130 补充：三套分母（O1、活跃 62,292、合并口径）份额；新增、回流中金卡以上人数（月月抽与回流任务的暴露规模）。只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd, numpy as np
B = _ROOT + '/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
col = {k: [x for x in a.columns if k in x][0] for k in ['会员编号', '注册', '最後登入', '卡别', '总充值', '身份']}
ID, CARD, IDN = col['会员编号'], col['卡别'], col['身份']
for d in (a, c):
    d.drop(d[d[IDN].isin(['機器人', '測試帳號'])].index, inplace=True)
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
u = pd.concat([a, leave])
notvb = lambda d: ~d[IDN].isin(['VIP', '黑名單'])
O1 = a[(a.days <= 7) & (a.S > 0) & notvb(a)]; O1 = O1[O1.R.notna()]
topR = O1.nlargest(134, 'R'); TR = topR.R.min()
topS = O1.nlargest(134, 'S'); TS = topS.S.min()
D1a = a[(a[CARD] >= 3) & notvb(a) & (a.days >= 8)]
D1b = leave[(leave[CARD] >= 3) & notvb(leave)]
D1 = pd.concat([D1a, D1b])
print('合并口径人数', len(u), '活跃', len(a), 'O1', len(O1), 'D1', len(D1))
den = {
  'O1': (O1.S.sum(), O1.R.sum()),
  '活跃 62,292': (a.S.clip(lower=0).sum(), a.R.sum()),
  '合并 %d' % len(u): (u.S.clip(lower=0).sum(), u.R.sum()),
}
for nm, t in [('R 集合', topR), ('S 集合', topS)]:
    for dn, (ds, dr) in den.items():
        print(nm, '占', dn, 'S %.2f%% R %.2f%%' % (t.S.clip(lower=0).sum() / ds * 100, t.R.sum() / dr * 100))
# D1 达标者的份额：分母 D1、合并
for nm, thr, key in [('R 门槛', TR, 'R'), ('S 门槛', TS, 'S')]:
    x = D1[D1[key] >= thr]
    print(nm, '达标', len(x), '占 D1 S %.2f%% R %.2f%%' % (x.S.clip(lower=0).sum() / D1.S.clip(lower=0).sum() * 100, x.R.sum() / D1.R.sum() * 100),
          '占合并 S %.2f%% R %.2f%%' % (x.S.clip(lower=0).sum() / den['合并 %d' % len(u)][0] * 100, x.R.sum() / den['合并 %d' % len(u)][1] * 100))
print('D1 占合并 S %.2f%% R %.2f%%' % (D1.S.clip(lower=0).sum() / den['合并 %d' % len(u)][0] * 100, D1.R.sum() / den['合并 %d' % len(u)][1] * 100))
# 新增、回流中金卡以上（月月抽自金卡起才有）
for idn in ['新增', '回流']:
    s = a[a[IDN] == idn]
    g = s[s[CARD] >= 3]
    print(idn, '近一月活跃', len(s), '金卡以上', len(g), '占该身份 %.2f%%' % (len(g) / len(s) * 100), '卡别', g[CARD].value_counts().sort_index().to_dict(),
          '其中 O1（0–7 天、储值>0）', int(g.index.isin(O1.index).sum()))
# 大户集合里新增、回流者的卡别、注册天数
for nm, t in [('R 集合', topR)]:
    for idn in ['新增', '回流']:
        x = t[t[IDN] == idn]
        print(nm, idn, len(x), '卡别', x[CARD].value_counts().sort_index().to_dict(), '注册天数', sorted(x.age.tolist()), 'S 合计', int(x.S.sum()))
# 新增、回流大户占各自身份累计储值
for idn in ['新增', '回流']:
    s = a[a[IDN] == idn]
    x = topR[topR[IDN] == idn]
    print(idn, '大户占该身份（活跃）累计储值 %.2f%%' % (x.S.sum() / s.S.clip(lower=0).sum() * 100))
