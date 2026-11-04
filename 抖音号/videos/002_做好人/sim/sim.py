"""重复囚徒困境的群体演化仿真（《做好人，会不会吃亏？》用）。

模型一句话：N 个人，每一代每人随机碰到 K 个人，每对连打 n 轮囚徒困境；
一代打完，每个人随便看一个别人，别人分比自己高，就按分差大小以一定概率改学他的打法。

收益（每轮）：都合作各得 R=3；都背叛各得 P=1；一方背叛一方合作，背叛的得 T=5，合作的得 S=0。
误会（e）：每一轮，每个人的动作都有 e 的概率出错（想合作变成背叛，或反过来），对方看到的是出错后的动作。
另有可选的“看错”（e_perc）：动作没错，但对方以 e_perc 的概率看反。

只用 numpy。所有随机数都来自一个种子，结果可以复现。
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

import numpy as np

T, R, P, S = 5.0, 3.0, 1.0, 0.0
# PAYF[2*我合作 + 对方合作]：0=我背叛对方背叛 P，1=我背叛对方合作 T，2=我合作对方背叛 S，3=都合作 R
PAYF = np.array([P, T, S, R])

# 策略表。p0 = 第一轮合作的概率；p = 上一轮状态下合作的概率，
# 状态编号 = 2*我上一轮合作 + 对方上一轮合作（0=DD 1=DC 2=CD 3=CC，前一个字母是我）。
# 记仇（GRIM）不是“只看上一轮”的策略，单独处理：只要见过对方背叛一次，就永远背叛。
STRATS = {
    'ALLC': dict(name='老实人', desc='永远合作', p0=1.0, p=[1, 1, 1, 1]),
    'ALLD': dict(name='骗子', desc='永远背叛', p0=0.0, p=[0, 0, 0, 0]),
    'TFT':  dict(name='以牙还牙', desc='先合作，之后照搬对方上一步', p0=1.0, p=[0, 1, 0, 1]),
    'GTFT': dict(name='宽容的以牙还牙', desc='先合作；对方合作就合作，对方背叛仍有 g 的概率合作', p0=1.0, p=None),
    'GRIM': dict(name='记仇', desc='先合作；对方背叛一次就永远背叛', p0=1.0, p=[0, 0, 0, 0]),
    'WSLS': dict(name='赢了不变输了就换', desc='Pavlov：上一轮得 3 或 5 就照旧，得 0 或 1 就换', p0=1.0, p=[1, 0, 0, 1]),
}
# 同时放两种宽容度时用的别名
STRATS['GTFT33'] = dict(STRATS['GTFT'], name='宽容 1/3', g=1 / 3)
STRATS['GTFT10'] = dict(STRATS['GTFT'], name='宽容 10%', g=0.10)

# 画图和给 Remotion 的建议色（浅底, 深底）。按 dataviz 默认分类色板的固定顺序分配，
# 画图顺序 = PLOT_ORDER；已用 validate_palette.js 校验相邻对（浅/深两套都通过）。
PLOT_ORDER = ['TFT', 'ALLD', 'GTFT', 'ALLC', 'GRIM', 'WSLS', 'GTFT33', 'GTFT10']
COLORS = {
    'TFT': ('#2a78d6', '#3987e5'), 'ALLD': ('#eb6834', '#d95926'),
    'GTFT': ('#1baf7a', '#199e70'), 'GTFT33': ('#1baf7a', '#199e70'),
    'ALLC': ('#eda100', '#c98500'), 'GRIM': ('#e87ba4', '#d55181'),
    'WSLS': ('#008300', '#008300'), 'GTFT10': ('#6250d6', '#9085e9'),
}


@dataclass
class Config:
    N: int = 1000                 # 人数（偶数）
    K: int = 10                   # 每人每代碰到几个人（matching='random'）
    n: int = 200                  # 每对连打几轮
    gens: int = 150               # 代数
    e: float = 0.0                # 动作出错率（误会）
    e_perc: float = 0.0           # 看错率（可选）
    noise_from: int = 0           # 从第几代开始有误会（0 = 一开始就有）
    strategies: List[str] = field(default_factory=lambda: ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM'])
    init: Dict[str, float] = field(default_factory=dict)   # 初始比例，空 = 平均分
    g: float = 1 / 3              # GTFT 被背叛后仍合作的概率
    matching: str = 'random'      # 'random' 每代随机配 K 次；'all' 全体循环
    rule: str = 'imitate'         # 'imitate' 按分差概率模仿；'fermi'；'best3' 看 3 人学最高；'wf' 按分繁殖
    beta: float = 2.0             # fermi 规则的选择强度
    mu: float = 0.0               # 每人每代随机换成任一策略的概率（突变）
    seed: int = 0
    you: Optional[int] = None     # 记录这个人的逐局遭遇
    record_individuals: bool = False


def _ptab(cfg):
    rows, p0, grim = [], [], []
    for k in cfg.strategies:
        s = STRATS[k]
        if k.startswith('GTFT'):
            g = s.get('g', cfg.g)
            rows.append([g, 1, g, 1])
        else:
            rows.append(s['p'])
        p0.append(s['p0'])
        grim.append(k == 'GRIM')
    return np.array(rows, float).ravel(), np.array(p0, float), np.array(grim, bool)


def play(sa, sb, n, e, e_perc, ptab, p0, is_grim, rng):
    """sa, sb：每对两边的策略编号。返回每对两边的总得分、各自收到的背叛次数、各自出错次数。"""
    M = len(sa)
    pay_a = np.zeros(M)
    pay_b = np.zeros(M)
    dA = np.zeros(M, np.int32)   # a 收到的背叛（真实动作）
    dB = np.zeros(M, np.int32)
    errA = np.zeros(M, np.int32)
    errB = np.zeros(M, np.int32)
    coop_total = 0
    ga, gb = is_grim[sa], is_grim[sb]
    base_a, base_b = sa * 4, sb * 4
    grudge_a = np.zeros(M, bool)
    grudge_b = np.zeros(M, bool)
    own_a = own_b = see_a = see_b = None
    for t in range(n):
        if t == 0:
            pa, pb = p0[sa], p0[sb]
        else:
            pa = ptab[base_a + 2 * own_a + see_a]
            pb = ptab[base_b + 2 * own_b + see_b]
            pa = np.where(ga, ~grudge_a, pa)
            pb = np.where(gb, ~grudge_b, pb)
        ia = rng.random(M) < pa      # 本来想不想合作
        ib = rng.random(M) < pb
        if e > 0:
            fa = rng.random(M) < e
            fb = rng.random(M) < e
            ca, cb = ia ^ fa, ib ^ fb
            errA += fa
            errB += fb
        else:
            ca, cb = ia, ib
        ca8, cb8 = ca.astype(np.int8), cb.astype(np.int8)
        pay_a += PAYF[2 * ca8 + cb8]
        pay_b += PAYF[2 * cb8 + ca8]
        dA += ~cb
        dB += ~ca
        coop_total += int(ca8.sum()) + int(cb8.sum())
        if e_perc > 0:
            sa_sees = cb ^ (rng.random(M) < e_perc)
            sb_sees = ca ^ (rng.random(M) < e_perc)
        else:
            sa_sees, sb_sees = cb, ca
        grudge_a |= ~sa_sees
        grudge_b |= ~sb_sees
        own_a, own_b = ca8, cb8
        see_a, see_b = sa_sees.astype(np.int8), sb_sees.astype(np.int8)
    return pay_a, pay_b, dA, dB, errA, errB, coop_total / (2 * M * n)


def init_population(cfg, rng):
    keys = cfg.strategies
    fr = np.array([cfg.init.get(k, 0.0) for k in keys]) if cfg.init else np.ones(len(keys))
    fr = fr / fr.sum()
    cnt = np.floor(fr * cfg.N).astype(int)
    rem = cfg.N - cnt.sum()
    order = np.argsort(-(fr * cfg.N - cnt))
    cnt[order[:rem]] += 1
    strat = np.repeat(np.arange(len(keys)), cnt)
    rng.shuffle(strat)
    return strat


def pairs_for(cfg, rng):
    N = cfg.N
    if cfg.matching == 'all':
        A, B = np.triu_indices(N, 1)
        return A, B
    A, B = [], []
    for _ in range(cfg.K):
        perm = rng.permutation(N)
        A.append(perm[0::2])
        B.append(perm[1::2])
    return np.concatenate(A), np.concatenate(B)


def update(strat, score, cfg, rng, nS):
    """返回新策略、每人看的是谁（-1 表示没有看人）、是否改了。"""
    N = len(strat)
    look = (np.arange(N) + rng.integers(1, N, N)) % N   # 随便看一个别人
    if cfg.rule == 'imitate':
        diff = score[look] - score
        p = np.clip(diff / (T - S), 0, 1)
        sw = rng.random(N) < p
        new = np.where(sw, strat[look], strat)
    elif cfg.rule == 'fermi':
        diff = score[look] - score
        p = 1 / (1 + np.exp(-cfg.beta * diff))
        sw = rng.random(N) < p
        new = np.where(sw, strat[look], strat)
    elif cfg.rule == 'best3':
        cand = np.stack([(np.arange(N) + rng.integers(1, N, N)) % N for _ in range(3)], 1)
        best = cand[np.arange(N), np.argmax(score[cand], 1)]
        look = best
        sw = score[best] > score
        new = np.where(sw, strat[best], strat)
    elif cfg.rule == 'wf':
        w = score / score.sum()
        parent = rng.choice(N, N, p=w)
        look = parent
        new = strat[parent]
        sw = np.ones(N, bool)
    else:
        raise ValueError(cfg.rule)
    if cfg.mu > 0:
        m = rng.random(N) < cfg.mu
        new = new.copy()
        new[m] = rng.integers(0, nS, int(m.sum()))
    return new, look, new != strat


def run(cfg: Config):
    rng = np.random.default_rng(cfg.seed)
    keys = cfg.strategies
    nS = len(keys)
    ptab, p0, is_grim = _ptab(cfg)
    strat = init_population(cfg, rng)
    N = cfg.N
    hist = dict(config=asdict(cfg), strategies=keys, counts=[], mean_score=[], coop=[])
    if cfg.record_individuals:
        hist['strat'], hist['score'] = [], []
    if cfg.you is not None:
        hist['you'] = []
    for gen in range(cfg.gens + 1):
        e = cfg.e if gen >= cfg.noise_from else 0.0
        ep = cfg.e_perc if gen >= cfg.noise_from else 0.0
        A, B = pairs_for(cfg, rng)
        pa, pb, dA, dB, errA, errB, coop = play(strat[A], strat[B], cfg.n, e, ep, ptab, p0, is_grim, rng)
        tot = np.bincount(A, pa, N) + np.bincount(B, pb, N)
        games = np.bincount(A, minlength=N) + np.bincount(B, minlength=N)
        score = tot / (games * cfg.n)
        cnt = np.bincount(strat, minlength=nS)
        ms = [float(score[strat == i].mean()) if cnt[i] else None for i in range(nS)]
        hist['counts'].append(cnt.tolist())
        hist['mean_score'].append(ms)
        hist['coop'].append(coop)
        if cfg.record_individuals:
            hist['strat'].append(strat.astype(np.int8).copy())
            hist['score'].append(score.astype(np.float32).copy())
        if gen == cfg.gens:
            if cfg.you is not None:
                hist['you'].append(_you_record(cfg, gen, strat, score, A, B, pa, pb, dA, dB, errA, errB, None, None, None, e))
            break
        new, look, changed = update(strat, score, cfg, rng, nS)
        if cfg.you is not None:
            hist['you'].append(_you_record(cfg, gen, strat, score, A, B, pa, pb, dA, dB, errA, errB, new, look, changed, e))
        strat = new
    hist['counts'] = np.array(hist['counts'])
    return hist


def _you_record(cfg, gen, strat, score, A, B, pa, pb, dA, dB, errA, errB, new, look, changed, e):
    y = cfg.you
    keys = cfg.strategies
    games = []
    for side, (X, Y, px, dX, eX, eY) in enumerate([(A, B, pa, dA, errA, errB), (B, A, pb, dB, errB, errA)]):
        for k in np.nonzero(X == y)[0]:
            games.append(dict(partner=int(Y[k]), partner_strategy=keys[strat[Y[k]]],
                              your_avg=round(float(px[k]) / cfg.n, 3),
                              betrayed=int(dX[k]), your_mistakes=int(eX[k]), partner_mistakes=int(eY[k])))
    rank = float((score < score[y]).mean())
    rec = dict(gen=gen, strategy=keys[strat[y]], score=round(float(score[y]), 3),
               percentile=round(rank, 3), noise=e,
               pop_mean=round(float(score.mean()), 3), games=games)
    if new is not None:
        j = int(look[y])
        rec['looked_at'] = dict(id=j, strategy=keys[strat[j]], score=round(float(score[j]), 3))
        rec['switched_to'] = keys[new[y]] if changed[y] else None
    return rec


def payoff_matrix(keys, n=200, e=0.0, g=1 / 3, games=4000, seed=1):
    """每种策略对每种策略，平均每轮得分（行 = 自己）。"""
    cfg = Config(strategies=keys, g=g)
    ptab, p0, is_grim = _ptab(cfg)
    rng = np.random.default_rng(seed)
    k = len(keys)
    M = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            sa = np.full(games, i)
            sb = np.full(games, j)
            pa, pb, *_ = play(sa, sb, n, e, 0.0, ptab, p0, is_grim, rng)
            M[i, j] = pa.mean() / n
    return M


def shares(hist):
    c = hist['counts']
    return c / c.sum(1, keepdims=True)
