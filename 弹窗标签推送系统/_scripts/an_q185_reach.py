# Q185：弹窗之外的人有多少（最后登录分档 × 身份 × 平台类）。只读，不读取任何联系方式。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

B = _ROOT + '/数据/'
act = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
lost = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
bad = ['機器人', '測試帳號']
act = act[~act['身份'].isin(bad)].copy()
lost = lost[~lost['身份'].isin(bad)].copy()
print('活跃', len(act), '流失名单(剔除后)', len(lost))
only = lost[~lost['会员编号'].isin(act['会员编号'])].copy()
print('仅在流失名单(离开者)', len(only))

ref = pd.Timestamp('2026-09-16')
for d in (act, only):
    d['dsl'] = (ref - pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()).dt.days
    p = d['登入平台'].astype(str).str.lower()
    d['plat'] = p.map(lambda x: 'App类' if x in ('android', 'ios', 'apk') else ('浏览器类' if x in ('mweb', 'web', 'h5', 'mh5') else '其他'))


def bucket(x):
    if x == 0:
        return '0天'
    if x <= 7:
        return '1-7天'
    if x <= 14:
        return '8-14天'
    return '15-31天'


act['bk'] = act['dsl'].map(bucket)
only['bk'] = '32-46天(仅流失名单)'
allp = pd.concat([act, only])
print(allp['bk'].value_counts().to_dict(), len(allp))
tot = len(allp)
print('合并口径', tot)

order = ['0天', '1-7天', '8-14天', '15-31天', '32-46天(仅流失名单)']
rows = []
for b in order:
    s = allp[allp['bk'] == b]
    row = {'档': b, '人数': len(s), '占合并': round(len(s) / tot * 100, 2)}
    for idn in ['新增', '回流', '持續']:
        row[idn] = (s['身份'] == idn).sum()
    row['其他身份'] = len(s) - row['新增'] - row['回流'] - row['持續']
    row['App类'] = (s['plat'] == 'App类').sum()
    row['浏览器类'] = (s['plat'] == '浏览器类').sum()
    row['App类占比'] = round((s['plat'] == 'App类').mean() * 100, 2)
    rows.append(row)
print(pd.DataFrame(rows).to_string())

wait = allp[allp['bk'].isin(['8-14天', '15-31天', '32-46天(仅流失名单)'])]
here = allp[allp['bk'].isin(['0天', '1-7天'])]
print('在场0-7天', len(here), round(len(here) / tot * 100, 2))
print('待再来>=8天', len(wait), round(len(wait) / tot * 100, 2))
print('待再来 身份', wait['身份'].value_counts().to_dict())
print('待再来 App类', (wait['plat'] == 'App类').sum(), round((wait['plat'] == 'App类').mean() * 100, 2), '浏览器类', (wait['plat'] == '浏览器类').sum(), '其他', (wait['plat'] == '其他').sum())
print('待再来 有储值', (wait['总充值金额'] > 0).sum(), round((wait['总充值金额'] > 0).mean() * 100, 2))
print('待再来 金卡以上(非VIP黑名单)', ((wait['卡别'] >= 3) & (~wait['身份'].isin(['VIP', '黑名單']))).sum())
# 活跃内 >=8
w2 = act[act['dsl'] >= 8]
print('活跃内>=8天', len(w2), round(len(w2) / len(act) * 100, 2))
print('平台原始取值', allp['登入平台'].astype(str).value_counts().to_dict())
