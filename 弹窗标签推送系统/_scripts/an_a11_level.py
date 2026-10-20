"""A11 会员等级：分布、与卡别的交叉、与储值/押注的关系（Q32）。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(d)
print('N', N)
print('会员等级 缺值', d['会员等级'].isna().sum(), ' 卡别缺值', d['卡别'].isna().sum())
lv = d['会员等级']
print('会员等级 min/max', lv.min(), lv.max(), ' 取值个数', lv.nunique())

pay = d['总充值金额'] > 0
print('有储值者', pay.sum())

# ---- ① 分布 ----
bins = [-1, 0, 1, 2, 5, 10, 20, 30, 50, 80, 1e9]
labs = ['0', '1', '2', '3–5', '6–10', '11–20', '21–30', '31–50', '51–80', '81+']
d['lvb'] = pd.cut(lv, bins, labels=labs)
print('\n== 表1 会员等级分布（全体 / 有储值者）')
t_all = d['lvb'].value_counts().reindex(labs)
t_pay = d.loc[pay, 'lvb'].value_counts().reindex(labs)
t = pd.DataFrame({'全体': t_all, '全体%': (t_all / N * 100).round(2),
                  '有储值': t_pay, '有储值%': (t_pay / pay.sum() * 100).round(2),
                  '该段储值率%': (t_pay / t_all * 100).round(2)})
print(t.to_string())
print('中位数 全体', lv.median(), ' 有储值', lv[pay].median(), ' 无储值', lv[~pay].median())
print('前 10 个取值人数'); print(lv.value_counts().head(10).to_string())

# ---- 与卡别交叉 ----
d['cg'] = pd.cut(d['卡别'], [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上'])
print('\n== 表2 会员等级段 × 卡别（人数）')
ct = pd.crosstab(d['lvb'], d['卡别'])
print(ct.to_string())
print('\n== 各卡别的会员等级分位数')
print(d.groupby('卡别')['会员等级'].describe(percentiles=[.01, .1, .5, .9, .99]).round(1).to_string())
print('\n== 各会员等级段的卡组构成（行%）')
print((pd.crosstab(d['lvb'], d['cg'], normalize='index') * 100).round(2).to_string())

# ---- ② 相关 ----
def sp(a, b):
    return a.rank().corr(b.rank())

cols = ['会员等级', '卡别', '总充值金额', '游戏总押注']
print('\n== 表3 Spearman（全体 62,292）')
print(d[cols].corr(method='spearman').round(4).to_string())
print('\n== Spearman（有储值者）')
print(d.loc[pay, cols].corr(method='spearman').round(4).to_string())

# 偏相关（基于秩）：x~y | z
def partial(df, x, y, z):
    r = df[[x, y, z]].rank().corr()
    rxy, rxz, ryz = r.loc[x, y], r.loc[x, z], r.loc[y, z]
    return (rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))

print('\n== 表4 秩偏相关')
for sub, name in [(d, '全体'), (d[pay], '有储值者')]:
    print(name,
          '卡别~储值|押注 %.4f' % partial(sub, '卡别', '总充值金额', '游戏总押注'),
          '卡别~押注|储值 %.4f' % partial(sub, '卡别', '游戏总押注', '总充值金额'),
          '等级~押注|储值 %.4f' % partial(sub, '会员等级', '游戏总押注', '总充值金额'),
          '等级~储值|押注 %.4f' % partial(sub, '会员等级', '总充值金额', '游戏总押注'))

# 分层：同一押注段内 卡别~储值、等级~储值；同一储值段内 卡别~押注、等级~押注
bb = [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf]
bl = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
db = [-np.inf, 0, 1e3, 1e4, 1e5, np.inf]
dl = ['≤0', '1–1千', '1千–1万', '1万–10万', '>10万']
d['betb'] = pd.cut(d['游戏总押注'], bb, labels=bl)
d['depb'] = pd.cut(d['总充值金额'], db, labels=dl)
print('\n== 表5a 同一押注段内的 Spearman（段内人数；卡别~储值；等级~储值；等级~押注；卡别~押注）')
for b in bl:
    s = d[d['betb'] == b]
    print(b, len(s), 'card~dep %.3f' % sp(s['卡别'], s['总充值金额']),
          'lv~dep %.3f' % sp(s['会员等级'], s['总充值金额']),
          'lv~bet %.3f' % sp(s['会员等级'], s['游戏总押注']),
          'card~bet %.3f' % sp(s['卡别'], s['游戏总押注']))
print('\n== 表5b 同一储值段内的 Spearman（卡别~押注；等级~押注；卡别~储值；等级~储值）')
for b in dl:
    s = d[d['depb'] == b]
    print(b, len(s), 'card~bet %.3f' % sp(s['卡别'], s['游戏总押注']),
          'lv~bet %.3f' % sp(s['会员等级'], s['游戏总押注']),
          'card~dep %.3f' % sp(s['卡别'], s['总充值金额']),
          'lv~dep %.3f' % sp(s['会员等级'], s['总充值金额']))

# 同一押注段内：各卡别的储值中位数（卡别是否随储值分档）
print('\n== 表6 同一押注段内，各卡组有储值者比例与储值中位数（人数≥30）')
for b in bl:
    s = d[d['betb'] == b]
    row = []
    for c in ['普卡', '银卡', '金卡以上']:
        x = s[s['cg'] == c]
        if len(x) >= 30:
            row.append('%s n=%d 储值率%.1f%% 储值中位%.0f' % (c, len(x), (x['总充值金额'] > 0).mean() * 100, x['总充值金额'].median()))
        else:
            row.append('%s n=%d' % (c, len(x)))
    print(b, ' | '.join(row))

# ---- 阈值检查：等级是否是押注的单调函数；卡别是否是储值的单调函数 ----
def overlap_check(df, key, val, name):
    g = df.groupby(key)[val]
    q = g.quantile([.01, .5, .99]).unstack()
    q['n'] = g.size()
    return q

print('\n== 表7 各卡别的累计储值分位数（1% / 50% / 99%）与从未储值人数')
q = overlap_check(d, '卡别', '总充值金额', '卡别')
q['从未储值(≤0)'] = d[d['总充值金额'] <= 0].groupby('卡别').size().reindex(q.index).fillna(0).astype(int)
print(q.round(0).to_string())
print('\n== 表7b 各卡别的累计押注分位数（1% / 50% / 99%）')
print(overlap_check(d, '卡别', '游戏总押注', '卡别').round(0).to_string())

# 等级 vs 押注 的单调性：按等级段的押注分位数
print('\n== 表8 各会员等级段的累计押注分位数（1% / 10% / 50% / 90% / 99%）与储值中位')
g = d.groupby('lvb', observed=True)
q8 = g['游戏总押注'].quantile([.01, .1, .5, .9, .99]).unstack()
q8['n'] = g.size()
q8['储值中位'] = g['总充值金额'].median()
q8['储值率%'] = g['总充值金额'].apply(lambda x: (x > 0).mean() * 100)
print(q8.round(1).to_string())

# 一致对比例：随机抽样对，按押注排序与按等级排序是否同向（Kendall 近似）
rng = np.random.default_rng(0)
def concord(a, b, m=400000):
    i = rng.integers(0, len(a), m); j = rng.integers(0, len(a), m)
    da = np.sign(a[i] - a[j]); db_ = np.sign(b[i] - b[j])
    ok = (da != 0) & (db_ != 0)
    return (da[ok] == db_[ok]).mean(), ok.mean()
A = d['会员等级'].to_numpy(float); B = d['游戏总押注'].to_numpy(float); C = d['卡别'].to_numpy(float); D = d['总充值金额'].to_numpy(float)
print('\n== 表9 抽样对同向比例（两者都不相等的对中）')
print('等级 vs 押注 同向 %.4f（有效对比例 %.3f）' % concord(A, B))
print('等级 vs 储值 同向 %.4f（有效对比例 %.3f）' % concord(A, D))
print('卡别 vs 储值 同向 %.4f（有效对比例 %.3f）' % concord(C, D))
print('卡别 vs 押注 同向 %.4f（有效对比例 %.3f）' % concord(C, B))

# ---- 两类反例人群 ----
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['tenure'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间']).dt.normalize()).dt.days

# ---- 字段量纲：会员等级是不是「等级」，还是一个累计分数 ----
print('\n== 表9b 量纲检查：押注 ÷ 等级（等级 ≥ 1 且押注 > 0）')
m = (d['会员等级'] >= 1) & (d['游戏总押注'] > 0)
r = d.loc[m, '游戏总押注'] / d.loc[m, '会员等级']
print('人数', m.sum(), '分位数', r.quantile([.1, .25, .5, .75, .9]).round(1).to_dict())
for c in range(1, 8):
    mm = m & (d['卡别'] == c)
    print('卡别', c, '押注÷等级 中位 %.0f' % (d.loc[mm, '游戏总押注'] / d.loc[mm, '会员等级']).median())
print('Spearman 等级~注册天数 %.4f；押注~注册天数 %.4f' % (sp(d['会员等级'], d['tenure']), sp(d['游戏总押注'], d['tenure'])))
print('偏相关 等级~注册天数|押注 %.4f' % partial(d, '会员等级', 'tenure', '游戏总押注'))
print('按身份：人数、等级中位、押注中位')
print(d.groupby('身份').agg(n=('会员等级', 'size'), lv=('会员等级', 'median'), bet=('游戏总押注', 'median')).to_string())
print('Spearman 等级~活动赠点 %.4f；等级~充值赠点 %.4f' % (sp(d['会员等级'], d['活动赠点']), sp(d['会员等级'], d['充值赠点'])))
# 同押注段内 等级 与 注册天数
for b in bl:
    s = d[d['betb'] == b]
    print(b, 'lv~tenure %.3f' % sp(s['会员等级'], s['tenure']))

print('\n== 表10 银卡以上从未储值（≤0）者')
x = d[(d['卡别'] >= 2) & (d['总充值金额'] <= 0)]
print('人数', len(x), ' 卡别分布', x['卡别'].value_counts().sort_index().to_dict())
print('押注中位 %.0f，押注>1千万 %d，会员等级中位 %.0f，等级 P10/P90 %.0f/%.0f' % (
    x['游戏总押注'].median(), (x['游戏总押注'] > 1e7).sum(), x['会员等级'].median(),
    x['会员等级'].quantile(.1), x['会员等级'].quantile(.9)))
print('身份', x['身份'].value_counts().to_dict())
print('\n== 表11 押注过千万的普卡')
y = d[(d['卡别'] == 1) & (d['游戏总押注'] > 1e7)]
print('人数', len(y), ' 押注中位 %.0f 储值中位 %.0f 有储值 %d' % (y['游戏总押注'].median(), y['总充值金额'].median(), (y['总充值金额'] > 0).sum()))
print('会员等级中位 %.0f，P10/P90 %.0f/%.0f' % (y['会员等级'].median(), y['会员等级'].quantile(.1), y['会员等级'].quantile(.9)))
z = d[(d['cg'] == '金卡以上') & (d['游戏总押注'] > 1e7) & (d['游戏总押注'] <= 1e8)]
print('对照：押注 1千万–1亿 的金卡以上 %d 人，会员等级中位 %.0f，P10/P90 %.0f/%.0f' % (
    len(z), z['会员等级'].median(), z['会员等级'].quantile(.1), z['会员等级'].quantile(.9)))
z2 = d[(d['cg'] == '普卡') & (d['游戏总押注'] > 1e6) & (d['游戏总押注'] <= 1e7)]
print('对照：押注 1百万–1千万 的普卡 %d 人，会员等级中位 %.0f' % (len(z2), z2['会员等级'].median()))
print('押注过千万普卡 0–7 天 %.2f%%' % ((y['days'] <= 7).mean() * 100))

# 等级在同一押注段内是否与最后登录相关（等级是否比押注多带了活跃信息）
print('\n== 表12 同一押注段内，会员等级高低两半的 0–7 天登录比例')
for b in bl:
    s = d[d['betb'] == b]
    if len(s) < 200: continue
    med = s['会员等级'].median()
    lo = s[s['会员等级'] <= med]; hi = s[s['会员等级'] > med]
    if len(hi) < 30: continue
    print(b, len(s), '等级中位', med, '低半 %.2f%% (n=%d) 高半 %.2f%% (n=%d)' % (
        (lo['days'] <= 7).mean() * 100, len(lo), (hi['days'] <= 7).mean() * 100, len(hi)))

# 卡别 vs 等级 本身
print('\n== 卡别~等级 Spearman %.4f；有储值者 %.4f' % (sp(d['卡别'], d['会员等级']), sp(d.loc[pay, '卡别'], d.loc[pay, '会员等级'])))
print('等级 1 的人数', (lv == 1).sum(), '其中普卡', ((lv == 1) & (d['卡别'] == 1)).sum())
print('等级 1 的人押注中位 %.0f，储值率 %.2f%%' % (d.loc[lv == 1, '游戏总押注'].median(), (d.loc[lv == 1, '总充值金额'] > 0).mean() * 100))
print('按身份的等级中位'); print(d.groupby('身份')['会员等级'].median().to_string())
