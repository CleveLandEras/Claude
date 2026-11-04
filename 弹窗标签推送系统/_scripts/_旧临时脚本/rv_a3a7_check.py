"""审查复算 A3、A7（2026-09-28 12:18 审查）。只读，不带参数。"""
import os
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
idt = df['身份'].replace({'VIP': '持續', '黑名單': '持續'})
cardn = df['卡别']
cg = pd.Series(np.where(cardn == 1, '普卡', np.where(cardn == 2, '银卡', '金卡以上')), index=df.index)
ref = pd.Timestamp('2026-09-16')
gap = (ref - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
reg = (ref - pd.to_datetime(df['注册时间'], errors='coerce').dt.normalize()).dt.days
pay = amt > 0
pp = (~pay) & (bet > 10000)
rec = gap <= 7

def pc(a, b):
    return f'{a / b * 100:.2f}%' if b else '-'

print('N', N, '有储值', int(pay.sum()), '从未储值', int((~pay).sum()), '负值', int((amt < 0).sum()))
print('pp', int(pp.sum()), '=0 口径', int(((amt == 0) & (bet > 10000)).sum()), '>=', int(((~pay) & (bet >= 10000)).sum()))
print('pp 普卡', int((pp & (cg == '普卡')).sum()), pc((pp & (cg == '普卡')).sum(), pp.sum()), 'pp 0-7', int((pp & rec).sum()), pc((pp & rec).sum(), pp.sum()))
print('pp 押注中位', bet[pp].median(), 'RTP中位', df.loc[pp, 'RTP'].median())
r = idt == '回流'
print('\n回流', int(r.sum()), '储值率', pc((r & pay).sum(), r.sum()))
rt = amt[r].sum()
for c in ['普卡', '银卡', '金卡以上']:
    m = r & (cg == c)
    print(c, int(m.sum()), pc((m & pay).sum(), m.sum()), '占回流储值', pc(amt[m].sum(), rt), '有储值', int((m & pay).sum()), '中位', amt[m & pay].median())
print('回流有储值中位', amt[r & pay].median())
for lo, hi, nm in [(30, 90, '30-90'), (91, 365, '91-365'), (366, 1095, '1-3y'), (1096, 10**6, '>3y'), (0, 29, '<30')]:
    m = r & (reg >= lo) & (reg <= hi)
    print(nm, int(m.sum()), pc((m & pay).sum(), m.sum()), round(amt[m].sum() / m.sum(), 1) if m.sum() else '-')
for f, nm in [(pay, '回流有储值'), (~pay, '回流从未')]:
    m = r & f
    print(nm, int(m.sum()), '0-7', pc((m & rec).sum(), m.sum()))
print('回流押注>10000', int((r & (bet > 10000)).sum()), '中位', bet[r].median())

print('\n重叠')
nb = idt.isin(['新增', '回流'])
print('B下限', int((nb & pp).sum()), pc((nb & pp).sum(), N), '0-7', int((nb & pp & rec).sum()), pc((nb & pp & rec).sum(), (nb & pp).sum()))
print('B上限', int((nb & (pp | pay)).sum()), pc((nb & (pp | pay)).sum(), N))
for k in ['新增', '回流', '持續']:
    m = idt == k
    print(k, int(m.sum()), 'pp', int((m & pp).sum()), pc((m & pp).sum(), m.sum()), '有储值', int((m & pay).sum()))
print('有储值 金卡以上', int((pay & (cg == '金卡以上')).sum()), pc((pay & (cg == '金卡以上')).sum(), pay.sum()))

print('\n530 人与卡别-储值关系')
hi = (~pay) & (cg != '普卡')
print('银卡以上从未储值', int(hi.sum()), '押注最小', bet[hi].min(), '押注>10万', int((hi & (bet > 100000)).sum()))
print('其中 负值', int((hi & (amt < 0)).sum()), '身份', idt[hi].value_counts().to_dict())
for c in ['银卡', '金卡以上']:
    m = pay & (cg == c)
    print(c, '有储值 最小', amt[m].min(), 'P5', amt[m].quantile(.05), '<1000人数', int((m & (amt < 1000)).sum()), '押注中位', bet[m].median())
m = (~pay) & (cg == '普卡')
print('普卡从未储值 押注>10万', int((m & (bet > 100000)).sum()), '押注最大', bet[m].max())
print('普卡有储值 押注>100万', int((pay & (cg == '普卡') & (bet > 1e6)).sum()))
print('530 人 活动赠点>0', pc((df.loc[hi, '活动赠点'] > 0).sum(), hi.sum()), '赠点中位', df.loc[hi, '活动赠点'].median(), '押注中位', bet[hi].median())
print('530 人 0-7', pc((hi & rec).sum(), hi.sum()))
