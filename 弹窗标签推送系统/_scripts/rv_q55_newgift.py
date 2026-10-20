"""审查复算 Q55 / R76（只读）：新增活动赠点恰为 1,000 / 2,000；50 元两档按平台与注册时长交叉。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
ref = pd.Timestamp('2026-09-16')
d['reg'] = (ref - pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()).dt.days
d['last'] = (ref - pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()).dt.days
d['br'] = d['登入平台'].astype(str).str.lower().isin(['web', 'mweb', 'mh5', 'h5'])

nw = d[d['身份'] == '新增']
g = nw['活动赠点'].round(0)
print('新增', len(nw), '赠点=1000', int((g == 1000).sum()), '赠点=2000', int((g == 2000).sum()))
e2 = nw[g == 2000]
print('=2000 押注中位', e2['游戏总押注'].median(), '只来当天(reg==last) %.2f' % ((e2['reg'] == e2['last']).mean() * 100))
print('>1000 %.2f  >2000 %.2f' % ((g > 1000).mean() * 100, (g > 2000).mean() * 100))
# 1000 与 2000 之间的高频值
mid = g[(g > 1000) & (g <= 2100)].value_counts().head(8).to_dict()
print('1000<g<=2100 高频', mid)

pay = d[d['总充值金额'] > 0].copy()
pay['A'] = pay['总充值金额'].round(2)
pay['G'] = pay['充值赠点'].round(0)
s50 = pay[pay['A'] == 50].copy()
s50['tier'] = s50['G'].map({16800: '16800', 15000: '15000'}).fillna('其他')
print('\n储值=50 平台×档位（全部）')
print(pd.crosstab(s50['br'], s50['tier']))
n50 = s50[s50['身份'] == '新增']
print('\n储值=50 平台×档位（新增）')
print(pd.crosstab(n50['br'], n50['tier']))
for t in ['16800', '15000']:
    x = s50[s50['tier'] == t]
    print(t, '人数', len(x), '注册<30天 %.2f' % ((x['reg'] <= 29).mean() * 100),
          '注册<=90 %.2f' % ((x['reg'] <= 90).mean() * 100),
          '注册中位', x['reg'].median(), '浏览器 %.2f' % (x['br'].mean() * 100))
# 注册年份分布
s50['ry'] = pd.to_datetime(s50['注册时间'], errors='coerce').dt.year
print(pd.crosstab(s50['ry'], s50['tier']))
