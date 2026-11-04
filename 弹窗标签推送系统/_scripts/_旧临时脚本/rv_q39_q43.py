"""审查复算 Q39–Q41（R54、R55、R57、R58）与 Q43（押注为 0 的 VIP）。只读，不带参数。"""
import numpy as np
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
print('列名', list(d.columns))
reg = pd.to_datetime(d['注册时间'])
d['rd'] = reg.dt.normalize()
d['ten'] = (pd.Timestamp('2026-09-16') - d['rd']).dt.days
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
d['pcls'] = np.where(d['plat'].isin(['android', 'ios', 'apk']), 'App', np.where(d['plat'] == '缺值', '缺值', '浏览器'))
H = d['活动赠点']; B = d['游戏总押注']; Y = d['总充值金额']; L = d['会员等级']

print('\n[R54 分口径表]')
grp = {'新增': d['身份'] == '新增', '回流': d['身份'] == '回流', '持续表口径': d['身份'].isin(['持續', 'VIP', '黑名單']), '全体': d['身份'].notna()}
for k, g in grp.items():
    x = d[g]
    old = x['rd'] < '2026-06-01'
    na = x['rd'].isna()
    new6 = ~old
    alt = np.where(old, x['活动赠点'] > 0, x['活动赠点'] > 1000)
    alt2 = np.where(old | na, x['活动赠点'] > 0, x['活动赠点'] > 1000)
    print(k, len(x), '6月前 %d (%.2f%%)' % (old.sum(), old.mean() * 100), '缺值', na.sum(),
          '6月前>0 %.2f%%' % ((x.loc[old, '活动赠点'] > 0).mean() * 100 if old.sum() else float('nan')),
          '6月起(含缺值)人数 %d >1000 %.2f%%' % (new6.sum(), (x.loc[new6, '活动赠点'] > 1000).mean() * 100),
          '6月起(不含缺值)人数 %d' % (new6 & ~na).sum(),
          '分口径 %d %.2f%%' % (alt.sum(), alt.mean() * 100), '缺值按>0 %.2f%%' % (alt2.mean() * 100),
          '全员>1000 %.2f%%' % ((x['活动赠点'] > 1000).mean() * 100))
r = d[d['身份'] == '回流']
old = r['rd'] < '2026-06-01'
print('6月前回流 >1000 %.2f%%' % ((r.loc[old, '活动赠点'] > 1000).mean() * 100))

print('\n[R58]')
new = d[d['身份'] == '新增']
e = new['活动赠点'] == 1000; m8 = new['ten'] >= 8; same = new['ten'] == new['days']
print('=1000 满8天', (e & m8).sum(), '只来当天', (e & m8 & same).sum(), '%.2f%%' % ((e & m8 & same).sum() / (e & m8).sum() * 100))

print('\n[R57 注册时长分层]')
lowb = (Y <= 0) & (B > 0) & (B < 1e4)
lowb2 = (Y <= 0) & (B > 0) & (B <= 1e4)
print('lowb(<1万)', lowb.sum(), 'lowb(<=1万)', lowb2.sum())
x = d[lowb2].copy()
hi = x['会员等级'] > 100
print('等级>100', hi.sum(), '浏览器', (hi & (x['pcls'] == '浏览器')).sum(), '身份', x.loc[hi, '身份'].value_counts().to_dict())
print('注册天数中位 高等级 %.1f，等级<=100 %.1f' % (x.loc[hi, 'ten'].median(), x.loc[~hi, 'ten'].median()))
for lab, cond in [('<1年', x['ten'] < 365), ('1–3年', (x['ten'] >= 365) & (x['ten'] < 1095)), ('3年以上', x['ten'] >= 1095),
                  ('1–3年(<=3*365)', (x['ten'] >= 365) & (x['ten'] <= 1095)), ('3年以上(>3*365)', x['ten'] > 1095)]:
    y = x[cond]
    yh = y[y['会员等级'] > 100]
    print(lab, '基数', len(y), '浏览器 %.2f%%' % ((y['pcls'] == '浏览器').mean() * 100 if len(y) else 0),
          '高等级', len(yh), '浏览器 %.2f%%' % ((yh['pcls'] == '浏览器').mean() * 100 if len(yh) else 0))

print('\n[R55 共同支撑限度]')
def cg(c):
    return np.where(c == 1, '普卡', np.where(c == 2, '银卡', '金卡以上'))
bins = [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf]
labs = ['≤1万', '1–10万', '10–100万', '1百万–1千万', '1千万–1亿', '>1亿']
for nm, dd in [('不含VIP', d[d['身份'] != 'VIP'].copy()), ('含VIP', d.copy())]:
    dd['cg'] = cg(dd['卡别']); dd['bs'] = pd.cut(dd['游戏总押注'], bins, labels=labs); dd['a'] = dd['days'] <= 7
    keep = labs[2:]
    w = dd['bs'].value_counts()[keep]; print(nm, '4段占比 %.2f%%' % (w.sum() / len(dd) * 100)); w = w / w.sum()
    print(nm, '权重', w.round(4).to_dict())
    res = {}
    for g in ['普卡', '银卡', '金卡以上']:
        rate = dd[dd['cg'] == g].groupby('bs', observed=False)['a'].mean()[keep]
        res[g] = (rate * w).sum() * 100
    print(nm, {k: round(v, 2) for k, v in res.items()}, '金-普', round(res['金卡以上'] - res['普卡'], 2), '银-普', round(res['银卡'] - res['普卡'], 2), '金-银', round(res['金卡以上'] - res['银卡'], 2))
    s = dd[dd['bs'] == '10–100万']
    print(nm, '10–100万段', s.groupby('cg')['a'].agg(['sum', 'size', 'mean']).to_string())

print('\n[Q43 押注为 0 的 VIP]')
tot = Y.sum()
print('全部累计储值', tot)
v = d[d['身份'] == 'VIP']
v0 = v[v['游戏总押注'] == 0]
v0p = v0[v0['总充值金额'] > 0]
print('VIP', len(v), '押注0', len(v0), '其中有储值', len(v0p), '合计', v0p['总充值金额'].sum(), '%.2f%%' % (v0p['总充值金额'].sum() / tot * 100))
print('60人 中位', v0p['总充值金额'].median(), '四分位', v0p['总充值金额'].quantile([.25, .75]).tolist(), '等级中位', v0p['会员等级'].median())
print('83人 储值中位', v0['总充值金额'].median(), '等级中位', v0['会员等级'].median())
wl = [c for c in d.columns if '输赢' in c or '輸贏' in c]
print('输赢列', wl)
for c in wl:
    print(c, '60人不为0', (v0p[c] != 0).sum())
print('60人 平台', v0p['plat'].value_counts().to_dict(), '0–7天 %.2f%%' % ((v0p['days'] <= 7).mean() * 100))
print('60人 卡别', v0p['卡别'].value_counts().to_dict())
print('60人 活动赠点中位', v0p['活动赠点'].median())
vn = v[(v['游戏总押注'] != 0) & (v['总充值金额'] > 0)]
print('押注不为0 VIP 有储值', len(vn), '占比 %.2f%%' % (vn['总充值金额'].sum() / tot * 100), '中位', vn['总充值金额'].median(),
      '四分位', vn['总充值金额'].quantile([.25, .75]).tolist(), '等级中位', vn['会员等级'].median(), 'web', (vn['plat'] == 'web').sum(),
      '0–7 %.2f%%' % ((vn['days'] <= 7).mean() * 100), '活动赠点中位', vn['活动赠点'].median(), '卡别', vn['卡别'].value_counts().to_dict())
for c in wl:
    print(c, '押注不为0 VIP 有储值 输赢不为0', (vn[c] != 0).sum())
# 剔除 83 人
rest = d.drop(v0.index)
print('剩余', len(rest), '储值', rest['总充值金额'].sum())
gold = lambda z: z.loc[z['卡别'] >= 3, '总充值金额'].sum() / z['总充值金额'].sum() * 100
print('金卡以上占比 全部 %.2f%% 剔除后 %.2f%%' % (gold(d), gold(rest)))
print('剩余VIP', (rest['身份'] == 'VIP').sum(), '占比 %.2f%%' % (rest.loc[rest['身份'] == 'VIP', '总充值金额'].sum() / rest['总充值金额'].sum() * 100))
print('VIP 全部占比 %.2f%%' % (v['总充值金额'].sum() / tot * 100))
def topk(z, frac):
    p = z[z['总充值金额'] > 0].sort_values('总充值金额', ascending=False)
    k = int(len(p) * frac)
    return k, p.head(k)
for frac in [0.001, 0.01, 0.1]:
    k, t = topk(d, frac)
    ins = t.index.isin(v0p.index)
    print('全部 前%.1f%%' % (frac * 100), k, '贡献 %.2f%%' % (t['总充值金额'].sum() / tot * 100), '其中60人', ins.sum(), '占这些人储值 %.2f%%' % (t.loc[ins, '总充值金额'].sum() / t['总充值金额'].sum() * 100))
    k2, t2 = topk(rest, frac)
    print('   剔除后', k2, '贡献 %.2f%%' % (t2['总充值金额'].sum() / rest['总充值金额'].sum() * 100))
nv = d[(d['身份'] != 'VIP') & (d['游戏总押注'] == 0) & (d['总充值金额'] > 0)]
print('非VIP 押注0有储值', len(nv), '占比 %.3f%%' % (nv['总充值金额'].sum() / tot * 100), '中位', nv['总充值金额'].median())
