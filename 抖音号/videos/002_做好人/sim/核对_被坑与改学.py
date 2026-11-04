"""核对：被坑越多是不是越早改学；学成什么由谁决定；“老实人变狠过”有多少来自开局配比。

只统计，不改模型、不改已有脚本和结果。

做法
  1. 主场景（误会5%，种子 1–20）按 experiments.py 的原参数重跑。循环照抄 sim.run，
     只多记几样不耗随机数的中间量：每人每代被背叛几次（收到的真实背叛动作，含对方手滑）、
     每人每代看的是谁。逐代和 results/main_误会5%.json 的各打法占比比对，
     再和 results/变狠统计.json 的逐种子结果比对；有一处对不上就报错退出。
  2. 对照（只改开局配比，误会 5%，种子 1–10）：
     - 敏感性表里已有的三组（六种平均分、骗子 2%、骗子 30%）原样重跑，
       用 experiments.metrics 和 results/sweep_raw.json 逐项比对；
     - 新加四组（骗子 0%、记仇 0%、骗子 2% 加记仇 2%、骗子和记仇都 0%），减掉的比例都加给老实人，
       和“骗子 2%”的做法一样。这四组是对照实验，不给片子用。

用法：/Users/decheng.huang/Documents/dy/.venv/bin/python 核对_被坑与改学.py
输出：results/核对_被坑与改学.json（新文件）
"""
import json
import os
from multiprocessing import Pool

import numpy as np

from sim import _ptab, play, init_population, pairs_for, update
from experiments import make_cfg, SCENARIOS, metrics

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results', '核对_被坑与改学.json')
SCN = '误会5%'
MAIN_SEEDS = list(range(1, 21))
CTRL_SEEDS = list(range(1, 11))
HARSH = ('ALLD', 'GRIM')

# 对照：只改开局配比（e=0.05 和主场景一样）。sweep_key 不为空的，是敏感性表里已有的，要逐项比对。
CONTROLS = [
    ('基准（老实人 50%，其余各 10%）', None, dict(ALLC=.5, ALLD=.1, TFT=.1, GTFT=.1, GRIM=.1, WSLS=.1)),
    ('六种平均分（老实人约 17%）', '初始比例|六种平均分|0.05', {k: 1.0 for k in ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM', 'WSLS', 'GTFT33', 'GTFT10']}),
    ('骗子 2%（老实人 58%）', '初始比例|骗子只有 2%|0.05', dict(ALLC=.58, ALLD=.02, TFT=.1, GTFT=.1, GRIM=.1, WSLS=.1)),
    ('骗子 30%（老实人 30%）', '初始比例|骗子 30%|0.05', dict(ALLC=.3, ALLD=.3, TFT=.1, GTFT=.1, GRIM=.1, WSLS=.1)),
    ('新·骗子 0%（老实人 60%）', None, dict(ALLC=.6, ALLD=0, TFT=.1, GTFT=.1, GRIM=.1, WSLS=.1)),
    ('新·记仇 0%（老实人 60%）', None, dict(ALLC=.6, ALLD=.1, TFT=.1, GTFT=.1, GRIM=0, WSLS=.1)),
    ('新·骗子 2%、记仇 2%（老实人 66%）', None, dict(ALLC=.66, ALLD=.02, TFT=.1, GTFT=.1, GRIM=.02, WSLS=.1)),
    ('新·骗子 0%、记仇 0%（老实人 70%）', None, dict(ALLC=.7, ALLD=0, TFT=.1, GTFT=.1, GRIM=0, WSLS=.1)),
]


# ---------------------------------------------------------------- 重跑（照抄 sim.run 的循环）
def run_traced(cfg):
    rng = np.random.default_rng(cfg.seed)
    keys = cfg.strategies
    nS = len(keys)
    ptab, p0, is_grim = _ptab(cfg)
    strat = init_population(cfg, rng)
    N = cfg.N
    S, P, B, L, counts, ms_all, coops = [], [], [], [], [], [], []
    for gen in range(cfg.gens + 1):
        e = cfg.e if gen >= cfg.noise_from else 0.0
        ep = cfg.e_perc if gen >= cfg.noise_from else 0.0
        A, Bp = pairs_for(cfg, rng)
        pa, pb, dA, dB, errA, errB, coop = play(strat[A], strat[Bp], cfg.n, e, ep, ptab, p0, is_grim, rng)
        tot = np.bincount(A, pa, N) + np.bincount(Bp, pb, N)
        games = np.bincount(A, minlength=N) + np.bincount(Bp, minlength=N)
        score = tot / (games * cfg.n)
        betr = np.bincount(A, dA, N) + np.bincount(Bp, dB, N)      # 这一代收到的背叛（真实动作）
        cnt = np.bincount(strat, minlength=nS)
        ms = [float(score[strat == i].mean()) if cnt[i] else None for i in range(nS)]
        S.append(strat.astype(np.int8).copy())
        P.append(score.copy())
        B.append(betr.astype(np.int32))
        counts.append(cnt.tolist())
        ms_all.append(ms)
        coops.append(coop)
        if gen == cfg.gens:
            break
        new, look, changed = update(strat, score, cfg, rng, nS)
        L.append(look.astype(np.int32))
        strat = new
    return dict(keys=keys, S=np.stack(S).astype(int), P=np.stack(P), B=np.stack(B), L=np.stack(L),
                counts=np.array(counts), mean_score=ms_all, coop=coops, N=N)


def exp_switch_prob(score):
    """只按分数算的改学概率：随便看一个别人 j，按 max(0, s_j − s_i)/5 学。对每个 i 取期望。"""
    N = len(score)
    s = np.sort(score)
    suf = np.append(np.cumsum(s[::-1])[::-1], 0.0)
    idx = np.searchsorted(s, score, side='right')
    cnt = N - idx
    return (suf[idx] - cnt * score) / 5.0 / (N - 1)


def exp_switch_prob_other(score_i, score_pool, N):
    """同上，但只算打法和自己不一样的人（看到同打法的人，学了也不算改）。score_pool = 这些人的分。"""
    s = np.sort(score_pool)
    suf = np.append(np.cumsum(s[::-1])[::-1], 0.0)
    idx = np.searchsorted(s, score_i, side='right')
    cnt = len(s) - idx
    return (suf[idx] - cnt * score_i) / 5.0 / (N - 1)


def quintile(x):
    r = np.argsort(np.argsort(x, kind='stable'), kind='stable')
    return (r * 5) // len(x)


def starters_basic(h):
    """开局老实人：变狠过、第一次改学、最后，口径和 stats_变狠.py 一样。"""
    keys, S = h['keys'], h['S']
    iC = keys.index('ALLC')
    G = S.shape[0] - 1
    hidx = [keys.index(k) for k in HARSH if k in keys]
    st = np.nonzero(S[0] == iC)[0]
    sub = S[:, st]
    n = len(st)
    harsh = np.isin(sub, hidx)
    notC = sub != iC
    has = notC.any(0)
    f = np.where(has, notC.argmax(0), G + 1)
    first_t = np.where(has, sub[np.minimum(f, G), np.arange(n)], -1)
    ever = harsh.any(0)
    end = sub[G]
    r = dict(n_starters=int(n), ever_harsh=int(ever.sum()), ever_harsh_share=round(float(ever.mean()), 4) if n else None)
    for k in HARSH:
        if k in keys:
            r[f'ever_{k}'] = int((sub == keys.index(k)).any(0).sum())
    r['first_switch_harsh'] = int(np.isin(first_t, hidx).sum())
    r['first_switch'] = {keys[i]: int((first_t == i).sum()) for i in range(len(keys)) if (first_t == i).any()}
    r['never_switched'] = int((~has).sum())
    r['end_harsh'] = int(np.isin(end, hidx).sum())
    if 'GTFT' in keys:
        r['harsh_then_gtft'] = int((ever & (end == keys.index('GTFT'))).sum())
    r['end'] = {keys[i]: int((end == i).sum()) for i in range(len(keys)) if (end == i).any()}
    return r, st, f, first_t, harsh


# ---------------------------------------------------------------- 问题 1：被坑多，是不是越早改学
def q1(h):
    keys, S, P, B, L = h['keys'], h['S'], h['P'], h['B'], h['L']
    nS = len(keys)
    iC = keys.index('ALLC')
    hidx = [keys.index(k) for k in HARSH]
    G = S.shape[0] - 1
    basic, st, f, first_t, harsh = starters_basic(h)
    n = len(st)
    out = {}

    # (a) 第 0 代（500 人都是老实人）按被背叛次数分五档
    b0 = B[0, st]
    q = quintile(b0)
    ever = harsh.any(0)
    a = []
    for k in range(5):
        m = q == k
        fk = f[m]
        a.append(dict(n=int(m.sum()), betrayed_sum=int(b0[m].sum()), score_sum=float(P[0, st][m].sum()),
                      switch_gen0=int((fk == 1).sum()), first_gens=fk.tolist(),
                      first_harsh=int(np.isin(first_t[m], hidx).sum()),
                      ever_harsh=int(ever[m].sum())))
    out['gen0_quintile'] = a

    # (c) 以前被坑多少，影响不影响以后改不改：第 g 代还没改过的开局老实人，按“前 5 代（g−5…g−1）被背叛的总数”
    #     代内分五档，看第 g 代末改不改；同时给出只按第 g 代分数算的预测
    past = [dict(n=0, sw=0, pred=0.0, past=0, now=0) for _ in range(5)]
    for g in range(5, G):
        alive = f > g
        if alive.sum() < 25:
            continue
        ids = st[alive]
        pb = B[g - 5:g, ids].sum(0)
        sw = f[alive] == g + 1
        pool = P[g][S[g] != iC]
        pred = exp_switch_prob_other(P[g, ids], pool, h['N'])
        qq = quintile(pb)
        for k in range(5):
            m = qq == k
            d = past[k]
            d['n'] += int(m.sum()); d['sw'] += int(sw[m].sum()); d['pred'] += float(pred[m].sum())
            d['past'] += int(pb[m].sum()); d['now'] += int(B[g, ids][m].sum())
    out['past5_quintile'] = past

    # (b) 逐代“危险率”：还没改过的开局老实人，这一代按被背叛次数分五档（代内分档），看这一代末改不改
    hz = [dict(n=0, sw=0, pred=0.0, pred2=0.0, betr=0, score=0.0, to=[0] * nS) for _ in range(5)]
    hz_score = [dict(n=0, sw=0, pred=0.0, pred2=0.0) for _ in range(5)]
    corr_num = corr_w = 0.0
    gens_used = []
    for g in range(G):
        alive = f > g
        if alive.sum() < 25:
            continue
        gens_used.append(g)
        ids = st[alive]
        b = B[g, ids]
        s = P[g, ids]
        sw = f[alive] == g + 1
        pred = exp_switch_prob(P[g])[ids]
        pred2 = exp_switch_prob_other(s, P[g][S[g] != iC], h['N'])
        tgt = S[g + 1, ids]
        if b.std() > 0 and s.std() > 0:
            corr_num += np.corrcoef(b, s)[0, 1] * len(ids)
            corr_w += len(ids)
        qq = quintile(b)
        for k in range(5):
            m = qq == k
            d = hz[k]
            d['n'] += int(m.sum()); d['sw'] += int(sw[m].sum()); d['pred'] += float(pred[m].sum())
            d['pred2'] += float(pred2[m].sum())
            d['betr'] += int(b[m].sum()); d['score'] += float(s[m].sum())
            for t in tgt[m & sw]:
                d['to'][int(t)] += 1
        qs = quintile(s)
        for k in range(5):
            m = qs == k
            hz_score[k]['n'] += int(m.sum()); hz_score[k]['sw'] += int(sw[m].sum()); hz_score[k]['pred'] += float(pred[m].sum())
            hz_score[k]['pred2'] += float(pred2[m].sum())
    out['hazard_by_betrayal'] = hz
    out['hazard_by_score'] = hz_score
    out['hazard_gens'] = [min(gens_used), max(gens_used)] if gens_used else None
    out['corr_betrayal_score'] = dict(num=corr_num, w=corr_w)

    # (e) 学成什么 vs 看的那个人：开局老实人第一次改学
    sw_first = f <= G
    d_gen = f[sw_first] - 1
    who = L[d_gen, st[sw_first]]
    look_s = S[d_gen, who]
    tgt = first_t[sw_first]
    out['first_switch_same_as_looked'] = dict(n=int(sw_first.sum()), same=int((look_s == tgt).sum()))
    # 全场所有改学：学成的打法是否就是看的那个人的打法
    tot = same = 0
    for g in range(G):
        ch = S[g + 1] != S[g]
        tot += int(ch.sum())
        same += int((S[g + 1][ch] == S[g][L[g][ch]]).sum())
    out['all_switches_same_as_looked'] = dict(n=tot, same=same)

    # (f) 第 0–10 代，还是老实人的开局老实人：看到哪种人、看到后学了的比例
    lk = [dict(n=0, sw=0, look_score=0.0, own_score=0.0) for _ in range(nS)]
    for g in range(0, 11):
        alive = f > g
        ids = st[alive]
        j = L[g, ids]
        ls = S[g, j]
        sw = f[alive] == g + 1
        for x in range(nS):
            m = ls == x
            lk[x]['n'] += int(m.sum()); lk[x]['sw'] += int(sw[m].sum())
            lk[x]['look_score'] += float(P[g, j][m].sum()); lk[x]['own_score'] += float(P[g, ids][m].sum())
    out['look_gen0_10'] = lk

    # (g) 变狠的那一下：开局老实人第一次变狠时，是从老实人直接变的，还是先变别的再变狠；当时全场狠人占多少
    first_h = np.where(harsh.any(0), harsh.argmax(0), -1)
    hs = h['counts'][:, hidx].sum(1) / h['N']
    ent = []
    for i in range(n):
        g1 = first_h[i]
        if g1 < 0:
            continue
        ent.append(dict(gen=int(g1), from_allc=bool(S[g1 - 1, st[i]] == iC), harsh_share_before=float(hs[g1 - 1])))
    out['harsh_entry'] = dict(
        n=len(ent),
        from_allc=sum(e['from_allc'] for e in ent),
        when_harsh_majority=sum(e['harsh_share_before'] >= 0.5 for e in ent),
        gen_median=float(np.median([e['gen'] for e in ent])) if ent else None,
        gen_p90=float(np.percentile([e['gen'] for e in ent], 90)) if ent else None)
    return basic, out


# ---------------------------------------------------------------- 问题 2：学成什么，和谁过得好
def phase_of(top_key):
    if top_key in HARSH:
        return '狠的分最高'
    if top_key == 'TFT':
        return '以牙还牙分最高'
    if top_key == 'GTFT':
        return '会原谅分最高'
    return '其他'


def q2(h, st, windows=None):
    keys, S, P = h['keys'], h['S'], h['P']
    nS = len(keys)
    N = h['N']
    G = S.shape[0] - 1
    is_st = np.zeros(N, bool)
    is_st[st] = True
    ph = {}
    tops = []
    per_gen = []
    for g in range(G):
        cnt = h['counts'][g]
        ms = np.array([P[g][S[g] == i].mean() if cnt[i] >= 5 else -1 for i in range(nS)])
        top = keys[int(ms.argmax())]
        tops.append(top)
        ch = S[g + 1] != S[g]
        tg = S[g + 1][ch]
        own = S[g][ch]
        tc = np.bincount(tg, minlength=nS)
        null = np.zeros(nS)
        for o in range(nS):
            k = int((own == o).sum())
            if k:
                v = cnt / max(1, N - cnt[o])
                v = v.astype(float)
                v[o] = 0
                null += k * v
        tc_st = np.bincount(S[g + 1][ch & is_st], minlength=nS)
        p = phase_of(top)
        d = ph.setdefault(p, dict(gens=0, to=np.zeros(nS), null=np.zeros(nS), to_st=np.zeros(nS), pop=np.zeros(nS),
                                  ssum=np.zeros(nS), scnt=np.zeros(nS), mat=np.zeros((nS, nS))))
        np.add.at(d['mat'], (own, tg), 1)
        d['gens'] += 1
        d['to'] += tc
        d['null'] += null
        d['to_st'] += tc_st
        d['pop'] += cnt / N
        d['ssum'] += np.bincount(S[g], P[g], nS)
        d['scnt'] += cnt
        gm = np.zeros((nS, nS))
        np.add.at(gm, (own, tg), 1)
        per_gen.append(dict(gen=g, top=top, to=tc.tolist(), mat=gm))
    # 各阶段的代数范围
    ranges = {}
    for g, t in enumerate(tops):
        p = phase_of(t)
        ranges.setdefault(p, []).append(g)
    out = dict(phases={p: dict(gens=d['gens'], first=min(ranges[p]), last=max(ranges[p]),
                               to=d['to'].astype(int).tolist(), null=np.round(d['null'], 2).tolist(),
                               to_st=d['to_st'].astype(int).tolist(),
                               pop_mean=np.round(d['pop'] / d['gens'], 4).tolist(),
                               ssum=d['ssum'].tolist(), scnt=d['scnt'].astype(int).tolist(),
                               mat=d['mat'].astype(int).tolist())
                      for p, d in ph.items()})
    if windows:
        w = {}
        for a, b in windows:
            tc = np.zeros(nS)
            pop = np.zeros(nS)
            mat = np.zeros((nS, nS))
            top_count = {}
            for g in range(a, min(b, G - 1) + 1):
                tc += per_gen[g]['to']
                mat += per_gen[g]['mat']
                pop += h['counts'][g] / N
                top_count[per_gen[g]['top']] = top_count.get(per_gen[g]['top'], 0) + 1
            w[f'{a}-{b}'] = dict(to=tc.astype(int).tolist(), pop_mean=np.round(pop / (min(b, G - 1) - a + 1), 4).tolist(),
                                 top=top_count, mat=mat.astype(int).tolist())
        out['windows'] = w
    return out


# ---------------------------------------------------------------- 任务
def main_job(seed):
    cfg = make_cfg(SCENARIOS[SCN], seed)
    h = run_traced(cfg)
    basic, a1 = q1(h)
    _, st, *_ = starters_basic(h)
    windows = [(0, 10), (11, 31), (32, 61), (62, 100), (101, 129), (130, 166), (167, 299)] if seed == 5 else None
    a2 = q2(h, st, windows)
    sh = h['counts'] / h['counts'].sum(1, keepdims=True)
    return seed, h['keys'], sh, basic, a1, a2


def ctrl_job(args):
    ci, seed = args
    label, sweep_key, init = CONTROLS[ci]
    cfg = make_cfg(dict(e=0.05, init=init), seed)
    h = run_traced(cfg)
    basic, *_ = starters_basic(h)
    keys = h['keys']
    hidx = [keys.index(k) for k in HARSH]
    sh = h['counts'] / h['counts'].sum(1, keepdims=True)
    hs = sh[:, hidx].sum(1)
    hm = dict(strategies=keys, counts=h['counts'], mean_score=h['mean_score'], coop=h['coop'])
    m = metrics(hm)
    basic.update(harsh_pop_peak=round(float(hs.max()), 4), harsh_pop_peak_gen=int(hs.argmax()),
                 alld_peak=round(float(sh[:, keys.index('ALLD')].max()), 4),
                 grim_peak=round(float(sh[:, keys.index('GRIM')].max()), 4),
                 winner=m['winner'], coop_final=m['coop_final'])
    return ci, seed, basic, m, sh


def main():
    stored = json.load(open(os.path.join(HERE, 'results', f'main_{SCN}.json')))
    stored_sh = {r['seed']: np.array(r['shares']) for r in stored['runs']}
    old = json.load(open(os.path.join(HERE, 'results', '变狠统计.json')))
    old_seed = {r['seed']: r for r in old['per_seed']}
    sweep = json.load(open(os.path.join(HERE, 'results', 'sweep_raw.json')))

    jobs_c = [(ci, sd) for ci in range(len(CONTROLS)) for sd in CTRL_SEEDS if CONTROLS[ci][1] is not None or ci > 0]
    with Pool(8) as pool:
        res_main = pool.map(main_job, MAIN_SEEDS, chunksize=1)
        res_ctrl = pool.map(ctrl_job, jobs_c, chunksize=1)

    # ---- 核对：主场景
    checks = []
    for seed, keys, sh, basic, a1, a2 in res_main:
        ref = stored_sh[seed]
        assert ref.shape == sh.shape, (seed, ref.shape, sh.shape)
        assert np.abs(ref - np.round(sh, 4)).max() < 1e-9, f'种子 {seed} 和 main_{SCN}.json 对不上'
        o = old_seed[seed]
        for k in ['ever_harsh', 'end_harsh', 'harsh_then_gtft']:
            assert o[k] == basic[k], (seed, k, o[k], basic[k])
        assert o['ever_grim'] == basic['ever_GRIM'] and o['ever_alld'] == basic['ever_ALLD'], seed
        fs_old = {k: v for k, v in o['first_switch'].items() if k != 'ALLC'}
        assert fs_old == basic['first_switch'], (seed, o['first_switch'], basic['first_switch'])
        assert o['first_switch'].get('ALLC', 0) == basic['never_switched'], seed
    checks.append('主场景 20 个种子：各打法占比逐代和 results/main_误会5%.json 一致；'
                  '变狠过、当过记仇/骗子、第一次改学、第 300 代狠人、狠过后会原谅，逐种子和 results/变狠统计.json 一致')

    # ---- 核对：对照里敏感性表已有的三组
    for ci, seed, basic, m, sh in res_ctrl:
        label, key, _ = CONTROLS[ci]
        if key is None:
            continue
        ref = next(r['metrics'] for r in sweep[key] if r['seed'] == seed)
        for k in ['winner', 'alld_peak', 'alld_peak_gen', 'grim_peak', 'grim_peak_gen', 'coop_final', 'allc_gone_gen', 'final']:
            assert ref[k] == m[k] or (isinstance(ref[k], float) and abs(ref[k] - m[k]) < 1e-9), (label, seed, k, ref[k], m[k])
    checks.append('对照里“六种平均分”“骗子 2%”“骗子 30%”三组 × 10 个种子：赢家、骗子峰值和代数、记仇峰值和代数、'
                  '终局合作率、老实人跌破 1% 的代、终局各打法占比，逐项和 results/sweep_raw.json 一致')
    print('\n'.join(checks))

    keys = res_main[0][1]
    nS = len(keys)
    hidx = [keys.index(k) for k in HARSH]
    iG, iT = keys.index('GTFT'), keys.index('TFT')

    # ---- 汇总问题 1
    def pool_list(name):
        return [r[4][name] for r in res_main]

    def summarize_a(bins_per_seed, betr_is_avg=False):
        rows = []
        for k in range(5):
            ds = [b[k] for b in bins_per_seed]
            n = sum(d['n'] for d in ds)
            fg = np.concatenate([np.array(d['first_gens']) for d in ds])
            G = 300
            sw = fg <= G
            row = dict(档=k + 1, 人数=n, 平均被背叛=round(sum(d['betrayed_sum'] for d in ds) / n, 1),
                       第一次改学代_中位=float(np.median(fg[sw])),
                       第5代前改学=round(float((fg <= 5).mean()), 3),
                       第10代前改学=round(float((fg <= 10).mean()), 3),
                       第一次改学学成狠的=round(sum(d['first_harsh'] for d in ds) / max(1, sw.sum()), 3),
                       变狠过=round(sum(d['ever_harsh'] for d in ds) / n, 3))
            if 'score_sum' in ds[0]:
                row['第0代平均分'] = round(sum(d['score_sum'] for d in ds) / n, 3)
                row['第0代末就改学'] = round(sum(d['switch_gen0'] for d in ds) / n, 3)
            rows.append(row)
        return rows

    gen0 = summarize_a(pool_list('gen0_quintile'))
    past_rows = []
    for k in range(5):
        ds = [r[4]['past5_quintile'][k] for r in res_main]
        n = sum(d['n'] for d in ds)
        past_rows.append(dict(档=k + 1, 人代数=n, 前5代被背叛合计_平均=round(sum(d['past'] for d in ds) / n, 1),
                              这一代被背叛_平均=round(sum(d['now'] for d in ds) / n, 1),
                              这一代末改学=round(sum(d['sw'] for d in ds) / n, 4),
                              只按这一代分数算=round(sum(d['pred'] for d in ds) / n, 4)))
    hz_rows = []
    for k in range(5):
        ds = [r[4]['hazard_by_betrayal'][k] for r in res_main]
        n = sum(d['n'] for d in ds); sw = sum(d['sw'] for d in ds)
        to = np.sum([d['to'] for d in ds], 0)
        hz_rows.append(dict(档=k + 1, 人代数=n, 平均被背叛=round(sum(d['betr'] for d in ds) / n, 1),
                            平均分=round(sum(d['score'] for d in ds) / n, 3),
                            这一代末改学=round(sw / n, 4),
                            只按分数算_含看到同打法=round(sum(d['pred'] for d in ds) / n, 4),
                            只按分数算=round(sum(d['pred2'] for d in ds) / n, 4),
                            改学的人学成狠的=round(float(to[hidx].sum() / max(1, sw)), 3),
                            学成={keys[i]: int(to[i]) for i in range(nS) if to[i]}))
    hzs_rows = []
    for k in range(5):
        ds = [r[4]['hazard_by_score'][k] for r in res_main]
        n = sum(d['n'] for d in ds)
        hzs_rows.append(dict(档=k + 1, 这一代末改学=round(sum(d['sw'] for d in ds) / n, 4),
                             只按分数算=round(sum(d['pred2'] for d in ds) / n, 4)))
    cn = sum(r[4]['corr_betrayal_score']['num'] for r in res_main)
    cw = sum(r[4]['corr_betrayal_score']['w'] for r in res_main)
    same_first = [r[4]['first_switch_same_as_looked'] for r in res_main]
    same_all = [r[4]['all_switches_same_as_looked'] for r in res_main]
    lk = []
    for x in range(nS):
        ds = [r[4]['look_gen0_10'][x] for r in res_main]
        n = sum(d['n'] for d in ds)
        if n == 0:
            continue
        lk.append(dict(看到的人=keys[x], 次数=n, 占看人次数=None, 看到后学了=round(sum(d['sw'] for d in ds) / n, 4),
                       对方平均分=round(sum(d['look_score'] for d in ds) / n, 3),
                       自己平均分=round(sum(d['own_score'] for d in ds) / n, 3)))
    tot_look = sum(d['次数'] for d in lk)
    tot_sw = sum(d['次数'] * d['看到后学了'] for d in lk)
    for d in lk:
        d['占看人次数'] = round(d['次数'] / tot_look, 3)
        d['占改学的人'] = round(d['次数'] * d['看到后学了'] / tot_sw, 3)
    ent = [r[4]['harsh_entry'] for r in res_main]
    q1_sum = dict(
        第0代被背叛分五档=gen0,
        前5代被背叛分五档_看这一代改不改=past_rows,
        逐代危险率_按被背叛分五档=dict(代数范围=[min(r[4]['hazard_gens'][0] for r in res_main), max(r[4]['hazard_gens'][1] for r in res_main)], 表=hz_rows),
        逐代危险率_按分数分五档=hzs_rows,
        老实人被背叛次数和分数的相关=round(cn / cw, 4),
        第一次改学_学成的就是看的那个人的打法=dict(人=sum(d['n'] for d in same_first), 一样=sum(d['same'] for d in same_first)),
        全场所有改学_学成的就是看的那个人的打法=dict(次=sum(d['n'] for d in same_all), 一样=sum(d['same'] for d in same_all)),
        第0到10代老实人看到谁=lk,
        第一次变狠=dict(人=sum(e['n'] for e in ent), 直接从老实人变=sum(e['from_allc'] for e in ent),
                     变狠前一代全场狠人过半=sum(e['when_harsh_majority'] for e in ent),
                     代数中位_各种子=[e['gen_median'] for e in ent]),
    )

    # ---- 汇总问题 2
    phases = ['狠的分最高', '以牙还牙分最高', '会原谅分最高', '其他']
    q2_pool = {}
    q2_seed = {p: dict(harsh=[], gtft=[], tft=[]) for p in phases}
    for r in res_main:
        for p, d in r[5]['phases'].items():
            agg = q2_pool.setdefault(p, dict(gens=0, to=np.zeros(nS), null=np.zeros(nS), to_st=np.zeros(nS), first=[], last=[],
                                             ssum=np.zeros(nS), scnt=np.zeros(nS), pop=np.zeros(nS), mat=np.zeros((nS, nS))))
            agg['mat'] += np.array(d['mat'])
            agg['gens'] += d['gens']; agg['to'] += d['to']; agg['null'] += d['null']; agg['to_st'] += d['to_st']
            agg['ssum'] += d['ssum']; agg['scnt'] += d['scnt']; agg['pop'] += np.array(d['pop_mean']) * d['gens']
            agg['first'].append(d['first']); agg['last'].append(d['last'])
            t = np.array(d['to'])
            if t.sum() >= 20:
                q2_seed[p]['harsh'].append(float(t[hidx].sum() / t.sum()))
                q2_seed[p]['gtft'].append(float(t[iG] / t.sum()))
                q2_seed[p]['tft'].append(float(t[iT] / t.sum()))
    q2_rows = []
    for p in phases:
        if p not in q2_pool:
            continue
        a = q2_pool[p]
        t, nl, ts = a['to'], a['null'], a['to_st']

        def rng3(v):
            return [round(min(v), 3), round(float(np.median(v)), 3), round(max(v), 3)] if v else None
        q2_rows.append(dict(
            阶段=p, 代数合计=a['gens'], 第一代_中位=float(np.median(a['first'])), 最后一代_中位=float(np.median(a['last'])),
            改学人次=int(t.sum()),
            学成狠的=round(float(t[hidx].sum() / t.sum()), 3), 学成会原谅=round(float(t[iG] / t.sum()), 3),
            学成以牙还牙=round(float(t[iT] / t.sum()), 3),
            只按人数算_学成狠的=round(float(nl[hidx].sum() / nl.sum()), 3),
            只按人数算_学成会原谅=round(float(nl[iG] / nl.sum()), 3),
            只按人数算_学成以牙还牙=round(float(nl[iT] / nl.sum()), 3),
            各种子_学成狠的_最小中位最大=rng3(q2_seed[p]['harsh']),
            各种子_学成会原谅_最小中位最大=rng3(q2_seed[p]['gtft']),
            开局老实人_改学人次=int(ts.sum()),
            开局老实人_学成狠的=round(float(ts[hidx].sum() / ts.sum()), 3) if ts.sum() else None,
            开局老实人_学成会原谅=round(float(ts[iG] / ts.sum()), 3) if ts.sum() else None,
            本来不狠的人改学_人次=int(a['mat'][[i for i in range(nS) if i not in hidx]].sum()),
            本来不狠的人改学_学成狠的=round(float(a['mat'][[i for i in range(nS) if i not in hidx]][:, hidx].sum()
                                       / max(1, a['mat'][[i for i in range(nS) if i not in hidx]].sum())), 3),
            本来不狠的人改学_学成会原谅=round(float(a['mat'][[i for i in range(nS) if i not in hidx]][:, iG].sum()
                                        / max(1, a['mat'][[i for i in range(nS) if i not in hidx]].sum())), 3),
            本来不狠的人改学_学成以牙还牙=round(float(a['mat'][[i for i in range(nS) if i not in hidx]][:, iT].sum()
                                         / max(1, a['mat'][[i for i in range(nS) if i not in hidx]].sum())), 3),
            本来狠的人改学_人次=int(a['mat'][hidx].sum()),
            本来狠的人改学_学成以牙还牙=round(float(a['mat'][hidx][:, iT].sum() / max(1, a['mat'][hidx].sum())), 3),
            本来狠的人改学_学成会原谅=round(float(a['mat'][hidx][:, iG].sum() / max(1, a['mat'][hidx].sum())), 3),
            本来狠的人改学_仍学成狠的=round(float(a['mat'][hidx][:, hidx].sum() / max(1, a['mat'][hidx].sum())), 3),
            从什么改成什么={f'{keys[i]}→{keys[j]}': int(a['mat'][i, j]) for i in range(nS) for j in range(nS) if a['mat'][i, j] >= 50},
            各打法平均分={keys[i]: round(float(a['ssum'][i] / a['scnt'][i]), 3) for i in range(nS) if a['scnt'][i] >= 5 * a['gens']},
            全场人数占比={keys[i]: round(float(a['pop'][i] / a['gens']), 3) for i in range(nS)},
            学成=({keys[i]: int(t[i]) for i in range(nS) if t[i]})))
    s5 = next(r for r in res_main if r[0] == 5)
    win_rows = []
    nonh = [i for i in range(nS) if i not in hidx]
    for w, d in s5[5]['windows'].items():
        t = np.array(d['to'])
        mt = np.array(d['mat'])
        win_rows.append(dict(代=w, 改学人次=int(t.sum()),
                             本来不狠的人改学_人次=int(mt[nonh].sum()),
                             本来不狠的人改学_学成狠的=round(float(mt[nonh][:, hidx].sum() / max(1, mt[nonh].sum())), 3),
                             本来不狠的人改学_学成会原谅=round(float(mt[nonh][:, iG].sum() / max(1, mt[nonh].sum())), 3),
                             学成狠的=round(float(t[hidx].sum() / t.sum()), 3) if t.sum() else None,
                             学成会原谅=round(float(t[iG] / t.sum()), 3) if t.sum() else None,
                             学成以牙还牙=round(float(t[iT] / t.sum()), 3) if t.sum() else None,
                             全场狠人占比=round(float(np.array(d['pop_mean'])[hidx].sum()), 3),
                             平均分最高的打法=d['top']))

    # ---- 汇总问题 3
    base_rows = [dict(seed=r[0], **r[3]) for r in res_main if r[0] in CTRL_SEEDS]
    by_ci = {}
    for ci, seed, basic, m, sh in res_ctrl:
        by_ci.setdefault(ci, []).append(dict(seed=seed, **basic))
    by_ci[0] = base_rows  # 基准就是主场景的种子 1–10
    q3_rows = []
    for ci, (label, key, init) in enumerate(CONTROLS):
        rs = sorted(by_ci[ci], key=lambda r: r['seed'])

        def med(k):
            v = [r[k] for r in rs if r.get(k) is not None]
            return [round(min(v), 3), round(float(np.median(v)), 3), round(max(v), 3)] if v else None

        def share(k):
            return [round(r[k] / r['n_starters'], 3) for r in rs]
        fs = [r['first_switch_harsh'] / max(1, r['n_starters'] - r['never_switched']) for r in rs]
        eg = [r.get('ever_GRIM', 0) / r['n_starters'] for r in rs]
        ea = [r.get('ever_ALLD', 0) / r['n_starters'] for r in rs]
        q3_rows.append(dict(
            对照=label, 已有=key is not None or ci == 0, 开局老实人=rs[0]['n_starters'],
            变狠过_最小中位最大=med('ever_harsh_share'),
            第一次改学就学成狠的_中位=round(float(np.median(fs)), 3),
            当过记仇_中位=round(float(np.median(eg)), 3), 当过骗子_中位=round(float(np.median(ea)), 3),
            全场狠人峰值_中位=round(float(np.median([r.get('harsh_pop_peak', np.nan) for r in rs])), 3) if 'harsh_pop_peak' in rs[0] else None,
            骗子峰值_中位=round(float(np.median([r['alld_peak'] for r in rs])), 3) if 'alld_peak' in rs[0] else None,
            记仇峰值_中位=round(float(np.median([r['grim_peak'] for r in rs])), 3) if 'grim_peak' in rs[0] else None,
            第300代还狠的_合计=int(sum(r['end_harsh'] for r in rs)),
            终局第一=({w: sum(1 for r in rs if r.get('winner') == w) for w in set(r.get('winner') for r in rs)} if 'winner' in rs[0] else None),
            逐种子=[dict(seed=r['seed'], 变狠过=r['ever_harsh_share'], 第一次改学=r['first_switch'], 最后=r['end']) for r in rs]))
    # 基准的峰值和赢家从主场景结果文件里补
    base_runs = {r['seed']: r for r in stored['runs']}
    bpk = [base_runs[s]['metrics'] for s in CTRL_SEEDS]
    shs = [np.array(base_runs[s]['shares']) for s in CTRL_SEEDS]
    q3_rows[0]['全场狠人峰值_中位'] = round(float(np.median([x[:, [1, 4]].sum(1).max() for x in shs])), 3)
    q3_rows[0]['骗子峰值_中位'] = round(float(np.median([m['alld_peak'] for m in bpk])), 3)
    q3_rows[0]['记仇峰值_中位'] = round(float(np.median([m['grim_peak'] for m in bpk])), 3)
    q3_rows[0]['终局第一'] = {w: sum(1 for m in bpk if m['winner'] == w) for w in set(m['winner'] for m in bpk)}

    summary = dict(
        说明='见 核对_被坑与改学.md；本文件由 核对_被坑与改学.py 生成',
        核对=checks,
        问题1=q1_sum,
        问题2=dict(按阶段_20个种子合计=q2_rows, 种子5_按代=win_rows,
                 阶段定义='每一代按“当代至少 5 人在用的打法里，平均分最高的是谁”归阶段；改学人次 = 这一代末打法变了的人数',
                 只按人数算='假如学谁只看人数、不看分：改学的人学成 X 的期望比例 = X 的人数 ÷ 除自己那种以外的总人数'),
        问题3_对照=q3_rows,
        主场景逐种子=[dict(seed=r[0], **r[3]) for r in res_main],
    )

    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(OUT, 'w') as fo:
        json.dump(summary, fo, ensure_ascii=False, indent=1, default=conv)
    print(json.dumps({k: summary[k] for k in ['问题1', '问题2']}, ensure_ascii=False, indent=1, default=conv))
    for r in q3_rows:
        print({k: v for k, v in r.items() if k != '逐种子'})


if __name__ == '__main__':
    main()
