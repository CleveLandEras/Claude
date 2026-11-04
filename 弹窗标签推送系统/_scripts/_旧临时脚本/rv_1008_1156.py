# 审查者独立复算（只读）：阶段1 12:00 后新增/未复核数字
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
cols = list(df.columns)
idn = [c for c in cols if '身份' in c][0]
df = df[~df[idn].isin(['機器人', '測試帳號'])].copy()
reg = cols[1]; last = cols[3]; card = [c for c in cols if '卡' in c][0]
pay = [c for c in cols if '总充值' in c or '總充值' in c or '充值金额' in c][0]
bet = [c for c in cols if '总押注' in c or '總押注' in c][0]
ref = pd.Timestamp('2026-09-16')
df['rd'] = pd.to_datetime(df[reg], errors='coerce').dt.normalize()
df['ld'] = pd.to_datetime(df[last], errors='coerce').dt.normalize()
df['dsl'] = (ref - df['ld']).dt.days
df['age'] = (ref - df['rd']).dt.days
print('N', len(df), df[idn].value_counts().to_dict())

pp = df[(df[pay] <= 0) & (df[bet] > 10000)]
print('潜在付费', len(pp), pp[idn].value_counts().to_dict())
print('新增+回流 in 潜在付费', pp[idn].isin(['新增', '回流']).sum())

g = df[df[card] >= 3]
print('金卡以上 全体', len(g), round(len(g) / len(df) * 100, 2), '储值占比', round(g[pay].sum() / df[pay].sum() * 100, 2))
gm = g[~g[idn].isin(['VIP', 'VIP玩家', '黑名單'])]
print('金卡以上 非VIP黑名单', len(gm), 'idn values', df[idn].unique())
print('金卡以上储值占比(只含有储值者分母同)', round(g[pay].sum() / df[pay].sum() * 100, 2))

nvr = df[(df[pay] <= 0) & (df['dsl'] <= 7)]
print('从未储值0-7天', len(nvr), '新增', (nvr[idn] == '新增').sum(), round((nvr[idn] == '新增').mean() * 100, 1))
old = nvr[(nvr[idn] == '持續') & (nvr['age'] >= 365)]
print('持續>=365', len(old), round(len(old) / len(nvr) * 100, 1))
# 新增中 储值者: 恰50 / 总
new = df[df[idn] == '新增']
print('新增储值者', (new[pay] > 0).sum(), '恰50', (new[pay] == 50).sum())
# 普卡储值率 / 回流储值率
rp = df[(df[idn] == '回流') & (df[card] == 1)]
cp = df[(df[idn] == '持續') & (df[card] == 1)]
print('回流普卡储值率', round((rp[pay] > 0).mean() * 100, 2), len(rp), '持續普卡', round((cp[pay] > 0).mean() * 100, 2), len(cp))
# 阶段1 声称: 5条规则..., 14,505: 有储值且充值赠点>=15000 -- 无赠点列时跳过
print([c for c in cols])
