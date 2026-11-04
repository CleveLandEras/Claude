"""汇总 experiments.py 的结果：主场景多种子统计、代表性种子、敏感性表。

输出：results/summary.json，results/敏感性.md
"""
import json
import os
from collections import Counter

import numpy as np

from sim import STRATS

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')
NAME = {k: v['name'] for k, v in STRATS.items()}
NAME['WSLS'] = 'Pavlov'

STEPS = ['1a_老实人减半', '1b_老实人被骗光', '2_骗子变多', '3_以牙还牙起来_骗子消失', '4_宽容赢过以牙还牙',
         'x_记仇一度过三成', 'x_Pavlov赢', 'x_没有赢家过半']


def load_main(name):
    return json.load(open(os.path.join(RES, f'main_{name}.json')))


def representative(runs):
    """离各种子中位数最近的那一次（按终局各策略比例 + 骗子峰值 + 老实人最低点 + 几个关键代数）。"""
    keys = runs[0]['strategies']

    def vec(m):
        v = [m['final'][k] for k in keys]
        v += [m.get('alld_peak', 0), m.get('allc_min', 0), m.get('grim_peak', 0)]
        v += [m.get('alld_peak_gen', 0) / 100, (m.get('tft_peak_gen') or 0) / 100]
        return np.array(v)

    V = np.stack([vec(r['metrics']) for r in runs])
    med = np.median(V, 0)
    d = np.abs(V - med).sum(1)
    i = int(np.argmin(d))
    return runs[i]['seed'], i


def agg(ms):
    out = {}
    st = [m['story'] for m in ms]
    out['steps'] = {k: round(np.mean([s[k] for s in st]), 2) for k in STEPS if k in st[0]}
    out['winners'] = dict(Counter(m['winner'] for m in ms).most_common())
    for key in ['alld_peak', 'alld_peak_gen', 'allc_min', 'allc_final', 'grim_peak', 'tft_peak_after', 'tft_final',
                'gtft_final', 'wsls_final', 'coop_final', 'alld_final', 'winner_share', 'allc_gone_gen', 'alld_gone_gen']:
        vals = [m.get(key) for m in ms]
        vals = [v for v in vals if v is not None]
        if vals:
            out[key] = dict(med=round(float(np.median(vals)), 3), lo=round(float(np.min(vals)), 3),
                            hi=round(float(np.max(vals)), 3), n=len(vals))
    return out


def winner_str(w, n):
    return '、'.join(f'{NAME.get(k, k)} {v}/{n}' for k, v in w.items())


def pct(x):
    return f'{x * 100:.0f}%'


def main():
    summary = dict(main={}, sweep={})
    for name in ['无误会', '误会5%', '转折_第100代起误会5%']:
        d = load_main(name)
        ms = [r['metrics'] for r in d['runs']]
        a = agg(ms)
        seed, i = representative(d['runs'])
        a['representative_seed'] = seed
        a['representative_metrics'] = d['runs'][i]['metrics']
        a['n_seeds'] = len(ms)
        summary['main'][name] = a
    raw = json.load(open(os.path.join(RES, 'sweep_raw.json')))
    for k, rs in raw.items():
        summary['sweep'][k] = agg([r['metrics'] for r in rs])
        summary['sweep'][k]['n_seeds'] = len(rs)
    json.dump(summary, open(os.path.join(RES, 'summary.json'), 'w'), ensure_ascii=False, indent=1)

    # 敏感性表（markdown）
    from experiments import VARIANTS, NOISE_VARIANTS
    lines = ['# 参数敏感性', '',
             '每格 10 个种子。“情节”一栏：①老实人被骗光（跌破 1%）②骗子变多（峰值 ≥ 初始 1.5 倍）'
             '③以牙还牙起来、骗子消失 ④宽容的赢过以牙还牙（且是第一）。数字 = 10 次里成立几次。', '',
             '| 分组 | 变体 | 误会 | ① | ② | ③ | ④ | 骗子峰值（中位） | 终局第一（次数） |',
             '|---|---|---|---|---|---|---|---|---|']

    def row(grp, label, e, a):
        st = a['steps']
        n = a['n_seeds']
        f = lambda k: str(round(st.get(k, 0) * n)) if k in st else '–'
        pk = pct(a['alld_peak']['med']) if 'alld_peak' in a else '–'
        return (f'| {grp} | {label} | {pct(e)} | {f("1b_老实人被骗光")} | {f("2_骗子变多")} | '
                f'{f("3_以牙还牙起来_骗子消失")} | {f("4_宽容赢过以牙还牙")} | {pk} | {winner_str(a["winners"], n)} |')

    # 基准行：用主场景前 10 个种子
    for name, e in [('无误会', 0.0), ('误会5%', 0.05)]:
        d = load_main(name)
        a = agg([r['metrics'] for r in d['runs'][:10]])
        a['n_seeds'] = 10
        lines.append(row('基准', 'N=1000，K=10，n=200，老实人 50%', e, a))
    for grp, label, over in VARIANTS:
        for e in (0.0, 0.05):
            k = f'{grp}|{label}|{e}'
            lines.append(row(grp, label, e, summary['sweep'][k]))
    for grp, label, over in NOISE_VARIANTS:
        e = over.get('e', 0.0)
        k = f'{grp}|{label}|{e}'
        lines.append(row(grp, label, over.get('e', over.get('e_perc', 0)), summary['sweep'][k]))
    open(os.path.join(RES, '敏感性.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    for name, a in summary['main'].items():
        print('\n==', name, 'seeds', a['n_seeds'], 'rep seed', a['representative_seed'])
        print(' steps', a['steps'])
        print(' winners', a['winners'])
        for key in ['alld_peak', 'alld_peak_gen', 'allc_min', 'allc_gone_gen', 'grim_peak', 'tft_peak_after', 'tft_final',
                    'gtft_final', 'wsls_final', 'coop_final', 'alld_gone_gen']:
            if key in a:
                print(' ', key, a[key])


if __name__ == '__main__':
    main()
