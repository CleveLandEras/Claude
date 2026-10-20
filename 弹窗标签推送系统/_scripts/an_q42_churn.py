"""Q42：八月离开的人是谁，和还在的人差在哪（照设计卡 S1–S6）。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']
APP = {'android', 'ios', 'apk'}
BRW = {'mweb', 'web', 'h5', 'mh5'}


def prep(d):
    d = d.copy()
    d['last'] = pd.to_datetime(d['最後登入時間']).dt.normalize()
    d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
    d['days'] = (T0 - d['last']).dt.days
    d['tenure'] = (T0 - d['reg']).dt.days
    d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
    d['pcls'] = np.where(d['plat'].isin(APP), 'App', np.where(d['plat'].isin(BRW), '浏览器', '缺值/其他'))
    d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
    d['dep'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
    d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
    d['pp'] = (d['dep'] <= 0) & (d['bet'] > 10000)
    return d


ra = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
rc = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
print('原始行数 活跃', len(ra), '流失名单', len(rc))
a = prep(ra[~ra['身份'].isin(EX)])
c = prep(rc[~rc['身份'].isin(EX)])
print('剔除后 活跃', len(a), '流失名单', len(c))

# ---------------- S1 口径核验
print('\n===== S1 口径核验')
print('会员编号重复：活跃', int(a['会员编号'].duplicated().sum()), '流失名单', int(c['会员编号'].duplicated().sum()))
inA = c['会员编号'].isin(a['会员编号'])
L = c[~inA].copy()
O = c[inA]
print('离开者（只在名单）', len(L), '重叠', len(O))
print('名单最后登录范围', c['last'].min().date(), c['last'].max().date())
print('离开者最后登录范围', L['last'].min().date(), L['last'].max().date(), '天数', L['days'].min(), L['days'].max())
a816 = a[(a['last'] >= '2026-08-16') & (a['last'] <= '2026-08-31')]
print('活跃中最后登录 8/16–8/31', len(a816), '其中在名单里', int(a816['会员编号'].isin(c['会员编号']).sum()))
# 重叠者逐字段比较
m = O.merge(a, on='会员编号', suffixes=('_c', '_a'))
print('重叠者在活跃里的最后登录：8/16–8/31', int(((m['last_a'] >= '2026-08-16') & (m['last_a'] <= '2026-08-31')).sum()),
      '；9/1 及以后', int((m['last_a'] >= '2026-09-01').sum()))
print('  其中名单最后登录早于 8/16', int((m['last_c'] < '2026-08-16').sum()), '，这些人在活跃里最后登录', m.loc[m['last_c'] < '2026-08-16', 'last_a'].value_counts().to_dict())
for col in ['卡别', '会员等级', '总充值金额', '游戏总押注', '活动赠点', '登入平台', '身份', '最後登入時間']:
    x, y = m[col + '_c'], m[col + '_a']
    diff = ~((x == y) | (x.isna() & y.isna()))
    print(f'  不一致 {col}: {int(diff.sum())}')
print('离开者身份', L['身份'].value_counts().to_dict())
print('离开者注册时间缺值', int(L['reg'].isna().sum()), '；活跃注册时间缺值', int(a['reg'].isna().sum()))
print('离开者 8/1 起注册（按日期）', int((L['reg'] >= '2026-08-01').sum()), '；注册 >= 8/1 或缺值', int(((L['reg'] >= '2026-08-01') | L['reg'].isna()).sum()))

# ---------------- 合并口径与分档
a['tier'] = pd.cut(a['days'], [-1, 7, 14, 31], labels=['0–7', '8–14', '15–31']).astype(str)
L['tier'] = '32–46'
U = pd.concat([a, L], ignore_index=True)
TIERS = ['0–7', '8–14', '15–31', '32–46']
WID = {'0–7': 8, '8–14': 7, '15–31': 17, '32–46': 15}
TOT = U['dep'].sum()
print('\n合并口径', len(U), '储值合计', f'{TOT:,.0f}', '；活跃储值合计', f'{a["dep"].sum():,.0f}', '；离开者', f'{L["dep"].sum():,.0f}')
print('活跃分档人数', a['tier'].value_counts().to_dict())


def ladder(X, title):
    print(f'\n===== {title}')
    rows = {}
    for t in TIERS:
        g = X[X['tier'] == t]
        n = len(g)
        p = g[g['dep'] > 0]
        r = {
            '人数': n,
            '日均': round(n / WID[t], 1),
            '普卡%': g['cg'].eq('普卡').mean() * 100,
            '银卡%': g['cg'].eq('银卡').mean() * 100,
            '金卡以上%': g['cg'].eq('金卡以上').mean() * 100,
            '金卡以上人数': int(g['cg'].eq('金卡以上').sum()),
            '有储值%': (g['dep'] > 0).mean() * 100,
            '有储值者中位': p['dep'].median(),
            '储值占合并%': g['dep'].sum() / TOT * 100,
            '押注中位': g['bet'].median(),
            '押注为0%': (g['bet'] == 0).mean() * 100,
            '潜在付费%': g['pp'].mean() * 100,
            '注册<30天%': (g['tenure'] < 30).mean() * 100,
            '注册30天-1年%': ((g['tenure'] >= 30) & (g['tenure'] < 365)).mean() * 100,
            '注册>=1年%': (g['tenure'] >= 365).mean() * 100,
            '注册缺值': int(g['tenure'].isna().sum()),
            '8/1起注册%': (g['reg'] >= '2026-08-01').mean() * 100,
            'App%': g['pcls'].eq('App').mean() * 100,
            '浏览器%': g['pcls'].eq('浏览器').mean() * 100,
            '会员等级中位': g['会员等级'].median(),
        }
        rows[t] = r
    df = pd.DataFrame(rows)
    with pd.option_context('display.float_format', lambda v: f'{v:,.2f}', 'display.width', 200):
        print(df)
    return df


ladder(U, '表 1a 四档构成（全部，合并口径 74,480）')
ladder(U[U['reg'] < '2026-08-01'], '表 1b 四档构成（只含 2026-08-01 前注册）')

print('\n===== 表 2 卡组内各档比例（分母=该卡组在合并口径的人数）')
for cg in ['普卡', '银卡', '金卡以上']:
    g = U[U['cg'] == cg]
    vc = g['tier'].value_counts()
    print(cg, len(g), {t: f'{vc.get(t,0)} ({vc.get(t,0)/len(g)*100:.2f}%)' for t in TIERS})
    g2 = g[g['reg'] < '2026-08-01']
    vc2 = g2['tier'].value_counts()
    print('  8/1 前注册', len(g2), {t: f'{vc2.get(t,0)} ({vc2.get(t,0)/len(g2)*100:.2f}%)' for t in TIERS})
# 按储值画像：有储值者、储值 >= 1 万者
for name, msk in [('有储值者', U['dep'] > 0), ('储值>=1万', U['dep'] >= 10000), ('储值>=10万', U['dep'] >= 100000)]:
    g = U[msk]
    vc = g['tier'].value_counts()
    print(name, len(g), {t: f'{vc.get(t,0)} ({vc.get(t,0)/len(g)*100:.2f}%)' for t in TIERS})

# ---------------- S3 价值规模
print('\n===== S3 价值规模')
LD, AD = L['dep'].sum(), a['dep'].sum()
print(f'离开者储值 {LD:,.0f}，活跃 {AD:,.0f}，比 {LD/AD*100:.2f}%；离开者占合并 {LD/TOT*100:.2f}%')
Lp = L[L['dep'] > 0].sort_values('dep', ascending=False)
print('离开者有储值', len(Lp), f'{len(Lp)/len(L)*100:.2f}%', '中位', Lp['dep'].median(), '四分位', Lp['dep'].quantile([.25, .75]).tolist())
top10 = Lp.head(10)
n1 = int(round(len(L) * 0.01))
print(f'前 10 人占离开者储值 {top10["dep"].sum()/LD*100:.2f}%；前 1%（{n1} 人，按离开者全体）占 {Lp.head(n1)["dep"].sum()/LD*100:.2f}%；'
      f'有储值者前 1%（{int(round(len(Lp)*0.01))} 人）占 {Lp.head(int(round(len(Lp)*0.01)))["dep"].sum()/LD*100:.2f}%')
print(f'去掉前 10 人后合计 {LD-top10["dep"].sum():,.0f}，与活跃之比 {(LD-top10["dep"].sum())/AD*100:.2f}%')
print('前 10 人（卡别、储值、押注、平台、会员等级、注册天数）：')
for _, r in top10.iterrows():
    print('  ', int(r['卡别']), f'{r["dep"]:,.0f}', f'{r["bet"]:,.0f}', r['plat'], r['会员等级'], r['tenure'])
# 对照：活跃前 10 占活跃储值
ap = a[a['dep'] > 0].sort_values('dep', ascending=False)
print(f'对照：活跃前 10 人占活跃储值 {ap.head(10)["dep"].sum()/AD*100:.2f}%；活跃有储值者前 1% 占 {ap.head(int(round(len(ap)*0.01)))["dep"].sum()/AD*100:.2f}%')
# 疑似代储
z = L[(L['bet'] == 0) & (L['dep'] > 0)]
print(f'离开者押注为 0 且储值 > 0：{len(z)} 人，储值 {z["dep"].sum():,.0f}（占离开者 {z["dep"].sum()/LD*100:.2f}%），卡别', z['卡别'].value_counts().to_dict(),
      '；剔除后离开者合计', f'{LD-z["dep"].sum():,.0f}')
za = a[(a['bet'] == 0) & (a['dep'] > 0)]
print(f'对照：活跃押注为 0 且储值 > 0：{len(za)} 人，储值 {za["dep"].sum():,.0f}；两边都剔除后离开者/活跃 {(LD-z["dep"].sum())/(AD-za["dep"].sum())*100:.2f}%')
# 金卡以上
print('\n金卡以上对照表')
for name, g in [('离开者 金卡以上', L[L['cg'] == '金卡以上']),
                ('活跃 金卡以上 8 天以上未登录', a[(a['cg'] == '金卡以上') & (a['days'] >= 8)]),
                ('活跃 金卡以上 15–31 天', a[(a['cg'] == '金卡以上') & (a['days'] >= 15)]),
                ('活跃 金卡以上 全部', a[a['cg'] == '金卡以上'])]:
    p = g[g['dep'] > 0]
    print(f'  {name}: {len(g)} 人，储值 {g["dep"].sum():,.0f}（占活跃储值 {g["dep"].sum()/AD*100:.2f}%；占合并 {g["dep"].sum()/TOT*100:.2f}%），'
          f'有储值者 {len(p)} 中位 {p["dep"].median()}，VIP {int((g["身份"]=="VIP").sum())}，卡别', g['卡别'].value_counts().sort_index().to_dict())
gL = L[L['cg'] == '金卡以上']
print('  离开者金卡以上前 10 占其储值', f'{gL.sort_values("dep", ascending=False).head(10)["dep"].sum()/gL["dep"].sum()*100:.2f}%', '押注为0', int((gL['bet'] == 0).sum()))
# 离开者储值按卡组
print('离开者储值按卡组', {k: f'{v:,.0f} ({v/LD*100:.2f}%)' for k, v in L.groupby('cg')['dep'].sum().items()})
print('活跃储值按卡组', {k: f'{v:,.0f} ({v/AD*100:.2f}%)' for k, v in a.groupby('cg')['dep'].sum().items()})

# ---------------- S4 卡别低估检查
print('\n===== S4 卡别低估检查')
ga = a[a['cg'] == '金卡以上']['dep']
q25, q50 = ga.quantile(.25), ga.median()
print('活跃金卡以上储值 P25', q25, '中位', q50)
for thr_name, thr in [('P25', q25), ('中位', q50)]:
    print(f' 阈值 {thr_name}={thr:,.0f}')
    for t in TIERS:
        g = U[(U['tier'] == t)]
        ng = g[g['cg'] != '金卡以上']
        hit = ng[ng['dep'] >= thr]
        gold = g[g['cg'] == '金卡以上']
        print(f'   {t}: 非金卡 {len(ng)}，储值≥阈值 {len(hit)}（{len(hit)/len(ng)*100:.3f}%），会员等级中位 {hit["会员等级"].median()}，押注中位 {hit["bet"].median():,.0f}'
              f'｜同档金卡以上 {len(gold)} 人，等级中位 {gold["会员等级"].median()}，押注中位 {gold["bet"].median():,.0f}；卡别', hit['卡别'].value_counts().to_dict())

# ---------------- S5 注册队列
print('\n===== S5 8/1–8/15 注册队列')
coh = U[(U['reg'] >= '2026-08-01') & (U['reg'] <= '2026-08-15')]
ref = a[(a['reg'] >= '2026-08-18') & (a['reg'] <= '2026-09-08')]
print(f'8/1–8/15 注册 {len(coh)} 人，日均 {len(coh)/15:.1f}；8/18–9/8 注册 {len(ref)} 人，日均 {len(ref)/22:.1f}；差 {(len(coh)/15)/(len(ref)/22)*100-100:.2f}%')
print('  其中在活跃', int(coh['tier'].ne('32–46').sum()), '离开者', int(coh['tier'].eq('32–46').sum()))
print('  各日注册人数', coh['reg'].dt.day.value_counts().sort_index().to_dict())
print('  8/16–8/17 注册（活跃+离开者）', int(((U['reg'] >= '2026-08-16') & (U['reg'] <= '2026-08-17')).sum()))
same = coh['last'] == coh['reg']
print(f'  已离开 {coh["tier"].eq("32–46").mean()*100:.2f}%；只来注册当天 {same.mean()*100:.2f}%（{int(same.sum())}）；赠点恰为 1,000 {coh["活动赠点"].eq(1000).mean()*100:.2f}%（{int(coh["活动赠点"].eq(1000).sum())}）')
print('  只来当天者中已离开', int((same & coh['tier'].eq('32–46')).sum()), '；离开者中只来当天', f'{same[coh["tier"].eq("32–46")].mean()*100:.2f}%')
print('  身份', coh['身份'].value_counts().to_dict(), '卡组', coh['cg'].value_counts().to_dict())
print(f'  有储值 {(coh["dep"]>0).mean()*100:.2f}%；押注中位 {coh["bet"].median()}；浏览器 {coh["pcls"].eq("浏览器").mean()*100:.2f}%')
m1000 = coh['活动赠点'].eq(1000)
print(f'  赠点恰为 1,000 者只来当天 {same[m1000].mean()*100:.2f}%（{int((same & m1000).sum())}/{int(m1000.sum())}）')
# 按注册后最后登录天数分布
coh_life = (coh['last'] - coh['reg']).dt.days
print('  注册到最后登录的天数：0 天', int((coh_life == 0).sum()), '1–7 天', int(coh_life.between(1, 7).sum()), '8–30', int(coh_life.between(8, 30).sum()), '31+', int((coh_life >= 31).sum()))
# 对照 A12 口径：8/18–9/8 注册
same_r = ref['last'] == ref['reg']
print(f'  对照 8/18–9/8 注册 {len(ref)}：只来当天 {same_r.mean()*100:.2f}%（{int(same_r.sum())}）')

# ---------------- S6 平台
print('\n===== S6 平台')
for name, g in [('活跃全体', a), ('离开者', L), ('离开者 8/1 前注册', L[L['reg'] < '2026-08-01']),
                ('离开者 金卡以上', L[L['cg'] == '金卡以上']), ('活跃 金卡以上', a[a['cg'] == '金卡以上']),
                ('离开者 有储值', L[L['dep'] > 0]), ('活跃 有储值', a[a['dep'] > 0])]:
    print(f'  {name} {len(g)}: App {g["pcls"].eq("App").mean()*100:.2f}%（{int(g["pcls"].eq("App").sum())}）浏览器 {g["pcls"].eq("浏览器").mean()*100:.2f}%（{int(g["pcls"].eq("浏览器").sum())}）其他 {int(g["pcls"].eq("缺值/其他").sum())}；细分', g['plat'].value_counts().to_dict())
