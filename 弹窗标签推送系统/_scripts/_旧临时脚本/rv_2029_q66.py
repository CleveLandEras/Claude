"""审查 20:29：独立复算 A20（Q66）关键数字。只读。"""
import pandas as pd

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
T0 = pd.Timestamp('2026-09-16')

act = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
lost = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
act = act[~act['身份'].isin(['機器人', '測試帳號'])].copy()
lost = lost[~lost['身份'].isin(['機器人', '測試帳號'])].copy()
lost = lost[~lost['会员编号'].isin(set(act['会员编号']))].copy()
act['is_left'] = False
lost['is_left'] = True
m = pd.concat([act, lost], ignore_index=True)

m['lastd'] = pd.to_datetime(m['最後登入時間']).dt.normalize()
m['regd'] = pd.to_datetime(m['注册时间'], errors='coerce').dt.normalize()
m['gap'] = (T0 - m['lastd']).dt.days
m['age'] = (T0 - m['regd']).dt.days
m['money'] = pd.to_numeric(m['总充值金额'], errors='coerce').fillna(0)
m['wager'] = pd.to_numeric(m['游戏总押注'], errors='coerce').fillna(0)
pl = m['登入平台'].astype(str).str.strip().str.lower()
m['is_app'] = pl.isin(['android', 'ios', 'apk'])
m['vipbl'] = m['身份'].isin(['VIP', '黑名單'])
total = m['money'].sum()
print('合并人数', len(m), '离开', int(m['is_left'].sum()), '合并储值', round(total))

silent = m[m['is_left'] | (m['gap'] >= 8)].copy()
print('D8', len(silent), '储值占合并 %.2f%%' % (silent['money'].sum() / total * 100))

hi = silent[(silent['卡别'] >= 3) & (~silent['vipbl'])]
nw = silent[(~silent['is_left']) & (silent['regd'] >= pd.Timestamp('2026-08-18')) & (silent['regd'] <= pd.Timestamp('2026-09-08')) & (silent['lastd'] == silent['regd'])]
rb = silent[(~silent['is_left']) & (silent['身份'] == '回流')]
ids = set(hi['会员编号']) | set(nw['会员编号']) | set(rb['会员编号'])
print('D1', len(hi), 'D2', len(nw), 'D3', len(rb), '并集', len(ids), 'D1∩D3', len(set(hi['会员编号']) & set(rb['会员编号'])))
print('D1 占 D8 储值 %.2f%%；D1 占合并 %.2f%%' % (hi['money'].sum() / silent['money'].sum() * 100, hi['money'].sum() / total * 100))

only = silent[~silent['会员编号'].isin(ids)].copy()
print('独有', len(only), '储值占合并 %.2f%%' % (only['money'].sum() / total * 100))
old = only[only['regd'] < pd.Timestamp('2026-08-01')].copy()
young = only[only['regd'] >= pd.Timestamp('2026-08-01')]
nareg = only[only['regd'].isna()]
print('8/1 后注册', len(young), '占独有 %.2f%%' % (len(young) / len(only) * 100), '老账号', len(old), '缺值', len(nareg))
u1a = young[(young['regd'] <= pd.Timestamp('2026-08-15')) & (young['lastd'] == young['regd'])]
print('U1a', len(u1a), '其中离开者', int(u1a['is_left'].sum()))
print('老账号卡别', old['卡别'].value_counts().sort_index().to_dict(), '身份', old['身份'].value_counts().to_dict())


def band(r):
    if r['is_left']:
        return '离开'
    return '15–31' if r['gap'] >= 15 else '8–14'


old['band'] = old.apply(band, axis=1)
print('老账号分档', old['band'].value_counts().to_dict(), 'App %.2f%%' % (old['is_app'].mean() * 100))

refg = act.copy()
refg = m[(~m['is_left']) & (m['gap'] <= 7) & (m['卡别'] == 1) & (~m['vipbl'])].copy()
q25 = refg['wager'].quantile(0.25)
q50 = refg['wager'].quantile(0.50)
print('参照组', len(refg), 'P25', round(q25), 'P50', round(q50))
top = old[old['wager'] >= q50]
mid = old[(old['wager'] >= q25) & (old['wager'] < q50)]
low = old[old['wager'] < q25]
for nm, g in [('低', low), ('中', mid), ('高', top)]:
    print(nm, len(g), '%.2f%%' % (len(g) / len(old) * 100), g['band'].value_counts().to_dict(),
          '有储值率 %.2f%%' % ((g['money'] > 0).mean() * 100), 'App %.2f%%' % (g['is_app'].mean() * 100))
print('高段中卡别', top['卡别'].value_counts().sort_index().to_dict())
print('老账号押注中位', round(old['wager'].median()), '独有押注中位', round(only['wager'].median()))

for lo, hi_, nm in [(366, 99999, '365 天以上'), (60, 365, '60–365'), (0, 59, '<60')]:
    x = old[(old['age'] >= lo) & (old['age'] <= hi_)]
    r = refg[(refg['age'] >= lo) & (refg['age'] <= hi_)]
    a1 = (x['wager'] >= q50).mean() * 100
    a2 = (r['wager'] >= q50).mean() * 100
    print(nm, len(x), '%.2f' % a1, len(r), '%.2f' % a2, '差 %.2f' % (a1 - a2))

# 敏感性：只用老账号中的普卡、并以 365 天分界为 >=365
op = old[old['卡别'] == 1]
print('老账号普卡', len(op), '其中高段', int((op['wager'] >= q50).sum()))
# 高段里已离开者之外（仍在近一月名单）的人数
print('高段 仍在近一月名单（8–31 天）', int((~top['is_left']).sum()))
rf = act[act['身份'] == '回流']
rfd = (T0 - pd.to_datetime(rf['最後登入時間']).dt.normalize()).dt.days
print('回流', len(rf), '0–7 天', int((rfd <= 7).sum()))
