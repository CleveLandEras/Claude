"""A11 补充：卡别的会员等级下限、储值下限；会员等级与注册天数、活动赠点的关系（Q32）。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['tenure'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间']).dt.normalize()).dt.days
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
lv = d['会员等级']
print('N', len(d))

print('== 各卡别：会员等级最小的 5 个值；储值>0 者的最小 5 个储值；储值≤0 人数')
for c in range(1, 8):
    s = d[d['卡别'] == c]
    p = s[s['总充值金额'] > 0]['总充值金额']
    print(c, len(s), '等级最小', sorted(s['会员等级'])[:5], '| 有储值最小', sorted(p)[:5], '| 储值≤0', (s['总充值金额'] <= 0).sum())

print('\n== 门槛检验：候选下限 T，卡别 ≥ c 的人是否全部 ≥ T；低一档里 ≥ T 的有多少')
for c, T in [(5, 750), (6, 5000), (7, 10000)]:
    ge = d[d['卡别'] >= c]
    below = (ge['会员等级'] < T).sum()
    lower = d[d['卡别'] == c - 1]
    print('卡别≥%d（%d 人）等级 < %d 的 %d 人；卡别 %d（%d 人）里等级 ≥ %d 的 %d 人（%.2f%%）' % (
        c, len(ge), T, below, c - 1, len(lower), T, (lower['会员等级'] >= T).sum(), (lower['会员等级'] >= T).mean() * 100))
    # 本档内紧贴下限的人数
    s = d[d['卡别'] == c]
    print('   卡别 %d 等级在 [%d, %d) 的 %d 人' % (c, T, int(T * 1.1), ((s['会员等级'] >= T) & (s['会员等级'] < T * 1.1)).sum()))

print('\n== 卡别 3、4、2 的等级低位分布（是否也有下限）')
for c in [2, 3, 4]:
    s = d[d['卡别'] == c]
    print(c, '等级<10: %d，<50: %d，<100: %d；分位 1%%/5%% %.0f/%.0f' % (
        (s['会员等级'] < 10).sum(), (s['会员等级'] < 50).sum(), (s['会员等级'] < 100).sum(),
        s['会员等级'].quantile(.01), s['会员等级'].quantile(.05)))
    low = s[s['会员等级'] < 50]
    if len(low):
        print('   其中储值中位 %.0f、押注中位 %.0f、注册天数中位 %.0f、身份 %s' % (
            low['总充值金额'].median(), low['游戏总押注'].median(), low['tenure'].median(), low['身份'].value_counts().to_dict()))

print('\n== 各卡别储值>0 的下限附近：卡别 c 里储值 < 候选下限的人数（含从未储值）')
for c in range(2, 8):
    s = d[d['卡别'] == c]
    q = s[s['总充值金额'] > 0]['总充值金额'].quantile([.01, .05, .1]).round(0).to_dict()
    print(c, '有储值者 1%/5%/10% 分位', q)

print('\n== 会员等级与注册天数、活动赠点')
print('注册时间缺值', d['tenure'].isna().sum())
def partial2(df, x, y, zs):
    r = df[[x, y] + zs].dropna().rank()
    import numpy.linalg as la
    Z = np.column_stack([np.ones(len(r))] + [r[z].to_numpy() for z in zs])
    rx = r[x].to_numpy() - Z @ la.lstsq(Z, r[x].to_numpy(), rcond=None)[0]
    ry = r[y].to_numpy() - Z @ la.lstsq(Z, r[y].to_numpy(), rcond=None)[0]
    return np.corrcoef(rx, ry)[0, 1]
print('等级~注册天数 | 押注、储值 %.4f' % partial2(d, '会员等级', 'tenure', ['游戏总押注', '总充值金额']))
print('等级~押注 | 注册天数、储值 %.4f' % partial2(d, '会员等级', '游戏总押注', ['tenure', '总充值金额']))
print('等级~活动赠点 | 注册天数、押注 %.4f' % partial2(d, '会员等级', '活动赠点', ['tenure', '游戏总押注']))
print('卡别~储值 | 押注、注册天数 %.4f' % partial2(d, '卡别', '总充值金额', ['游戏总押注', 'tenure']))
print('卡别~押注 | 储值、注册天数 %.4f' % partial2(d, '卡别', '游戏总押注', ['总充值金额', 'tenure']))
print('卡别~等级 | 储值、押注 %.4f' % partial2(d, '卡别', '会员等级', ['总充值金额', '游戏总押注']))
print('Spearman 注册天数~活动赠点 %.4f' % d['tenure'].rank().corr(d['活动赠点'].rank()))

print('\n== 注册天数分段的会员等级中位（看是否随时间增长）')
tb = [-1, 30, 90, 180, 365, 730, 1460, 1e9]
tl = ['≤30', '31–90', '91–180', '181–365', '1–2年', '2–4年', '>4年']
d['tb'] = pd.cut(d['tenure'], tb, labels=tl)
print(d.groupby('tb', observed=True).agg(n=('会员等级', 'size'), 等级中位=('会员等级', 'median'),
      押注中位=('游戏总押注', 'median'), 等级为1占比=('会员等级', lambda x: round((x == 1).mean() * 100, 2))).to_string())

print('\n== 等级 1 的 20,207 人：身份、注册天数中位、押注分布')
o = d[lv == 1]
print(o['身份'].value_counts().to_dict(), '注册天数中位', o['tenure'].median(),
      '押注>1万 %d（%.2f%%）' % ((o['游戏总押注'] > 1e4).sum(), (o['游戏总押注'] > 1e4).mean() * 100),
      '押注>10万 %d' % (o['游戏总押注'] > 1e5).sum())

print('\n== VIP 108 人的押注与等级')
v = d[d['身份'] == 'VIP']
print('押注=0 %d，押注中位 %.0f，储值中位 %.0f，等级中位 %.1f' % ((v['游戏总押注'] == 0).sum(), v['游戏总押注'].median(), v['总充值金额'].median(), v['会员等级'].median()))

print('\n== 控制押注后，会员等级是否仍与最后登录相关：同押注段 × 同注册天数段 内，等级高半 vs 低半 0–7 天比例（格≥200 人）')
bb = [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf]
bl = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
d['betb'] = pd.cut(d['游戏总押注'], bb, labels=bl)
rows = []
for b in bl:
    for t in tl:
        s = d[(d['betb'] == b) & (d['tb'] == t)]
        if len(s) < 200: continue
        med = s['会员等级'].median()
        lo = s[s['会员等级'] <= med]; hi = s[s['会员等级'] > med]
        if len(hi) < 30 or len(lo) < 30: continue
        a, bb_ = (lo['days'] <= 7).mean() * 100, (hi['days'] <= 7).mean() * 100
        rows.append((b, t, len(s), med, round(a, 2), round(bb_, 2), round(bb_ - a, 2)))
r = pd.DataFrame(rows, columns=['押注段', '注册段', 'n', '等级中位', '低半0-7天%', '高半0-7天%', '差'])
print(r.to_string(index=False))
print('格数', len(r), '差>0 的格数', (r['差'] > 0).sum(), '差的中位', r['差'].median())
