# 只读复核 Q59：卡别 5-7 最小会员等级；应升未升 2,742 人中只差一档比例；873 名普卡注册时长（检验「结算延迟」解释）
import pandas as pd
import numpy as np

p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
bet = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
lv = pd.to_numeric(d['会员等级'], errors='coerce')
pay = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
card = pd.to_numeric(d['卡别'], errors='coerce')
for c in (5, 6, 7):
    print('卡别', c, '最小等级', lv[card == c].min(), '人数', int((card == c).sum()))
thr_pay = {2: 1000, 3: 3000, 4: 8000, 5: 20000, 6: 50000, 7: 100000}
thr_bet = {2: 5e6, 3: 1.8e7, 4: 4e7, 5: 1e8, 6: 3e8, 7: 6e8}
thr_lv = {5: 750, 6: 5000, 7: 10000}
tc = np.ones(len(d))
for c in range(2, 8):
    okc = (pay >= thr_pay[c]) | (bet >= thr_bet[c])
    if c in thr_lv:
        okc = okc & (lv >= thr_lv[c])
    tc = np.where(okc, c, tc)
tc = pd.Series(tc, index=d.index)
up = tc > card
print('应升未升', int(up.sum()), round(up.mean() * 100, 2))
print('其中只差一档', round(((tc - card)[up] == 1).mean() * 100, 2))
reg = pd.to_datetime(d['注册时间'], errors='coerce')
days = (pd.Timestamp('2026-09-16') - reg.dt.normalize()).dt.days
m873 = (card == 1) & (tc >= 2)
print('普卡应>=银卡', int(m873.sum()), '注册天数中位', days[m873].median(), '注册<=60天占', round((days[m873] <= 60).mean() * 100, 2))
print('  其中靠储值达标', int((m873 & (pay >= 1000)).sum()), '靠押注达标', int((m873 & (bet >= 5e6)).sum()))
print('全部应升未升 注册<=60天占', round((days[up] <= 60).mean() * 100, 2))
