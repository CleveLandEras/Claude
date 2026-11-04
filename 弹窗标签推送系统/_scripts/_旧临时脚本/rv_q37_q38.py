"""审查复算 Q37、Q38（只读，不带参数）：6,000 押注构成；45 人平台拆分；七成从未储值；A8 标准化 31.49 / 36.60 两种写法。"""
import numpy as np
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('总人数', len(d))
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['a'] = d['days'] <= 7
d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
never = d['总充值金额'] <= 0
print('从未储值', never.sum(), '%.2f%%' % (never.mean() * 100))
for v in [5000, 6000, 7000]:
    x = d[d['游戏总押注'] == v]
    print('押注恰为', v, len(x), x['cg'].value_counts().to_dict(), x['身份'].value_counts().to_dict())
bl = ['≤1万', '1万–10万', '10万–1百万', '1百万–1千万', '1千万–1亿', '>1亿']
d['bs'] = pd.cut(d['游戏总押注'], [-np.inf, 1e4, 1e5, 1e6, 1e7, 1e8, np.inf], labels=bl)
nov = d[d['身份'] != 'VIP']
s = nov[(nov['bs'] == '≤1万') & (nov['cg'] == '银卡')]
print('60 名银卡平台', s['plat'].value_counts().to_dict(), '押注值', s['游戏总押注'].value_counts().to_dict())
g = d[(d['bs'] == '≤1万') & (d['cg'] == '金卡以上')]
print('≤1万 金卡以上', len(g), g['身份'].value_counts().to_dict(), '押注为0', (g['游戏总押注'] == 0).sum())


def stdz(df, common_only):
    rate = df.groupby(['bs', 'cg'], observed=False)['a'].mean().unstack()
    w = df['bs'].value_counts().reindex(bl)
    out = {}
    for c in ['普卡', '银卡', '金卡以上']:
        r = rate[c]
        ok = r.notna() & (w > 0)
        out[c] = float((r[ok] * w[ok]).sum() / w[ok].sum() * 100)
    return {k: round(v, 2) for k, v in out.items()}, round(out['金卡以上'] - out['普卡'], 2)


print('含 VIP 各组各自重归一', stdz(d, False))
print('不含 VIP 各组各自重归一', stdz(nov, False))
