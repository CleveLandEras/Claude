# Q187（潜在流失、破产）口径复算与同卡别离散度。只读。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(df))
df['last'] = pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()
df['dsl'] = (pd.Timestamp('2026-09-16') - df['last']).dt.days
pay = '总充值金额'
main = df[~df['身份'].isin(['VIP', '黑名單'])]
print('main N', len(main))


def grp(c):
    return '普卡' if c == 1 else ('银卡' if c == 2 else '金卡以上')


for name, d in [('含VIP黑名单', df), ('主数', main)]:
    d = d.copy()
    d['g'] = d['卡别'].map(grp)
    print('==', name)
    print('卡别总数', d['g'].value_counts().to_dict())
    hp = d[d[pay] > 0]
    print('有储值', hp['g'].value_counts().to_dict(), len(hp))
    for g in ['普卡', '银卡', '金卡以上']:
        s = hp[hp['g'] == g]
        s0 = s[s['dsl'] <= 7]
        print(g, '有储值', len(s), '0-7天', len(s0), '>=8天', (s['dsl'] >= 8).sum())
        for lab, x in [('全部', s), ('0-7天', s0)]:
            q = x[pay].quantile([.25, .5, .75, .9]).tolist()
            print('  ', lab, 'P25/50/75/90', [round(v) for v in q], 'max', x[pay].max(), 'P90/P25', round(q[3] / q[0], 1) if q[0] else None, '均值', round(x[pay].mean()))
        top = s[pay].value_counts().head(5)
        print('   最常见累计储值', top.to_dict())

# 金卡以上分卡别
m = main[(main['卡别'] >= 3) & (main[pay] > 0)]
print('金卡以上有储值 分卡别')
for c in range(3, 8):
    s = m[m['卡别'] == c]
    q = s[pay].quantile([.25, .5, .75, .9]).tolist()
    print(c, len(s), [round(v) for v in q], round(q[3] / q[0], 1))

# 卡别内：卡别 3 与 7 的中位比
med = m.groupby('卡别')[pay].median()
print('卡别中位', med.to_dict(), '最大/最小', round(med.max() / med.min(), 1))

# 破产数字核对
hp = main[(main[pay] > 0)]
g2 = hp[hp['充值赠点'] >= 15000]
print('有储值且赠点>=15000 主数', len(g2), '其中金卡以上', (g2['卡别'] >= 3).sum(), '占有储值总额', round(g2[g2['卡别'] >= 3][pay].sum() / hp[pay].sum() * 100, 2))
print('其中0-7天', (g2['dsl'] <= 7).sum())
print('从未储值主数', (main[pay] <= 0).sum())

# 金卡以上储值额占比
print('金卡以上储值占活跃总额(含VIP)', round(df[df['卡别'] >= 3][pay].clip(lower=0).sum() / df[pay].clip(lower=0).sum() * 100, 2))
