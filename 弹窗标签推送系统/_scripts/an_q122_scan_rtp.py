"""Q122：① 列使用扫描（各列在分析文件里出现的文件数）；② 输赢（RTP）与高卡「8 天以上没来」的关系（同押注档内比较）。
照设计卡 Q122 第一、二部分 S1–S6。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import glob
import os
import numpy as np
import pandas as pd

B = _ROOT + '/'
EX = ['機器人', '測試帳號']
TODAY = pd.Timestamp('2026-09-16')

a = pd.read_csv(B + '数据/近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(EX)].copy()
l = pd.read_csv(B + '数据/八月登录流失名单_20260916.csv', encoding='utf-8-sig')
l = l[~l['身份'].isin(EX)].copy()

# ---------------- 第一部分：列扫描 ----------------
print('===== 列扫描：各列名在 分析/*.md 中出现的文件数（共 %d 个文件）' % len(glob.glob(B + '分析/*.md')))
files = {f: open(f, encoding='utf-8').read() for f in glob.glob(B + '分析/*.md')}
for c in a.columns:
    key = {'最後登入時間': '最後登入', '游戏总押注': '总押注', '游戏总输赢': '总输赢', '总充值金额': '总充值'}.get(c, c)
    n = sum(1 for t in files.values() if key in t)
    print(f'  {c}（检索词「{key}」）：{n} 个文件')

# ---------------- 第二部分 ----------------
a['gap'] = (TODAY - pd.to_datetime(a['最後登入時間'], errors='coerce').dt.normalize()).dt.days
a['reg_days'] = (TODAY - pd.to_datetime(a['注册时间'], errors='coerce').dt.normalize()).dt.days
a['S'] = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
hi = a[(a['卡别'] >= 3) & (~a['身份'].isin(['VIP', '黑名單']))].copy()
hi['y'] = (hi['gap'] >= 8).astype(int)
print('\n高卡（卡 3–7，去 VIP、黑名单）', len(hi), '；8 天以上没来', int(hi['y'].sum()), round(hi['y'].mean() * 100, 2), '%')


def q4(s):
    return pd.qcut(s.rank(method='first'), 4, labels=[1, 2, 3, 4]).astype(int)


hi['rq'] = q4(hi['RTP'])
print('\n===== S1 复现：全体高卡按 RTP 四等份（1 = 最低）')
t = hi.groupby('rq')['y'].agg(['size', 'mean'])
t['mean'] = (t['mean'] * 100).round(1)
print(t.T.to_string())
print('  试算参照：18.1% / 10.7% / 8.4% / 10.6%；人数 1577 / 1573 / 1579 / 1570')


def dstat(df, low=1, mid=(2, 3), hi_=None):
    """返回 (D, se, n_low, n_mid, rate_low, rate_mid)；hi_ 不为 None 时 D' = 最高份 − 中间"""
    a1 = df[df['rq'] == (hi_ if hi_ else low)]
    m = df[df['rq'].isin(mid)]
    if len(a1) == 0 or len(m) == 0:
        return None
    p1, p2 = a1['y'].mean(), m['y'].mean()
    se = np.sqrt(p1 * (1 - p1) / len(a1) + p2 * (1 - p2) / len(m))
    return p1 - p2, se, len(a1), len(m), p1, p2


def by_bet(df, label, ycol='y', qfun=q4):
    """押注四档内按 RTP 排名四等份，返回逐档结果与加权合并"""
    df = df.copy()
    df['bq'] = qfun(df['游戏总押注'])
    rows, ws, ds, vs = [], [], [], []
    ws2, ds2, vs2 = [], [], []
    for b in sorted(df['bq'].unique()):
        sub = df[df['bq'] == b].copy()
        sub['rq'] = qfun(sub['RTP'])
        r = dstat(sub)
        r2 = dstat(sub, hi_=4)
        rows.append((b, len(sub), r[2], r[4], r[5], r[0], r[1], r2[0]))
        ws.append(r[2]); ds.append(r[0]); vs.append(r[1] ** 2)
        ws2.append(r2[2]); ds2.append(r2[0])
    ws = np.array(ws, float); ds = np.array(ds); vs = np.array(vs)
    D = (ws * ds).sum() / ws.sum()
    se = np.sqrt(((ws ** 2) * vs).sum()) / ws.sum()
    ws2 = np.array(ws2, float)
    D2 = (ws2 * np.array(ds2)).sum() / ws2.sum()
    print(f'\n--- {label}')
    print('  押注档 | 档人数 | 档内最低25%人数 | 最低25%比例 | 中间两份比例 | D(百分点) | D 的 SE | D\'(最高25%−中间)')
    for r in rows:
        print(f'  B{r[0]} | {r[1]} | {r[2]} | {r[3]*100:.1f}% | {r[4]*100:.1f}% | {r[5]*100:+.1f} | {r[6]*100:.1f} | {(r[7])*100:+.1f}')
    print(f'  合并 D = {D*100:+.2f} 个百分点（95% 区间 {(D-1.96*se)*100:+.2f} ~ {(D+1.96*se)*100:+.2f}）；合并 D\' = {D2*100:+.2f}')
    n_ge3 = sum(1 for d in ds if d >= 0.03)
    print(f'  档内 D ≥ 3 个百分点的档数：{n_ge3} / {len(ds)}')
    return D, se, D2, rows


print('\n===== S2 主分析（押注四档内的 RTP 排名）与 S3 U 形检查')
D, se, D2, rows = by_bet(hi, 'S2/S3 高卡全体')

print('\n===== S4 分层复核（合并 D；格子 < 100 人只报人数）')
for lab, mask in [('卡 3', hi['卡别'] == 3), ('卡 4', hi['卡别'] == 4), ('卡 5–7', hi['卡别'] >= 5),
                  ('注册 ≤ 365 天', hi['reg_days'] <= 365), ('注册 366–1,095 天', (hi['reg_days'] > 365) & (hi['reg_days'] <= 1095)),
                  ('注册 > 1,095 天', hi['reg_days'] > 1095)]:
    sub = hi[mask]
    if len(sub) < 400:
        print(f'  {lab}：{len(sub)} 人（格子太小，只报人数）')
        continue
    by_bet(sub, f'S4 {lab}（{len(sub)} 人）')

print('\n===== S5 敏感性：并入八月流失名单里的高卡离开者（32–46 天，y = 1）')
lk = l[(l['卡别'] >= 3) & (~l['身份'].isin(['VIP', '黑名單']))].copy()
only = lk[~lk['会员编号'].isin(a['会员编号'])].copy()
print('  流失名单高卡', len(lk), '；其中只在名单里（8/1–8/15 最后登录）', len(only))
only['y'] = 1
comb = pd.concat([hi[['会员编号', '游戏总押注', 'RTP', 'y']], only[['会员编号', '游戏总押注', 'RTP', 'y']]], ignore_index=True)
by_bet(comb, f'S5 并入离开者后（{len(comb)} 人）')

print('\n===== 反例检查 ①：押注十等份内排名代替四等份')


def q10(s):
    return pd.qcut(s.rank(method='first'), 10, labels=list(range(1, 11))).astype(int)


hd = hi.copy()
hd['bq'] = q10(hd['游戏总押注'])
ws, ds = [], []
for b in sorted(hd['bq'].unique()):
    sub = hd[hd['bq'] == b].copy()
    sub['rq'] = q4(sub['RTP'])
    r = dstat(sub)
    ws.append(r[2]); ds.append(r[0])
print('  押注十等份内 RTP 四等份，加权合并 D = %+.2f 个百分点' % ((np.array(ws) * np.array(ds)).sum() / np.array(ws).sum() * 100))

print('\n===== 反例检查 ②：普卡、银卡做同样的 S2')
py = a[(a['卡别'] <= 2) & (~a['身份'].isin(['VIP', '黑名單']))].copy()
py['y'] = (py['gap'] >= 8).astype(int)
by_bet(py, f'普卡、银卡（{len(py)} 人）')

print('\n===== S6 量级（先算，是否使用按判读规则）')
hi['bq'] = q4(hi['游戏总押注'])
low = []
for b in sorted(hi['bq'].unique()):
    sub = hi[hi['bq'] == b].copy()
    sub['rq'] = q4(sub['RTP'])
    low.append(sub[sub['rq'] == 1])
low = pd.concat(low)
n_low = len(low)
tot_S = a['S'].sum()
mon = np.maximum(a['S'], 0) / np.maximum(a['reg_days'] / 30.44, 1)
low_mon = np.maximum(low['S'], 0) / np.maximum(low['reg_days'] / 30.44, 1)
print('  档内最低 25% 的高卡合计', n_low, '；其中 0–7 天在场', int((low['gap'] <= 7).sum()), '；8 天以上没来', int(low['y'].sum()))
print(f'  超额人数 ≈ 合并 D × 最低 25% 人数 = {D * n_low:.0f} 人')
print(f'  最低 25% 的累计储值占全平台（62,292 人）累计储值 {low["S"].sum() / tot_S * 100:.2f}%；历史月均口径 {low_mon.sum() / mon.sum() * 100:.2f}%')
print(f'  其中 8 天以上没来那部分：累计储值占 {low[low["y"] == 1]["S"].sum() / tot_S * 100:.2f}%')
print(f'  高卡 8 天以上没来这一层（755 人）累计储值占 {hi[hi["y"] == 1]["S"].sum() / tot_S * 100:.2f}%（对照 A16 的 7.18% 含离开者 172 人）')
