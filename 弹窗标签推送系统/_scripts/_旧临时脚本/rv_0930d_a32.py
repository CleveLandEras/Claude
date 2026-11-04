# 只读复算 A32（审查用，独立实现）：高卡 RTP 档内排名 D、S5、S6 占比
import numpy as np
import pandas as pd
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
print('活跃剔除后', len(a))
T = pd.Timestamp('2026-09-16')
a['last'] = pd.to_datetime(a['最後登入時間'], errors='coerce')
a['gap'] = (T - a['last'].dt.normalize()).dt.days
a['S'] = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
print('RTP 缺失', a['RTP'].isna().sum(), '；gap 缺失', a['gap'].isna().sum(), '；gap 范围', a['gap'].min(), a['gap'].max())
h = a[(a['卡别'] >= 3) & (~a['身份'].isin(['VIP', '黑名單']))].copy()
h['y'] = (h['gap'] >= 8).astype(int)
print('高卡', len(h), 'y=1', h['y'].sum())

def q(s, k):
    r = s.rank(method='first', pct=True)
    return np.ceil(r * k).clip(1, k).astype(int)

def D(df):
    df = df.copy()
    df['bq'] = q(df['游戏总押注'], 4)
    out = []
    for b, g in df.groupby('bq'):
        rq = q(g['RTP'], 4)
        lo = g[rq == 1]['y'].mean(); mid = g[rq.isin([2, 3])]['y'].mean(); top = g[rq == 4]['y'].mean()
        out.append((b, len(g), (rq == 1).sum(), lo, mid, lo - mid, top - mid))
    w = np.array([o[2] for o in out], float)
    d = np.array([o[5] for o in out]); d2 = np.array([o[6] for o in out])
    for o in out:
        print('  档', o[0], '人', o[1], '低', o[2], f'{o[3]*100:.1f}% 中 {o[4]*100:.1f}% D {o[5]*100:+.2f} Dp {o[6]*100:+.2f}')
    print(f'  合并 D {(w*d).sum()/w.sum()*100:+.2f}  Dp {(w*d2).sum()/w.sum()*100:+.2f}')
    return df

print('S2'); D(h)
for lab, m in [('卡3', h['卡别'] == 3), ('卡4', h['卡别'] == 4), ('卡5-7', h['卡别'] >= 5)]:
    print(lab, m.sum()); D(h[m])
# S5
l = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
l = l[~l['身份'].isin(['機器人', '測試帳號'])]
lk = l[(l['卡别'] >= 3) & (~l['身份'].isin(['VIP', '黑名單']))]
only = lk[~lk['会员编号'].isin(a['会员编号'])].copy(); only['y'] = 1
print('S5 名单高卡', len(lk), '只在名单', len(only))
D(pd.concat([h[['游戏总押注', 'RTP', 'y']], only[['游戏总押注', 'RTP', 'y']]]))
# S6
h['bq'] = q(h['游戏总押注'], 4)
h['rq'] = h.groupby('bq')['RTP'].transform(lambda s: q(s, 4))
low = h[h['rq'] == 1]
tot = a['S'].sum()
print('S6 低 25% 人数', len(low), '在场', (low['gap'] <= 7).sum(), '没来', low['y'].sum())
print(f'  累计储值占比 {low["S"].sum()/tot*100:.2f}%；其中没来 {low[low["y"]==1]["S"].sum()/tot*100:.2f}%；高卡 8 天以上没来层 {h[h["y"]==1]["S"].sum()/tot*100:.2f}%')
# 另一种解释：低 RTP 组最后登录前是否押注更少（活跃度）——看档内低 RTP 组押注中位与中间组比
for b, g in h.groupby('bq'):
    print('  档', b, '押注中位 低/中', round(g[g['rq']==1]['游戏总押注'].median()/g[g['rq'].isin([2,3])]['游戏总押注'].median(), 3))
