import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
import numpy as np
# Q59 / R83 复算：会员报告卡别门槛（储值或押注达标，钻石以上另需账号等级达标）套本地累计值
B = _ROOT + '/数据/'
d = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(d)
print('N', N)
print('卡别取值', d['卡别'].value_counts(dropna=False).sort_index().to_dict())
bet = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
lv = pd.to_numeric(d['会员等级'], errors='coerce').fillna(0)
pay = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
card = pd.to_numeric(d['卡别'], errors='coerce')
print('卡别缺失', card.isna().sum())

# 1) 账号等级公式 floor(押注/10万)+1
pred = np.floor(bet / 100000) + 1
ok = (lv == pred)
print('公式精确命中', ok.sum(), f'{ok.mean()*100:.2f}%')
print('实际等级 > 公式', (lv > pred).sum(), f'{(lv > pred).mean()*100:.2f}%')
print('实际等级 < 公式', (lv < pred).sum(), f'{(lv < pred).mean()*100:.2f}%')

# 2) 门槛表
thr = {2: (1000, 5e6, 0), 3: (3000, 1.8e7, 0), 4: (8000, 4e7, 0),
       5: (20000, 1e8, 750), 6: (50000, 3e8, 5000), 7: (100000, 6e8, 10000)}
q = pd.Series(1, index=d.index)
for c, (p, b, l) in thr.items():
    m = ((pay >= p) | (bet >= b)) & (lv >= l)
    q[m] = c
hi = (q > card)
lo = (q < card)
print('按终身累计应得卡别 > 实际', hi.sum(), f'{hi.mean()*100:.2f}%')
print('  其中实际普卡', (hi & (card == 1)).sum())
print('  其中差一档', (hi & (q - card == 1)).sum(), f'{(hi & (q - card == 1)).sum()/hi.sum()*100:.2f}% of hi')
print('按终身累计应得卡别 < 实际', lo.sum(), f'{lo.mean()*100:.2f}%')

# 3) 各卡别满足本档门槛的比例（本档门槛含等级）
for c, (p, b, l) in thr.items():
    s = card == c
    m = ((pay >= p) | (bet >= b)) & (lv >= l)
    print(f'卡别{c}: {s.sum()} 人, 满足本档门槛 {(s & m).sum()} = {(s & m).sum()/s.sum()*100:.2f}%')

# 4) 卡别 5-7 的会员等级最小值（A11 反推下限）
for c in [5, 6, 7]:
    s = card == c
    print(f'卡别{c} 会员等级 min {lv[s].min():.0f}, 低于门槛人数 {(lv[s] < thr[c][2]).sum()}')
