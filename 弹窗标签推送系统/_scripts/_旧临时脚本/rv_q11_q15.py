# 审查复算（只读）：A14 / A15 关键数字
import pandas as pd

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
raw = pd.read_csv(BASE + '近一月活跃_20260916.csv', encoding='utf-8-sig')
lv_raw = pd.read_csv(BASE + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
print('列:', list(raw.columns))

ID = '会员编号'
BAD = ['機器人', '測試帳號']
REF = pd.Timestamp('2026-09-16')


def prep(df):
    df = df.copy()
    df['last'] = pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()
    df['reg'] = pd.to_datetime(df['注册时间'], errors='coerce').dt.normalize()
    df['ld'] = (REF - df['last']).dt.days
    df['rd'] = (REF - df['reg']).dt.days
    df['pay'] = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
    df['bet'] = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
    df['card'] = pd.to_numeric(df['卡别'], errors='coerce')
    return df


raw = prep(raw)
lv_raw = prep(lv_raw)
act = raw[~raw['身份'].isin(BAD)]
lv_all = lv_raw[~lv_raw['身份'].isin(BAD)]
lv = lv_all[~lv_all[ID].isin(act[ID])]
print('活跃', len(act), '离开', len(lv), '合并', len(act) + len(lv))
TOT_A = act['pay'].sum()
TOT_M = TOT_A + lv['pay'].sum()
print('活跃储值', TOT_A, '合并储值', TOT_M)
print('负储值行数 活跃', (act['pay'] < 0).sum(), '离开', (lv['pay'] < 0).sum())

vipbl = ['VIP', '黑名單']
# D1
a_g = act[(act['card'] >= 3) & (~act['身份'].isin(vipbl))]
l_g = lv[(lv['card'] >= 3) & (~lv['身份'].isin(vipbl))]
print('D1 暴露', len(a_g), round(len(a_g) / len(act) * 100, 2), round(a_g['pay'].sum() / TOT_A * 100, 2))
d1a = a_g[a_g['ld'] >= 8]
d1 = pd.concat([d1a, l_g])
print('D1 风险 活跃', len(d1a), '离开', len(l_g), '合计', len(d1), '储值', d1['pay'].sum(), round(d1['pay'].sum() / TOT_M * 100, 2))
top10 = d1['pay'].nlargest(10).sum() / d1['pay'].sum()
print('D1 前10占', round(top10 * 100, 2))
# D8
d8a = act[act['ld'] >= 8]
d8 = pd.concat([d8a, lv])
print('D8', len(d8a), len(lv), len(d8), '储值', d8['pay'].sum(), round(d8['pay'].sum() / TOT_M * 100, 2),
      '正储值部分', round(d8.loc[d8['pay'] > 0, 'pay'].sum() / TOT_M * 100, 2), (d8['pay'] > 0).sum())
d8x = d8[~d8['身份'].isin(vipbl)]
print('D8 剔VIP', len(d8x), round(d8x['pay'].sum() / TOT_M * 100, 2))
# D2
new = act[act['身份'] == '新增']
new8 = new[new['rd'] >= 8]
d2 = new8[new8['last'] == new8['reg']]
print('新增', len(new), '满8天', len(new8), 'D2', len(d2), round(len(d2) / len(new8) * 100, 2))
# D3
ret = act[act['身份'] == '回流']
d3 = ret[ret['ld'] >= 8]
cont = act[act['身份'] == '持續']
print('回流', len(ret), 'D3', len(d3), round(len(d3) / len(ret) * 100, 2), '持續同口径', round((cont['ld'] >= 8).mean() * 100, 2))
# D4b
nev = act[(act['pay'] <= 0) & (~act['身份'].isin(vipbl))]
d4b = nev[nev['ld'] <= 7]
print('从未储值主数', len(nev), 'D4b', len(d4b), '其中押注>1万', (d4b['bet'] > 10000).sum())
# 重叠
ids1, ids2, ids3, ids8 = set(d1[ID]), set(d2[ID]), set(d3[ID]), set(d8[ID])
print('D1⊂D8', ids1 <= ids8, 'D2⊂D8', ids2 <= ids8, 'D3⊂D8', ids3 <= ids8)
print('D1∩D3', len(ids1 & ids3), 'D1∩D2', len(ids1 & ids2), 'D2∩D3', len(ids2 & ids3))
u = ids1 | ids2 | ids3
print('并集', len(u))
uniq = d8[~d8[ID].isin(u)]
print('D8独有', len(uniq), '储值', round(uniq['pay'].sum() / TOT_M * 100, 2))
print(uniq['身份'].value_counts().to_dict())
print('普卡占', round((uniq['card'] == 1).mean() * 100, 2))
print('离开者里身份分布', lv['身份'].value_counts().to_dict())
# E1
bots = raw[raw['身份'] == '機器人']
tests = raw[raw['身份'] == '測試帳號']
print('机器人注册<=29', (bots['rd'] <= 29).sum(), '测试<=29', (tests['rd'] <= 29).sum())
print('0-7天全部行', (raw['ld'] <= 7).sum(), '坏账号0-7', ((raw['ld'] <= 7) & raw['身份'].isin(BAD)).sum())
print('测试有储值', (tests['pay'] > 0).sum(), tests.loc[tests['pay'] > 0, 'pay'].sum())
reg29 = act[act['rd'] <= 29]
reg30 = act[act['rd'] <= 30]
print('注册<=29', len(reg29), '与新增交集', reg29[ID].isin(new[ID]).sum(), '注册<=30', len(reg30))
pay = raw[~raw['身份'].isin(BAD) & (raw['pay'] > 0)]
print('有储值', len(pay), '普银', (pay['card'] <= 2).sum(), '金+', (pay['card'] >= 3).sum(), '0-7天', (pay['ld'] <= 7).sum())
