"""审查者复算：A2 储值档位分布、环节1 R21 更正（注册时长表、最后登录）。只读。"""
import pandas as pd

p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
d['id3'] = d['身份'].replace({'VIP': '持續', '黑名單': '持續'})
d['amt'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
d['cg'] = d['卡别'].map(lambda c: {1: '普卡', 2: '银卡'}.get(c, '金卡以上'))
base = pd.Timestamp('2026-09-16')
reg = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
d['rdays'] = (base - reg).dt.days
lg = pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()
d['ldays'] = (base - lg).dt.days

pay = d[d['amt'] > 0].copy()
print('有储值', len(pay), '总额', d['amt'].sum())


def tier(s):
    n = len(s)
    a = s['amt']
    c = [(a < 200).sum(), ((a >= 200) & (a < 1000)).sum(), ((a >= 1000) & (a < 10000)).sum(), (a >= 10000).sum()]
    return n, [f'{x}({x / n * 100:.2f}%)' for x in c], a.median()


print('== 全体', tier(pay))
for k, s in pay.groupby('id3'):
    print('身份', k, tier(s))
for k, s in pay.groupby('卡别'):
    print('卡别', k, tier(s))
for k, s in pay.groupby('cg'):
    print('卡组', k, tier(s))
for k, s in pay.groupby(['id3', 'cg']):
    print('身份卡组', k, tier(s))

print('<200 中普卡', ((pay['amt'] < 200) & (pay['cg'] == '普卡')).sum(), (pay['amt'] < 200).sum())
nw = d[d['id3'] == '新增']
print('新增普卡', (nw['cg'] == '普卡').sum(), len(nw))
pn = pay[pay['id3'] == '新增']
print('有储值新增普卡', (pn['cg'] == '普卡').sum(), len(pn))
tot = d['amt'].sum()
a = pay['amt']
for lo, hi in [(0, 200), (200, 1000), (1000, 10000), (10000, 1e18)]:
    m = (a >= lo) & (a < hi)
    print('档', lo, m.sum(), f'{a[m].sum() / tot * 100:.2f}%')
q = pay[pay['rdays'].between(0, 90)]
for k, s in q.groupby('id3'):
    print('0-90', k, len(s), f"{(s['amt'] < 200).mean() * 100:.2f}%")
q3 = q[q['cg'] == '普卡']
for k, s in q3.groupby('id3'):
    print('0-90普卡', k, len(s), f"{(s['amt'] < 200).mean() * 100:.2f}%", s['amt'].median())
for k, s in pay.groupby('id3'):
    print('<=50', k, (s['amt'] <= 50).sum(), len(s))

print('== R21 注册时长')
for k, s in d.groupby('id3'):
    r = s['rdays']
    print(k, len(s), 'null', r.isna().sum(), '0-29', r.between(0, 29).sum(), '30-90', r.between(30, 90).sum(),
          '91-365', r.between(91, 365).sum(), '366-1095', r.between(366, 1095).sum(), '>1095', (r > 1095).sum(),
          'min', r.min(), 'neg', (r < 0).sum())
    print('  >1y', (r > 365).sum(), f'{(r > 365).sum() / len(s) * 100:.2f}%', '>3y', f'{(r > 1095).sum() / len(s) * 100:.2f}%')
cs = d[d['id3'] == '持續']
print('持续最晚注册日', reg[cs.index].max(), (reg[cs.index] == reg[cs.index].max()).sum())
print('新增注册日范围', reg[nw.index].min(), reg[nw.index].max())
print('== R21 最后登录')
for k, s in d.groupby('id3'):
    l = s['ldays']
    print(k, len(s), 'null', l.isna().sum(), 'day0', (l == 0).sum(), '<=7', f'{(l <= 7).mean() * 100:.2f}%',
          '0-6', f'{(l <= 6).mean() * 100:.2f}%', '15-31', f'{l.between(15, 31).mean() * 100:.2f}%',
          'max', l.max())
