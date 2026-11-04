"""审查复算（只读）：A8 表 3c 全部格（含银卡对金卡以上、MH 合并）；A9 表 4 两口径、表 2 不含 VIP 列、卡组内 App 对浏览器、VIP 构成。"""
import os
import pandas as pd

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
raw = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = raw[~raw['身份'].isin(['機器人', '測試帳號'])].copy()
print('总人数', len(df))
card = pd.to_numeric(df['卡别'], errors='coerce')
print('卡别缺值', card.isna().sum())
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
pay = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
d = pd.to_datetime(df['最後登入時間'].astype(str).str[:10], errors='coerce')
near = (pd.Timestamp('2026-09-16') - d).dt.days <= 7
grp = pd.Series('金卡以上', index=df.index)
grp[card == 1] = '普卡'
grp[card == 2] = '银卡'


def bband(x):
    if x <= 1e4: return '1≤1万'
    if x <= 1e5: return '21万-10万'
    if x <= 1e6: return '310万-1百万'
    if x <= 1e7: return '41百万-1千万'
    if x <= 1e8: return '51千万-1亿'
    return '6>1亿'


def pband(x):
    if x <= 0: return '1≤0'
    if x <= 1e3: return '21-1千'
    if x <= 1e4: return '31千-1万'
    if x <= 1e5: return '41万-10万'
    return '5>10万'


t = pd.DataFrame({'g': grp, 'near': near, 'b': bet.map(bband), 'p': pay.map(pband)})


def pair(g1, g0, excl=None):
    print(f'\n== {g1} 减 {g0}，两组都 >= 30 的全部格 ==')
    num = den = 0.0
    for (b, p), s in t.groupby(['b', 'p']):
        a = s[s.g == g0]
        c = s[s.g == g1]
        if len(a) >= 30 and len(c) >= 30:
            diff = c.near.mean() - a.near.mean()
            w = len(a) * len(c) / (len(a) + len(c))
            flag = ''
            if excl and b in excl:
                flag = ' *'
            print(f'  {b} × {p}：{g0} {int(a.near.sum())}/{len(a)}={a.near.mean()*100:.2f}%；{g1} {int(c.near.sum())}/{len(c)}={c.near.mean()*100:.2f}%；差 {diff*100:.2f}{flag}')
            num += w * diff
            den += w
    if den:
        print(f'  MH 合并 {num/den*100:.2f}')


pair('金卡以上', '普卡')
pair('银卡', '普卡')
pair('金卡以上', '银卡')

# ---------- A9 ----------
p = df['登入平台']
p = p.where(p.isna(), p.astype(str).str.strip()).fillna('缺值')
p = p.where(p != 'Web', 'web')
df['平台'] = p
df['dep'] = pay
df['card'] = card
df['near'] = near
brw = ['mweb', 'web', 'h5', 'mh5']
df['br'] = df['平台'].isin(brw)
df['web'] = df['平台'] == 'web'
TOT = df['dep'].sum()
vip = df['身份'] == 'VIP'
print('\nVIP 人数', vip.sum(), '储值', df.loc[vip, 'dep'].sum(), '0-7天', df.loc[vip, 'near'].sum())
print('黑名單 储值', df.loc[df['身份'] == '黑名單', 'dep'].sum(), '人数', (df['身份'] == '黑名單').sum())
print('VIP App类人数', (vip & ~df['br']).sum(), 'VIP 浏览器类人数', (vip & df['br']).sum())
nv = df[~df['身份'].isin(['VIP', '黑名單'])]
T2 = nv['dep'].sum()
print('不含VIP 人数', len(nv), '储值', T2)
print('\n各平台储值占比（不含 VIP、黑名單）')
for k, g in nv.groupby('平台'):
    print(f'  {k} {g["dep"].sum()/T2*100:.2f}%')
print(f'  浏览器类 人数 {nv["br"].mean()*100:.2f}% ({nv["br"].sum()}) 储值 {nv.loc[nv.br,"dep"].sum()/T2*100:.2f}%')
print(f'  App类 人数 {(~nv["br"]).mean()*100:.2f}% 储值 {nv.loc[~nv.br,"dep"].sum()/T2*100:.2f}%')
print(f'  全部口径 App类 人数 {(~df["br"]).mean()*100:.2f}% 储值 {df.loc[~df.br,"dep"].sum()/TOT*100:.2f}%')
nw = nv[nv['web']]
print('不含VIP web人数', len(nw), 'web中金卡以上', (nw['card'] >= 3).sum(), f"{(nw['card']>=3).mean()*100:.2f}%")
w = nw.sort_values('dep', ascending=False)
print(f"不含VIP web前10占web储值 {w['dep'].head(10).sum()/w['dep'].sum()*100:.2f}%，去掉后占本口径 {(w['dep'].sum()-w['dep'].head(10).sum())/T2*100:.2f}%")
top10 = nv.sort_values('dep', ascending=False).head(10)
print('不含VIP 前10 web', top10['web'].sum())
top100 = nv.sort_values('dep', ascending=False).head(100)
print('不含VIP 前100 平台', top100['平台'].value_counts().to_dict())
gold = nv[nv['card'] >= 3]
print(f"不含VIP 金卡以上 浏览器人数 {gold['br'].mean()*100:.2f}% 储值 {gold.loc[gold.br,'dep'].sum()/gold['dep'].sum()*100:.2f}%")
print('\n卡组内 App 对浏览器（全部口径）')
df['grp'] = grp
for gname, g in df.groupby('grp'):
    for lab, s in [('App', g[~g.br]), ('浏览器', g[g.br])]:
        pos = s[s.dep > 0]['dep']
        print(f'  {gname} {lab} 有储值中位 {pos.median()} (n={len(pos)}) 0-7天 {s.near.mean()*100:.2f}%')
print('\n卡组内 App（不含缺值）')
for gname, g in df[df['平台'] != '缺值'].groupby('grp'):
    s = g[~g.br]
    pos = s[s.dep > 0]['dep']
    print(f'  {gname} App 有储值中位 {pos.median()} (n={len(pos)}) 0-7天 {s.near.mean()*100:.2f}%')
x = df[(df['平台'] != '缺值') & ~df['身份'].isin(['VIP', '黑名單']) & (df['card'] >= 3) & ~df.br]
print('  不含VIP 金卡以上 App 不含缺值', x[x.dep > 0]['dep'].median(), f'{x.near.mean()*100:.2f}%')
nn = df[df['平台'] != '缺值']
print(f"  全部 App类 不含缺值 人数 {(~nn.br).sum()/len(df)*100:.2f}%")
nv2 = df[~df['身份'].isin(['VIP', '黑名單'])]
g = nv2[nv2['card'] >= 3]
for lab, s in [('App', g[~g.br]), ('浏览器', g[g.br])]:
    pos = s[s.dep > 0]['dep']
    print(f'  不含VIP 金卡以上 {lab} 有储值中位 {pos.median()} 0-7天 {s.near.mean()*100:.2f}%')
# 全部 web 储值占比，VIP web 占全部 web 储值
print(f"VIP web 占 web 储值 {df.loc[vip & df.web,'dep'].sum()/df.loc[df.web,'dep'].sum()*100:.2f}%")
# VIP web 中 普卡/银卡人数
vw = df[vip & df.web]
print('VIP web 人数', len(vw), '其中普卡银卡', (vw['card'] <= 2).sum())
# 金卡以上 各平台储值(全部口径) 与 "金卡以上里浏览器类 31.21%"
ga = df[df['card'] >= 3]
print(f"全部 金卡以上 浏览器人数 {ga['br'].mean()*100:.2f}% 储值 {ga.loc[ga.br,'dep'].sum()/ga['dep'].sum()*100:.2f}%")
