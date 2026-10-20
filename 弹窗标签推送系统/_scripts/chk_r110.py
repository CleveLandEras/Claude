"""R110 复核：D4b 参照组口径（身份新增 vs 注册 ≤ 30 天）。只读，不带参数。复用 an_q76_perf.load。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
sys.path.insert(0, _ROOT + '/_scripts/')
from an_q76_perf import load, elastic  # noqa: E402

g, U = load()
TS, TR = U['S'].sum(), U['R'].sum()
p = U[U['dep'] > 0]
a = p[p['reg'] >= '2026-08-18']
b = p[p['tenure'] <= 30]
c = p[p['身份'] == '新增']
for k, x in [('注册 8/18 起', a), ('注册 ≤ 30 天', b), ('身份新增', c)]:
    print(f'{k}: n={len(x):,} 均值 {x.dep.mean():.1f} 中位 {x.dep.median():.1f} 注册最早 {x.reg.min()}')
extra = b[~b['会员编号'].isin(a['会员编号'])]
print('≤30 天但不在 8/18 起：', len(extra), '注册日分布', extra['reg'].astype(str).str[:10].value_counts().to_dict())
for k, x in [('8/18 起', a), ('≤30 天', b)]:
    em, ed = elastic(20883, x.dep.mean()), elastic(20883, x.dep.median())
    print(f'{k}: 1% 弹性 均值参照 {em:,.0f}（S {em/TS*100:.4f}% R {em/TR*100:.3f}%）中位参照 {ed:,.0f}')
