# 审查者只读复算 A9 登录平台分布 与 Q24 数据观察（不写任何文件）
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
print('原始行', len(raw))
rp = raw['登入平台'].astype(str).str.strip()
print('原始 bo 行', (rp.str.lower() == 'bo').sum(), '其身份', raw.loc[rp.str.lower() == 'bo', '身份'].value_counts().to_dict())
print('原始缺值', raw['登入平台'].isna().sum(), '其中機器人', (raw['登入平台'].isna() & (raw['身份'] == '機器人')).sum())

df = raw[~raw['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
print('剔除后', N)
p = df['登入平台']
p = p.where(p.isna(), p.astype(str).str.strip())
print('原始取值', p.value_counts(dropna=False).to_dict())
p = p.fillna('缺值')
p = p.where(p != 'Web', 'web')
df['平台'] = p
dep = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
df['dep'] = dep
df['bet'] = bet
TOT = dep.sum()
print('储值合计', TOT)
card = pd.to_numeric(df['卡别'], errors='coerce')
df['card'] = card
df['grp'] = pd.cut(card, [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上'])
df['pot'] = (dep <= 0) & (bet > 10000)
print('潜在付费', df['pot'].sum())
app = ['android', 'ios', 'apk']
brw = ['mweb', 'web', 'h5', 'mh5']
df['cls'] = df['平台'].map(lambda x: 'App' if x in app else ('浏览器' if x in brw else '缺值'))
lt = pd.to_datetime(df['最後登入時間'].astype(str).str[:10], errors='coerce')
days = (pd.Timestamp('2026-09-16') - lt).dt.days
df['r07'] = days.between(0, 7)

def row(g, name):
    n = len(g)
    payers = g[g['dep'] > 0]
    print(f"{name}: n={n} {n/N:.2%} dep占={g['dep'].sum()/TOT:.2%} 储值率={len(payers)/n:.2%} 中位={payers['dep'].median()} 金卡以上={ (g['grp']=='金卡以上').sum()} ({(g['grp']=='金卡以上').mean():.2%}) 0-7={g['r07'].mean():.2%} 潜在={g['pot'].sum()}")

for k, g in df.groupby('平台'):
    row(g, k)
for k, g in df.groupby('cls'):
    row(g, k)
row(df, '全部')

print('--- 表2')
def t2(g, name):
    b = g[g['cls'] == '浏览器']
    sd = g['dep'].sum()
    print(f"{name}({len(g)}): 浏览器 {len(b)} {len(b)/len(g):.2%} 储值中 {b['dep'].sum()/sd if sd else float('nan'):.2%}")
for k, g in df.groupby('grp', observed=True):
    t2(g, k)
for k, g in df.groupby('身份'):
    t2(g, k)
t2(df[df['身份'].isin(['VIP', '黑名單'])], '其他')
t2(df[df['pot']], '潜在付费')
hl = df[df['身份'] == '回流']
print('回流 mweb', (hl['平台'] == 'mweb').sum())
xz = df[df['身份'] == '新增']
print('新增 mh5', (xz['平台'] == 'mh5').sum())
oth = df[df['身份'].isin(['VIP', '黑名單'])]
print('其他 web', (oth['平台'] == 'web').sum(), '其他储值占全部', oth['dep'].sum() / TOT, 'VIP', df.loc[df['身份']=='VIP','dep'].sum()/TOT, '黑', df.loc[df['身份']=='黑名單','dep'].sum()/TOT)

print('--- 表3')
for c, g in df.groupby('card'):
    print(c, len(g), (g['平台'] == 'web').sum(), f"{(g['平台']=='web').mean():.2%}", f"{(g['cls']=='浏览器').mean():.2%}")

print('--- 反例')
for k in ['web', 'android', 'ios', 'mweb', 'apk']:
    g = df[df['平台'] == k].sort_values('dep', ascending=False)
    s = g['dep'].sum()
    k1 = max(1, int(round(len(g) * 0.01)))
    print(k, f"top10占本平台 {g['dep'].head(10).sum()/s:.2%} top1%({k1}) {g['dep'].head(k1).sum()/s:.2%} 去top10占全部 {(s-g['dep'].head(10).sum())/TOT:.2%}")
top100 = df.sort_values('dep', ascending=False).head(100)
print('top100', top100['平台'].value_counts().to_dict())
top10 = df.sort_values('dep', ascending=False).head(10)
print('top10', top10['平台'].value_counts().to_dict(), top10.loc[top10['平台']=='web','grp'].tolist())
gold = df[df['grp'] == '金卡以上']
gw = gold[gold['平台'] == 'web']
print('金卡以上 web', len(gw), f"{len(gw)/len(gold):.2%}", '储值占金卡以上', gw['dep'].sum() / gold['dep'].sum())
for k in ['web', 'android', 'ios']:
    gg = gold[(gold['平台'] == k) & (gold['dep'] > 0)]
    print('金卡以上有储值中位', k, gg['dep'].median())
# 同卡组内浏览器 vs App 储值中位（检查 web 同卡别是否花更多）
for gname, gg in df.groupby('grp', observed=True):
    for c in ['App', '浏览器']:
        x = gg[(gg['cls'] == c) & (gg['dep'] > 0)]['dep']
        print('卡组', gname, c, '有储值者中位', x.median(), 'n', len(x))

print('--- 浏览器类最后登录是否近 (0-7天) 按卡组')
for gname, gg in df.groupby('grp', observed=True):
    for c in ['App', '浏览器']:
        x = gg[gg['cls'] == c]
        print(gname, c, len(x), f"{x['r07'].mean():.2%}")

print('--- Q24 新增 vs 注册30天')
reg = pd.to_datetime(df['注册时间'].astype(str).str[:10], errors='coerce')
win = (reg >= pd.Timestamp('2026-08-18')) & (reg <= pd.Timestamp('2026-09-16'))
print('新增', (df['身份'] == '新增').sum(), '注册8/18-9/16', win.sum(), '交叉', ((df['身份'] == '新增') & win).sum())
print('新增内注册日范围', reg[df['身份'] == '新增'].min(), reg[df['身份'] == '新增'].max())
print('非新增但注册在窗口', ((df['身份'] != '新增') & win).sum())
neg = df[df['dep'] < 0]
print('储值为负', len(neg), '其中押注>1万', (neg['bet'] > 10000).sum())
