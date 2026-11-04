# 审查者独立复算（只读）：阶段1 本轮引用的关键数字
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
cols = list(df.columns)
print(cols)
idn = [c for c in cols if '身份' in c][0]
df = df[~df[idn].isin(['機器人', '測試帳號'])].copy()
print('N', len(df))
g = lambda *ks: [c for c in cols if all(k in c for k in ks)][0]
reg = cols[1]; last = cols[3]; card = [c for c in cols if '卡' in c][0]
pay = [c for c in cols if '总充值' in c or '總充值' in c or '充值金额' in c][0]
bet = [c for c in cols if '总押注' in c or '總押注' in c][0]
act = [c for c in cols if '活动赠点' in c or '活動贈點' in c][0]
print(reg, last, card, pay, bet, act)
ref = pd.Timestamp('2026-09-16')
df['rd'] = pd.to_datetime(df[reg], errors='coerce').dt.normalize()
df['ld'] = pd.to_datetime(df[last], errors='coerce').dt.normalize()
df['dsl'] = (ref - df['ld']).dt.days
df['age'] = (ref - df['rd']).dt.days

# 卡别储值率
for name, m in [('普卡', df[card] == 1), ('银卡', df[card] == 2), ('金以上', df[card] >= 3), ('银以上', df[card] >= 2)]:
    s = df[m]
    print(name, len(s), round((s[pay] > 0).mean() * 100, 2))

new = df[df[idn] == '新增']
print('新增', len(new), round(len(new) / len(df) * 100, 2))
n8 = new[new['age'] >= 8]
only = n8[n8['rd'] == n8['ld']]
print('满8天', len(n8), '只来当天', len(only), round(len(only) / len(n8) * 100, 2))
b = only[bet]
print('押注0', (b == 0).sum(), '<=1000', (b <= 1000).sum(), round((b <= 1000).mean() * 100, 2))
z = only[b == 0]
print('押注0赠点=1000', (z[act] == 1000).sum(), round((z[act] == 1000).mean() * 100, 2))
print('押注0赠点>=1000', (z[act] >= 1000).sum())
print('押注0赠点分布', z[act].value_counts().head(6).to_dict())

ret = df[df[idn] == '回流']
rp = ret[ret[card] == 1]
print('回流', len(ret), round(len(ret) / len(df) * 100, 2), '普卡', len(rp), round(len(rp) / len(ret) * 100, 2))
print('普卡回流>=8', (rp['dsl'] >= 8).sum(), round((rp['dsl'] >= 8).mean() * 100, 2))
cp = df[(df[idn] == '持續') & (df[card] == 1)]
print('持續普卡>=8', len(cp), round((cp['dsl'] >= 8).mean() * 100, 2))
print('全部回流>=8', (ret['dsl'] >= 8).sum())
nz = rp[(rp[pay] <= 0) & (rp[bet] == 0)]
print('普卡回流 未储值且押注0', len(nz), round(len(nz) / len(rp) * 100, 2))
print('普卡回流 押注0(不论储值)', (rp[bet] == 0).sum())
print('普卡回流 押注0 注册龄中位', nz['age'].median(), '注册<30天', (nz['age'] < 30).sum())

pp = df[(df[pay] <= 0) & (df[bet] > 10000)]
print('潜在付费', len(pp), round(len(pp) / len(df) * 100, 2), '普卡', round((pp[card] == 1).mean() * 100, 2))
print(pp[idn].value_counts().to_dict())
nvr = df[(df[pay] <= 0) & (df['dsl'] <= 7)]
print('从未储值0-7天', len(nvr))
print('新增', (nvr[idn] == '新增').sum(), '持續>=365', ((nvr[idn] == '持續') & (nvr['age'] >= 365)).sum(), '回流>=365', ((nvr[idn] == '回流') & (nvr['age'] >= 365)).sum())
print('持續 注册>=365 且 押注>10000', ((nvr[idn] == '持續') & (nvr['age'] >= 365) & (nvr[bet] > 10000)).sum())
nv_old = nvr[(nvr[idn] == '持續') & (nvr['age'] >= 365)]
print('持續老账号 押注中位', nv_old[bet].median(), '押注=0', (nv_old[bet] == 0).sum())
# 新增 29天内
n29 = new[new['age'] <= 29]
print('新增<=29天', len(n29), '有储值', (n29[pay] > 0).sum(), '恰50', (n29[pay] == 50).sum())
print('新增全体', len(new), '有储值', (new[pay] > 0).sum(), '恰50', (new[pay] == 50).sum())
# 新增的卡别：储值恰50 的多是什么
print('新增 储值值分布top', new[new[pay] > 0][pay].value_counts().head(6).to_dict())
