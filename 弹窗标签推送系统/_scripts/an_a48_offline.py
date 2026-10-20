# A48 推送受众：离线分档、构成、各通路受众侧范围（不输出会员编号、不读联系方式）
import numpy as np
import pandas as pd
from an_a45_members import load, _read

df, m = load()
pay, bet, idn, card, plat = m['pay'], m['bet'], m['idn'], m['card'], m['plat']
dfa, ma = _read('八月登录流失名单_20260916.csv')
only = dfa[~dfa[ma['id']].isin(set(df[m['id']]))].copy()
N = len(df)
TOT = df[pay].sum()
TOT_M = TOT + only[pay].sum()
print('活跃 N', N, '已离开者（仅名单）', len(only), '合并', N + len(only), '累计储值 活跃', int(TOT), '已离开者', int(only[pay].sum()), '合并', int(TOT_M))

for d in (df, only):
    d['tier'] = np.where(d[card] == 1, '普卡', np.where(d[card] == 2, '银卡', '金卡以上'))
    d['p'] = d[plat].astype(str).str.lower()
    d['app'] = d['p'].isin(['android', 'ios', 'apk'])
    d['web'] = d['p'].isin(['mweb', 'web', 'h5', 'mh5'])
al = pd.concat([df.assign(src='活跃'), only.assign(src='名单独有')], ignore_index=True)
M = len(al)

print('\n=== ① 分档 ===')
def layer(x):
    if x == 0: return '0天'
    if x <= 7: return '1-7天'
    if x <= 14: return '8-14天'
    if x <= 31: return '15-31天'
    return '32-46天'
al['layer'] = al['dsl'].apply(layer)
order = ['0天', '1-7天', '8-14天', '15-31天', '32-46天']
vc = al['layer'].value_counts().reindex(order)
print(vc.to_dict())
pres = int((al['dsl'] <= 7).sum()); off = int((al['dsl'] >= 8).sum()); off15 = int((al['dsl'] >= 15).sum())
print('在场', pres, '离线≥8', off, f'{off / M * 100:.2f}%', '≥15', off15, f'{off15 / M * 100:.2f}%')
print('活跃内离线', int((df['dsl'] >= 8).sum()), f"{(df['dsl'] >= 8).mean() * 100:.2f}%", '活跃内 ≥15', int((df['dsl'] >= 15).sum()))
print('恒等式', pres, '+', int((df['dsl'] >= 8).sum()), '+', len(only), '=', pres + int((df['dsl'] >= 8).sum()) + len(only), ' 在场+活跃内离线=', pres + int((df['dsl'] >= 8).sum()))

print('\n逐日人数（合并）')
daily = al['dsl'].value_counts().sort_index()
print(daily.to_dict())
s = daily[daily.index >= 8]
drops = [(int(i), int(s[i - 1]), int(s[i]), round((1 - s[i] / s[i - 1]) * 100, 1)) for i in s.index if i - 1 in s.index and s[i - 1] > 0 and (1 - s[i] / s[i - 1]) >= 0.30]
print('gap≥8 内相邻两日降幅≥30%:', drops)
print('仅活跃内 逐日 gap≥8 降幅≥30%:')
d2 = df['dsl'].value_counts().sort_index(); s2 = d2[d2.index >= 8]
print([(int(i), int(s2[i - 1]), int(s2[i])) for i in s2.index if i - 1 in s2.index and (1 - s2[i] / s2[i - 1]) >= 0.30])
l814 = al[al['layer'] == '8-14天']
print('8-14天 最后登录星期', l814['ld'].dt.dayofweek.value_counts().sort_index().to_dict(), '(0=周一)')

print('\n=== ② 构成 ===')
for L in ['8-14天', '15-31天', '32-46天']:
    x = al[al['layer'] == L]
    print(f'--- {L} n={len(x):,}')
    print('  身份', x[idn].value_counts().to_dict(), '卡别', x['tier'].value_counts().to_dict())
    print('  有储值', int((x[pay] > 0).sum()), f'{(x[pay] > 0).mean() * 100:.2f}%', '储值合计', int(x[pay].sum()))
offl = al[al['dsl'] >= 8]
print('--- 离线合计 n=', len(offl), '身份', offl[idn].value_counts().to_dict(), '卡别', offl['tier'].value_counts().to_dict())
print('  有储值', int((offl[pay] > 0).sum()), f"{(offl[pay] > 0).mean() * 100:.2f}%", '储值合计', int(offl[pay].sum()), '占合并口径', round(offl[pay].sum() / TOT_M * 100, 2))
oa = df[df['dsl'] >= 8]
print('--- 活跃内离线 储值合计', int(oa[pay].sum()), '占活跃口径', round(oa[pay].sum() / TOT * 100, 2))
print('金卡以上离线 非VIP黑名單', int(((offl['tier'] == '金卡以上') & ~offl[idn].isin(['VIP', '黑名單'])).sum()), '含', int((offl['tier'] == '金卡以上').sum()))
print('已离开者 有储值', int((only[pay] > 0).sum()), '储值合计', int(only[pay].sum()), '身份', only[idn].value_counts().to_dict(), '卡别', only['tier'].value_counts().to_dict())

print('\n--- 离线 × 五类（活跃内，分母=各类自身）---')
S = {'新增': df['is_new'], '回流存量': df['is_back'], '潜在付费宽': df['pp_wide'], '潜在流失宽': df['churn_ub']}
for k, g in S.items():
    n = int(g.sum()); o = int((g & (df['dsl'] >= 8)).sum()); o15 = int((g & (df['dsl'] >= 15)).sum())
    print(f'  {k}: {n:,}  ≥8天 {o:,} ({o / n * 100:.2f}%)  ≥15天 {o15:,} ({o15 / n * 100:.2f}%)')

print('\n=== ③ 通路受众侧 ===')
print('离线 App 类（android/ios/apk）', int(offl['app'].sum()), f"{offl['app'].mean() * 100:.2f}%", '浏览器类', int(offl['web'].sum()), '空/未归类', int((~offl['app'] & ~offl['web']).sum()))
print('平台取值', offl['p'].value_counts().to_dict())
print('≥15天 App 类', int(al[al['dsl'] >= 15]['app'].sum()), '共', off15)
for L in ['8-14天', '15-31天', '32-46天']:
    x = al[al['layer'] == L]
    print(f'  {L} App {x["app"].mean() * 100:.2f}%')

print('\n=== 反例检查 ===')
for L in ['8-14天', '15-31天', '32-46天']:
    x = al[al['layer'] == L]
    print(f'{L} 金卡以上占 {(x["tier"] == "金卡以上").mean() * 100:.2f}%  有储值率 {(x[pay] > 0).mean() * 100:.2f}%')
print('回流存量 ≥8天', int((df['is_back'] & (df['dsl'] >= 8)).sum()), '在场', int((df['is_back'] & (df['dsl'] <= 7)).sum()))
