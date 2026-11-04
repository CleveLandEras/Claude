"""给 Remotion 画面用的数据。

用法：python export_visual.py 场景名 种子
  场景名见 experiments.SCENARIOS；种子用 analyze.py 选出的代表性种子。

输出（visual/ 目录）：
  pop_<场景>.json   1000 人每一代各策略人数、各策略平均分、合作率、关键事件
  dots_<场景>.json  从 1000 人里固定抽 300 个点，每代每点的策略编号和得分（“你”也在里面）
  you_<场景>.json   “你”每一代碰到谁、被背叛几次、自己手滑几次、看了谁、改没改
"""
import json
import os
import sys
from collections import Counter

import numpy as np

from sim import run, STRATS, COLORS
from experiments import make_cfg, SCENARIOS, metrics

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'visual')


def path_of(col):
    p = [int(col[0])]
    for v in col[1:]:
        if v != p[-1]:
            p.append(int(v))
    return tuple(p)


def switch_gens(col):
    return [g for g in range(1, len(col)) if col[g] != col[g - 1]]


def pick_you(strat_hist, keys, start='ALLC'):
    """在开局是 start 的人里，找最常见的“打法路径”，再挑换打法时间最接近该路径中位数的人。"""
    S = np.stack(strat_hist)  # gens × N
    s0 = keys.index(start)
    cand = np.nonzero(S[0] == s0)[0]
    paths = {i: path_of(S[:, i]) for i in cand}
    cnt = Counter(paths.values())
    total = len(cand)
    common = cnt.most_common(8)
    best_path = common[0][0]
    members = [i for i in cand if paths[i] == best_path]
    sw = np.array([switch_gens(S[:, i]) for i in members]) if len(best_path) > 1 else None
    if sw is not None and sw.size:
        med = np.median(sw, 0)
        dist = np.abs(sw - med).sum(1)
        you = int(members[int(np.argmin(dist))])
        med_list = med.tolist()
    else:
        you, med_list = int(members[0]), []
    table = [dict(path=[keys[j] for j in p], count=c, share=round(c / total, 3)) for p, c in common]
    return you, dict(start=start, n_start=total, paths=table, chosen_path=[keys[j] for j in best_path],
                     chosen_path_share=round(cnt[best_path] / total, 3), median_switch_gens=med_list)


def main(scn, seed, start='ALLC'):
    os.makedirs(OUT, exist_ok=True)
    over = SCENARIOS[scn]
    cfg = make_cfg(over, seed)
    cfg.record_individuals = True
    h = run(cfg)
    keys = h['strategies']
    you, pinfo = pick_you(h['strat'], keys, start)
    # 同一个种子再跑一遍，记录“你”的逐局细节（记录不消耗随机数，结果完全一样）
    cfg2 = make_cfg(over, seed)
    cfg2.you = you
    h2 = run(cfg2)
    assert (h2['counts'] == h['counts']).all()

    m = metrics(h)
    legend = [dict(code=k, index=i, name=STRATS[k]['name'], desc=STRATS[k]['desc'],
                   color_light=COLORS[k][0], color_dark=COLORS[k][1]) for i, k in enumerate(keys)]
    cfgd = dict(h['config'])
    cfgd.pop('you', None)
    cfgd.pop('record_individuals', None)
    events = dict(
        alld_peak_gen=m.get('alld_peak_gen'), alld_peak_share=m.get('alld_peak'),
        allc_below_1pct_gen=m.get('allc_gone_gen'), alld_below_1pct_gen=m.get('alld_gone_gen'),
        alld_score_below_tft_gen=m.get('alld_below_tft_gen'),
        tft_peak_gen=m.get('tft_peak_gen'), tft_peak_share=m.get('tft_peak_after'),
        grim_peak_gen=m.get('grim_peak_gen'), grim_peak_share=m.get('grim_peak'),
        noise_from=cfgd['noise_from'] if cfgd['e'] > 0 else None,
    )
    # 宽容的以牙还牙第一次超过以牙还牙
    c = h['counts']
    if 'GTFT' in keys and 'TFT' in keys:
        iG, iT = keys.index('GTFT'), keys.index('TFT')
        pk = m.get('tft_peak_gen') or 0
        over_g = [g for g in range(pk, len(c)) if c[g, iG] > c[g, iT]]
        events['gtft_overtakes_tft_gen'] = over_g[0] if over_g else None
    pop = dict(scenario=scn, seed=seed, config=cfgd, strategies=legend,
               note='counts[g][i] = 第 g 代用第 i 种打法的人数（共 N 人）；mean_score 为每轮平均得分；coop = 这一代所有动作里合作的比例',
               counts=c.tolist(),
               mean_score=[[None if v is None else round(v, 3) for v in row] for row in h['mean_score']],
               coop=[round(v, 4) for v in h['coop']], events=events, metrics=m)
    json.dump(pop, open(os.path.join(OUT, f'pop_{scn}.json'), 'w'), ensure_ascii=False)

    rng = np.random.default_rng(12345)
    ids = rng.choice(cfg.N, 300, replace=False)
    if you not in ids:
        ids[0] = you
    ids = np.sort(ids)
    S = np.stack(h['strat'])[:, ids]
    P = np.stack(h['score'])[:, ids]
    dots = dict(scenario=scn, seed=seed, strategies=legend, ids=ids.tolist(), you_dot=int(np.nonzero(ids == you)[0][0]),
                note='s[g][k] = 第 g 代第 k 个点的打法编号（见 strategies.index）；p[g][k] = 这一代每轮平均得分。'
                     '点是从 1000 人里随机固定抽的 300 人，每个点一直是同一个人。',
                share_check=[np.bincount(S[g], minlength=len(keys)).tolist() for g in (0, len(S) // 2, len(S) - 1)],
                s=S.astype(int).tolist(), p=np.round(P, 2).tolist())
    json.dump(dots, open(os.path.join(OUT, f'dots_{scn}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))

    yd = dict(scenario=scn, seed=seed, you_id=you, you_dot=dots['you_dot'], how_chosen=pinfo,
              note='每代一条：strategy 这一代用的打法；score 每轮平均分；percentile 分数比多少比例的人高；'
                   'games 这一代碰到的 10 个人（partner_strategy 对方打法、your_avg 你在这一局每轮平均分、betrayed 你被背叛的次数（200 轮里）、'
                   'your_mistakes 你手滑的次数、partner_mistakes 对方手滑的次数）；looked_at 这一代结束时你看了谁；switched_to 你改学成什么（null = 没改）',
              generations=h2['you'])
    json.dump(yd, open(os.path.join(OUT, f'you_{scn}.json'), 'w'), ensure_ascii=False, indent=1)
    print('you', you, json.dumps(pinfo, ensure_ascii=False))
    print('events', events)
    return yd


if __name__ == '__main__':
    scn = sys.argv[1]
    seed = int(sys.argv[2])
    start = sys.argv[3] if len(sys.argv) > 3 else 'ALLC'
    main(scn, seed, start)
