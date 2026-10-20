"""审查 15:5x 退回 R54、R55、R57、R58 的复算。只读，不带参数。
R54：活动赠点「扣掉新手礼包」按注册时间分口径（2026-06 前注册看 > 0，6 月起看 > 1,000）。
R55：A8 表 3b 剔除 VIP 后，在三组都有人的押注段（共同支撑）上做全体权重标准化。
R57：从未储值、押注 0–1 万、会员等级 > 100 的人数与平台分布（押注部分漏记的信号）。
R58：恰为 1,000 的新增中注册满 8 天者只来注册当天的比例。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('剔除后', len(d))
reg = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
last = pd.to_datetime(d['最後登入時間']).dt.normalize()
d['tenure'] = (pd.Timestamp('2026-09-16') - reg).dt.days
d['days'] = (pd.Timestamp('2026-09-16') - last).dt.days
d['r07'] = d['days'] <= 7
d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
d['pc'] = np.where(d['plat'].isin(['mweb', 'web', 'h5', 'mh5']), '浏览器类', np.where(d['plat'] == '缺值', '缺值', 'App类'))
d['grp'] = np.where(d['身份'].isin(['持續', 'VIP', '黑名單']), '表口径持续', d['身份'])
hd = d['活动赠点']

print('\n==== R54 按注册时间分口径 ====')
pre = reg < '2026-06-01'
print('注册时间缺值', int(reg.isna().sum()), '身份', d.loc[reg.isna(), '身份'].value_counts().to_dict())
for g in ['表口径持续', '回流', '新增']:
    x = d['grp'] == g
    n = int(x.sum())
    print(f'{g} n={n}  6月前注册占比 {pre[x].mean()*100:.2f}%  缺注册时间 {int(reg[x].isna().sum())}')
    for tag, prem in [('缺值按6月前', pre | reg.isna()), ('缺值按6月起', pre)]:
        ok = np.where(prem, hd > 0, hd > 1000)
        k = int(ok[x.values].sum())
        print(f'   分口径（{tag}）: {k} / {n} = {k/n*100:.2f}%')
    print(f'   原 >1,000: {(hd[x] > 1000).mean()*100:.2f}%   原 >0: {(hd[x] > 0).mean()*100:.2f}%   >2,000: {(hd[x] > 2000).mean()*100:.2f}%')
    xp = x & pre
    if xp.sum():
        print(f'   其中 6 月前注册 {int(xp.sum())}：>0 {(hd[xp] > 0).mean()*100:.2f}%，>1,000 {(hd[xp] > 1000).mean()*100:.2f}%')
    xn = x & (reg >= '2026-06-01')
    if xn.sum():
        print(f'   其中 6 月起注册 {int(xn.sum())}：>1,000 {(hd[xn] > 1000).mean()*100:.2f}%')
tot_ok = np.where(pre | reg.isna(), hd > 0, hd > 1000)
print('全体分口径', f'{tot_ok.mean()*100:.2f}%')
r = d['身份'] == '回流'
print('回流 ≤1,000 的人数', int((hd[r] <= 1000).sum()), '其中 6 月前注册', int((hd[r & pre] <= 1000).sum()), '其中 6 月前注册且赠点 ≤0', int((hd[r & pre] <= 0).sum()))

print('\n==== R55 共同支撑标准化 ====')
bb = [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf]
bl = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
d['betb'] = pd.cut(d['游戏总押注'], bb, labels=bl)
G = ['普卡', '银卡', '金卡以上']
vip = d['身份'] == 'VIP'
for name, x in [('全部', d), ('不含 VIP', d[~vip])]:
    cnt = x.groupby(['betb', 'cg'], observed=False).size().unstack().reindex(columns=G)
    rate = x.groupby(['betb', 'cg'], observed=False)['r07'].mean().unstack().reindex(columns=G)
    print(name, '各段各组人数：'); print(cnt.to_string())
    for sname, segs in [('三组都有人的段', [s for s in bl if (cnt.loc[s] > 0).all()]), ('押注 ≥ 10 万 4 段', bl[2:])]:
        w = x['betb'].value_counts().reindex(bl).fillna(0)
        w = w[segs]
        share = w.sum() / len(x) * 100
        std = {g: float((rate.loc[segs, g] * w).sum() / w.sum() * 100) for g in G}
        print(f'  {sname} {segs} 权重覆盖 {share:.2f}%：', {g: round(v, 2) for g, v in std.items()},
              '金减普', round(std['金卡以上'] - std['普卡'], 2), '银减普', round(std['银卡'] - std['普卡'], 2), '金减银', round(std['金卡以上'] - std['银卡'], 2))
    # 原算法（每组各自在有人的段上重归一）
    w = x['betb'].value_counts(normalize=True).reindex(bl).fillna(0)
    std = {}
    for g in G:
        rr = rate[g]; ok = rr.notna() & (w > 0)
        std[g] = round(float((rr[ok] * w[ok]).sum() / w[ok].sum() * 100), 2)
    print('  原算法（各组各自重归一）', std, '差', round(std['金卡以上'] - std['普卡'], 2))

print('\n==== R57 押注部分漏记的信号 ====')
nopay = d['总充值金额'] <= 0
low = (d['游戏总押注'] >= 0) & (d['游戏总押注'] <= 10000)
base = d[nopay & low]
print('从未储值且押注 0–1 万', len(base), '浏览器类占', f"{(base['pc'] == '浏览器类').mean()*100:.2f}%")
s = base[base['会员等级'] > 100]
print('其中会员等级 > 100:', len(s), '平台', s['pc'].value_counts().to_dict(), f"浏览器类占 {(s['pc'] == '浏览器类').mean()*100:.2f}%",
      '身份', s['身份'].value_counts().to_dict(), '押注=0', int((s['游戏总押注'] == 0).sum()))
print('其中会员等级 > 500:', int((base['会员等级'] > 500).sum()), '浏览器类', int(((base['会员等级'] > 500) & (base['pc'] == '浏览器类')).sum()))
nv0 = s[(s['游戏总押注'] == 0) & (s['身份'] != 'VIP') & (s['身份'] != '新增')]
print('368 人中押注=0 的非 VIP 非新增（即原 178 人口径的一部分）', len(nv0))
s2 = s[s['身份'] != 'VIP']
print('368 人中非 VIP', len(s2), '注册天数中位', s['tenure'].median())
ref = d[(d['游戏总押注'] > 10000) & (d['游戏总押注'] <= 20000)]
print('参照：押注 1–2 万者会员等级中位', ref['会员等级'].median(), '第 90 百分位', ref['会员等级'].quantile(.9))
print('合计信号（178 + 23 + 368 去重）', int(((nopay & (d['游戏总押注'] == 0) & (d['会员等级'] > 100) & (d['身份'] != '新增')) | (vip & nopay & (d['游戏总押注'] == 0)) | (nopay & low & (d['会员等级'] > 100))).sum()))

pos = nopay & (d['游戏总押注'] > 0) & (d['游戏总押注'] <= 10000)
b2 = d[pos]
s3 = b2[b2['会员等级'] > 100]
print('\n[押注 > 0 且 ≤ 1 万（审查口径）] 从未储值', len(b2), f"浏览器类 {(b2['pc']=='浏览器类').sum()} = {(b2['pc']=='浏览器类').mean()*100:.2f}%")
print('  会员等级 > 100:', len(s3), '平台', s3['pc'].value_counts().to_dict(), f"浏览器类占 {(s3['pc']=='浏览器类').mean()*100:.2f}%", '身份', s3['身份'].value_counts().to_dict())
print('  会员等级 > 500:', int((b2['会员等级'] > 500).sum()), '浏览器类', int(((b2['会员等级'] > 500) & (b2['pc'] == '浏览器类')).sum()))
print('  368 人注册天数中位', s3['tenure'].median(), '；对照：同口径等级 ≤ 100 者注册天数中位', b2.loc[b2['会员等级'] <= 100, 'tenure'].median())
print('  368 人中 VIP', int((s3['身份'] == 'VIP').sum()), '占潜在付费 25,972', f'{len(s3)/25972*100:.2f}%', '加 201 后', f'{(len(s3)+201)/25972*100:.2f}%')
for t_lo, t_hi in [(0, 365), (365, 1095), (1095, 99999)]:
    q = b2[(b2['tenure'] >= t_lo) & (b2['tenure'] < t_hi)]
    qq = q[q['会员等级'] > 100]
    print(f'  注册 {t_lo}–{t_hi} 天：基数 {len(q)} 浏览器类 {(q["pc"]=="浏览器类").mean()*100:.2f}%；等级>100 {len(qq)} 人，其中浏览器类 {(qq["pc"]=="浏览器类").mean()*100 if len(qq) else 0:.2f}%')

print('\n==== R58 ====')
nw = d[d['身份'] == '新增']
e = nw[nw['活动赠点'] == 1000]
same = reg[e.index] == last[e.index]
print('恰为 1,000:', len(e), '只来注册当天', int(same.sum()), f'{same.mean()*100:.2f}%')
m8 = e['tenure'] >= 8
print('注册满 8 天', int(m8.sum()), '只来当天', int(same[m8].sum()), f'{same[m8].mean()*100:.2f}%', '注册不到 8 天', int((~m8).sum()))
