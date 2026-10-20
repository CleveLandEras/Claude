"""Q29：A9 登录平台分布的「不含 VIP、黑名單」口径（62,169 人）对照。不带参数运行，只读。
口径同 an_a9_platform.py：剔除機器人、測試帳號；平台去空格、先填缺值再把 Web 并入 web；
App 类 = android、ios、apk；浏览器类 = mweb、web、h5、mh5。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
pf = d['登入平台'].astype('string').str.strip().fillna('缺值')
d['平台'] = pf.mask(pf == 'Web', 'web')
APP, BRW = ['android', 'ios', 'apk'], ['mweb', 'web', 'h5', 'mh5']
d['类'] = d['平台'].map(lambda x: 'App 类' if x in APP else ('浏览器类' if x in BRW else '缺值'))
d['卡组'] = pd.cut(d['卡别'], [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上']).astype(str)
d['储值'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
d['天'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間'].astype(str).str[:10])).dt.days
ALL = d
TOT_ALL = ALL['储值'].sum()

print('== VIP、黑名單 ==')
for s in ['VIP', '黑名單']:
    g = ALL[ALL['身份'] == s]
    print(f'  {s} {len(g)} 人，储值 {int(g["储值"].sum())}（占全部 {g["储值"].sum() / TOT_ALL * 100:.2f}%），0–7 天 {(g["天"] <= 7).mean() * 100:.2f}%（{int((g["天"] <= 7).sum())}/{len(g)}），'
          f'金卡以上 {int((g["卡组"] == "金卡以上").sum())}')
    print('   平台', g['平台'].value_counts().to_dict())
    gw = g[g['平台'] == 'web']
    print(f'   其中 web {len(gw)} 人，储值占全部 {gw["储值"].sum() / TOT_ALL * 100:.2f}%')
vip_brw = ALL[(ALL['身份'] == 'VIP') & (ALL['类'] == '浏览器类')]
print(f'  VIP 浏览器类 {len(vip_brw)} 人，储值占全部 {vip_brw["储值"].sum() / TOT_ALL * 100:.2f}%')


def block(df, label):
    N, TOT = len(df), df['储值'].sum()
    print(f'\n######## 口径：{label}（{N} 人，储值 {int(TOT)}）')
    print('-- 两类 --')
    for c in ['App 类', '浏览器类', '缺值']:
        g = df[df['类'] == c]
        print(f'  {c} {len(g)}（{len(g) / N * 100:.2f}%），储值占 {g["储值"].sum() / TOT * 100:.2f}%')
    print('-- 平台 --')
    for p in ['android', 'ios', 'mweb', 'web', 'apk', 'mh5', 'h5']:
        g = df[df['平台'] == p]
        print(f'  {p} {len(g)}（{len(g) / N * 100:.2f}%），储值占 {g["储值"].sum() / TOT * 100:.2f}%，金卡以上 {int((g["卡组"] == "金卡以上").sum())}（{(g["卡组"] == "金卡以上").mean() * 100:.2f}%）')
    hi = df[df['卡组'] == '金卡以上']
    hb = hi[hi['类'] == '浏览器类']
    print(f'-- 金卡以上 {len(hi)} 人：浏览器类 {len(hb)}（{len(hb) / len(hi) * 100:.2f}%），储值占金卡以上 {hb["储值"].sum() / hi["储值"].sum() * 100:.2f}%')
    print('-- 卡别 web 占比 --')
    for c in range(1, 8):
        g = df[df['卡别'] == c]
        print(f'  卡别 {c}：{len(g)} 人，web {int((g["平台"] == "web").sum())}（{(g["平台"] == "web").mean() * 100:.2f}%），浏览器类 {(g["类"] == "浏览器类").mean() * 100:.2f}%')
    w = df[df['平台'] == 'web']['储值'].sort_values(ascending=False)
    print(f'-- web 前 10 名占 web 储值 {w.head(10).sum() / w.sum() * 100:.2f}%，去掉前 10 名后 web 占本口径储值 {(w.sum() - w.head(10).sum()) / TOT * 100:.2f}%')
    top = df.sort_values('储值', ascending=False)
    print('-- 储值前 10 名：', top.head(10).apply(lambda r: f'{r["平台"]}/{r["身份"]}', axis=1).tolist())
    print('-- 储值前 100 名平台：', top.head(100)['平台'].value_counts().to_dict())
    print('-- 储值前 100 名身份：', top.head(100)['身份'].value_counts().to_dict())


block(ALL, '全部')
block(ALL[~ALL['身份'].isin(['VIP', '黑名單'])], '不含 VIP、黑名單')
