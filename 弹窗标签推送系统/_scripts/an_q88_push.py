"""Q88：推送方案比较（A27）的覆盖矩阵。照设计卡 Q88 方法：只算四格的 App 类占比与 S / R。
人群定义复用 an_q76_perf.load（内部 an_q66_push：D1、UQ = D8 独有）。不读联系方式。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys

sys.path.insert(0, _ROOT + '/_scripts')
import contextlib  # noqa: E402
import io  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    from an_q76_perf import load  # noqa: E402
    g, U = load()
TS, TR = U['S'].sum(), U['R'].sum()
Uv = U.set_index('会员编号')
D1, UQ = g['D1'], g['UQ']

cells = {
    'D1 待再来': D1[D1['tier'] != '离开'],
    'D1 离开': D1[D1['tier'] == '离开'],
    'D8 独有 待再来': UQ[UQ['tier'] != '离开'],
    'D8 独有 离开': UQ[UQ['tier'] == '离开'],
}
print(f'S 总额 {TS:,.0f}；R 总额 {TR:,.0f}')
for nm, x in cells.items():
    y = Uv.loc[list(x['会员编号'])]
    app = int(y['app'].sum())
    nv = y[y['nov']] if 'nov' in y else y
    print(f'{nm}: n {len(y):,}｜App 类 {app:,}（{app / len(y) * 100:.2f}%）｜剔除 VIP、黑名单后 App {int(nv["app"].sum()):,} / {len(nv):,}'
          f'｜S {y.S.sum():,.0f}（{y.S.sum() / TS * 100:.2f}%）｜R {y.R.sum():,.0f}（{y.R.sum() / TR * 100:.2f}%）｜分档 {x["tier"].value_counts().to_dict()}'
          f'｜平台 {y["plat"].value_counts().head(5).to_dict()}')
    # App 类人的 S / R 占该格
    a = y[y['app']]
    print(f'    App 类占该格 S {a.S.sum() / y.S.sum() * 100 if y.S.sum() else 0:.2f}%，R {a.R.sum() / y.R.sum() * 100 if y.R.sum() else 0:.2f}%')
