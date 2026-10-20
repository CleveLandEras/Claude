"""Q10 / A1 用户价值结构：身份 × 卡别的人数、储值率、累计储值占比、人均与中位数；储值集中度。只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
raw = len(df)
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
print('原始行', raw, '剔除后', N)

pay = '总充值金额'
card = '卡别'
df[pay] = pd.to_numeric(df[pay], errors='coerce').fillna(0)
df['有储值'] = df[pay] > 0
TOTAL = df[pay].sum()
PAYERS = int(df['有储值'].sum())
print('累计储值总额', round(TOTAL, 2), '有储值人数', PAYERS, '储值率', round(PAYERS / N * 100, 2))

cmap = {1: '普卡', 2: '银卡'}
df['卡组'] = df[card].map(lambda c: cmap.get(c, '金卡至至尊卡'))
df['卡名'] = df[card].astype(str)


def summarize(g, label):
    rows = []
    for k, s in g:
        n = len(s)
        p = s[s['有储值']]
        rows.append({
            label: k, '人数': n, '占活跃%': round(n / N * 100, 2),
            '有储值人数': len(p), '储值率%': round(len(p) / n * 100, 2) if n else 0,
            '累计储值占比%': round(s[pay].sum() / TOTAL * 100, 2),
            '有储值者人均': round(p[pay].mean(), 0) if len(p) else 0,
            '有储值者中位数': round(p[pay].median(), 0) if len(p) else 0,
        })
    return pd.DataFrame(rows)


pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 20)
print('\n== 表1 按身份 ==')
t1 = summarize(df.groupby('身份'), '身份')
print(t1.sort_values('人数', ascending=False).to_string(index=False))
print('\n== 表2 按卡别 ==')
print(summarize(df.groupby(card), '卡别').to_string(index=False))
print('\n== 表3 按卡组 ==')
print(summarize(df.groupby('卡组'), '卡组').to_string(index=False))
print('\n== 表4 身份 × 卡组 ==')
t4 = summarize(df.groupby(['身份', '卡组']), '身份卡组')
print(t4.to_string(index=False))

print('\n== 集中度 ==')
p = df.loc[df['有储值'], pay].sort_values(ascending=False).reset_index(drop=True)
for q in [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]:
    k = int(round(len(p) * q))
    print(f'有储值者前{q*100:g}%（{k} 人，分母 {len(p)}）贡献', round(p.head(k).sum() / TOTAL * 100, 2), '%',
          '门槛', round(p.iloc[k - 1], 0) if k else None)
a = df[pay].sort_values(ascending=False).reset_index(drop=True)
for q in [0.01, 0.1]:
    k = int(round(N * q))
    print(f'全体活跃前{q*100:g}%（{k} 人，分母 {N}）贡献', round(a.head(k).sum() / TOTAL * 100, 2), '%')

# 卡别门槛交叉：高卡用户累计储值最小值，用于判断卡别是否按储值定级
print('\n== 各卡别累计储值分位（全部，含 0） ==')
print(df.groupby(card)[pay].describe(percentiles=[.05, .25, .5]).round(0).to_string())

# 注册年限：用于说明累计时间偏差
reg = pd.to_datetime(df['注册时间'], errors='coerce')
df['注册年'] = reg.dt.year
print('\n== 身份 × 注册年份（人数） ==')
print(pd.crosstab(df['身份'], df['注册年'], margins=True).to_string())
print('\n== 卡组 × 注册年份（人数） ==')
print(pd.crosstab(df['卡组'], df['注册年'], margins=True).to_string())

print('\n== 注册年限偏差检查 ==')
print('注册时间缺失', int(reg.isna().sum()))
for idn in ['持續', '回流', '新增']:
    s = df[df['身份'] == idn]
    r = reg[df['身份'] == idn].dropna()
    print(idn, '有注册时间', len(r), '2023 年及以前注册占比', round((r.dt.year <= 2023).mean() * 100, 2),
          '注册时间中位数', r.median().date())
print('\n== 金额异常 ==')
print('累计储值为负的人数', int((df[pay] < 0).sum()), '负值合计', round(df.loc[df[pay] < 0, pay].sum(), 0))
print('高卡（3–7）中累计储值为 0 或负的人数', int(((df[card] >= 3) & (df[pay] <= 0)).sum()), '分母', int((df[card] >= 3).sum()))
print('普卡中累计储值 >= 10000 的人数', int(((df[card] == 1) & (df[pay] >= 10000)).sum()), '分母', int((df[card] == 1).sum()))
