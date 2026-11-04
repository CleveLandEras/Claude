# 只读复核：会员等级 = floor(游戏总押注 / 100,000) + 1 是否成立；120 名普卡会员等级中位；钻石以上是否都满足等级门槛
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
pred = np.floor(bet / 100000) + 1
print('等级 == floor(押注/1e5)+1 命中率', round((pred == lv).mean() * 100, 2))
print('|差| <= 1 命中率', round(((pred - lv).abs() <= 1).mean() * 100, 2))
print('等级 > 预测 比例', round((lv > pred).mean() * 100, 2), '等级 < 预测 比例', round((lv < pred).mean() * 100, 2))
print('相关', round(np.corrcoef(np.log1p(bet), np.log1p(lv.fillna(0)))[0, 1], 4))
# 按押注分段
for lo, hi in [(0, 0), (1, 1e6), (1e6, 1e7), (1e7, 1e8), (1e8, 1e13)]:
    m = (bet >= lo) & (bet <= hi) if lo == hi else (bet > lo) & (bet <= hi)
    print('押注段', lo, hi, '人数', int(m.sum()), '命中', round((pred[m] == lv[m]).mean() * 100, 2) if m.sum() else None)
# 120 名普卡：押注 1千万-1亿
m = (card == 1) & (bet > 1e7) & (bet <= 1e8)
print('普卡 押注1千万-1亿', int(m.sum()), '等级中位', lv[m].median(), '押注中位', bet[m].median(), '预测等级中位', pred[m].median())
reg = pd.to_datetime(d['注册时间'], errors='coerce')
days = (pd.Timestamp('2026-09-16') - reg.dt.normalize()).dt.days
print('  注册天数中位', days[m].median())
m2 = (card == 2) & (bet > 1e7) & (bet <= 1e8)
print('银卡 押注1千万-1亿', int(m2.sum()), '等级中位', lv[m2].median(), '注册天数中位', days[m2].median())
# 门槛表：钻石(5)750、黑卡(6)5000、至尊(7)10000；银卡储值1000或押注500万
thr_pay = {2: 1000, 3: 3000, 4: 8000, 5: 20000, 6: 50000, 7: 100000}
thr_bet = {2: 5e6, 3: 1.8e7, 4: 4e7, 5: 1e8, 6: 3e8, 7: 6e8}
thr_lv = {5: 750, 6: 5000, 7: 10000}
for c in range(2, 8):
    mc = card == c
    ok = (pay[mc] >= thr_pay[c]) | (bet[mc] >= thr_bet[c])
    if c in thr_lv:
        ok = ok & (lv[mc] >= thr_lv[c])
    print('卡别', c, '人数', int(mc.sum()), '累计值满足本档门槛', round(ok.mean() * 100, 2))
# 应升未升：按累计值满足更高一档门槛却在低档
def top_card(i):
    best = 1
    for c in range(2, 8):
        okc = (pay.iloc[i] >= thr_pay[c]) or (bet.iloc[i] >= thr_bet[c])
        if c in thr_lv:
            okc = okc and (lv.iloc[i] >= thr_lv[c])
        if okc:
            best = c
    return best
tc = np.ones(len(d))
for c in range(2, 8):
    okc = (pay >= thr_pay[c]) | (bet >= thr_bet[c])
    if c in thr_lv:
        okc = okc & (lv >= thr_lv[c])
    tc = np.where(okc, c, tc)
tc = pd.Series(tc, index=d.index)
print('累计值推出的卡别 > 实际卡别 人数', int((tc > card).sum()), '占', round((tc > card).mean() * 100, 2))
print('累计值推出的卡别 < 实际卡别 人数', int((tc < card).sum()), '占', round((tc < card).mean() * 100, 2))
print('其中实际普卡、按累计值应>=银卡', int(((card == 1) & (tc >= 2)).sum()))
