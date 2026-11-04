import sys, json, time
sys.path.insert(0, '/Users/decheng.huang/Documents/dy/videos/002_做好人/sim')
from sim import Config, run
import numpy as np
out = []
for mu in (0.002, 0.01):
    for seed in (1, 2, 3, 4):
        t = time.time()
        cfg = Config(N=1000, K=10, n=200, gens=2000, e=0.05, strategies=['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM', 'WSLS'],
                     init={'ALLC': 0.5, 'ALLD': 0.1, 'TFT': 0.1, 'GTFT': 0.1, 'GRIM': 0.1, 'WSLS': 0.1}, g=1/3,
                     matching='random', rule='imitate', mu=mu, seed=seed)
        h = run(cfg)
        c = np.array(h['counts']) / 1000.0
        harsh = c[:, 1] + c[:, 4]
        forgive = c[:, 3]
        honest = c[:, 0]
        coop = np.array(h['coop'])
        # 300 代以后：狠人占比超过 30% 的“回潮”有几次（从 <10% 涨到 >30% 算一次）
        waves, low = 0, False
        for g in range(300, len(harsh)):
            if harsh[g] < 0.10: low = True
            if low and harsh[g] > 0.30: waves += 1; low = False
        r = dict(mu=mu, seed=seed, secs=round(time.time() - t, 1), waves_after300=waves,
                 harsh_max_after300=round(float(harsh[300:].max()), 3), honest_max_after300=round(float(honest[300:].max()), 3),
                 forgive_mean_after300=round(float(forgive[300:].mean()), 3), coop_min_after300=round(float(coop[300:].min()), 3),
                 snap={g: [round(float(x), 2) for x in c[g]] for g in (300, 600, 900, 1200, 1500, 2000)})
        out.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
json.dump(out, open('/private/tmp/claude-502/-Users-decheng-huang-Documents-dy/ae3d8432-15cd-4912-94e0-9032042d27c8/scratchpad/cycle_test.json', 'w'), ensure_ascii=False, indent=1)
