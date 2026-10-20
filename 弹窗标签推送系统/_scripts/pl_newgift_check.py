# 规划者只读试算：Dk 既有资料 ⑦（新手注册＋绑手机合计 2,000）与 ①（首储 NT$50 = 16,800 点）对 A12、A10 的影响量级
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
new = d[d['身份'] == '新增']
print('新增', len(new))
for v in [0, 1000, 2000]:
    g = new[new['活动赠点'].round(0) == v]
    print('活动赠点 ==', v, len(g), 'bet median', g['游戏总押注'].median())
print('新增 活动赠点 top values')
print(new['活动赠点'].round(0).value_counts().head(8))
# 首储指纹
pay50 = d[d['总充值金额'] == 50]
print('储值=50', len(pay50))
print(pay50['充值赠点'].round(0).value_counts().head(6))
