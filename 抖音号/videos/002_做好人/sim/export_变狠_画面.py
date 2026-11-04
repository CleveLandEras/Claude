"""《被坑多了，人会变狠吗？》横屏版画面要的三份新数据。只导出，不改参数，不覆盖任何已有文件。

做法：用 experiments.py 里同一套参数（场景“误会5%”，种子 1–20），打开 record_individuals 原样再跑一遍
（记录不消耗随机数，结果和已有文件完全一样）。导出之前逐项比对，有一处对不上就报错退出：
  - 20 个种子：每一代各打法占比 == results/main_误会5%.json 的 runs[].shares（和 stats_变狠.py 同一个比法）；
  - 种子 5：每一代各打法人数 == visual/pop_误会5%.json 的 counts；
  - 种子 5：300 个跟踪点每一代的打法 == visual/dots_误会5%.json 的 s；
  - 种子 5：变狠过 / 回到会原谅 等人数 == results/变狠统计.json 的 seed5。

输出（都是新文件，在 visual/ 下）：
  starters_误会5%.json   种子 5，开局是老实人的 500 人：每人每代打法、第一次变狠的代数、第 300 代的打法……
                         开场“变狠过 0→473”计数和结尾 473 人方块用
  history20_误会5%.json  20 个种子，每一代各打法人数。收尾 20 条历史条用
  crowd_误会5%.json      种子 5，1000 人每人每代的打法。远景点阵用（这样 1000 个点个个是真人，不用按总数补齐）

用法：cd 到本目录，/Users/decheng.huang/Documents/dy/.venv/bin/python export_变狠_画面.py
"""
import json
import os
from multiprocessing import Pool

import numpy as np

from sim import run
from experiments import make_cfg, SCENARIOS

HERE = os.path.dirname(os.path.abspath(__file__))
SCN = '误会5%'
SEEDS = list(range(1, 21))
SEED = 5
VIS = os.path.join(HERE, 'visual')
OUT_STARTERS = os.path.join(VIS, f'starters_{SCN}.json')
OUT_HIST = os.path.join(VIS, f'history20_{SCN}.json')
OUT_CROWD = os.path.join(VIS, f'crowd_{SCN}.json')


def one(seed):
    cfg = make_cfg(SCENARIOS[SCN], seed)
    cfg.record_individuals = True
    h = run(cfg)
    S = np.stack(h['strat']).astype(np.int8)   # 代 × 人
    return seed, h['strategies'], np.asarray(h['counts']), S, np.array(h['coop'])


def digits(row):
    return ''.join(str(int(v)) for v in row)


def main():
    for p in (OUT_STARTERS, OUT_HIST, OUT_CROWD):
        assert not os.path.exists(p), f'{p} 已存在，不覆盖。要重导先手动挪走'

    stored = json.load(open(os.path.join(HERE, 'results', f'main_{SCN}.json')))
    stored_sh = {r['seed']: np.array(r['shares']) for r in stored['runs']}
    pop = json.load(open(os.path.join(VIS, f'pop_{SCN}.json')))
    dots = json.load(open(os.path.join(VIS, f'dots_{SCN}.json')))
    stats = json.load(open(os.path.join(HERE, 'results', '变狠统计.json')))
    you_rec = json.load(open(os.path.join(VIS, f'you_{SCN}.json')))

    with Pool(8) as pool:
        res = pool.map(one, SEEDS, chunksize=1)
    res.sort(key=lambda r: r[0])

    # 1. 20 个种子逐代比对
    keys0 = res[0][1]
    for seed, keys, counts, S, coop in res:
        assert keys == keys0
        sh = counts / counts.sum(1, keepdims=True)
        ref = stored_sh[seed]
        assert ref.shape == sh.shape, (seed, ref.shape, sh.shape)
        assert np.abs(ref - np.round(sh, 3)).max() < 1e-9, f'种子 {seed} 和 results/main_{SCN}.json 的曲线对不上'
        # 逐人记录加起来要等于每代人数
        for g in range(S.shape[0]):
            assert (np.bincount(S[g], minlength=len(keys)) == counts[g]).all(), (seed, g)
    print(f'[对上] 20 个种子 × {res[0][3].shape[0]} 代，各打法占比和 results/main_{SCN}.json 逐代一致')

    seed, keys, counts, S, coop = next(r for r in res if r[0] == SEED)
    G = S.shape[0] - 1
    # 2. 种子 5：人数、跟踪点、合作率
    assert np.array_equal(counts, np.array(pop['counts'])), '种子 5 人数和 pop 对不上'
    ids = np.array(dots['ids'])
    assert np.array_equal(S[:, ids], np.array(dots['s'])), '种子 5 的 300 个跟踪点和 dots 对不上'
    # pop 里的合作率保留 4 位小数；0.66035 这类“正好一半”的数两种舍入法会差一个末位，所以按差不超过半个末位比
    assert np.abs(coop - np.array(pop['coop'])).max() <= 5e-5 + 1e-9, '合作率和 pop 对不上'
    you = you_rec['you_id']
    assert ids[dots['you_dot']] == you
    you_path = [you_rec['generations'][g]['strategy'] for g in range(G + 1)]
    assert [keys[v] for v in S[:, you]] == you_path, '“你”的每代打法和 you 对不上'
    print(f'[对上] 种子 {SEED}：每代人数 == pop；300 个跟踪点 == dots；合作率 == pop；第 {you} 号每代打法 == you')

    # 3. 500 个开局老实人
    iC, iD, iT, iG, iR = (keys.index(k) for k in ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM'])
    starters = np.nonzero(S[0] == iC)[0]
    sub = S[:, starters]
    harsh = (sub == iR) | (sub == iD)
    ever = harsh.any(0)
    first_harsh = np.where(ever, harsh.argmax(0), -1)
    last_harsh = np.where(ever, G - harsh[::-1].argmax(0), -1)
    n_grim = (sub == iR).sum(0)
    n_alld = (sub == iD).sum(0)
    harsh_main = np.where(~ever, -1, np.where(n_grim >= n_alld, iR, iD))
    end = sub[G]
    # 最后一次改学的那一代（之后一直是第 300 代的打法）
    end_since = np.zeros(len(starters), int)
    for k in range(len(starters)):
        col = sub[:, k]
        ch = np.nonzero(col != col[G])[0]
        end_since[k] = int(ch[-1] + 1) if len(ch) else 0
    ever_by_gen = [int((first_harsh[first_harsh >= 0] <= g).sum()) for g in range(G + 1)]

    s5 = stats['seed5']
    assert len(starters) == s5['n_starters']
    assert int(ever.sum()) == s5['ever_harsh']
    assert int((ever & (end == iG)).sum()) == s5['harsh_then_gtft']
    assert int((ever & (end == iT)).sum()) == s5['harsh_then_tft']
    assert int((end == iG).sum()) == s5['end_gtft'] and int((end == iT).sum()) == s5['end_tft']
    assert int(((end == iR) | (end == iD)).sum()) == s5['end_harsh'] == 0
    last_new = int(first_harsh.max())
    print(f'[对上] 开局老实人 {len(starters)}，变狠过 {int(ever.sum())}，其中第 {G} 代会原谅 {int((ever & (end == iG)).sum())}、'
          f'以牙还牙 {int((ever & (end == iT)).sum())}，还狠着 0；最后一个新变狠的在第 {last_new} 代；和 results/变狠统计.json 一致')

    legend = pop['strategies']
    you_k = int(np.nonzero(starters == you)[0][0])
    st = dict(
        scenario=SCN, seed=SEED, strategies=legend,
        note=('开局是老实人（ALLC）的 500 人。ids[k] = 第 k 人在 1000 人里的编号；s[g] 是第 g 代这 500 人的打法，'
              '一个字一个人，字 = strategies.index。“变狠”= 当记仇（GRIM）或骗子（ALLD）。'
              'first_harsh_gen / last_harsh_gen：第一次 / 最后一次当狠人的那一代，没变狠过 = -1；harsh_gens：当狠人的代数；'
              'harsh_main：狠的时候主要是哪一种（记仇和骗子代数一样多时算记仇），没变狠过 = -1；'
              'end：第 300 代的打法；end_since：从第几代起一直是 end；ever_harsh_by_gen[g]：到第 g 代为止变狠过的人数（开场计数用）'),
        check='已核对：每代人数 == pop；300 个跟踪点 == dots；变狠过 473、回到会原谅 428 == results/变狠统计.json seed5',
        ids=starters.tolist(), you_id=int(you), you_index=you_k,
        ever_harsh=int(ever.sum()), harsh_then_gtft=int((ever & (end == iG)).sum()),
        harsh_then_tft=int((ever & (end == iT)).sum()), last_new_harsh_gen=last_new,
        first_harsh_gen=first_harsh.tolist(), last_harsh_gen=last_harsh.tolist(),
        harsh_gens=harsh.sum(0).tolist(), harsh_main=harsh_main.tolist(),
        end=end.tolist(), end_since=end_since.tolist(),
        ever_harsh_by_gen=ever_by_gen,
        s=[digits(sub[g]) for g in range(G + 1)],
    )
    json.dump(st, open(OUT_STARTERS, 'w'), ensure_ascii=False, separators=(',', ':'))

    hist = dict(
        scenario=SCN, seeds=SEEDS, strategies=legend, n=int(counts[0].sum()), gens=G,
        note='counts[i][g][j] = 第 i 个种子（seeds[i]）第 g 代用第 j 种打法的人数（j = strategies.index）',
        check=f'已核对：20 个种子逐代各打法占比 == results/main_{SCN}.json',
        counts=[r[2].astype(int).tolist() for r in res],
    )
    json.dump(hist, open(OUT_HIST, 'w'), ensure_ascii=False, separators=(',', ':'))

    crowd = dict(
        scenario=SCN, seed=SEED, strategies=legend, n=int(S.shape[1]), you_id=int(you),
        note='s[g] 是第 g 代 1000 人的打法，第 i 个字是第 i 号人（字 = strategies.index）',
        check='已核对：每代人数 == pop counts；dots 里的 300 个跟踪点逐代一致',
        s=[digits(S[g]) for g in range(G + 1)],
    )
    json.dump(crowd, open(OUT_CROWD, 'w'), ensure_ascii=False, separators=(',', ':'))
    for p in (OUT_STARTERS, OUT_HIST, OUT_CROWD):
        print('写出', os.path.relpath(p, HERE), f'{os.path.getsize(p) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
