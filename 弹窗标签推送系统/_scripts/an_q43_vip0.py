"""Q43：押注为 0 的 VIP（疑似代储或币商）的储值规模与画像；剔除后价值集中的对照数。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['tenure'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()).dt.days
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
d['gold'] = d['卡别'] >= 3
dep = d['总充值金额']
TOT = dep.sum()
print('全体', len(d), '累计储值合计', f'{TOT:,.0f}')

vip = d['身份'] == 'VIP'
v0 = d[vip & (d['游戏总押注'] == 0)]
v1 = d[vip & (d['游戏总押注'] != 0)]
print('\nVIP', int(vip.sum()), '押注为 0', len(v0), '押注不为 0', len(v1))
print('VIP 全体储值占比', f'{dep[vip].sum()/TOT*100:.2f}%')
for name, x in [('押注为 0 的 VIP', v0), ('押注不为 0 的 VIP', v1)]:
    p = x[x['总充值金额'] > 0]
    print(f'\n== {name}：{len(x)} 人，储值 > 0 的 {len(p)} 人')
    print(f'  储值合计 {x["总充值金额"].sum():,.0f}，占全部 {x["总充值金额"].sum()/TOT*100:.2f}%')
    print('  全组储值中位', x['总充值金额'].median(), '；有储值者中位', p['总充值金额'].median(),
          '四分位', p['总充值金额'].quantile([.25, .75]).tolist(), '最大', p['总充值金额'].max())
    print('  会员等级中位：全组', x['会员等级'].median(), '有储值者', p['会员等级'].median())
    print('  卡别（有储值者）', p['卡别'].value_counts().sort_index().to_dict(), '；全组', x['卡别'].value_counts().sort_index().to_dict())
    print('  平台（有储值者）', p['plat'].value_counts().to_dict())
    print('  游戏总输赢 非 0 人数（有储值者）', int((p['游戏总输赢'] != 0).sum()), '；RTP 非空', int(p['RTP'].notna().sum()))
    print('  活动赠点中位（有储值者）', p['活动赠点'].median(), '；充值赠点 / 储值回馈比中位', p['储值回馈比'].median())
    print('  最后登录 0–7 天（有储值者）', f'{(p["days"]<=7).mean()*100:.2f}%', '；注册天数中位', p['tenure'].median())

p0 = v0[v0['总充值金额'] > 0]
print('\n== 押注为 0、储值为 0 的 VIP', int((v0['总充值金额'] <= 0).sum()))

print('\n== 剔除押注为 0 的 83 名 VIP 后的价值集中对照')
r = d.drop(v0.index)
T2 = r['总充值金额'].sum()
print('剩余', len(r), '人，储值合计', f'{T2:,.0f}')
print('金卡以上储值占比：全体', f'{dep[d["gold"]].sum()/TOT*100:.2f}%', '→ 剔除后', f'{r.loc[r["gold"], "总充值金额"].sum()/T2*100:.2f}%')
print('VIP 储值占比：全体 13.09% → 剔除后剩余 VIP', f'{r.loc[r["身份"]=="VIP", "总充值金额"].sum()/T2*100:.2f}%')
# 有储值者前 1% 中有几个是这 60 人
pay = d[dep > 0].sort_values('总充值金额', ascending=False)
for k in [18, 183, 1826]:
    top = pay.head(k)
    print(f'有储值者前 {k} 名中押注为 0 的 VIP：{int(top.index.isin(p0.index).sum())} 人，占这批人储值 {top.loc[top.index.isin(p0.index), "总充值金额"].sum()/top["总充值金额"].sum()*100:.2f}%')
pay2 = r[r['总充值金额'] > 0].sort_values('总充值金额', ascending=False)
n1 = int(round(len(pay2) * 0.01)); n10 = int(round(len(pay2) * 0.10))
print(f'剔除后有储值者 {len(pay2)}，前 1%（{n1} 人）贡献 {pay2.head(n1)["总充值金额"].sum()/T2*100:.2f}%，前 10%（{n10} 人）贡献 {pay2.head(n10)["总充值金额"].sum()/T2*100:.2f}%')
# 押注为 0 且储值 > 0 的非 VIP，作对照
nv = d[(~vip) & (d['游戏总押注'] == 0) & (dep > 0)]
print('\n对照：押注为 0、储值 > 0 的非 VIP', len(nv), '储值合计占全部', f'{nv["总充值金额"].sum()/TOT*100:.3f}%', '中位', nv['总充值金额'].median())
