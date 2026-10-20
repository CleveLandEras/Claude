"""Q130 补充：核对与 A25 份额（22.33% / 33.34%）差在哪；提取 02 文本到 _versions/02_text.txt 供对照。只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
import pandas as pd
B = _ROOT + '/'
a = pd.read_csv(B + '数据/近一月活跃_20260916.csv', encoding='utf-8-sig')
c = pd.read_csv(B + '数据/八月登录流失名单_20260916.csv', encoding='utf-8-sig')
col = {k: [x for x in a.columns if k in x][0] for k in ['会员编号', '注册', '最後登入', '卡别', '总充值', '身份']}
ID, IDN = col['会员编号'], col['身份']
for d in (a, c):
    d.drop(d[d[IDN].isin(['機器人', '測試帳號'])].index, inplace=True)
ref = pd.Timestamp('2026-09-16')
def prep(d):
    d = d.copy()
    d['days'] = (ref - pd.to_datetime(d[col['最後登入']]).dt.normalize()).dt.days
    d['age'] = (ref - pd.to_datetime(d[col['注册']], errors='coerce').dt.normalize()).dt.days
    d['S'] = d[col['总充值']]
    d['R'] = d['S'].clip(lower=0) / (d['age'] / 30.44).clip(lower=1)
    return d
a = prep(a); c = prep(c)
leave = c[~c[ID].isin(a[ID])]
u = pd.concat([a, leave])
print('合并口径人数', len(u))
O1 = a[(a.days <= 7) & (a.S > 0) & ~a[IDN].isin(['VIP', '黑名單'])]
O1 = O1[O1.R.notna()]
t = O1.nlargest(134, 'R')
for nm, d in [('活跃 62,292', a), ('合并 74,561', u)]:
    print(nm, 'S 合计', int(d.S.clip(lower=0).sum()), 'R 合计', round(d.R.sum()),
          '大户 S 占 %.2f%%  R 占 %.2f%%' % (t.S.sum() / d.S.clip(lower=0).sum() * 100, t.R.sum() / d.R.sum() * 100))
# 02 文本
h = open(B + '支撑文件/02_弹窗分人群定制方案.html', encoding='utf-8').read()
h = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', h, flags=re.S)
h = re.sub(r'</(p|div|tr|li|h\d|summary|details|table)>', '\n', h)
h = re.sub(r'<[^>]+>', '', h)
h = re.sub(r'\n\s*\n+', '\n', h)
open(B + '_versions/02_text.txt', 'w', encoding='utf-8').write(h)
print('02 文本字数', len(h))
