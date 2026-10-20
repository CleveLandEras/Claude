"""Q22：卡别 × 最后登录（环节1 第一节第 4 小节）。卡组三档与卡别 3–7 分列，最后登录按日期相减、9/16 记第 0 天，
分 0、1–3、4–7、8–14、15–31 天（与 A3 表 5 一致）。每格：人数、行内占比、该格累计储值占全部累计储值的比例。
另给每行的有储值人数与合计储值，供核对。不带参数运行，只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd
import numpy as np

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
pay = '总充值金额'
df[pay] = pd.to_numeric(df[pay], errors='coerce').fillna(0)
df['卡别'] = pd.to_numeric(df['卡别'], errors='coerce')
df['卡组'] = np.where(df['卡别'] == 1, '普卡', np.where(df['卡别'] == 2, '银卡', '金卡以上'))
ref = pd.Timestamp('2026-09-16')
df['距末登'] = (ref - pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()).dt.days
TOTAL = df[pay].sum()
print('剔除后', N, '累计储值合计', int(TOTAL), '距末登 空值', int(df['距末登'].isna().sum()),
      '最小', df['距末登'].min(), '最大', df['距末登'].max())
print('卡别分布', df['卡别'].value_counts().sort_index().to_dict())

bins = [-1, 0, 3, 7, 14, 31]
labels = ['0', '1–3', '4–7', '8–14', '15–31']
df['档'] = pd.cut(df['距末登'], bins=bins, labels=labels)
print('未入档', int(df['档'].isna().sum()))


def row(name, s):
    n = len(s)
    cnt = s['档'].value_counts().reindex(labels, fill_value=0)
    amt = s.groupby('档', observed=False)[pay].sum().reindex(labels, fill_value=0)
    parts = [f'{l}: {int(cnt[l])} ({cnt[l]/n*100:.2f}%) 储值占比 {amt[l]/TOTAL*100:.2f}%' for l in labels]
    le3 = int(cnt['0'] + cnt['1–3'])
    le7 = le3 + int(cnt['4–7'])
    gt7 = n - le7
    print(f'\n[{name}] 人数 {n}，行储值占比 {s[pay].sum()/TOTAL*100:.2f}%，有储值 {int((s[pay] > 0).sum())}')
    print('  ' + '；'.join(parts))
    print(f'  0–3 天 {le3} ({le3/n*100:.2f}%)，0–7 天 {le7} ({le7/n*100:.2f}%)，8 天以上 {gt7} ({gt7/n*100:.2f}%)'
          f'；8 天以上储值占比 {s.loc[s["距末登"] > 7, pay].sum()/TOTAL*100:.2f}%'
          f'；行内 8 天以上储值占本行 {s.loc[s["距末登"] > 7, pay].sum()/max(s[pay].sum(),1)*100:.2f}%')


row('全部', df)
for g in ['普卡', '银卡', '金卡以上']:
    row(g, df[df['卡组'] == g])
for c in [3, 4, 5, 6, 7]:
    row(f'卡别{c}', df[df['卡别'] == c])

print('\n== 核对：各格人数合计与储值占比合计 ==')
print('人数合计', int(df['档'].value_counts().sum()), '储值占比合计',
      round(df.groupby('档', observed=False)[pay].sum().sum() / TOTAL * 100, 2))

print('\n== 对照：按 9/17 基准（规划者速算口径）金卡以上 ==')
g = df[df['卡组'] == '金卡以上']
d17 = (pd.Timestamp('2026-09-17') - pd.to_datetime(g['最後登入時間'], errors='coerce')).dt.days
print('9/17 基准 ≤3 天', f'{(d17 <= 3).mean()*100:.2f}%', '>7 天', f'{(d17 > 7).mean()*100:.2f}%')
