"""R30 / R33：① 从未储值者按累计押注 >1 百万、>1 千万、>1 亿的人数（按卡组、身份），潜在付费上限 25,972 与
A7 下限 9,786 对这批人的敏感度；② A3 表 5「0–7 天合计」用人数直接相除核对。不带参数运行，只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
pay, bet = '总充值金额', '游戏总押注'
df[pay] = pd.to_numeric(df[pay], errors='coerce').fillna(0)
df[bet] = pd.to_numeric(df[bet], errors='coerce').fillna(0)
df['活动赠点'] = pd.to_numeric(df['活动赠点'], errors='coerce').fillna(0)
df['身份3'] = df['身份'].replace({'VIP': '持續', '黑名單': '持續'})
df['卡组'] = np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上'))
df['付费'] = df[pay] > 0
ref = pd.Timestamp('2026-09-16')
df['距末登'] = (ref - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
print('剔除后', N, '有储值', int(df['付费'].sum()), '从未储值', int((~df['付费']).sum()))

np_ = df[~df['付费']]
pp = np_[np_[bet] > 10000]
print('潜在付费上限', len(pp))
print('从未储值押注：最大', int(np_[bet].max()), '中位', round(np_[bet].median()))

print('\n== ① 从未储值 × 押注极大（分母：从未储值 44,027；潜在付费 25,972） ==')
ths = [1e6, 1e7, 1e8]
for th in ths:
    s = np_[np_[bet] > th]
    print(f'押注>{int(th):,}：{len(s)}（占从未储值 {len(s)/len(np_)*100:.2f}%，占潜在付费 {len(s)/len(pp)*100:.2f}%）',
          '卡组', s['卡组'].value_counts().reindex(['普卡', '银卡', '金卡以上'], fill_value=0).to_dict(),
          '身份', s['身份3'].value_counts().reindex(['持續', '回流', '新增'], fill_value=0).to_dict(),
          '0–7天登录', int((s['距末登'] <= 7).sum()),
          f'剔除后潜在付费 {len(pp) - len(s)}')

print('\n== 对照：有储值者押注分布（分母：有储值 18,265） ==')
pd_ = df[df['付费']]
for th in ths:
    s = pd_[pd_[bet] > th]
    print(f'押注>{int(th):,}：{len(s)}（{len(s)/len(pd_)*100:.2f}%）')
print('有储值押注 P90', round(pd_[bet].quantile(.9)), 'P99', round(pd_[bet].quantile(.99)))
print('从未储值押注 P90', round(np_[bet].quantile(.9)), 'P99', round(np_[bet].quantile(.99)))

print('\n== 530 人（从未储值 × 银卡以上） ==')
h = np_[np_['卡组'] != '普卡']
print('人数', len(h), '押注最小', int(h[bet].min()), '中位', round(h[bet].median()), '最大', int(h[bet].max()))
for th in ths:
    print(f'  押注>{int(th):,}', int((h[bet] > th).sum()))

print('\n== 押注 / 活动赠点 比值中位（赠点>0 者） ==')
for name, s in [('潜在付费', pp), ('有储值', pd_), ('从未储值押注>1百万', np_[np_[bet] > 1e6])]:
    t = s[s['活动赠点'] > 0]
    print(name, len(t), '比值中位', round((t[bet] / t['活动赠点']).median(), 1))

print('\n== A7 下限 9,786（新增或回流 ∩ 潜在付费）敏感度 ==')
nr = pp[pp['身份3'].isin(['新增', '回流'])]
print('下限', len(nr))
for th in ths:
    print(f'  剔除押注>{int(th):,}：减 {int((nr[bet] > th).sum())}，剩 {len(nr) - int((nr[bet] > th).sum())}')

print('\n== ② A3 表 5 0–7 天合计（人数直接相除） ==')
groups = [('回流', df[df['身份3'] == '回流']),
          ('回流·有储值', df[(df['身份3'] == '回流') & df['付费']]),
          ('回流·从未储值', df[(df['身份3'] == '回流') & ~df['付费']]),
          ('持续', df[df['身份3'] == '持續']),
          ('新增', df[df['身份3'] == '新增']),
          ('潜在付费', pp)]
for name, s in groups:
    k = int((s['距末登'] <= 7).sum())
    print(name, len(s), '0–7天', k, f'{k/len(s)*100:.2f}%')
