"""把仿真导出的画面数据精简成 data.json，给 002 横屏灰框用。只读 sim/visual/，不改它们。

读：pop / dots / you / crowd / starters / history20（都是 sim/visual/*_误会5%.json）
写：studio/src/videos/002/data.json

另做三件只和画面有关的事（都按固定种子，可复现）：
  1. 远景 1000 个点怎么排：50 列 × 20 行。你（第 72 号）在第 16 列第 10 行；你右边那格放第 0 代坑你的骗子（第 957 号），
     开场拉远时“一黄一橙两颗点”就是你们俩。dots 里那 300 个跟踪点排在离你最近的格子里（中景里能用它们的真分数画条），
     其余 700 人随机排在外圈。
  2. 远景里黄点变成橙、粉那一下“从旁边连过来的一道线”（分镜 22.4 秒，示意）：对每个从老实人改成骗子或记仇的人，
     找离他最近、当时正是那种打法的点，连一条线。
  1′. 第 7 代被你坑的 6 个老实人（you 第 7 代 games 里打法是老实人的那 6 个）排在你周围 3–6 格：
     “和你”那一扎从你的点连粉线连到他们，推镜画面里要看得见（只是排布，不改数据）。
  3. 473 人方块里谁排在哪：按“从第几代起一直是最后那种打法”排序，先回来的先翻色（示意，最后的颜色是真的）。

用法：/Users/decheng.huang/Documents/dy/.venv/bin/python /Users/decheng.huang/Documents/dy/studio/src/videos/002/make_data.py
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = os.path.abspath(os.path.join(HERE, '../../../../videos/002_做好人/sim/visual'))
SCN = '误会5%'
OUT = os.path.join(HERE, 'data.json')

COLS, ROWS = 50, 20
YOU_CELL = (16, 10)


def load(name):
    return json.load(open(os.path.join(VIS, f'{name}_{SCN}.json')))


def main():
    pop, dots, you, crowd, st, h20 = (load(n) for n in ['pop', 'dots', 'you', 'crowd', 'starters', 'history20'])
    keys = [s['code'] for s in pop['strategies']]
    K = {k: i for i, k in enumerate(keys)}
    G = len(pop['counts']) - 1
    N = crowd['n']
    S = np.array([[int(c) for c in row] for row in crowd['s']], np.int8)     # 代 × 人
    assert (np.array([np.bincount(S[g], minlength=6) for g in range(G + 1)]) == np.array(pop['counts'])).all()
    me = you['you_id']

    # 1. 远景格子
    rng = np.random.default_rng(2002)
    cells = [(c, r) for r in range(ROWS) for c in range(COLS)]
    dist = np.array([np.hypot(c - YOU_CELL[0], (r - YOU_CELL[1]) * 1.0) + 1e-3 * rng.random() for c, r in cells])
    order = np.argsort(dist)                  # 离你从近到远的格子
    cell_of = -np.ones(N, int)
    swindler = 957                            # 第 0 代坑你的骗子之一（you 第 0 代 games）
    assert you['generations'][0]['games'][0]['partner'] == swindler and S[0, swindler] == K['ALLD']
    right = cells.index((YOU_CELL[0] + 1, YOU_CELL[1]))
    cell_of[me] = order[0]
    cell_of[swindler] = right
    used = {order[0], right}
    # 第 7 代被你坑的老实人
    g7 = you['generations'][7]
    victims = [g['partner'] for g in g7['games'] if g['partner_strategy'] == 'ALLC']
    assert len(victims) == 6 and all(S[7, v] == K['ALLC'] for v in victims)
    VIC_CELLS = [(13, 7), (20, 7), (22, 10), (11, 11), (19, 13), (14, 14)]
    for v, (c, r) in zip(victims, VIC_CELLS):
        cell_of[v] = cells.index((c, r))
        used.add(cell_of[v])
    tracked = [i for i in dots['ids'] if i not in (me, swindler, *victims)]
    rest = [i for i in range(N) if i not in set(dots['ids']) | {swindler, *victims}]
    rng.shuffle(rest)
    free = [c for c in order if c not in used]
    for i, c in zip(tracked + rest, free):
        cell_of[i] = c
    assert (cell_of >= 0).all() and len(set(cell_of.tolist())) == N
    person_at = np.empty(N, int)
    person_at[cell_of] = np.arange(N)
    # 每代按格子顺序的打法串：画面直接按格子取字
    grid_s = [''.join(str(int(v)) for v in S[g, person_at]) for g in range(G + 1)]

    # 中景的条：跟踪点前 13 代的分数（第 4–7 代那拍用），按格子存
    ids = np.array(dots['ids'])
    P = np.array(dots['p'])                    # 代 × 300
    cell_score = {}
    for k, pid in enumerate(ids):
        cell_score[int(cell_of[pid])] = [round(float(P[g, k]), 2) for g in range(13)]

    # 2. 变狠时连过来的线（第 1–70 代）
    xy = np.array(cells, float)
    links = []
    for g in range(1, 71):
        sw = np.nonzero((S[g - 1] == K['ALLC']) & ((S[g] == K['ALLD']) | (S[g] == K['GRIM'])))[0]
        for pid in sw:
            new = S[g, pid]
            cand = np.nonzero(S[g - 1] == new)[0]
            if not len(cand):
                continue
            d = np.hypot(*(xy[cell_of[cand]] - xy[cell_of[pid]]).T)
            j = cand[int(np.argmin(d))]
            if d.min() <= 6:
                links.append([g, int(cell_of[pid]), int(cell_of[j]), int(new)])

    # 3. 473 人方块
    sid = np.array(st['ids'])
    first = np.array(st['first_harsh_gen'])
    ever = first >= 0
    harsh_idx = np.nonzero(ever)[0]
    end_since = np.array(st['end_since'])
    flip_order = harsh_idx[np.argsort(end_since[harsh_idx], kind='stable')]
    block = [dict(cell=int(cell_of[sid[k]]), main=int(st['harsh_main'][k]), end=int(st['end'][k]),
                  since=int(end_since[k]), you=bool(sid[k] == me)) for k in flip_order]
    starters_cells = [int(cell_of[i]) for i in sid]

    # “你”每代
    yg = []
    for r in you['generations']:
        yg.append(dict(
            s=K[r['strategy']], sc=r['score'], pct=r['percentile'],
            opp=[K[x['partner_strategy']] for x in r['games']],
            bet=[x['betrayed'] for x in r['games']],
            look=r['looked_at']['score'] if r.get('looked_at') else None,
            lookS=K[r['looked_at']['strategy']] if r.get('looked_at') else None,
            sw=K[r['switched_to']] if r.get('switched_to') else -1,
        ))
    sc = np.array([r['score'] for r in you['generations']])
    segs = [(0, 4), (5, 108), (109, 166), (167, 300)]
    you_avg = [round(float(sc[a:b + 1].mean()), 2) for a, b in segs]
    assert [K[you['generations'][a]['strategy']] for a, _ in segs] == [K['ALLC'], K['GRIM'], K['TFT'], K['GTFT']]

    # 收尾 20 条：种子 5 排第一条（就是顶上那条复制下来的），其余按种子号
    seeds = h20['seeds']
    order20 = [seeds.index(5)] + [i for i in range(len(seeds)) if seeds[i] != 5]
    assert h20['counts'][seeds.index(5)] == pop['counts']

    out = dict(
        note='由 make_data.py 从 sim/visual/*_误会5%.json 生成，别手改',
        strategies=[dict(code=s['code'], name=s['name'], color=s['color_dark']) for s in pop['strategies']],
        names=dict(ALLC='老实人', ALLD='骗子', TFT='以牙还牙', GTFT='会原谅', GRIM='记仇', WSLS='不点名'),
        counts=pop['counts'], coop=pop['coop'],
        grid=dict(cols=COLS, rows=ROWS, youCell=int(cell_of[me]), swindlerCell=int(right), s=grid_s,
                  victims=[int(cell_of[v]) for v in victims],
                  starters=starters_cells, score=cell_score),
        links=links,
        you=yg, youAvg=you_avg,
        starters=dict(n=len(sid), ever=int(ever.sum()), everByGen=st['ever_harsh_by_gen'],
                      harshThenGtft=st['harsh_then_gtft'], block=block),
        hist20=dict(seeds=[seeds[i] for i in order20], counts=[h20['counts'][i] for i in order20]),
    )
    # 第七版（10/30）：第 300 代起接着跑、加“新人进来”（sim/循环_接着跑.py），给“可新人一多，狠人又回来了”那拍用。
    # cycle.s[k] 是第 300+k 代按格子顺序的打法串（和 grid.s 同一套格子）；第 0 项必须等于 grid.s[300]。
    cpath = os.path.join(VIS, f'continue_{SCN}.json')
    if os.path.exists(cpath):
        cont = json.load(open(cpath))
        CS = np.array([[int(c) for c in row] for row in cont['s']], np.int8)
        cyc_s = [''.join(str(int(v)) for v in CS[k, person_at]) for k in range(len(CS))]
        assert cyc_s[0] == grid_s[300], '接着跑的第 300 代和 grid.s[300] 对不上'
        out['cycle'] = dict(gen0=cont['gen0'], gen1=cont['gen1'], mu=cont['mu'], harshBack30=cont['harsh_back_30'],
                            harshPeak=cont['harsh_peak'], harshPeakShare=cont['harsh_peak_share'], counts=cont['counts'], s=cyc_s)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('写出', OUT, f'{os.path.getsize(OUT) / 1024:.0f} KB')
    print('你四段平均分', you_avg, '；变色连线', len(links), '条；方块', len(block), '格')


if __name__ == '__main__':
    main()
