"""Q12 / A2 储值档位分布：同一快照内，有储值者累计储值的档位分布，按身份、卡别、身份 × 卡组分列；
另做累计时长对照（注册 ≤90 天的持续、回流 vs 新增）。只读。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
import pandas as pd

BASE = _ROOT + ''
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
pay = '总充值金额'
df[pay] = pd.to_numeric(df[pay], errors='coerce').fillna(0)
p = df[df[pay] > 0].copy()
print('剔除后', N, '有储值', len(p))

bins = [0, 200, 1000, 10000, float('inf')]
labels = ['<200', '200–999', '1,000–9,999', '≥10,000']
p['档'] = pd.cut(p[pay], bins=bins, labels=labels, right=False)
# 0 已排除（>0），1–199 落在 [0,200)
# 身份三分法：持续含 VIP、黑名单，与环节1 一致
p['身份3'] = p['身份'].replace({'VIP': '持續', '黑名單': '持續'})
p['卡组'] = p['卡别'].map(lambda c: {1: '普卡', 2: '银卡'}.get(c, '金卡以上'))


def dist(g, name):
    rows = []
    for k, s in g:
        n = len(s)
        vc = s['档'].value_counts().reindex(labels, fill_value=0)
        r = {name: k, '有储值人数': n}
        for l in labels:
            r[l] = f"{vc[l]}（{vc[l] / n * 100:.2f}%）"
        r['中位数'] = round(s[pay].median(), 0)
        rows.append(r)
    return pd.DataFrame(rows)


pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 20)
print('\n== 全体 ==')
print(dist([('全体', p)], '组').to_string(index=False))
print('\n== 按身份（三分法） ==')
print(dist(p.groupby('身份3'), '身份').to_string(index=False))
print('\n== 按卡别 1–7 ==')
print(dist(p.groupby('卡别'), '卡别').to_string(index=False))
print('\n== 按卡组 ==')
print(dist(p.groupby('卡组'), '卡组').to_string(index=False))
print('\n== 身份 × 卡组 ==')
print(dist(p.groupby(['身份3', '卡组']), '身份卡组').to_string(index=False))

# 累计时长对照：按日期相减（与 an_xianzhuang 修正后一致）
reg = pd.to_datetime(p['注册时间'], errors='coerce').dt.normalize()
p['注册天数'] = (pd.Timestamp('2026-09-16') - reg).dt.days
print('\n== 累计时长对照：注册 ≤90 天（注册天数 0–90）的有储值者 ==')
q = p[p['注册天数'].between(0, 90)]
print(dist(q.groupby('身份3'), '身份').to_string(index=False))
print('\n== 累计时长对照：注册 31–90 天 ==')
q2 = p[p['注册天数'].between(31, 90)]
print(dist(q2.groupby('身份3'), '身份').to_string(index=False))
print('\n== 累计时长对照：普卡且注册 ≤90 天 ==')
q3 = q[q['卡组'] == '普卡']
print(dist(q3.groupby('身份3'), '身份').to_string(index=False))

# 各档对累计储值的贡献
TOTAL = df[pay].sum()
print('\n== 各档人数与累计储值占比（分母：有储值人数 / 全部累计储值） ==')
for l in labels:
    s = p[p['档'] == l]
    print(l, len(s), f"{len(s) / len(p) * 100:.2f}%", f"储值占比 {s[pay].sum() / TOTAL * 100:.2f}%")

# 首储礼包 NT$50 对照：累计储值 ≤50 的比例
print('\n== 累计储值 ≤50（约等于只买过一次首储礼包或更少）比例 ==')
for k, s in p.groupby('身份3'):
    print(k, int((s[pay] <= 50).sum()), len(s), f"{(s[pay] <= 50).mean() * 100:.2f}%")
print('全体', int((p[pay] <= 50).sum()), len(p), f"{(p[pay] <= 50).mean() * 100:.2f}%")
