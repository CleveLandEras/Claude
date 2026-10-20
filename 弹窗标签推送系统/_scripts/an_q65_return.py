"""Q65：回流又走与价值分层（D3）。照设计卡 Q65 S1–S3。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']

d = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
d = d[~d['身份'].isin(EX)].copy()
d['last'] = pd.to_datetime(d['最後登入時間']).dt.normalize()
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()
d['days'] = (T0 - d['last']).dt.days
d['tenure'] = (T0 - d['reg']).dt.days
d['dep'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
d['bet'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
d['cg'] = np.where(d['卡别'] == 1, '普卡', np.where(d['卡别'] == 2, '银卡', '金卡以上'))
d['r8'] = d['days'] >= 8
d['tier'] = pd.cut(d['days'], [-1, 0, 3, 7, 14, 31], labels=['0', '1–3', '4–7', '8–14', '15–31']).astype(str)
d['tb'] = pd.cut(d['tenure'], [-1, 29, 90, 365, 1095, 100000], labels=['<30', '30–90', '91–365', '1–3 年', '3 年以上']).astype(str)
d['pay'] = np.where(d['dep'] > 0, '有储值', '从未储值')
R = d[d['身份'] == '回流']
C = d[d['身份'] == '持續']
TA = d['dep'].sum()
TR = R['dep'].sum()
print(f'回流 {len(R):,}，储值 {TR:,.0f}（占活跃 {TR / TA * 100:.2f}%）；持續 {len(C):,}')
print('回流注册时长', R['tb'].value_counts().to_dict(), '；注册缺值', int(R['reg'].isna().sum()))

print('\n===== S1 卡组 × 登录五档（回流）')
for cg in ['普卡', '银卡', '金卡以上', '全部']:
    x = R if cg == '全部' else R[R.cg == cg]
    vc = x['tier'].value_counts()
    cells = '  '.join(f'{t}:{int(vc.get(t, 0)):,}({vc.get(t, 0) / len(x) * 100:.1f}%)' for t in ['0', '1–3', '4–7', '8–14', '15–31'])
    print(f'  {cg} {len(x):,}｜{cells}｜≥8 天 {int(x.r8.sum()):,}（{x.r8.mean() * 100:.2f}%），储值 {x.loc[x.r8, "dep"].sum():,.0f}')
print(f'  持續对照 ≥8 天：普卡 {C[C.cg == "普卡"].r8.mean() * 100:.2f}%、银卡 {C[C.cg == "银卡"].r8.mean() * 100:.2f}%、金卡以上 {C[C.cg == "金卡以上"].r8.mean() * 100:.2f}%')

print('\n===== S2 24 格对照（回流 vs 持續，≥8 天比例）')
rows = []
pos = neg = 0.0
for cg in ['普卡', '银卡', '金卡以上']:
    for tb in ['30–90', '91–365', '1–3 年', '3 年以上']:
        for pay in ['有储值', '从未储值']:
            r = R[(R.cg == cg) & (R.tb == tb) & (R.pay == pay)]
            c = C[(C.cg == cg) & (C.tb == tb) & (C.pay == pay)]
            ok = len(r) >= 30 and len(c) >= 30
            judged = ok and tb != '30–90'
            pr = r.r8.mean() * 100 if len(r) else np.nan
            pc = c.r8.mean() * 100 if len(c) else np.nan
            diff = pr - pc if ok else np.nan
            ex = len(r) * (pr - pc) / 100 if judged else np.nan
            if judged:
                if ex > 0:
                    pos += ex
                else:
                    neg += ex
            rows.append({'卡组': cg, '注册': tb, '付费': pay, '回流n': len(r), '回流≥8%': round(pr, 2) if ok else '—', '持續n': len(c),
                         '持續≥8%': round(pc, 2) if ok else '—', '差': round(diff, 2) if ok else '—', '进判读': '是' if judged else ('30–90 不进' if ok else '小格'),
                         '超出人数': round(ex, 1) if judged else '—'})
df = pd.DataFrame(rows)
print(df.to_string(index=False))
print(f'\n超出基线：正的和 {pos:,.1f}，负的和 {neg:,.1f}；占 D3 风险层 8,542 的 {pos / 8542 * 100:.2f}%')
pk = df[(df['卡组'] == '普卡') & (df['进判读'] == '是')]
print('普卡进判读格数', len(pk), '；差 ≥5 的格数', int((pk['差'].astype(float) >= 5).sum()), '；差 <5 的格数', int((pk['差'].astype(float) < 5).sum()))

print('\n===== S3 价值分层')
for cg in ['金卡以上', '银卡', '普卡']:
    x = R[R.cg == cg]
    s = x['dep'].sum()
    top10 = x['dep'].nlargest(10).sum() / s * 100 if s > 0 else 0
    print(f'  {cg}: {len(x):,} 人，储值 {s:,.0f}（占回流储值 {s / TR * 100:.2f}%），≥8 天 {int(x.r8.sum()):,}（{x.r8.mean() * 100:.2f}%），≥8 天储值 {x.loc[x.r8, "dep"].sum():,.0f}，前 10 人占本组储值 {top10:.2f}%')
p = R[R.cg == '普卡']
z = p[(p.dep <= 0) & (p.bet <= 0)]
print(f'  普卡·从未储值且押注为 0：{len(z):,}（占普卡回流 {len(z) / len(p) * 100:.2f}%），≥8 天 {int(z.r8.sum()):,}（{z.r8.mean() * 100:.2f}%）')
pp = p[p.dep > 0]
print(f'  普卡·有储值：{len(pp):,}，≥8 天 {int(pp.r8.sum()):,}（{pp.r8.mean() * 100:.2f}%）')
print(f'  回流全体押注为 0：{int((R.bet <= 0).sum()):,}（{(R.bet <= 0).mean() * 100:.2f}%）；≥8 天中押注为 0 {int((R.r8 & (R.bet <= 0)).sum()):,}（{(R[R.r8].bet <= 0).mean() * 100:.2f}%）')
g = R[(R.cg == '金卡以上') & R.r8]
print(f'  金卡以上回流 ≥8 天 {len(g)}，卡别', g['卡别'].value_counts().sort_index().to_dict())
