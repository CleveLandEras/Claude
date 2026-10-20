"""Q20 / A7 目标人群重叠。不带参数运行，只读。
人群：身份三类（新增、回流、其余 = 持续 + VIP + 黑名单，三者互斥），潜在付费代理（累计储值 <= 0 且累计押注 > 10,000），
潜在流失（当月储值 < 上月 50%，无月度数据，不可算；只给上限：累计储值 > 0）。
日期按日期相减，9/16 记第 0 天（与环节1 口径一致）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
raw = len(df)
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
print('原始', raw, '剔除后', N)

amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
ident = df['身份'].map({'持續': '其余', 'VIP': '其余', '黑名單': '其余', '回流': '回流', '新增': '新增'})
print('身份未映射', int(ident.isna().sum()))
card = pd.Series(np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上')), index=df.index)
gap = (pd.Timestamp('2026-09-16') - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
recent = gap <= 7
pay = amt > 0
pp = (amt <= 0) & (bet > 10000)       # 潜在付费代理（上限）
churn_ub = pay                         # 潜在流失上限：上月有储值的前提是累计储值 > 0

def pct(a, b):
    return f'{a / b * 100:.2f}%' if b else '—'

ids = ['新增', '回流', '其余']
cards = ['普卡', '银卡', '金卡以上']
print('\n== 身份人数 ==', {k: int((ident == k).sum()) for k in ids})
print('潜在付费', int(pp.sum()), pct(pp.sum(), N), '潜在流失上限（有储值）', int(churn_ub.sum()), pct(churn_ub.sum(), N))
print('潜在付费 ∩ 有储值（应为 0）', int((pp & pay).sum()))

print('\n== 两两重叠（格内人数，括号：占 62,292）==')
groups = {'新增': ident == '新增', '回流': ident == '回流', '其余': ident == '其余', '潜在付费': pp, '潜在流失上限': churn_ub}
names = list(groups)
for a in names:
    row = []
    for b in names:
        c = int((groups[a] & groups[b]).sum())
        row.append(f'{b}:{c}')
    print(a, row)

print('\n== 潜在付费 × 身份：人数、占该身份、占潜在付费、0–7 天登录 ==')
for k in ids:
    m = pp & (ident == k)
    print(k, int(m.sum()), '占身份', pct(m.sum(), (ident == k).sum()), '占潜在付费', pct(m.sum(), pp.sum()),
          '0–7天', int((m & recent).sum()), pct((m & recent).sum(), m.sum()))

print('\n== 潜在流失上限 × 身份 ==')
for k in ids:
    m = churn_ub & (ident == k)
    print(k, int(m.sum()), '占身份', pct(m.sum(), (ident == k).sum()), '0–7天', int((m & recent).sum()), pct((m & recent).sum(), m.sum()))

print('\n== 同时落在 2 类及以上 ==')
# 口径 A：五类都算（其余也算一类）
kA_low = pp                      # 潜在流失取 0
kA_up = pp | churn_ub            # 潜在流失取上限
print('A 下限', int(kA_low.sum()), pct(kA_low.sum(), N), 'A 上限', int(kA_up.sum()), pct(kA_up.sum(), N))
# 口径 B：不把其余算一类（与规划者速算同口径）
nb = (ident != '其余')
kB_low = nb & pp
kB_up = nb & (pp | churn_ub)
print('B 下限', int(kB_low.sum()), pct(kB_low.sum(), N), 'B 上限', int(kB_up.sum()), pct(kB_up.sum(), N))
print('B 下限中 0–7 天登录', int((kB_low & recent).sum()), pct((kB_low & recent).sum(), kB_low.sum()))
# 3 类及以上：身份互斥、潜在付费与潜在流失互斥 → 最多 2 类
k = (ident == '新增').astype(int) + (ident == '回流').astype(int) + (ident == '其余').astype(int) + pp.astype(int) + churn_ub.astype(int)
print('A 上限口径下类数分布', k.value_counts().sort_index().to_dict())

print('\n== 对照：规划者速算的登录代理（银卡以上且 >7 天未登录，旧基准 9/17）==')
gap17 = (pd.Timestamp('2026-09-17') - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
proxy_old = (card != '普卡') & (gap17 > 7)
kk = (ident == '新增').astype(int) + (ident == '回流').astype(int) + pp.astype(int) + proxy_old.astype(int)
print('旧速算 2 类及以上', int((kk >= 2).sum()), pct((kk >= 2).sum(), N))
proxy_new = (card != '普卡') & (gap > 7)
kk2 = (ident == '新增').astype(int) + (ident == '回流').astype(int) + pp.astype(int) + proxy_new.astype(int)
print('登录代理按 9/16 基准 2 类及以上', int((kk2 >= 2).sum()), pct((kk2 >= 2).sum(), N), '代理人数', int(proxy_new.sum()))
print('回流 ∩ 潜在付费', int(((ident == '回流') & pp).sum()))

print('\n== 身份 × 卡组 9 格：人数、储值率、潜在付费、潜在流失上限（有储值）==')
for k in ids:
    for c in cards:
        m = (ident == k) & (card == c)
        n = int(m.sum())
        print(k, c, n, pct(n, N), '储值率', pct((m & pay).sum(), n), '有储值', int((m & pay).sum()),
              '潜在付费', int((m & pp).sum()), pct((m & pp).sum(), n), '0–7天', pct((m & recent).sum(), n))
for c in cards:
    m = card == c
    print('合计', c, int(m.sum()), '储值率', pct((m & pay).sum(), m.sum()), '有储值', int((m & pay).sum()), '潜在付费', int((m & pp).sum()))
