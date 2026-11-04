"""审查 20:06 复算：A16（D1）、A19（D4a/D4b）、A18（D3 超出基线）关键数。只读。"""
import numpy as np
import pandas as pd

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']
NOV = ['VIP', '黑名單']
APP = {'android', 'ios', 'apk'}


def prep(d):
    d = d[~d['身份'].isin(EX)].copy()
    d['days'] = (T0 - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
    d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
    d['ten'] = (T0 - d['reg']).dt.days
    d['dep'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
    d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
    d['bon'] = pd.to_numeric(d['充值赠点'], errors='coerce').fillna(0)
    d['nov'] = ~d['身份'].isin(NOV)
    d['app'] = d['登入平台'].fillna('').astype(str).str.strip().str.lower().isin(APP)
    return d


a = prep(pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig'))
c = prep(pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig'))
L = c[~c['会员编号'].isin(a['会员编号'])]
TU = a.dep.sum() + L.dep.sum()
print('活跃', len(a), '离开', len(L), '合并总额', round(TU))

# ---- D1
ga = a[(a['卡别'] >= 3) & a.nov]
gl = L[(L['卡别'] >= 3) & L.nov]
risk = pd.concat([ga[ga.days >= 8], gl])
G = pd.concat([ga, gl])
s = risk.dep.sum()
print('\n[D1] 风险', len(risk), '活跃≥8', int((ga.days >= 8).sum()), '离开', len(gl))
print('  储值', round(s), '占合并 %.2f%%' % (s / TU * 100), '占高卡合并 %.2f%%' % (s / G.dep.sum() * 100))
srt = risk.dep.sort_values(ascending=False)
cs = srt.cumsum() / s
print('  前10 %.2f%%' % (srt.head(10).sum() / s * 100), '50%需', int((cs < .5).sum()) + 1, '80%需', int((cs < .8).sum()) + 1)
print('  离开占人数 %.2f%% 储值 %.2f%%' % (len(gl) / len(risk) * 100, gl.dep.sum() / s * 100))
print('  卡别3 占风险 %.2f%% 占高卡 %.2f%%' % ((risk['卡别'] == 3).mean() * 100, (G['卡别'] == 3).mean() * 100))
print('  风险有储值中位', risk[risk.dep > 0].dep.median(), '0-7天有储值中位', ga[(ga.days <= 7) & (ga.dep > 0)].dep.median())
print('  推播上界', int(risk.app.sum()))
# 755 人按天数分布：8-14 与 15-31 的人在活跃文件里，"还会回来"无数据支撑，只看分布
print('  755 中 8-14 天', int(((ga.days >= 8) & (ga.days <= 14)).sum()), '15-31 天', int((ga.days >= 15).sum()))

# ---- D4a
pay = a[a.dep > 0]
lb = pay[pay.bon < 15000]
print('\n[D4a] 下界', len(lb), '普卡 %.2f%%' % ((lb['卡别'] == 1).mean() * 100), '中位', lb.dep.median(), '0-7天', int((lb.days <= 7).sum()), 'VIP黑', int((~lb.nov).sum()))
ub = pay[(pay.bon >= 15000) & ~((pay.dep == 50) & (pay.bon == 16800)) & pay.nov]
print('  上界金卡以上主数', int((ub['卡别'] >= 3).sum()))

# ---- D4b
nb = a[(a.dep <= 0) & a.nov & (a.days <= 7)]
old = nb[nb.ten >= 366]
print('\n[D4b]', len(nb), '一年以上', len(old), '%.2f%%' % (len(old) / len(nb) * 100))
print('  一年以上按身份', old['身份'].value_counts().to_dict())
print('  一年以上 回流占 %.2f%%' % ((old['身份'] == '回流').mean() * 100))
print('  一年以上 持續 且 押注>1万', int(((old['身份'] == '持續') & (old.bet > 10000)).sum()))
print('  一年以上 押注=0', int((old.bet <= 0).sum()), '押注<=1000', int((old.bet <= 1000).sum()))
print('  一年以上 最后登录 0 天', int((old.days == 0).sum()))

# ---- D3 超出基线
r = a[a['身份'] == '回流'].copy()
p = a[a['身份'] == '持續'].copy()
for d in (r, p):
    d['cg'] = np.where(d['卡别'] == 1, 1, np.where(d['卡别'] == 2, 2, 3))
    d['tb'] = pd.cut(d.ten, [29, 90, 365, 1095, 100000], labels=['30-90', '91-365', '1-3y', '3y+']).astype(str)
    d['pay'] = d.dep > 0
    d['g8'] = d.days >= 8
print('\n[D3] 回流', len(r), '≥8', int(r.g8.sum()))
pos = neg = 0.0
for k, gr in r.groupby(['cg', 'tb', 'pay']):
    if k[1] in ('30-90', 'nan'):
        continue
    gp = p[(p.cg == k[0]) & (p.tb == k[1]) & (p.pay == k[2])]
    if len(gr) < 30 or len(gp) < 30:
        continue
    diff = gr.g8.mean() - gp.g8.mean()
    v = len(gr) * diff
    if v > 0:
        pos += v
    else:
        neg += v
print('  超出基线正 %.1f 负 %.1f 占8542 %.2f%%' % (pos, neg, pos / 8542 * 100))
