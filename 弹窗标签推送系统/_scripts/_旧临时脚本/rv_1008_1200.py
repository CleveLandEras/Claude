# 审查复核 Q187：只读
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(df))
df['last'] = pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()
df['dsl'] = (pd.Timestamp('2026-09-16') - df['last']).dt.days
pay = '总充值金额'
main = df[~df['身份'].isin(['VIP', '黑名單'])]
hp = main[main[pay] > 0]

# 1 在场有储值
for lab, f in [('普卡', hp['卡别'] == 1), ('银卡', hp['卡别'] == 2), ('金卡以上', hp['卡别'] >= 3)]:
    s = hp[f]
    print(lab, len(s), (s['dsl'] <= 7).sum(), (s['dsl'] >= 8).sum())

# 2 卡别带宽：每个卡别累计储值的最小/最大，看分档是否由卡别阈值决定
for c in range(1, 8):
    s = hp[hp['卡别'] == c][pay]
    print('卡别', c, 'n', len(s), 'min', s.min(), 'P1', s.quantile(.01), 'P99', s.quantile(.99), 'max', s.max())

# 3 破产：14,505 的构成与占比
g2 = hp[hp['充值赠点'] >= 15000]
print('g2', len(g2), '金卡以上', (g2['卡别'] >= 3).sum())
hi = g2[g2['卡别'] >= 3]
print('金卡以上储值/有储值总额', round(hi[pay].sum() / hp[pay].sum() * 100, 2))
print('金卡以上储值/g2储值', round(hi[pay].sum() / g2[pay].sum() * 100, 2))
print('g2占有储值人数', round(len(g2) / len(hp) * 100, 2))
# 充值赠点 >=15000 的卡别分布
print(g2['卡别'].value_counts().sort_index().to_dict())
print('有储值但赠点<15000', (hp['充值赠点'] < 15000).sum(), '其中普卡', ((hp['充值赠点'] < 15000) & (hp['卡别'] == 1)).sum())

# 4 金卡以上当天登录
mm = main[main['卡别'] >= 3]
print('金卡以上主数', len(mm), '0天', (mm['dsl'] == 0).sum(), round((mm['dsl'] == 0).mean() * 100, 1))
# 5 金卡以上 >=8 天的有储值 / 无储值
print('金卡以上>=8天', (mm['dsl'] >= 8).sum(), '其中有储值', ((mm['dsl'] >= 8) & (mm[pay] > 0)).sum())
