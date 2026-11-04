# 审查者只读复算：A45/A46 关键数字（独立于 an_a45_members.py 的口径写法）
import pandas as pd
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
df = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = list(df.columns)
print(c)
idn = [x for x in c if '身份' in x][0]
card = [x for x in c if '卡' in x][0]
pay = [x for x in c if '总充值' in x or '總充值' in x][0]
bet = [x for x in c if '总押注' in x or '總押注' in x][0]
act = [x for x in c if '活动赠点' in x or '活動贈點' in x][0]
dep = [x for x in c if '充值赠点' in x or '充值贈點' in x][0]
df = df[~df[idn].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
df['age'] = (ref - pd.to_datetime(df[c[1]], errors='coerce').dt.normalize()).dt.days
df['dsl'] = (ref - pd.to_datetime(df[c[3]], errors='coerce').dt.normalize()).dt.days
N = len(df); print('N', N, 'dsl min/max', df['dsl'].min(), df['dsl'].max(), 'card vals', df[card].value_counts().to_dict())
tot = df[pay].sum(); print('总储值', tot)
new = df[df[idn] == '新增']; back = df[df[idn] == '回流']
print('新增', len(new), new['age'].min(), new['age'].max(), '全体age<=29', (df['age'] <= 29).sum(), 'age<=30', (df['age'] <= 30).sum())
print('回流', len(back), '>=8天', (back['dsl'] >= 8).sum(), '在场', (back['dsl'] <= 7).sum(), '当天', (back['dsl'] == 0).sum())
pp = df[(df[pay] <= 0) & (df[bet] > 10000)]
print('PP', len(pp), '可核实(age<=120)', (pp['age'] <= 120).sum(), '在场', (pp['dsl'] <= 7).sum(), '普卡占', (pp[card] == 1).mean())
print('PP 注册缺失', pp['age'].isna().sum())
ch = df[df[pay] > 0]; print('有储值', len(ch), '在场', (ch['dsl'] <= 7).sum(), '>=8', (ch['dsl'] >= 8).sum())
print('在场全体', (df['dsl'] <= 7).sum(), '在场且押注>0', ((df['dsl'] <= 7) & (df[bet] > 0)).sum())
print('读法乙确定', ((df[pay] > 0) & (df[dep] < 15000)).sum())
# 集中度
def conc(sub, name):
    s = sub[sub[pay] > 0][pay].sort_values(ascending=False)
    n = len(s); t = s.sum()
    print(name, 'n', n, '合计', t, 'top1%', s.head(max(1, int(round(n*0.01)))).sum()/t, 'top10%', s.head(int(round(n*0.1))).sum()/t)
    g = sub[(sub[pay] > 0) & (sub[card] >= 3)]
    print('  金卡以上', len(g), g[pay].sum()/t)
conc(new, '新增'); conc(back, '回流'); conc(back[back['dsl'] <= 7], '回流在场'); conc(ch, '潜在流失上界'); conc(ch[ch['dsl'] <= 7], '替代甲')
print('占总储值: 新增', new[pay].sum()/tot, '回流', back[pay].sum()/tot, '替代甲', ch[ch['dsl'] <= 7][pay].sum()/tot)
# 新增押注为0
z = new[new[bet] == 0]; print('新增押注0', len(z), (z[act] == 1000).sum(), (z[act] == 1000).mean())
# 回流 从未储值且押注0
r0 = back[(back[pay] <= 0) & (back[bet] == 0)]; print('回流未储值押注0', len(r0), r0['age'].median(), (r0['age'] >= 365).sum())
# 潜在付费 持續 在场 >=365
q = pp[(pp[idn] == '持續') & (pp['dsl'] <= 7) & (pp['age'] >= 365)]; print('PP 持續在场>=365', len(q))
# 区分度：回流 vs 非回流 中位
nb = df[df[idn] != '回流']
for col in [bet, act]:
    print(col, '回流/非回流中位比', back[col].median()/nb[col].median())
print('回流当天登录率', (back['dsl'] == 0).mean(), (nb['dsl'] == 0).mean())
print('回流有储值率', (back[pay] > 0).mean(), (nb[pay] > 0).mean())
print('PP 注册天数中位/非PP', pp['age'].median(), df.drop(pp.index)['age'].median(), '活动赠点', pp[act].median(), df.drop(pp.index)[act].median())
