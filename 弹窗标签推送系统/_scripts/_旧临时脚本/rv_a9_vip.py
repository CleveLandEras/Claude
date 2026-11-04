# 审查者只读复算：A9 储值占比中 VIP 的贡献；金卡以上中位数口径
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = raw[~raw['身份'].isin(['機器人', '測試帳號'])].copy()
p = df['登入平台']
p = p.where(p.isna(), p.astype(str).str.strip()).fillna('缺值')
p = p.where(p != 'Web', 'web')
df['平台'] = p
df['dep'] = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
df['card'] = pd.to_numeric(df['卡别'], errors='coerce')
brw = ['mweb', 'web', 'h5', 'mh5']
df['br'] = df['平台'].isin(brw)
df['web'] = df['平台'] == 'web'
TOT = df['dep'].sum()
vip = df['身份'] == 'VIP'
print('VIP 人数', vip.sum(), '储值占全部', df.loc[vip, 'dep'].sum() / TOT)
print('VIP 卡别分布', df.loc[vip, 'card'].value_counts().sort_index().to_dict())
print('VIP 平台', df.loc[vip, '平台'].value_counts().to_dict())
print('VIP 浏览器储值占全部', df.loc[vip & df['br'], 'dep'].sum() / TOT, 'VIP web 储值占全部', df.loc[vip & df['web'], 'dep'].sum() / TOT)
print('VIP 非浏览器储值占全部', df.loc[vip & ~df['br'], 'dep'].sum() / TOT)
nv = df[~df['身份'].isin(['VIP', '黑名單'])]
T2 = nv['dep'].sum()
print('去 VIP黑名單 人数', len(nv), '浏览器人数占', nv['br'].mean(), '浏览器储值占', nv.loc[nv['br'], 'dep'].sum() / T2)
print('去 VIP黑名單 web 人数占', nv['web'].mean(), 'web 储值占', nv.loc[nv['web'], 'dep'].sum() / T2, 'web人数', nv['web'].sum())
print('全部 web 储值中 VIP 占', df.loc[vip & df['web'], 'dep'].sum() / df.loc[df['web'], 'dep'].sum())
# 去 VIP 后各卡别 web 占比
for c, g in nv.groupby('card'):
    print('去VIP 卡别', c, len(g), f"web {g['web'].mean():.2%} 浏览器 {g['br'].mean():.2%}")
gold = nv[nv['card'] >= 3]
print('去VIP 金卡以上', len(gold), '浏览器人数占', gold['br'].mean(), '浏览器储值占', gold.loc[gold['br'], 'dep'].sum() / gold['dep'].sum())
# top100 中 VIP
top100 = df.sort_values('dep', ascending=False).head(100)
print('top100 VIP 数', (top100['身份'] == 'VIP').sum(), 'top100 web 中 VIP', ((top100['身份'] == 'VIP') & top100['web']).sum())
top10 = df.sort_values('dep', ascending=False).head(10)
print('top10 身份平台', list(zip(top10['身份'], top10['平台'])))
# web 去 VIP 再去 top10
w = nv[nv['web']].sort_values('dep', ascending=False)
print('去VIP web 前10占本平台', w['dep'].head(10).sum() / w['dep'].sum(), '去VIP去前10 web 占全部(原分母)', (w['dep'].sum() - w['dep'].head(10).sum()) / TOT)
# 金卡以上中位数：含零 vs 仅有储值
g_all = df[df['card'] >= 3]
for k in ['web', 'android', 'ios']:
    x = g_all[g_all['平台'] == k]['dep']
    print('金卡以上', k, '全部中位', x.median(), '有储值中位', x[x > 0].median(), 'n', len(x))
