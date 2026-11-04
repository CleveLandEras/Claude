# 审查者复算（只读）：A41 的 74,480 / 40,117 / 77.92% 与 20,883
import pandas as pd
D = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(D + '近一月活跃_20260916.csv', encoding='utf-8-sig')
b = pd.read_csv(D + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
bad = ['機器人', '測試帳號']
a = a[~a['身份'].isin(bad)].copy(); b = b[~b['身份'].isin(bad)].copy()
b2 = b[~b['会员编号'].isin(a['会员编号'])].copy()
print('A', len(a), 'B', len(b), 'B only', len(b2))
u = pd.concat([a, b2])
ref = pd.Timestamp('2026-09-16')
u['dsl'] = (ref - pd.to_datetime(u['最後登入時間']).dt.normalize()).dt.days
print('union', len(u), '>=8', (u['dsl'] >= 8).sum(), round((u['dsl'] >= 8).mean() * 100, 2), '>=15', (u['dsl'] >= 15).sum())
w = u[u['dsl'] >= 8]
plat = w['登入平台'].astype(str).str.lower()
app = plat.isin(['android', 'ios', 'apk'])
print('app', app.sum(), round(app.mean() * 100, 2))
print(plat.value_counts().to_dict())
# 20,883: 从未储值 0-7 天, 剔除 VIP/黑名單
a['dsl'] = (ref - pd.to_datetime(a['最後登入時間']).dt.normalize()).dt.days
x = a[(a['总充值金额'] <= 0) & (a['dsl'] <= 7)]
print('从未储值0-7', len(x), '剔VIP黑名單', (~x['身份'].isin(['VIP', '黑名單'])).sum())
# 近一月内 >=8 占比
print('近一月内 >=8 占比', round((a['dsl'] >= 8).mean() * 100, 2))
# 卡别 1-99 分位 (金卡)
for c in [2, 3, 4, 5, 6, 7]:
    s = a[(a['卡别'] == c) & (a['总充值金额'] > 0) & (~a['身份'].isin(['VIP', '黑名單']))]['总充值金额']
    print(c, len(s), s.quantile([.01, .05, .25, .9, .95, .99]).round(0).tolist(), s.max(), round(s.quantile(.9) / s.quantile(.25), 1))
