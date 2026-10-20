"""R72–R74 复算：点数粗算在 1,904 人、银卡以上、金卡以上中的命中数；有储值者对照（本底）。只读，不带参数。
口径同 pl_coin_balance.py：从未储值 = 总充值金额 ≤ 0；超出 = 输掉的点数（−游戏总输赢）− 活动赠点；
有储值者超出 = 输掉的点数 − (总充值 × 100 + 充值赠点 + 活动赠点)；门槛 10 万点。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['loss'] = -d['游戏总输赢']
never = d[d['总充值金额'] <= 0].copy()
pay = d[d['总充值金额'] > 0].copy()
never['big'] = (never['loss'] - never['活动赠点']) > 100000
pay['big'] = (pay['loss'] - (pay['总充值金额'] * 100 + pay['充值赠点'] + pay['活动赠点'])) > 100000
print('从未储值', len(never), ' 超门槛', int(never['big'].sum()), ' 其押注最小', never.loc[never['big'], '游戏总押注'].min())
b = never[never['游戏总押注'] > 1e6]
print('从未储值押注 > 1 百万', len(b), ' 超门槛', int(b['big'].sum()), ' 占 %.2f%%' % (b['big'].mean() * 100))
s = never[never['卡别'] >= 2]
print('从未储值银卡以上', len(s), ' 超门槛', int(s['big'].sum()), ' 占 %.2f%%' % (s['big'].mean() * 100))
g = never[never['卡别'] >= 3]
print('从未储值金卡以上', len(g), ' 超门槛', int(g['big'].sum()), ' 占 %.2f%%' % (g['big'].mean() * 100))
pb = pay[pay['游戏总押注'] > 1e6]
print('有储值', len(pay), ' 超门槛', int(pay['big'].sum()), ' 占 %.2f%%' % (pay['big'].mean() * 100))
print('有储值押注 > 1 百万', len(pb), ' 超门槛', int(pb['big'].sum()), ' 占 %.2f%%' % (pb['big'].mean() * 100))
print('从未储值押注 ≤ 1 百万的超门槛', int(never.loc[never['游戏总押注'] <= 1e6, 'big'].sum()))
print('从未储值银卡以上押注 < 500 万', int((s['游戏总押注'] < 5e6).sum()))
