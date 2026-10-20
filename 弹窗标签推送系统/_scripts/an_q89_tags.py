"""Q89：标签取舍（A28）S3 本地覆盖核对。照设计卡 Q89 S3：D1、D8 独有各按「最后登录距 9/16 的天数」切 8–30 / 31 / 32–46（离开）三档 × 卡组。
人群定义复用 an_q76_perf.load（内部 an_q66_push：D1、UQ = D8 独有），不另定义。只读，不带参数。
附：剔除前原始数据中测试账号落在金卡以上 0–7 天的人数（判断 N1 对象是否会圈进测试账号，只计数）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys

sys.path.insert(0, _ROOT + '/_scripts')
import contextlib  # noqa: E402
import io  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    from an_q76_perf import load  # noqa: E402
    g, U = load()

D1, UQ = g['D1'], g['UQ']


def band(d):
    return np.where(d <= 30, '8–30', np.where(d == 31, '31', '32+'))


def cg(c):
    return np.where(c >= 3, '金卡以上', np.where(c == 2, '银卡', '普卡'))


for nm, x in [('D1', D1), ('D8 独有', UQ)]:
    x = x.copy()
    x['band'] = band(x['days'])
    x['cg'] = cg(x['卡别'])
    print(f'===== {nm}：n {len(x):,}｜days 范围 {int(x.days.min())}–{int(x.days.max())}')
    print('  来源 × 三档：')
    print(pd.crosstab(x['src'], x['band'], margins=True).to_string())
    print('  三档 × 卡组：')
    print(pd.crosstab(x['band'], x['cg'], margins=True).to_string())
    w = x[x['src'] != '离开']
    n8 = int((w['band'] == '8–30').sum())
    print(f'  待再来 {len(w):,}；其中 8–30 天 {n8:,}（{n8 / len(w) * 100:.2f}%）；31 天 {int((w["band"] == "31").sum()):,}')
    l = x[x['src'] == '离开']
    print(f'  离开 {len(l):,}；days 范围 {int(l.days.min()) if len(l) else "—"}–{int(l.days.max()) if len(l) else "—"}；其中 ≤ 30 天 {int((l.days <= 30).sum())}')
    # 按卡组的 8–30 覆盖占待再来
    for c in ['普卡', '银卡', '金卡以上']:
        wc = w[w['cg'] == c]
        if len(wc):
            print(f'    {c}：待再来 {len(wc):,}，8–30 天 {int((wc["band"] == "8–30").sum()):,}（{(wc["band"] == "8–30").mean() * 100:.2f}%）')
    # 身份分布（VIP、黑名单是否在内）
    print('  身份：', x['身份'].value_counts().to_dict())

# 附：「7–30 天未登入」按名称会同时圈进第 7 天、仍算在场的人
a = g['a']
d7 = a[a['days'] == 7]
print(f'\n附 1：活跃中最后登录恰为第 7 天 {len(d7):,} 人（按名称「7–30 天」会被圈入，但属 0–7 天在场）')

# 附 2：测试账号在金卡以上 0–7 天（原始数据，剔除前；只计数）
B = _ROOT + '/数据/'
raw = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
t = raw[raw['身份'] == '測試帳號'].copy()
t['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(t['最後登入時間']).dt.normalize()).dt.days
hi = t[t['卡别'] >= 3]
print(f'附 2：测试账号 {len(t)}；金卡以上 {len(hi)}；其中 0–7 天 {int((hi.days <= 7).sum())}')
# N1 对象（金卡以上 0–7 天，剔除后）规模，作分母参照
n1 = a[(a['卡别'] >= 3) & (a['days'] <= 7)]
print(f'附 3：剔除后金卡以上 0–7 天 {len(n1):,}；其中有储值 {int((n1.dep > 0).sum()):,}；无储值 {int((n1.dep <= 0).sum()):,}')
print('    按卡别：', n1['卡别'].value_counts().sort_index().to_dict())
g3 = n1[n1['卡别'] == 3]
print(f'    其中金卡（卡别 3）{len(g3):,}，占 {len(g3) / len(n1) * 100:.2f}%；金卡储值占金卡以上 0–7 天储值 {g3.dep.sum() / n1.dep.sum() * 100:.2f}%')
