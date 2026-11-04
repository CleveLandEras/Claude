"""核第七版三改的两句字幕：重跑 循环_接着跑.py 的同一遍（不多耗随机数，逐代和画面数据对得上），记每类人的平均分。
好欺负＝老实人＋不点名（看输赢换打法）；狠＝骗子＋记仇。结果在 results/循环_平均分.txt。
用法：/Users/decheng.huang/Documents/dy/.venv/bin/python -I 循环_平均分.py"""
import json, os, sys
import numpy as np
SIM = '/Users/decheng.huang/Documents/dy/videos/002_做好人/sim'
sys.path.insert(0, SIM)
from sim import Config, run, pairs_for, play, update, _ptab
MU, CSEED, G1 = 0.005, 1003, 900
base = dict(N=1000, K=10, n=200, gens=300, e=0.05, strategies=['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM', 'WSLS'],
            init={'ALLC': 0.5, 'ALLD': 0.1, 'TFT': 0.1, 'GTFT': 0.1, 'GRIM': 0.1, 'WSLS': 0.1}, g=1/3,
            matching='random', rule='imitate', seed=5, record_individuals=True)
h = run(Config(**base))
strat = np.array(h['strat'][-1]).astype(np.int64)
ref = json.load(open(os.path.join(SIM, 'visual/continue_误会5%.json')))
cfg = Config(**{**base, 'mu': MU, 'seed': CSEED, 'record_individuals': False})
rng = np.random.default_rng(CSEED)
ptab, p0, is_grim = _ptab(cfg)
fam = {'soft': [0, 5], 'harsh': [1, 4], 'tft': [2], 'gtft': [3]}
rows = []
for gen in range(301, G1 + 1):
    A, B = pairs_for(cfg, rng)
    pa, pb, dA, dB, errA, errB, coop = play(strat[A], strat[B], cfg.n, cfg.e, 0.0, ptab, p0, is_grim, rng)
    tot = np.bincount(A, pa, 1000) + np.bincount(B, pb, 1000)
    games = np.bincount(A, minlength=1000) + np.bincount(B, minlength=1000)
    score = tot / (games * cfg.n)
    ms = {k: (float(score[np.isin(strat, v)].mean()) if np.isin(strat, v).any() else None) for k, v in fam.items()}
    cnt = {k: int(np.isin(strat, v).sum()) for k, v in fam.items()}
    rows.append((gen - 1, cnt, ms, float(score.mean())))
    strat, _, _ = update(strat, score, cfg, rng, 6)
    assert np.bincount(strat, minlength=6).tolist() == ref['counts'][gen - 300], gen
print('和画面数据逐代对得上')
for g, cnt, ms, pm in rows:
    if g % 25 == 0 or 760 <= g <= 800 and g % 5 == 0:
        f = lambda x: '  -  ' if x is None else '%.2f' % x
        print(g, '人数', cnt, '平均分 好欺负%s 狠%s 有来有往%s 原谅%s 全体%.2f' % (f(ms['soft']), f(ms['harsh']), f(ms['tft']), f(ms['gtft']), pm))
# 狠的平均分高于全体平均的代
hi = [g for g, cnt, ms, pm in rows if ms['harsh'] is not None and ms['harsh'] > pm]
print('狠的平均分高于全体平均的代数', len(hi), '范围', hi[:3], '...', hi[-3:])
top = [g for g, cnt, ms, pm in rows if ms['harsh'] is not None and all(ms['harsh'] >= v for k, v in ms.items() if v is not None)]
print('狠的平均分最高的代数', len(top), top[:5], top[-5:])
