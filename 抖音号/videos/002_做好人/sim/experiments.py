"""批量实验：两个主场景 × 多种子，转折场景，参数敏感性，收益表。

用法：/Users/decheng.huang/Documents/dy/.venv/bin/python experiments.py
输出：results/*.json，results/敏感性.md
"""
import json
import os
import time
from multiprocessing import Pool

import numpy as np

from sim import Config, run, shares, payoff_matrix, STRATS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results')

S6 = ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM', 'WSLS']
S5 = ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM']
MOSTLY_HONEST = dict(ALLC=.5, ALLD=.1, TFT=.1, GTFT=.1, GRIM=.1, WSLS=.1, GTFT33=.1, GTFT10=.1)
BASE = dict(N=1000, K=10, n=200, gens=300, strategies=S6, init=MOSTLY_HONEST, g=1 / 3,
            rule='imitate', mu=0.0, matching='random')
MAIN_SEEDS = list(range(1, 21))
SWEEP_SEEDS = list(range(1, 11))


def make_cfg(over, seed):
    d = dict(BASE)
    d.update(over)
    d['init'] = {k: v for k, v in d['init'].items() if k in d['strategies']}
    return Config(seed=seed, **d)


def _col(s, keys, k):
    return s[:, keys.index(k)] if k in keys else None


def metrics(h):
    s = shares(h)
    keys = h['strategies']
    ms = h['mean_score']
    fin = s[-20:].mean(0)
    m = dict(final={k: round(float(fin[i]), 4) for i, k in enumerate(keys)})
    m['winner'] = keys[int(np.argmax(fin))]
    m['winner_share'] = round(float(fin.max()), 4)
    m['coop_final'] = round(float(np.mean(h['coop'][-20:])), 4)
    c, d, t = _col(s, keys, 'ALLC'), _col(s, keys, 'ALLD'), _col(s, keys, 'TFT')
    gt_idx = [i for i, k in enumerate(keys) if k.startswith('GTFT')]
    gt = s[:, gt_idx].sum(1) if gt_idx else None
    gr, w = _col(s, keys, 'GRIM'), _col(s, keys, 'WSLS')

    def first_below(x, thr, start=0):
        idx = np.nonzero(x[start:] < thr)[0]
        return int(idx[0] + start) if len(idx) else None

    if c is not None:
        m.update(allc_init=float(c[0]), allc_min=float(c.min()), allc_min_gen=int(c.argmin()),
                 allc_gone_gen=first_below(c, 0.01), allc_final=float(fin[keys.index('ALLC')]))
    if d is not None:
        pk = int(d.argmax())
        m.update(alld_init=float(d[0]), alld_peak=float(d.max()), alld_peak_gen=pk,
                 alld_gone_gen=first_below(d, 0.01, pk), alld_final=float(fin[keys.index('ALLD')]))
        if 'ALLC' in keys:
            m['allc_at_alld_peak'] = float(c[pk])
    if t is not None:
        pk = m.get('alld_peak_gen', 0)
        after = t[pk:]
        m.update(tft_init=float(t[0]), tft_at_alld_peak=float(t[pk]), tft_peak_after=float(after.max()),
                 tft_peak_gen=int(pk + after.argmax()), tft_final=float(fin[keys.index('TFT')]))
        # 骗子的平均分第一次低于以牙还牙的那一代
        iD, iT = keys.index('ALLD') if 'ALLD' in keys else None, keys.index('TFT')
        cross = None
        if iD is not None:
            for gen in range(1, len(ms)):
                a, b = ms[gen][iD], ms[gen][iT]
                if a is not None and b is not None and a < b:
                    cross = gen
                    break
        m['alld_below_tft_gen'] = cross
    if gt is not None:
        m['gtft_final'] = float(gt[-20:].mean())
        m['gtft_peak'] = float(gt.max())
    if gr is not None:
        m.update(grim_init=float(gr[0]), grim_peak=float(gr.max()), grim_peak_gen=int(gr.argmax()),
                 grim_final=float(fin[keys.index('GRIM')]))
    if w is not None:
        m.update(wsls_peak=float(w.max()), wsls_final=float(fin[keys.index('WSLS')]))

    # 情节各步（自动判定，阈值在说明.md 里写明）
    st = {}
    if c is not None:
        st['1a_老实人减半'] = m['allc_min'] <= 0.5 * m['allc_init']
        st['1b_老实人被骗光'] = m['allc_gone_gen'] is not None
    if d is not None:
        st['2_骗子变多'] = m['alld_init'] > 0 and m['alld_peak'] >= 1.5 * m['alld_init'] and m['alld_peak_gen'] > 0
    if t is not None and d is not None:
        st['3_以牙还牙起来_骗子消失'] = (m['tft_peak_after'] >= max(1.5 * m['tft_at_alld_peak'], 1.5 * m['tft_init'], 0.05)
                                 and m['tft_peak_gen'] > m['alld_peak_gen'] and m['alld_final'] < 0.01)
    if t is not None and gt is not None:
        st['4_宽容赢过以牙还牙'] = m['gtft_final'] > m['tft_final'] and m['winner'].startswith('GTFT')
    if gr is not None:
        st['x_记仇一度过三成'] = m['grim_peak'] >= 0.3
    if w is not None:
        st['x_Pavlov赢'] = m['winner'] == 'WSLS'
    st['x_没有赢家过半'] = m['winner_share'] < 0.5
    m['story'] = st
    return m


def job(args):
    tag, over, seed, keep_series = args
    cfg = make_cfg(over, seed)
    t0 = time.time()
    h = run(cfg)
    m = metrics(h)
    out = dict(tag=tag, seed=seed, metrics=m, secs=round(time.time() - t0, 2))
    if keep_series:
        out['shares'] = np.round(shares(h), 4).tolist()
        out['coop'] = np.round(h['coop'], 4).tolist()
        out['mean_score'] = [[None if v is None else round(v, 3) for v in row] for row in h['mean_score']]
        out['strategies'] = h['strategies']
    return out


SCENARIOS = {
    '无误会': dict(e=0.0),
    '误会5%': dict(e=0.05),
    '转折_第100代起误会5%': dict(e=0.05, noise_from=100),
}

# (分组, 标签, 覆盖参数)；每个变体都跑 e=0 和 e=0.05 两列，除非标了 noise_fixed
VARIANTS = [
    ('每对打几轮', 'n=1（一次性）', dict(n=1)),
    ('每对打几轮', 'n=3', dict(n=3)),
    ('每对打几轮', 'n=10', dict(n=10)),
    ('每对打几轮', 'n=50', dict(n=50)),
    ('初始比例', '六种平均分', dict(init={k: 1.0 for k in MOSTLY_HONEST})),
    ('初始比例', '骗子只有 2%', dict(init=dict(ALLC=.58, ALLD=.02, TFT=.1, GTFT=.1, GRIM=.1, WSLS=.1))),
    ('初始比例', '骗子 30%', dict(init=dict(ALLC=.3, ALLD=.3, TFT=.1, GTFT=.1, GRIM=.1, WSLS=.1))),
    ('初始比例', '老实人 90% 骗子 10%（其余靠突变）', dict(init=dict(ALLC=.9, ALLD=.1), mu=0.002)),
    ('初始比例', '没有以牙还牙（靠突变冒出来）', dict(init=dict(ALLC=.6, ALLD=.1, GTFT=.1, GRIM=.1, WSLS=.1), mu=0.002)),
    ('模仿规则', 'Fermi（β=5，分差越大越可能学）', dict(rule='fermi', beta=5.0)),
    ('模仿规则', '看 3 个人，学分最高的', dict(rule='best3')),
    ('模仿规则', '按分数比例繁殖（Wright-Fisher）', dict(rule='wf')),
    ('配对方式', '每代只碰 3 个人', dict(K=3)),
    ('配对方式', '全体循环（N=200）', dict(matching='all', N=200)),
    ('突变', 'μ=0.001', dict(mu=0.001)),
    ('突变', 'μ=0.01', dict(mu=0.01)),
    ('宽容度', 'g=10%', dict(g=0.10)),
    ('宽容度', 'g=1/3 和 10% 都放', dict(strategies=['ALLC', 'ALLD', 'TFT', 'GTFT33', 'GTFT10', 'GRIM', 'WSLS'])),
    ('策略集', '不放 Pavlov（五种）', dict(strategies=S5)),
    ('人数', 'N=300', dict(N=300)),
]
NOISE_VARIANTS = [
    ('误会率', 'e=1%', dict(e=0.01)),
    ('误会率', 'e=10%', dict(e=0.10)),
    ('误会率', '动作不错、5% 看错', dict(e=0.0, e_perc=0.05)),
    ('误会率', 'e=5%，μ=0.01，跑 1000 代', dict(e=0.05, mu=0.01, gens=1000)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    # 收益表
    keys = ['ALLC', 'ALLD', 'TFT', 'GTFT33', 'GTFT10', 'GRIM', 'WSLS']
    pm = {}
    for e in (0.0, 0.01, 0.05, 0.10):
        M = payoff_matrix(keys, n=200, e=e, games=4000)
        pm[str(e)] = np.round(M, 3).tolist()
    json.dump(dict(keys=keys, n=200, note='行 = 自己，列 = 对手；平均每轮得分', matrices=pm),
              open(os.path.join(OUT, 'payoff_matrix.json'), 'w'), ensure_ascii=False, indent=1)
    print('payoff done', round(time.time() - t0, 1))

    jobs = []
    for name, over in SCENARIOS.items():
        for sd in MAIN_SEEDS:
            jobs.append((('main', name), over, sd, True))
    for grp, label, over in VARIANTS:
        for e in (0.0, 0.05):
            o = dict(over)
            o['e'] = e
            for sd in SWEEP_SEEDS:
                jobs.append((('sweep', grp, label, e), o, sd, False))
    for grp, label, over in NOISE_VARIANTS:
        for sd in SWEEP_SEEDS:
            jobs.append((('sweep', grp, label, over.get('e', 0.0)), over, sd, False))
    print('jobs', len(jobs))
    with Pool(8) as pool:
        res = pool.map(job, jobs, chunksize=1)
    print('runs done', round(time.time() - t0, 1))

    main_out, sweep_out = {}, {}
    for r in res:
        tag = r['tag']
        if tag[0] == 'main':
            main_out.setdefault(tag[1], []).append(r)
        else:
            sweep_out.setdefault('|'.join(map(str, tag[1:])), []).append(r)
    for name, rs in main_out.items():
        rs.sort(key=lambda r: r['seed'])
        json.dump(dict(scenario=name, config=dict(BASE, **SCENARIOS[name]), runs=rs),
                  open(os.path.join(OUT, f'main_{name}.json'), 'w'), ensure_ascii=False)
    json.dump({k: [dict(seed=r['seed'], metrics=r['metrics']) for r in v] for k, v in sweep_out.items()},
              open(os.path.join(OUT, 'sweep_raw.json'), 'w'), ensure_ascii=False)
    print('saved', round(time.time() - t0, 1))


if __name__ == '__main__':
    main()
