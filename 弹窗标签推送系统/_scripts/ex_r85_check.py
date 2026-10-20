"""R85 回归复算（只读，不带参数）：应升未升 2,742 人与其中 873 名普卡的注册天数分布，
用来判断「新号还没来得及结算」能否解释（结算延迟的一个子情形）。口径同 ex_q59_level.py，注册天数以 2026-09-16 为基准。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd
B = _ROOT + '/数据/'
d = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
bet = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
lv = pd.to_numeric(d['会员等级'], errors='coerce').fillna(0)
pay = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
card = pd.to_numeric(d['卡别'], errors='coerce')
ten = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()).dt.days
thr = {2: (1000, 5e6, 0), 3: (3000, 1.8e7, 0), 4: (8000, 4e7, 0),
       5: (20000, 1e8, 750), 6: (50000, 3e8, 5000), 7: (100000, 6e8, 10000)}
q = pd.Series(1, index=d.index)
for c, (p, b, l) in thr.items():
    q[((pay >= p) | (bet >= b)) & (lv >= l)] = c
hi = q > card
pu = hi & (card == 1)
print('应升未升', hi.sum(), f'{hi.mean()*100:.2f}%', '其中普卡', pu.sum())
for name, m in [('应升未升全体', hi), ('其中普卡', pu)]:
    t = ten[m]
    print(f'{name}: 注册天数有值 {t.notna().sum()}，中位 {t.median():.0f}，<60 天 {(t < 60).sum()}（{(t < 60).sum()/m.sum()*100:.2f}%），<30 天 {(t < 30).sum()}')
# 873 普卡靠哪条达标
print('普卡中储值达标', (pu & (pay >= 1000)).sum(), '押注达标', (pu & (bet >= 5e6)).sum(), '两者都达标', (pu & (pay >= 1000) & (bet >= 5e6)).sum())
