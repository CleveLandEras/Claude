# 只读试算：为 Q86 设计卡定切分方式（在场高卡按卡别 × 注册时长的格子人数、R 分布离散度）
# 不得出结论，只看格子够不够大、分布多偏
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
df = pd.read_csv(BASE + '近一月活跃_20260916.csv', encoding='utf-8-sig')
print('列：', list(df.columns))

def col(*names):
    for n in names:
        if n in df.columns:
            return n
    raise KeyError(names)

c_id = col('会员编号', '會員編號')
c_reg = col('注册时间', '註冊時間')
c_last = col('最後登入時間', '最后登入时间', '最後登入时间')
c_card = col('卡别', '卡別')
c_dep = col('总充值金额', '總充值金額')
c_bet = col('游戏总押注', '遊戲總押注')
c_id2 = col('身份')

df = df[~df[c_id2].isin(['機器人', '測試帳號'])].copy()
print('剔除后人数', len(df))
ref = pd.Timestamp('2026-09-16')
df['last_d'] = (ref.normalize() - pd.to_datetime(df[c_last], errors='coerce').dt.normalize()).dt.days
df['reg_d'] = (ref.normalize() - pd.to_datetime(df[c_reg], errors='coerce').dt.normalize()).dt.days
df['S'] = df[c_dep]
df['R'] = df[c_dep].clip(lower=0) / (df['reg_d'] / 30.44).clip(lower=1)

o1 = df[(df['last_d'] <= 7) & (df[c_dep] > 0) & (~df[c_id2].isin(['VIP', '黑名單']))]
hi = o1[o1[c_card] >= 3].copy()
print('O1 人数', len(o1), '金卡以上', len(hi))

bins = [-1, 90, 365, 1095, 100000]
labels = ['<=90', '91-365', '366-1095', '>1095']
hi['regbin'] = pd.cut(hi['reg_d'], bins=bins, labels=labels)
g = hi.groupby([c_card, 'regbin'], observed=False)['R']
tab = g.agg(['count', 'median', lambda s: s.quantile(0.25), lambda s: s.quantile(0.75)])
tab.columns = ['n', 'R_med', 'R_p25', 'R_p75']
print(tab.round(0))

# 押注段（金卡以上内部三分位）× 卡组，看格子人数
hi['betq'] = pd.qcut(hi[c_bet].rank(method='first'), 3, labels=['低', '中', '高'])
print(hi.groupby(['regbin', 'betq'], observed=False).size())

# 格内「低于中位者补到中位」的 R 缺口，占 O1 金卡以上 R 底盘的比例（只看量级，决定这个参照是否有意义）
def gap(s):
    m = s.median()
    return (m - s[s < m]).sum()
cellgap = hi.groupby([c_card, 'regbin'], observed=False)['R'].apply(gap).sum()
print('格内补到中位的 R 缺口 / O1 高卡 R 底盘 =', round(cellgap / hi['R'].sum() * 100, 1), '%')
# 同押注段口径
cellgap2 = hi.groupby(['regbin', 'betq'], observed=False)['R'].apply(gap).sum()
print('（注册×押注段）格内补到中位缺口 / 底盘 =', round(cellgap2 / hi['R'].sum() * 100, 1), '%')

# D1 风险层人均 R 分布（活跃 >=8 天、金卡以上、有储值与否不限、非VIP）——只看活跃部分的离散度
d1a = df[(df['last_d'] >= 8) & (df[c_card] >= 3) & (~df[c_id2].isin(['VIP', '黑名單']))]
print('D1 活跃部分 人数', len(d1a))
print('D1 活跃部分 R 分位', d1a['R'].quantile([0.25, 0.5, 0.75, 0.9, 0.99]).round(0).to_dict(), '均值', round(d1a['R'].mean(), 0))
print('O1 高卡 R 分位', hi['R'].quantile([0.25, 0.5, 0.75, 0.9, 0.99]).round(0).to_dict(), '均值', round(hi['R'].mean(), 0))
