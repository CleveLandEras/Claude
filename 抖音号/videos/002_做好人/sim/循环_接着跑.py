"""从画面用的那一遍（误会 5%、种子 5）第 300 代接着跑，加“新人进来”（每人每代 0.5% 概率随机换一种打法），跑到第 900 代。
给第二条第七版 49–51 秒那一拍“可新人一多，狠人又回来了”用。接着跑的随机种子 1003（10/30 试过的三个之一，第 774 代狠人回到三成）。
写 visual/continue_误会5%.json：s[k] 是第 300+k 代每个人的打法（和 crowd 的人序号一致）。
用法：/Users/decheng.huang/Documents/dy/.venv/bin/python -I 循环_接着跑.py"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import Config, run, pairs_for, play, update, _ptab
HERE = os.path.dirname(os.path.abspath(__file__))
MU, CSEED, G1 = 0.005, 1003, 900
base = dict(N=1000, K=10, n=200, gens=300, e=0.05, strategies=['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM', 'WSLS'],
            init={'ALLC': 0.5, 'ALLD': 0.1, 'TFT': 0.1, 'GTFT': 0.1, 'GRIM': 0.1, 'WSLS': 0.1}, g=1/3,
            matching='random', rule='imitate', seed=5, record_individuals=True)
h = run(Config(**base))
crowd = json.load(open(os.path.join(HERE, 'visual/crowd_误会5%.json')))
s300 = np.array([int(c) for c in crowd['s'][300]], np.int64)
strat = np.array(h['strat'][-1]).astype(np.int64)
assert (strat == s300).all(), '第 300 代的人和画面数据对不上'
cfg = Config(**{**base, 'mu': MU, 'seed': CSEED, 'record_individuals': False})
rng = np.random.default_rng(CSEED)
ptab, p0, is_grim = _ptab(cfg)
rows, counts, coop_l = [''.join(map(str, strat))], [np.bincount(strat, minlength=6).tolist()], [None]
for gen in range(301, G1 + 1):
    A, B = pairs_for(cfg, rng)
    pa, pb, dA, dB, errA, errB, coop = play(strat[A], strat[B], cfg.n, cfg.e, 0.0, ptab, p0, is_grim, rng)
    tot = np.bincount(A, pa, 1000) + np.bincount(B, pb, 1000)
    games = np.bincount(A, minlength=1000) + np.bincount(B, minlength=1000)
    score = tot / (games * cfg.n)
    strat, _, _ = update(strat, score, cfg, rng, 6)
    rows.append(''.join(map(str, strat)))
    counts.append(np.bincount(strat, minlength=6).tolist())
    coop_l.append(float(coop))
harsh = [(c[1] + c[4]) / 1000 for c in counts]
g30 = next(300 + k for k, v in enumerate(harsh) if v >= 0.30)
gmax = 300 + int(np.argmax(harsh))
out = dict(note='第 300 代起接着跑：每人每代 0.5% 概率随机换打法（新人进来）', mu=MU, seed_continue=CSEED, gen0=300, gen1=G1,
           harsh_back_30=g30, harsh_peak=gmax, harsh_peak_share=round(max(harsh), 3), counts=counts, s=rows)
json.dump(out, open(os.path.join(HERE, 'visual/continue_误会5%.json'), 'w'))
print('第 300 代对得上；狠人回到三成：第', g30, '代；最高：第', gmax, '代', round(max(harsh), 3))
for g in (300, 500, 700, 774, 800, 841, 900):
    print(g, counts[g - 300])
