import numpy as np
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
ref = pd.Timestamp('2026-09-16')
d['last'] = (ref - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['regd'] = (ref - pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()).dt.days
d['r07'] = d['last'] <= 7
pay = d['总充值金额']
bet = d['游戏总押注']
lv = d['会员等级']
card = d['卡别']
plat = d['登入平台'].astype(str).str.lower()
browser = plat.isin(['web', 'mweb', 'mh5', 'h5'])
d['browser'] = browser

print('\n=== A10 ===')
p = d[pay > 0].copy()
print('payers', len(p))
fl = np.floor(p['充值赠点'] / p['总充值金额'])
print('floor eq', (fl == p['储值回馈比']).mean(), 'na', p['储值回馈比'].isna().sum())
print('ratio==100', (p['储值回馈比'] == 100).sum(), '<100', (p['储值回馈比'] < 100).sum())
f = p[(p['总充值金额'] == 50) & (p['储值回马比'.replace('马', '馈')] == 300)]
print('50@300', len(f), f['充值赠点'].unique()[:5])
r300 = p[p['储值回馈比'] == 300]
print('ratio300 total', len(r300), r300['总充值金额'].unique()[:5])
for amt, r in [(70, 200), (30, 333), (33, 303), (50, 336), (30, 108), (30, 100), (50, 100), (60, 104)]:
    g = p[(p['总充值金额'] == amt) & (p['储值回馈比'] == r)]
    print(f'{amt}@{r}', len(g), g['身份'].value_counts().to_dict(), round(g['browser'].mean() * 100, 1))
combos = [(120, 29000), (80, 18240), (80, 18000), (80, 25000), (83, 25000), (150, 39000), (100, 24000)]
for a, pts in combos:
    print('combo', a, pts, ((p['总充值金额'] == a) & (p['充值赠点'] == pts)).sum())
print('pay==50', (p['总充值金额'] == 50).sum(), 'pay==70', (p['总充值金额'] == 70).sum())
pp = d[(pay <= 0) & (bet > 10000)]
print('potential', len(pp))
for name, g in [('f', d.loc[f.index]), ('pp', pp)]:
    print(name, 'card1', round((g['卡别'] == 1).mean() * 100, 2),
          'reg<91', round((g['regd'] < 91).mean() * 100, 2),
          'r07', round(g['r07'].mean() * 100, 2),
          'betmed', g['游戏总押注'].median(),
          'bet>10w', round((g['游戏总押注'] > 100000).mean() * 100, 2),
          'browser', round(g['browser'].mean() * 100, 2),
          'lvmed', g['会员等级'].median())
new_p = p[p['身份'] == '新增']
print('new payers', len(new_p), 'at50', (new_p['总充值金额'] == 50).sum(),
      '50@300', ((new_p['总充值金额'] == 50) & (new_p['储值回馈比'] == 300)).sum())
le100 = p[p['总充值金额'] <= 100]
gt2w = p[p['总充值金额'] > 20000]
print('<=100', len(le100), round((le100['储值回馈比'] >= 150).mean() * 100, 2),
      '>2w', len(gt2w), round((gt2w['储值回馈比'] >= 150).mean() * 100, 2))
print('f pay share', f['总充值金额'].sum() / pay[pay > 0].sum(), pay.sum())

print('\n=== A11 ===')
print('lv range', lv.min(), lv.max(), lv.nunique(), 'med all', lv.median(), 'payers', lv[pay > 0].median())
def spearmanr(a, b):
    return (a.rank().corr(b.rank()),)


fz = d.loc[f.index]
print('f reg<91 excl na', round((fz['regd'] < 91).sum() / fz['regd'].notna().sum() * 100, 2), fz['regd'].isna().sum(),
      'pp', round((pp['regd'] < 91).sum() / pp['regd'].notna().sum() * 100, 2))
print('sp lv~bet', spearmanr(lv, bet)[0], 'lv~pay', spearmanr(lv, pay)[0],
      'card~pay', spearmanr(card, pay)[0], 'card~bet', spearmanr(card, bet)[0])
dd = d.dropna(subset=['regd'])
R = dd[['会员等级', '卡别', '总充值金额', '游戏总押注', 'regd']].rank()


def pcor(x, y, ctrl):
    X = np.column_stack([np.ones(len(R))] + [R[c].values for c in ctrl])
    rx = R[x].values - X @ np.linalg.lstsq(X, R[x].values, rcond=None)[0]
    ry = R[y].values - X @ np.linalg.lstsq(X, R[y].values, rcond=None)[0]
    return np.corrcoef(rx, ry)[0, 1]


print('lv~pay|bet', pcor('会员等级', '总充值金额', ['游戏总押注']))
print('lv~reg|bet,pay', pcor('会员等级', 'regd', ['游戏总押注', '总充值金额']))
print('card~pay|bet,reg', pcor('卡别', '总充值金额', ['游戏总押注', 'regd']))
print('card~bet|pay,reg', pcor('卡别', '游戏总押注', ['总充值金额', 'regd']))
for c in [5, 6, 7]:
    ge = d[card >= c]
    below = d[card == c - 1]
    mins = sorted(d.loc[card == c, '会员等级'])[:3]
    print('card', c, 'n', (card == c).sum(), 'mins', mins, 'ge n', len(ge), 'ge min', ge['会员等级'].min(),
          'below over', (below['会员等级'] >= mins[0]).sum(), len(below))
print('card med lv', d.groupby('卡别')['会员等级'].median().to_dict())
print('card never paid', d[pay <= 0].groupby('卡别').size().to_dict())

# A8 cell
bins = [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf]
d['betseg'] = pd.cut(bet, bins, right=True)
d['cg'] = np.where(card == 1, '普', np.where(card == 2, '银', '金'))
cell = d[(bet > 1e6) & (bet <= 1e7) & (pay > 1000) & (pay <= 10000)].copy()
print('cell n', len(cell))
if len(cell) != 3188:
    cell = d[(bet >= 1e6) & (bet < 1e7) & (pay >= 1000) & (pay < 10000)].copy()
    print('cell alt n', len(cell))
print(cell.groupby('cg').agg(n=('r07', 'size'), r07=('r07', 'mean'), lv=('会员等级', 'median'),
                              reg=('regd', 'median'), pay=('总充值金额', 'median')))
cell['q'] = pd.qcut(cell['会员等级'], 4, labels=False, duplicates='drop')


def mh(a, b):
    num = 0; den = 0
    for q, g in cell.groupby('q'):
        ga = g[g['cg'] == a]; gb = g[g['cg'] == b]
        if len(ga) == 0 or len(gb) == 0:
            continue
        w = len(ga) * len(gb) / (len(ga) + len(gb))
        num += w * (ga['r07'].mean() - gb['r07'].mean()); den += w
    return num / den * 100


print('MH 银-普', mh('银', '普'), '金-普', mh('金', '普'), '金-银', mh('金', '银'))

# 130 普卡 bet>1e7
g130 = d[(card == 1) & (bet > 1e7)]
print('普卡 bet>1e7', len(g130), 'r07', g130['r07'].mean(), 'paymed', g130['总充值金额'].median(),
      'lvmed', g130['会员等级'].median(), 'regmed', g130['regd'].median())
for cgv in ['普', '银', '金']:
    g = d[(d['cg'] == cgv) & (bet > 1e7) & (bet <= 1e8)]
    print('1千万-1亿', cgv, len(g), 'r07', round(g['r07'].mean() * 100, 2), 'paymed', g['总充值金额'].median(),
          'lvmed', g['会员等级'].median(), 'regmed', g['regd'].median(), 'betmed', g['游戏总押注'].median())
# VIP
v = d[d['身份'] == 'VIP']
print('VIP', len(v), 'bet0', (v['游戏总押注'] == 0).sum(), 'in <=1w', (v['游戏总押注'] <= 1e4).sum())
lowgold = d[(bet <= 1e4) & (card >= 3)]
print('<=1w gold', len(lowgold), 'VIP', (lowgold['身份'] == 'VIP').sum(), 'bet0', (lowgold['游戏总押注'] == 0).sum())
