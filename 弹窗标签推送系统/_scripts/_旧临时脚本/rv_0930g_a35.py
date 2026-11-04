# 审查 2026-09-30 11:0x：独立复算 A35 关键数（只读）
import pandas as pd
P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
print('列：', list(d.columns))
cols = list(d.columns)
def col(*keys):
    for c in cols:
        if all(k in c for k in keys):
            return c
    raise KeyError(keys)
c_id = col('身份'); c_card = col('卡')
c_pay = col('充值金额'); c_bet = col('押注'); c_win = col('输赢') if any('输赢' in c for c in cols) else col('輸贏')
c_act = col('活动赠点') if any('活动赠点' in c for c in cols) else col('活動')
c_rch = col('充值赠点') if any('充值赠点' in c for c in cols) else col('充值贈')
print('用列：', c_id, c_card, c_pay, c_bet, c_act, c_rch)
d = d[~d[c_id].isin(['機器人', '測試帳號'])].copy()
print('剔除后', len(d))
for c in [c_pay, c_bet, c_act, c_rch]:
    d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0)
d['act0'] = d[c_act].clip(lower=0)
d['grp'] = d[c_card].map({1: '普卡', 2: '银卡', 3: '金卡', 4: '白金', 5: '钻石', 6: '黑卡至尊', 7: '黑卡至尊'})
A = d['act0'].sum(); S = d[c_pay].sum(); B = d[c_bet].sum()
print('活动赠点合计(截0)', A, '保留负值', d[c_act].sum(), '负值人数', (d[c_act] < 0).sum())
print('活动赠点/押注 全体 %.4f%%' % (A / B * 100))
print('名义折算 A/100/S = %.2f%%' % (A / 100 / S * 100), '储值合计', S)
g = d.groupby('grp').agg(n=('act0', 'size'), act=('act0', 'sum'), pay=(c_pay, 'sum'), bet=(c_bet, 'sum'))
g['act_share'] = g.act / A * 100; g['pay_share'] = g.pay / S * 100; g['diff'] = g.act_share - g.pay_share
g['act_per_bet'] = g.act / g.bet * 100
print(g.round(2))
print('普卡/黑卡至尊 倍数 %.2f' % (g.loc['普卡', 'act_per_bet'] / g.loc['黑卡至尊', 'act_per_bet']))
nv = d[d[c_pay] <= 0]
print('从未储值', len(nv), '占活动赠点 %.2f%%' % (nv.act0.sum() / A * 100))
nv2 = nv[nv[c_bet] > 10000]
print('从未储值且押注>1万', len(nv2), '%.2f%%' % (nv2.act0.sum() / A * 100))
ids = d.groupby(c_id).agg(n=('act0', 'size'), act=('act0', 'sum'), pay=(c_pay, 'sum'))
ids['act_share'] = ids.act / A * 100; ids['pay_share'] = ids.pay / S * 100
print(ids.round(2))
# 加赠点
p = d[d[c_pay] > 0].copy()
p['extra'] = (p[c_rch] - 100 * p[c_pay]).clip(lower=0)
E = p.extra.sum()
print('有储值', len(p), '加赠点(截0)', E, '占充值赠点 %.2f%%' % (E / p[c_rch].sum() * 100))
pv = p.groupby(c_id).extra.sum() / E * 100
print('加赠点按身份占比', pv.round(2).to_dict())
# 集中度
for c in ['act0', c_pay]:
    s = d[c].sort_values(ascending=False)
    n = len(s)
    print(c, '前1%% %.1f%%  前10%% %.1f%%' % (s.iloc[:round(n * 0.01)].sum() / s.sum() * 100, s.iloc[:round(n * 0.1)].sum() / s.sum() * 100))
# 高卡去VIP、黑名单 占比
hi = d[d[c_card] >= 3]
hi2 = hi[~hi[c_id].isin(['VIP', '黑名單'])]
print('金卡以上有储值', (hi[c_pay] > 0).sum(), '去VIP黑名单有储值', (hi2[c_pay] > 0).sum(), '去VIP黑名单人数', len(hi2))
