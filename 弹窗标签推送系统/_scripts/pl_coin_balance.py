# 规划者只读试算：25 a 答复（总充值=付费，转帐不算）后，用「点数守恒」看从未储值者的币从哪来
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('N', len(d))
for c in ['总充值金额', '游戏总押注', '游戏总输赢', '活动赠点', '充值赠点', 'RTP']:
    print(c, d[c].describe().round(1).to_dict())
# 输赢符号：看 RTP 与输赢关系
d['rtp_calc'] = (d['游戏总押注'] + d['游戏总输赢']) / d['游戏总押注'].where(d['游戏总押注'] > 0)
print('corr rtp vs (bet+winloss)/bet', d[['RTP', 'rtp_calc']].corr().iloc[0, 1])
print(d.loc[d['游戏总押注'] > 0, ['RTP', 'rtp_calc', '游戏总输赢', '游戏总押注']].head(8))
# 来源点数：储值点数 = 总充值*100 + 充值赠点（假设充值赠点为加赠）；另一种：充值赠点已含全部
d['src_a'] = d['总充值金额'] * 100 + d['充值赠点'] + d['活动赠点']
d['src_b'] = d['充值赠点'] + d['活动赠点']
d['loss'] = -d['游戏总输赢']
never = d[d['总充值金额'] <= 0]
pay = d[d['总充值金额'] > 0]
print('never', len(never), 'pay', len(pay))
for name, g in [('never', never), ('pay', pay)]:
    for src in ['src_a', 'src_b']:
        gap = g['loss'] - g[src]
        print(name, src, 'loss>src:', (gap > 0).sum(), ' loss>src+10k:', (gap > 10000).sum(),
              ' loss>src+100k:', (gap > 100000).sum(), ' loss>2*src+100k:', (g['loss'] > 2 * g[src] + 100000).sum())
# 从未储值者：净输 vs 活动赠点 按押注段
never = never.copy()
never['bet_band'] = pd.cut(never['游戏总押注'], [-1, 1e4, 1e5, 1e6, 1e7, 1e8, 1e12],
                           labels=['<=1万', '1-10万', '10-100万', '100-1000万', '1000万-1亿', '>1亿'])
never['excess'] = never['loss'] - never['活动赠点']
print(never.groupby('bet_band', observed=True).agg(n=('会员编号', 'size'),
      loss_med=('loss', 'median'), gift_med=('活动赠点', 'median'),
      excess_pos=('excess', lambda s: (s > 0).mean()),
      excess_big=('excess', lambda s: (s > 100000).mean())).round(3))
# 潜在付费代理（从未储值且押注>1万）中净输超过活动赠点10万点以上的人数
pot = never[never['游戏总押注'] > 10000]
print('potential', len(pot), 'excess>0', (pot['excess'] > 0).sum(), 'excess>100k', (pot['excess'] > 100000).sum())
print('by card', pot.assign(big=pot['excess'] > 100000).groupby('卡别')['big'].agg(['size', 'sum']))
print('by id', pot.assign(big=pot['excess'] > 100000).groupby('身份')['big'].agg(['size', 'sum']))
# VIP 押注为0 有储值者：储值点数去向
v = d[(d['身份'] == 'VIP') & (d['游戏总押注'] == 0) & (d['总充值金额'] > 0)]
print('VIP0 pay n', len(v), 'sum pay', v['总充值金额'].sum(), 'sum pts', (v['总充值金额'] * 100 + v['充值赠点']).sum())
print('never-paid total excess (>0) pts', pot.loc[pot['excess'] > 0, 'excess'].sum())
