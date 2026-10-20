# Q184 第一轮（新增、回流、潜在付费）复算核对。只读。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
print(list(df.columns))


def col(*keys):
    for c in df.columns:
        if all(k in c for k in keys):
            return c
    raise KeyError(keys)


c_id = col('会员编号') if any('会员编号' in c for c in df.columns) else df.columns[0]
c_reg = col('注册')
c_last = [c for c in df.columns if '登入時間' in c or '登入时间' in c or ('登' in c and '時間' in c) or ('登' in c and '时间' in c)]
print('last cols', c_last)
c_last = c_last[0]
c_plat = col('平台')
c_card = col('卡别') if any('卡别' in c for c in df.columns) else col('卡')
c_pay = col('充值金额') if any('充值金额' in c for c in df.columns) else col('儲值')
c_bet = col('押注') if any('押注' in c for c in df.columns) else col('押注')
c_act = col('活动赠点') if any('活动赠点' in c for c in df.columns) else col('活動')
c_idn = col('身份')
print(c_reg, c_last, c_plat, c_card, c_pay, c_bet, c_act, c_idn)

df = df[~df[c_idn].isin(['機器人', '測試帳號'])].copy()
print('N', len(df))
df['reg'] = pd.to_datetime(df[c_reg], errors='coerce')
df['last'] = pd.to_datetime(df[c_last], errors='coerce')
ref = pd.Timestamp('2026-09-16')
df['rd'] = df['reg'].dt.normalize()
df['ld'] = df['last'].dt.normalize()
df['days_since_last'] = (ref - df['ld']).dt.days
df['reg_age'] = (ref - df['rd']).dt.days

# ---- 新增 ----
new = df[df[c_idn] == '新增']
print('新增', len(new))
n8 = new[new['reg_age'] >= 8]
print('满8天新增', len(n8))
only = n8[n8['rd'] == n8['ld']]
print('只来当天', len(only), round(len(only) / len(n8) * 100, 2))
b = only[c_bet]
z = only[b == 0]
low = only[(b >= 0) & (b <= 1000)]
print('押注0', len(z), '押注<=1000', len(low), round(len(low) / len(only) * 100, 2))
print('押注0中活动赠点=1000', (z[c_act] == 1000).sum(), round((z[c_act] == 1000).sum() / len(z) * 100, 2))
print('押注0中活动赠点分布前5', z[c_act].value_counts().head(5).to_dict())
lowpos = only[(b > 0) & (b <= 1000)]
print('押注1-1000', len(lowpos), '其中赠点=1000', (lowpos[c_act] == 1000).sum())
# 新增整体有储值
print('新增有储值', (new[c_pay] > 0).sum(), round((new[c_pay] > 0).mean() * 100, 2))
print('新增中50元', (new[c_pay] == 50).sum())
# 来过两天以上的新增 vs 只来当天: 储值率（描述）
rest = n8[n8['rd'] != n8['ld']]
print('满8天新增 非只当天', len(rest), '有储值率', round((rest[c_pay] > 0).mean() * 100, 2), '只当天有储值率', round((only[c_pay] > 0).mean() * 100, 2))

# ---- 回流 ----
ret = df[df[c_idn] == '回流']
print('回流', len(ret))
rp = ret[ret[c_card] == 1]
print('普卡回流', len(rp), '>=8天', (rp['days_since_last'] >= 8).sum(), round((rp['days_since_last'] >= 8).mean() * 100, 2))
cont = df[(df[c_idn] == '持續') & (df[c_card] == 1)]
print('普卡持續>=8天', round((cont['days_since_last'] >= 8).mean() * 100, 2), len(cont))
nz = rp[(rp[c_pay] <= 0) & (rp[c_bet] == 0)]
print('普卡回流 从未储值且押注0', len(nz), round(len(nz) / len(rp) * 100, 2), '其中>=8天', (nz['days_since_last'] >= 8).sum(), round((nz['days_since_last'] >= 8).mean() * 100, 2))
print('回流 >=8天 总', (ret['days_since_last'] >= 8).sum())
# 回流中，8天以上/不足的人: 有储值率
print('普卡回流有储值率', round((rp[c_pay] > 0).mean() * 100, 2), '普卡持續有储值率', round((cont[c_pay] > 0).mean() * 100, 2))
print('回流储值总额', ret[c_pay].clip(lower=0).sum(), '金卡以上回流储值占比', round(ret[ret[c_card] >= 3][c_pay].clip(lower=0).sum() / ret[c_pay].clip(lower=0).sum() * 100, 2))

# ---- 潜在付费 ----
pp = df[(df[c_pay] <= 0) & (df[c_bet] > 10000)]
print('潜在付费', len(pp), '普卡', (pp[c_card] == 1).sum(), round((pp[c_card] == 1).mean() * 100, 2))
print('身份分布', pp[c_idn].value_counts().to_dict())
print('新增+回流 ∩ 潜在付费', len(pp[pp[c_idn].isin(['新增', '回流'])]), round(len(pp[pp[c_idn].isin(['新增', '回流'])]) / len(df) * 100, 2))
nvr = df[(df[c_pay] <= 0) & (df['days_since_last'] <= 7)]
print('从未储值 0-7天', len(nvr))
print('从未储值 0-7天 新增 <30天', (nvr[c_idn] == '新增').sum(), '持續', (nvr[c_idn] == '持續').sum(), '回流', (nvr[c_idn] == '回流').sum())
print('从未储值 0-7天 持續 注册>=365天', ((nvr[c_idn] == '持續') & (nvr['reg_age'] >= 365)).sum())
# 付过费、确定没买首储: 储值>0 且 充值赠点<15000
c_cz = col('充值赠点') if any('充值赠点' in c for c in df.columns) else col('充值')
paid = df[df[c_pay] > 0]
nf = paid[paid[c_cz] < 15000]
print('有储值', len(paid), '确定没买首储', len(nf), '普卡占', round((nf[c_card] == 1).mean() * 100, 2), '储值中位', nf[c_pay].median())
# 新增 29天内 有储值且恰50
