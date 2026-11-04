"""《被坑多了，人会变狠吗？》用的统计。只统计，不改参数、不出新结果。

做法：
  1. 用 experiments.py 里同一套参数（场景“误会5%”，种子 1–20）原样再跑一遍，打开 record_individuals
     记下每个人每一代的打法和分数。记录不消耗随机数，所以结果和 results/main_误会5%.json 完全一样；
     脚本会逐代核对 20 个种子的各打法占比，有一处对不上就报错退出。
  2. 只看开局是老实人（ALLC）的 500 人：
     - “变狠过”= 300 代里任何一代当过记仇（GRIM）或骗子（ALLD）；
     - “回到肯原谅的那一边”= 第 300 代是会原谅的以牙还牙（GTFT）；
     - 另记：第一次改学成什么、狠了多少代、最后是什么。
  3. 分数（每轮平均分，0–5）按“这一代用什么打法”分组，看同一时期谁过得好。

用法：/Users/decheng.huang/Documents/dy/.venv/bin/python stats_变狠.py
输出：打印摘要；另存 results/变狠统计.json（新文件，不覆盖任何已有文件）。
"""
import json
import os
from collections import Counter
from multiprocessing import Pool

import numpy as np

from sim import run
from experiments import make_cfg, SCENARIOS

HERE = os.path.dirname(os.path.abspath(__file__))
SCN = '误会5%'
SEEDS = list(range(1, 21))
OUT = os.path.join(HERE, 'results', '变狠统计.json')


def one(seed):
    cfg = make_cfg(SCENARIOS[SCN], seed)
    cfg.record_individuals = True
    h = run(cfg)
    keys = h['strategies']
    S = np.stack(h['strat']).astype(int)      # 代 × 人
    P = np.stack(h['score']).astype(float)    # 代 × 人
    sh = h['counts'] / h['counts'].sum(1, keepdims=True)
    return seed, keys, S, P, sh, np.array(h['coop'])


def path_of(col):
    p = [int(col[0])]
    for v in col[1:]:
        if v != p[-1]:
            p.append(int(v))
    return p


def analyse(seed, keys, S, P, coop):
    iC, iD, iT, iG, iR, iW = (keys.index(k) for k in ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM', 'WSLS'])
    G = S.shape[0] - 1
    starters = np.nonzero(S[0] == iC)[0]
    n = len(starters)
    sub = S[:, starters]
    harsh = (sub == iR) | (sub == iD)
    ever_harsh = harsh.any(0)
    ever_grim = (sub == iR).any(0)
    ever_alld = (sub == iD).any(0)
    end = sub[G]
    end_g = end == iG
    end_t = end == iT
    end_harsh = (end == iR) | (end == iD)
    harsh_gens = harsh.sum(0)

    # 第一次改学成什么
    first = []
    for k in range(n):
        col = sub[:, k]
        ch = np.nonzero(col != iC)[0]
        first.append(keys[col[ch[0]]] if len(ch) else 'ALLC')
    first_cnt = Counter(first)

    # 没变狠过的人走了哪些路
    never = [tuple(keys[j] for j in path_of(sub[:, k])) for k in np.nonzero(~ever_harsh)[0]]

    r = dict(
        seed=seed, n_starters=int(n),
        ever_harsh=int(ever_harsh.sum()), ever_harsh_share=round(float(ever_harsh.mean()), 4),
        ever_grim=int(ever_grim.sum()), ever_alld=int(ever_alld.sum()), ever_both=int((ever_grim & ever_alld).sum()),
        end_gtft=int(end_g.sum()), end_tft=int(end_t.sum()), end_harsh=int(end_harsh.sum()),
        harsh_then_gtft=int((ever_harsh & end_g).sum()),
        harsh_then_gtft_share=round(float((ever_harsh & end_g).sum() / max(1, ever_harsh.sum())), 4),
        harsh_then_tft=int((ever_harsh & end_t).sum()),
        harsh_gens_median=float(np.median(harsh_gens[ever_harsh])) if ever_harsh.any() else None,
        harsh_gens_p10_p90=[float(np.percentile(harsh_gens[ever_harsh], q)) for q in (10, 90)] if ever_harsh.any() else None,
        first_switch={k: int(v) for k, v in first_cnt.most_common()},
        never_harsh_paths={' → '.join(p): c for p, c in Counter(never).most_common()},
    )
    return r


def detail_seed5(keys, S, P, coop):
    """种子 5（画面用的那一次）：分数按打法分组；被坑多的老实人是不是先变。"""
    iC, iD, iT, iG, iR = (keys.index(k) for k in ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM'])
    G = S.shape[0] - 1
    out = {}

    # 1. 同一时期各打法的平均分（每轮）
    def mean_by(strat_idx, g0, g1):
        vals = [P[g][S[g] == strat_idx] for g in range(g0, g1 + 1)]
        vals = np.concatenate(vals) if vals else np.array([])
        return round(float(vals.mean()), 3) if vals.size else None

    windows = [(0, 10), (0, 31), (32, 61), (62, 100), (101, 129), (130, 166), (167, 300), (281, 300)]
    out['mean_score_by_strategy'] = {
        f'{a}-{b}': {k: mean_by(keys.index(k), a, b) for k in ['ALLC', 'ALLD', 'GRIM', 'TFT', 'GTFT']}
        for a, b in windows}
    out['coop_by_window'] = {f'{a}-{b}': round(float(coop[a:b + 1].mean()), 3) for a, b in windows}

    # 2. 开局老实人：狠的那几代 vs 后来会原谅的那几代，平均每轮分
    starters = np.nonzero(S[0] == iC)[0]
    sub, subP = S[:, starters], P[:, starters]
    harsh = (sub == iR) | (sub == iD)
    ever = harsh.any(0)
    def avg(mask):
        return round(float(subP[mask].mean()), 3) if mask.any() else None
    gens = np.arange(G + 1)[:, None] * np.ones((1, len(starters)), int)
    out['starters_score'] = dict(
        as_allc=avg(sub == iC),
        as_harsh_all=avg(harsh),
        as_harsh_gen_lt_32=avg(harsh & (gens < 32)),     # 还有老实人可吃的时候
        as_harsh_gen_ge_32=avg(harsh & (gens >= 32)),    # 老实人没了以后
        as_harsh_gen_40_100=avg(harsh & (gens >= 40) & (gens <= 100)),
        as_tft=avg(sub == iT),
        as_gtft=avg(sub == iG),
        as_gtft_gen_ge_167=avg((sub == iG) & (gens >= 167)),
    )
    # 狠得越久，一生平均分越低吗（只算变狠过的人）
    hg = harsh.sum(0)[ever]
    life = subP.mean(0)[ever]
    out['harsh_gens_vs_lifetime_score'] = dict(
        corr=round(float(np.corrcoef(hg, life)[0, 1]), 3),
        quartiles=[dict(harsh_gens=f'{int(np.percentile(hg, q0))}-{int(np.percentile(hg, q1))}',
                        lifetime_mean=round(float(life[(hg >= np.percentile(hg, q0)) & (hg <= np.percentile(hg, q1))].mean()), 3))
                   for q0, q1 in [(0, 25), (25, 50), (50, 75), (75, 100)]])

    # 3. 被坑多的老实人，是不是先变？（老实人的分越低 = 被背叛越多）
    #    第 0–31 代，每一代把当时的老实人按分数分成低一半、高一半，看下一代改学的比例和改成了什么
    lo_sw = hi_sw = lo_n = hi_n = 0
    lo_to = Counter()
    hi_to = Counter()
    for g in range(0, 32):
        idx = np.nonzero(S[g] == iC)[0]
        if len(idx) < 10:
            continue
        sc = P[g, idx]
        med = np.median(sc)
        nxt = S[g + 1, idx]
        sw = nxt != iC
        lo = sc < med
        hi = sc >= med
        lo_n += lo.sum(); hi_n += hi.sum()
        lo_sw += (sw & lo).sum(); hi_sw += (sw & hi).sum()
        lo_to.update(keys[v] for v in nxt[sw & lo])
        hi_to.update(keys[v] for v in nxt[sw & hi])
    out['allc_switch_by_score_gen0_31'] = dict(
        low_half_switch_rate=round(lo_sw / lo_n, 4), high_half_switch_rate=round(hi_sw / hi_n, 4),
        low_half_to={k: int(v) for k, v in lo_to.most_common()},
        high_half_to={k: int(v) for k, v in hi_to.most_common()})
    return out


def main():
    stored = json.load(open(os.path.join(HERE, 'results', f'main_{SCN}.json')))
    stored_sh = {r['seed']: np.array(r['shares']) for r in stored['runs']}
    with Pool(8) as pool:
        res = pool.map(one, SEEDS, chunksize=1)
    per_seed, d5 = [], None
    for seed, keys, S, P, sh, coop in res:
        ref = stored_sh[seed]
        assert ref.shape == sh.shape, (seed, ref.shape, sh.shape)
        assert np.abs(ref - np.round(sh, 3)).max() < 1e-9, f'种子 {seed} 和 results 里的曲线对不上'
        per_seed.append(analyse(seed, keys, S, P, coop))
        if seed == 5:
            d5 = detail_seed5(keys, S, P, coop)
    per_seed.sort(key=lambda r: r['seed'])

    def rng(key):
        v = [r[key] for r in per_seed]
        return dict(min=min(v), median=float(np.median(v)), max=max(v))

    summary = dict(
        scenario=SCN, seeds=SEEDS, check='20 个种子的各打法占比逐代和 results/main_误会5%.json 一致',
        definitions=dict(
            starters='开局是老实人的 500 人',
            ever_harsh='300 代里任何一代当过记仇或骗子',
            back_to_forgiving='第 300 代是会原谅的以牙还牙',
        ),
        across_20=dict(
            ever_harsh_share=rng('ever_harsh_share'),
            harsh_then_gtft_share=rng('harsh_then_gtft_share'),
            end_harsh=rng('end_harsh'),
            harsh_gens_median=rng('harsh_gens_median'),
        ),
        seed5=next(r for r in per_seed if r['seed'] == 5),
        seed5_detail=d5,
        per_seed=per_seed,
    )
    with open(OUT, 'w') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ['across_20', 'seed5', 'seed5_detail']}, ensure_ascii=False, indent=1))
    print('每个种子：变狠过 / 其中回到会原谅 / 最后还狠')
    for r in per_seed:
        print(r['seed'], r['ever_harsh'], r['ever_harsh_share'], r['harsh_then_gtft'], r['harsh_then_gtft_share'], r['end_harsh'], r['end_tft'])


if __name__ == '__main__':
    main()
