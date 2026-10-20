"""R45、R46：A9 补充数字。不带参数运行，只读。口径同 an_a9_platform.py。
① 金卡以上各平台：有储值者中位数（储值 > 0）与全体中位数（含 ≤ 0）；
② 卡组内浏览器类对 App 类：有储值者中位数、0–7 天比例；
③ web 储值中 VIP 的占比；储值前 100 名中 VIP 的平台；VIP 在 App 类、浏览器类的储值占全部。"""
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
TOT = d['储值'].sum()

print('== ① 金卡以上各平台中位数 ==')
hi = d[d['卡组'] == '金卡以上']
for p in ['web', 'android', 'ios', 'mweb', 'apk']:
    g = hi[hi['平台'] == p]
    pay = g[g['储值'] > 0]
    print(f'  {p}：{len(g)} 人，全体中位数 {g["储值"].median():,.1f}；有储值 {len(pay)} 人，有储值者中位数 {pay["储值"].median():,.1f}')

for label, df in [('全部', d), ('不含 VIP、黑名單', d[~d['身份'].isin(['VIP', '黑名單'])])]:
    print(f'\n== ② 卡组内 浏览器类 对 App 类（{label}）==')
    for cg in ['普卡', '银卡', '金卡以上']:
        for c in ['App 类', '浏览器类']:
            g = df[(df['卡组'] == cg) & (df['类'] == c)]
            pay = g[g['储值'] > 0]
            print(f'  [{cg}] {c}：{len(g)} 人，有储值 {len(pay)} 人，有储值者中位数 {pay["储值"].median():,.1f}，0–7 天 {(g["天"] <= 7).mean()*100:.2f}%（{int((g["天"] <= 7).sum())}/{len(g)}）')

print('\n== ③ VIP ==')
vip = d[d['身份'] == 'VIP']
w = d[d['平台'] == 'web']
print(f'  web 储值 {int(w["储值"].sum())}，其中 VIP {int(w[w["身份"] == "VIP"]["储值"].sum())}，占 {w[w["身份"] == "VIP"]["储值"].sum() / w["储值"].sum() * 100:.2f}%')
for c in ['App 类', '浏览器类']:
    print(f'  VIP 在 {c}：{int((vip["类"] == c).sum())} 人，储值占全部 {vip[vip["类"] == c]["储值"].sum() / TOT * 100:.2f}%')
top = d.sort_values('储值', ascending=False).head(100)
tv = top[top['身份'] == 'VIP']
print(f'  储值前 100 名中 VIP {len(tv)} 人，平台 {tv["平台"].value_counts().to_dict()}')
print(f'  VIP 卡组 {vip["卡组"].value_counts().to_dict()}，卡别 {vip["卡别"].value_counts().sort_index().to_dict()}')
print(f'  VIP 最后在 web 登录 {int((vip["平台"] == "web").sum())} / {len(vip)} = {(vip["平台"] == "web").mean()*100:.2f}%')
