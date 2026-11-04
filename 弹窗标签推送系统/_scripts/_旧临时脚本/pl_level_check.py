import pandas as pd
import numpy as np
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
d = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
bet = pd.to_numeric(d['游戏总押注'], errors='coerce')
lv = pd.to_numeric(d['会员等级'], errors='coerce')
pred = np.floor(bet / 100000) + 1
ok = (lv == pred)
print('exact match', ok.sum(), round(ok.mean() * 100, 2))
diff = (lv - pred)
print('abs diff<=1', (diff.abs() <= 1).sum(), round((diff.abs() <= 1).mean() * 100, 2))
print('diff describe', diff.describe())
print('corr', np.corrcoef(lv.fillna(0), pred.fillna(0))[0, 1])
# card thresholds: under lifetime cumulative, who qualifies above current card
pay = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
card = pd.to_numeric(d['卡别'], errors='coerce')
thr = {2: (1000, 5e6, 0), 3: (3000, 1.8e7, 0), 4: (8000, 4e7, 0), 5: (20000, 1e8, 750), 6: (50000, 3e8, 5000), 7: (100000, 6e8, 10000)}
q = pd.Series(1, index=d.index)
for c, (p, b, l) in thr.items():
    m = ((pay >= p) | (bet.fillna(0) >= b)) & (lv.fillna(0) >= l)
    q[m] = c
print('lifetime-qualified card > current:', (q > card).sum(), round((q > card).mean() * 100, 2))
print('lifetime-qualified card < current:', (q < card).sum(), round((q < card).mean() * 100, 2))
print(pd.crosstab(card, q))
