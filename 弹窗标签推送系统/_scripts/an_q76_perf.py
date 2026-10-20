"""Q76：对业绩的影响量级（A23）。照设计卡 Q76 S1–S6。只读，不带参数。
两个单位：S = 累计储值（合并口径，含负值行）；R = max(累计储值,0) ÷ max(账号月龄,1)，月龄 = 注册距 9/16 天数 ÷ 30.44，注册缺值不计入 R。
人群定义复用 an_q66_push.py（D1、D2、D3、D8、独有、U1、U2）与 an_q65_return.py（D3 的 24 格对照），不另定义。
Q77 可 import：from an_q76_perf import load, unit_S, unit_R, expose, elastic（import 时不运行主程序）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

SC = _ROOT + '/_scripts/'
MONTH = 30.44


def _run(name):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return runpy.run_path(SC + name)


def unit_S(df):
    return df['dep']


def unit_R(df):
    m = (df['tenure'] / MONTH).clip(lower=1)
    return (df['dep'].clip(lower=0) / m).where(df['tenure'].notna())


def load():
    g = _run('an_q66_push.py')
    U = g['U'].copy()
    U['S'] = unit_S(U)
    U['R'] = unit_R(U)
    return g, U


def expose(U, ids, TS, TR):
    """ids: 会员编号集合。返回该人群在两个单位下的暴露与集中度。"""
    x = U[U['会员编号'].isin(ids)]
    s, r = x['S'].sum(), x['R'].sum()
    t10s = x['S'].nlargest(10).sum()
    t10r = x['R'].nlargest(10).sum()
    return {'n': len(x), 'S': s, 'S%': s / TS * 100, 'R': r, 'R%': r / TR * 100, '有储值率': (x['dep'] > 0).mean() * 100,
            '前10占S': t10s / s * 100 if s else np.nan, '前10占R': t10r / r * 100 if r else np.nan,
            '去前10 S%': (s - t10s) / TS * 100, '去前10 R%': (r - t10r) / TR * 100}


def elastic(n, value):
    """风险层每改善 1% 对应的储值当量 = n × 1% × 每人价值。"""
    return n * 0.01 * value


def fmt(e):
    return (f"n={e['n']:,}｜S {e['S']:,.0f}（{e['S%']:.2f}%）｜R {e['R']:,.0f}（{e['R%']:.2f}%）｜有储值 {e['有储值率']:.2f}%"
            f"｜前10 占 S {e['前10占S']:.2f}% / R {e['前10占R']:.2f}%｜去前10 S {e['去前10 S%']:.2f}% R {e['去前10 R%']:.2f}%")


if __name__ == '__main__':
    g, U = load()
    TS = U['S'].sum()
    TR = U['R'].sum()
    print(f'合并 {len(U):,}；S 总额 {TS:,.0f}；R 总额 {TR:,.0f}；R 缺（注册缺值）{int(U["R"].isna().sum())}')
    vip = U['身份'].isin(['VIP', '黑名單'])
    print(f'VIP+黑名单 占 S {U.loc[vip, "S"].sum() / TS * 100:.2f}%，占 R {U.loc[vip, "R"].sum() / TR * 100:.2f}%')

    print('\n===== S2 偏向检查：有储值者按注册时长五档')
    p = U[U['dep'] > 0].copy()
    p['tb'] = pd.cut(p['tenure'], [-1, 30, 90, 365, 1095, 1e6], labels=['0–30', '31–90', '91–365', '366–1,095', '1,096+']).astype(str)
    for tb in ['0–30', '31–90', '91–365', '366–1,095', '1,096+']:
        x = p[p.tb == tb]
        print(f'  {tb}: n={len(x):,}｜R 均值 {x.R.mean():,.0f}，中位 {x.R.median():,.0f}｜S 均值 {x.S.mean():,.0f}，中位 {x.S.median():,.0f}')
    nw = U['reg'] >= '2026-08-18'
    print(f'  新增队列（注册 8/18 起）{int(nw.sum()):,} 人：占 S {U.loc[nw, "S"].sum() / TS * 100:.2f}%，占 R {U.loc[nw, "R"].sum() / TR * 100:.2f}%')

    print('\n===== S3 存量型暴露')
    D1, D3, UQ, U2 = g['D1'], g['D3'], g['UQ'], g['U2']
    U1ids = set(g['U1a']['会员编号']) | set(g['U1b']['会员编号']) | set(g['U1c']['会员编号'])
    hi = U2[U2.seg == '高']
    groups = {'D1': set(D1['会员编号']), 'D3': set(D3['会员编号']), 'D8 独有': set(UQ['会员编号']),
              '　U1（8 月新人）': U1ids, '　U2（老账号）': set(U2['会员编号']), '　U2 高段': set(hi['会员编号']),
              '　U2 高段·普卡': set(hi.loc[hi['卡别'] == 1, '会员编号'])}
    EXP = {}
    for k, ids in groups.items():
        e = expose(U, ids, TS, TR)
        EXP[k] = e
        print(f'  {k}: ' + fmt(e))
        x = U[U['会员编号'].isin(ids)]
        cells = []
        for t in ['0–7', '8–14', '15–31', '离开']:
            y = x[x['tier'] == t]
            cells.append(f'{t}: n {len(y):,} S {y.S.sum() / TS * 100:.2f}% R {y.R.sum() / TR * 100:.2f}%')
        print('     四格｜' + '｜'.join(cells))
        xs = x[x['tier'] == '离开']
        print(f'     离开格占暴露：S {xs.S.sum() / x.S.sum() * 100 if x.S.sum() else 0:.2f}%，R {xs.R.sum() / x.R.sum() * 100 if x.R.sum() else 0:.2f}%')
        xv = x[~x['身份'].isin(['VIP', '黑名單'])]
        print(f'     剔除 VIP、黑名单：n {len(xv):,}，S {xv.S.sum() / TS * 100:.2f}%，R {xv.R.sum() / TR * 100:.2f}%')
    print(f'  D1 ∩ D3 = {len(groups["D1"] & groups["D3"])}')

    print('\n===== S3 D3 超出基线（A18 进判读的格，只加正的格）')
    g65 = _run('an_q65_return.py')
    Rt, cells = g65['R'].copy(), g65['df']
    Rt['S'] = unit_S(Rt)
    Rt['R'] = unit_R(Rt)
    exS = exR = exN = 0.0
    for _, c in cells.iterrows():
        if c['进判读'] != '是' or c['超出人数'] == '—' or float(c['超出人数']) <= 0:
            continue
        y = Rt[(Rt.cg == c['卡组']) & (Rt.tb == c['注册']) & (Rt.pay == c['付费']) & Rt.r8]
        n = float(c['超出人数'])
        exN += n
        exS += n * y.S.mean()
        exR += n * y.R.mean()
        print(f'  {c["卡组"]} {c["注册"]} {c["付费"]}：超出 {n:.1f} 人 × 人均 S {y.S.mean():,.0f} / R {y.R.mean():,.1f}')
    print(f'  合计超出 {exN:,.1f} 人；S {exS:,.0f}（{exS / TS * 100:.3f}%）；R {exR:,.0f}（{exR / TR * 100:.3f}%）')

    print('\n===== S4 潜力型 1% 弹性')
    a = g['a']
    NC = a[(a['reg'] >= '2026-08-18') & (a['reg'] <= '2026-09-08')].copy()
    NC['cal'] = NC['last'] == NC['reg']
    only, back = NC[NC.cal], NC[~NC.cal]
    print(f'  D2 队列 {len(NC):,}；只来当天 {len(only):,}；来过不止当天 {len(back):,}')
    for nm, x in [('来过不止当天（参照）', back), ('只来当天', only)]:
        pp = x[x.dep > 0]
        print(f'  {nm}: 人均储值 {x.dep.mean():,.1f}｜付费率 {(x.dep > 0).mean() * 100:.2f}%｜付费者人均 {pp.dep.mean():,.1f}，中位 {pp.dep.median():,.0f}')
    v_mean = back.dep.mean() - only.dep.mean()
    pr_b, pr_o = (back.dep > 0).mean(), (only.dep > 0).mean()
    v_med = pr_b * back[back.dep > 0].dep.median() - pr_o * only[only.dep > 0].dep.median()
    e2m, e2d = elastic(len(only), v_mean), elastic(len(only), v_med)
    print(f'  D2 每人价值 均值差 {v_mean:,.1f}；中位拆解（付费率 × 付费者中位）差 {v_med:,.1f}')
    print(f'  D2 1% 弹性：均值 {e2m:,.0f}（S {e2m / TS * 100:.4f}%，R {e2m / TR * 100:.4f}%）；中位 {e2d:,.0f}（S {e2d / TS * 100:.4f}%，R {e2d / TR * 100:.4f}%）')

    a['r07'] = a['days'] <= 7
    d4b = a[(a['dep'] <= 0) & a['nov'] & a['r07']]
    old = d4b['tenure'] > 365
    g1 = d4b[old & (d4b['身份'] == '持續')]
    g2 = d4b[old & (d4b['身份'] == '回流')]
    g3 = d4b[d4b['tenure'] < 30]
    print(f'  D4b {len(d4b):,}；持續老账号 {len(g1):,}；回流老账号 {len(g2):,}；注册 < 30 天 {len(g3):,}')
    newp = a[(a['身份'] == '新增') & (a['dep'] > 0)]
    vm, vd = newp.dep.mean(), newp.dep.median()
    print(f'  参照：新增付费者 {len(newp):,} 人，储值均值 {vm:,.1f}，中位 {vd:,.0f}（注册 ≤ 30 天，累计即 30 天内）')
    E4 = {}
    for nm, n in [('D4b 全部', len(d4b)), ('持續老账号', len(g1)), ('回流老账号', len(g2)), ('注册 < 30 天', len(g3))]:
        em, ed = elastic(n, vm), elastic(n, vd)
        E4[nm] = (em, ed)
        print(f'  {nm}：1% = {n * 0.01:,.1f} 人首付｜均值 {em:,.0f}（S {em / TS * 100:.4f}%，R {em / TR * 100:.4f}%）｜中位 {ed:,.0f}（S {ed / TS * 100:.4f}%，R {ed / TR * 100:.4f}%）')

    print('\n===== S5 D4a 高卡错位上界、E2 继承格')
    gold_paid = a[(a['卡别'] >= 3) & a['nov'] & (a['dep'] > 0) & (pd.to_numeric(a['充值赠点'], errors='coerce').fillna(0) >= 15000)]
    e = expose(U, set(gold_paid['会员编号']), TS, TR)
    print('  D4a 高卡上界（金卡以上有储值且赠点 ≥ 15,000）：' + fmt(e))
    x = U[U['会员编号'].isin(groups['D8 独有'])]
    y = x[x['tier'].isin(['8–14', '15–31', '离开'])]
    print(f'  E2 定向 / 数据 → D8 独有待再来 + 离开：S {y.S.sum() / TS * 100:.2f}%，R {y.R.sum() / TR * 100:.2f}%')

    print('\n===== S6 两两比较与持平倍数（1% 弹性；存量型 = 暴露 × 1%）')
    stock = {k: (EXP[k]['S'] * 0.01, EXP[k]['R'] * 0.01) for k in ['D1', 'D3', 'D8 独有']}
    stock_nt = {k: (EXP[k]['去前10 S%'] * TS / 100 * 0.01, EXP[k]['去前10 R%'] * TR / 100 * 0.01) for k in stock}
    pot = {'D2': (e2m, e2d), 'D4b': E4['D4b 全部']}
    keys = ['D1', 'D3', 'D8 独有']
    for i, A in enumerate(keys):
        for B_ in keys[i + 1:]:
            rs, rr = stock[A][0] / stock[B_][0], stock[A][1] / stock[B_][1]
            rs10, rr10 = stock_nt[A][0] / stock_nt[B_][0], stock_nt[A][1] / stock_nt[B_][1]
            print(f'  {A} vs {B_}：S 比 {rs:.2f}，R 比 {rr:.2f}｜去前10：S {rs10:.2f}，R {rr10:.2f}')
    for A in keys:
        for P, (pm, pd_) in pot.items():
            print(f'  {A} vs {P}：S 下 {A} 每1% {stock[A][0]:,.0f} / {P} 均值 {pm:,.0f} 中位 {pd_:,.0f} → 倍数 均 {stock[A][0] / pm:.2f} 中 {stock[A][0] / pd_ if pd_ else np.inf:.2f}'
                  f'｜R 下 {A} 每1% {stock[A][1]:,.0f} → 倍数 均 {stock[A][1] / pm:.2f} 中 {stock[A][1] / pd_ if pd_ else np.inf:.2f}')
    print(f'  D4b vs D2：均值 {E4["D4b 全部"][0] / e2m:.2f}，中位 {E4["D4b 全部"][1] / e2d if e2d else np.inf:.2f}')
