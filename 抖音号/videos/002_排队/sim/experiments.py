"""跑全部场景，写 results/summary.json、results/curves.json、results/结果表.md。

用法：python experiments.py        （8 核机器约 1 分钟）
"""
import json
import math
import os
import zlib

import numpy as np

from sim import (H, I, S, simulate, dp_basic, dp_identified, wrong_cascade_limit, bhw_eq3,
                 independent_majority, all_speak_last_wrong, wilson, lam_of, dp_from)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')
N = 100          # 一条队的人数
R = 200_000      # 每个场景重复多少条队
R_SWEEP = 50_000


def seed_of(name):
    return zlib.crc32(name.encode('utf-8'))


def rate(mask):
    k, n = int(mask.sum()), int(mask.size)
    lo, hi = wilson(k, n)
    return {'rate': k / n, 'ci95': [lo, hi], 'k': k, 'n': n}


def q_of(arr, qs=(0.1, 0.5, 0.9)):
    return [float(np.quantile(arr, q)) for q in qs]


def first_true(mask):
    """每行第一个 True 的位置（1 起算）；没有则 = 列数 + 1。"""
    has = mask.any(axis=1)
    idx = mask.argmax(axis=1) + 1
    return np.where(has, idx, mask.shape[1] + 1)


def basic_metrics(r, tie):
    p, n = r['p'], r['n']
    T, sig, ch, lk = r['T'], r['sig'], r['choice'], r['locked']
    wrong = ch != T[:, None]
    nwrong = wrong.sum(1)
    out = {}
    out['last_wrong'] = rate(wrong[:, -1])
    out['majority_wrong'] = rate(nwrong > n / 2)
    out['half_half'] = rate(nwrong == n / 2)
    out['mean_wrong_per_person'] = float(wrong.mean())
    dpw, _ = dp_basic(p, n, tie)
    out['analytic_last_wrong'] = float(dpw[-1])
    out['analytic_limit'] = wrong_cascade_limit(p, tie)
    out['analytic_mean_wrong_per_person'] = float(dpw.mean())

    # 锁死
    lock = first_true(lk)
    out['lock'] = {
        'p_at_3': float((lock == 3).mean()),
        'p_le_3': float((lock <= 3).mean()),
        'p_le_5': float((lock <= 5).mean()),
        'p_le_9': float((lock <= 9).mean()),
        'p_never_by_n': float((lock > n).mean()),
        'mean': float(lock[lock <= n].mean()),
        'median': float(np.median(lock[lock <= n])),
        'q10_50_90': q_of(lock[lock <= n]),
    }
    if tie == 'own':
        qq = p * p + (1 - p) ** 2
        out['lock']['analytic_p_at_3'] = qq
        out['lock']['analytic_mean'] = 1 + 2 / qq
    else:
        qq = 1 - p * (1 - p)
        out['lock']['analytic_p_at_3'] = qq
        out['lock']['analytic_mean'] = 1 + 2 / qq
    # 锁死前用了自己信号的人数（= 公开出来的信号条数）
    informative = (~lk).sum(1)
    out['informative_people'] = {'mean': float(informative[lock <= n].mean()),
                                 'q10_50_90': q_of(informative[lock <= n])}

    # 锁死以后：信号说"隔壁好"（≠ 自己的选择）的人
    contrary = lk & (sig != ch)
    n_locked = lk.sum(1)
    n_contrary = contrary.sum(1)
    final_wrong = wrong[:, -1]
    out['after_lock'] = {
        'locked_people_mean': float(n_locked.mean()),
        'contrary_mean': float(n_contrary.mean()),
        'contrary_share_of_locked': float(n_contrary.sum() / n_locked.sum()),
        'contrary_followed_share': 1.0,  # 定义上：锁死的人全都跟队
        'in_wrong_queues': {
            'locked_mean': float(n_locked[final_wrong].mean()),
            'contrary_mean': float(n_contrary[final_wrong].mean()),
            'contrary_share': float(n_contrary[final_wrong].sum() / n_locked[final_wrong].sum()),
        },
        'in_right_queues': {
            'locked_mean': float(n_locked[~final_wrong].mean()),
            'contrary_mean': float(n_contrary[~final_wrong].mean()),
            'contrary_share': float(n_contrary[~final_wrong].sum() / n_locked[~final_wrong].sum()),
        },
    }
    # 排错的队（第 100 人在错店）里：100 人中，信号其实指向好吃那家的人数；其中站在错店的人数
    right_sig = (sig == T[:, None])
    n_right_sig = right_sig.sum(1)
    stuck = (right_sig & wrong).sum(1)   # 朋友说对了、人却站在错店
    wq = final_wrong
    aw = (nwrong == n)
    out['wrong_queue_people_with_right_signal'] = {
        'mean': float(n_right_sig[wq].mean()),
        'q10_50_90': q_of(n_right_sig[wq]),
        'share_queues_where_majority_had_right_signal': float((n_right_sig[wq] > n / 2).mean()),
        'right_signal_but_at_wrong_shop_mean': float(stuck[wq].mean()),
        'right_signal_but_at_wrong_shop_q10_50_90': q_of(stuck[wq]),
        'people_at_wrong_shop_mean': float(nwrong[wq].mean()),
        'queues_all_100_wrong_share_of_all': float(aw.mean()),
        'queues_all_100_wrong_share_of_wrong': float(aw[wq].mean()),
    }
    # 队有多长 vs 可不可信：前 k 人全选同一家时，那家真好吃的概率
    rel = {}
    for k in (1, 2, 3, 5, 10, 20, 50, 100):
        same = (ch[:, :k] == ch[:, :1]).all(1)
        good = ch[:, 0] == T
        rel[str(k)] = {'share_of_queues': float(same.mean()),
                       'p_right': float(good[same].mean()),
                       'ci95': list(wilson(int(good[same].sum()), int(same.sum())))}
    out['first_k_same_reliability'] = rel
    # 锁死时，一个信号说"隔壁好"的看队的人，自己算出来队里那家好吃的概率
    if 'L' in r:
        L = r['L'].astype(np.float64)
        lam = lam_of(p)
        post = 1 / (1 + np.exp(-(np.abs(L) - lam)))
        post = post[contrary]
        out['contrary_follower_belief'] = {'mean': float(post.mean()), 'min': float(post.min()),
                                           'max': float(post.max())}
    return out


def breaking_metrics(r, label, dp=None):
    n = r['n']
    T, sig, ch, sched, hid, lk = r['T'], r['sig'], r['choice'], r['sched'], r['hidden'], r['locked']
    wrong = ch != T[:, None]
    nwrong = wrong.sum(1)
    special = np.zeros_like(wrong)
    special[:, sched != H] = True
    special |= hid
    herd = ~special
    out = {'label': label,
           'last_wrong': rate(wrong[:, -1]),
           'majority_wrong': rate(nwrong > n / 2),
           'mean_wrong_all': float(wrong.mean()),
           'mean_wrong_herders': float(wrong[herd].mean()),
           'mean_wrong_special': float(wrong[special].mean()) if special.any() else None,
           'special_share': float(special.mean())}
    if dp is not None:
        out['analytic_last_wrong'] = float(dp[-1])
    contrary = herd & lk & (sig != ch)
    out['contrary_locked_followers_mean'] = float(contrary.sum(1).mean())
    return out


def per_position(r):
    return (r['choice'] != r['T'][:, None]).mean(0).tolist()


def sched_every(k, n=N, typ=I):
    s = np.zeros(n, dtype=np.int8)
    s[k - 1::k] = typ
    s[n - 1] = H
    return s


def main():
    os.makedirs(RES, exist_ok=True)
    summary = {'N': N, 'R': R, 'note': '所有比例来自 R 条独立的队；ci95 = Wilson 95% 区间。'}
    curves = {}

    # ---------- 1. 基础：p = 0.6 / 0.7 / 0.8，两种平局规则 ----------
    base = {}
    for tie in ('own', 'coin'):
        for p in (0.6, 0.7, 0.8):
            name = f'base_{tie}_{p}'
            r = simulate(p, N, R, seed_of(name), tie=tie, record_L=True)
            m = basic_metrics(r, tie)
            # 对照：每人只听自己
            # 只听自己时，每人的选择 = 他的信号（simulate 会把第 N 人强制成看队的人，所以这里直接数信号）
            rc = simulate(p, N, R, seed_of('indep_' + name), schedule=np.full(N, I, np.int8))
            nw = (rc['sig'] != rc['T'][:, None]).sum(1)
            gt, eq, lt = independent_majority(p, N)
            m['control_independent'] = {
                'majority_right': rate(nw < N / 2), 'tie_50_50': rate(nw == N / 2),
                'majority_wrong': rate(nw > N / 2),
                'analytic_majority_right': gt, 'analytic_tie': eq, 'analytic_majority_wrong': lt,
                'mean_wrong_per_person': 1 - p,
            }
            m['all_speak_analytic_last_wrong'] = all_speak_last_wrong(p, N)
            base[name] = m
            if tie == 'own' and p == 0.6:
                curves['base_own_0.6'] = per_position(r)
            del r, rc
            print(name, 'last_wrong=%.4f (analytic %.4f)' % (m['last_wrong']['rate'], m['analytic_last_wrong']))
    summary['base'] = base

    # BHW 式 (3) 核对（n=100）
    summary['bhw_eq3_check'] = {str(p): dict(zip(('correct', 'none', 'wrong'), bhw_eq3(p, N))) for p in (0.6, 0.7, 0.8)}

    # ---------- 2. 队长敏感性 ----------
    qlen = {}
    for p in (0.6, 0.7):
        for n in (10, 20, 50, 100, 1000):
            dpw, _ = dp_basic(p, n, 'own')
            qlen[f'{p}_{n}'] = float(dpw[-1])
    summary['queue_length_analytic_last_wrong'] = qlen

    # ---------- 3. p 扫描（画图用） ----------
    sweep = []
    for p in [round(x, 2) for x in np.arange(0.55, 0.951, 0.05)]:
        row = {'p': p}
        for tie in ('own', 'coin'):
            r = simulate(p, N, R_SWEEP, seed_of(f'sweep_{tie}_{p}'), tie=tie)
            row[f'sim_{tie}'] = rate(r['choice'][:, -1] != r['T'])
            row[f'analytic_{tie}'] = float(dp_basic(p, N, tie)[0][-1])
        gt, eq, lt = independent_majority(p, N)
        row['independent_majority_wrong'] = lt
        row['independent_majority_wrong_or_tie'] = lt + eq
        row['all_speak_last_wrong'] = all_speak_last_wrong(p, N)
        sweep.append(row)
    summary['sweep'] = sweep
    print('sweep done')

    # ---------- 4. 能不能打破 ----------
    brk = {}
    for p in (0.6, 0.7):
        rows = []
        r = simulate(p, N, R, seed_of(f'brk_base_{p}'))
        rows.append(breaking_metrics(r, '基准：全是看队的人', dp_basic(p, N)[0]))
        for k in (10, 5, 3, 2):
            sc = sched_every(k, typ=I)
            r = simulate(p, N, R, seed_of(f'brk_I{k}_{p}'), schedule=sc)
            rows.append(breaking_metrics(r, f'每 {k} 人有 1 个只听自己的人（大家知道他不看队）', dp_identified(p, N, sc)))
            if p == 0.6 and k in (10, 5):
                curves[f'I{k}_0.6'] = per_position(r)
        for k in (10, 5, 1):
            sc = sched_every(k, typ=S)
            r = simulate(p, N, R, seed_of(f'brk_S{k}_{p}'), schedule=sc)
            lab = '每个人都把朋友的话说出来' if k == 1 else f'每 {k} 人有 1 个把朋友的话说出来（照样跟队）'
            rows.append(breaking_metrics(r, lab, dp_identified(p, N, sc)))
            if p == 0.6 and k == 1:
                curves['S1_0.6'] = per_position(r)
        for q in (0.1, 0.25, 0.5):
            r = simulate(p, N, R, seed_of(f'brk_hid{q}_{p}'), q_hidden=q)
            rows.append(breaking_metrics(r, f'{int(q * 100)}% 的人只听自己，但认不出是谁；看队的人会算'))
            if p == 0.6 and q == 0.25:
                curves['hid25_bayes_0.6'] = per_position(r)
        for q in (0.1, 0.25, 0.5):
            r = simulate(p, N, R, seed_of(f'brk_naive{q}_{p}'), q_hidden=q, observer='naive')
            rows.append(breaking_metrics(r, f'{int(q * 100)}% 的人只听自己；看队的人只数人头'))
            if p == 0.6 and q == 0.25:
                curves['hid25_naive_0.6'] = per_position(r)
        brk[str(p)] = rows
        print('breaking', p, 'done')
    summary['breaking'] = brk

    # 更长的队（1000 人）：打破的效果会不会继续变好
    long = []
    p = 0.6
    for lab, kw in [('基准', {}), ('每 5 人 1 个只听自己（认得出）', {'schedule': sched_every(5, 1000, I)}),
                    ('25% 只听自己，认不出，看队的人会算', {'q_hidden': 0.25}),
                    ('25% 只听自己，看队的人只数人头', {'q_hidden': 0.25, 'observer': 'naive'})]:
        r = simulate(p, 1000, 40_000, seed_of('long_' + lab), probe=[99], **kw)
        w = r['choice'] != r['T'][:, None]
        long.append({'label': lab, 'wrong_at_100': rate(w[:, 99]), 'wrong_at_1000': rate(w[:, -1])})
    summary['long_queue_0.6'] = long

    # ---------- 4b. “你”一个人：跟着排、说出来、走到空的那家 ----------
    summary['you_decision'] = you_decision()

    # ---------- 5. 20 条队一组：排错的有几条 ----------
    r = simulate(0.6, N, R, seed_of('base_own_0.6_batches'))
    w = (r['choice'][:, -1] != r['T']).reshape(-1, 20).sum(1)
    summary['batches_of_20_p0.6'] = {
        'mean': float(w.mean()), 'q10_50_90': q_of(w),
        'p_at_least_3': float((w >= 3).mean()), 'p_between_4_and_8': float(((w >= 4) & (w <= 8)).mean()),
        'n_batches': int(w.size)}

    with open(os.path.join(RES, 'summary.json'), 'w') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    with open(os.path.join(RES, 'curves.json'), 'w') as f:
        json.dump({'note': '每个位置上的人排错的概率（p=0.6，平局听自己，20 万条队）', 'curves': curves},
                  f, ensure_ascii=False)
    write_tables(summary)


def you_decision(p=0.6, pos=7, n=N):
    """你排第 pos 个；队已经锁死（公开净信号 = 2 条）；你的信号说隔壁好。
    三种做法：A 闷声跟着排；B 跟着排，但把朋友的话说出来；C 走到空的那家，并且大家知道你不看队。
    B 和 C 对后面的人效果一样（都把你的信号公开了），区别只在你自己。"""
    m = n - pos
    p_wrong = 1 - p                      # 按你知道的，队排错的概率
    r_sil_w, lw_sil_w = dp_from(p, -2, m)
    r_sil_r, lw_sil_r = dp_from(p, 2, m)
    r_spk_w, lw_spk_w = dp_from(p, -1, m)  # 队错：你的（对的）信号让净数变成 -1
    r_spk_r, lw_spk_r = dp_from(p, 1, m)   # 队对：你的（错的）信号让净数变成 +1
    out = {
        'p': p, 'pos': pos, 'behind': m,
        'your_belief_queue_right': p,
        'A_silent': {'you_right': p,
                     'behind_right_mean': p_wrong * r_sil_w + p * r_sil_r,
                     'last_wrong': p_wrong * lw_sil_w + p * lw_sil_r},
        'B_speak_and_queue': {'you_right': p,
                              'behind_right_mean': p_wrong * r_spk_w + p * r_spk_r,
                              'last_wrong': p_wrong * lw_spk_w + p * lw_spk_r},
        'C_go_empty_visible': {'you_right': 1 - p,
                               'behind_right_mean': p_wrong * r_spk_w + p * r_spk_r,
                               'last_wrong': p_wrong * lw_spk_w + p * lw_spk_r},
        'if_queue_really_wrong': {'silent_last_wrong': lw_sil_w, 'speak_last_wrong': lw_spk_w,
                                  'silent_behind_right': r_sil_w, 'speak_behind_right': r_spk_w},
        'if_queue_really_right': {'silent_last_wrong': lw_sil_r, 'speak_last_wrong': lw_spk_r,
                                  'silent_behind_right': r_sil_r, 'speak_behind_right': r_spk_r},
    }
    # 仿真复核：第 pos 人是"说出来的人"vs 普通看队的人，只看"锁死且他信号相反"的那些队
    for lab, sc in (('mc_silent', None), ('mc_speak', 'S')):
        sched = np.zeros(n, dtype=np.int8)
        if sc:
            sched[pos - 1] = S
        r = simulate(p, n, 400_000, seed_of('you_' + lab), schedule=sched)
        T, sig, ch, lk = r['T'], r['sig'], r['choice'], r['locked']
        sel = lk[:, pos - 1] & (sig[:, pos - 1] != ch[:, pos - 1])
        wr = ch != T[:, None]
        out[lab] = {'n_selected': int(sel.sum()),
                    'queue_wrong_share': float(wr[sel, pos - 1].mean()),
                    'behind_right_mean': float((~wr[sel, pos:]).sum(1).mean()),
                    'last_wrong': rate(wr[sel, -1])}
    return out


def pct(x, d=1):
    return f'{x * 100:.{d}f}%'


def ci(r, d=1):
    return f"{pct(r['rate'], d)}（{pct(r['ci95'][0], d)}–{pct(r['ci95'][1], d)}）"


def write_tables(s):
    L = ['# 结果表（experiments.py 自动生成）', '',
         f"每个场景 {s['R']:,} 条队，每条 {s['N']} 人。括号里是 95% 区间。", '']
    L += ['## 基础模型', '',
          '| p | 平局 | 第 100 人排错 | 解析解 | 多数人排错 | 对照：只听自己时多数人选错（含 50:50 平） | 都说出来时第 100 人排错 |',
          '|---|---|---|---|---|---|---|']
    for name, m in s['base'].items():
        _, tie, p = name.split('_')
        c = m['control_independent']
        L.append(f"| {p} | {'听自己' if tie == 'own' else '抛硬币'} | {ci(m['last_wrong'])} | {pct(m['analytic_last_wrong'])} "
                 f"| {ci(m['majority_wrong'])} | {pct(c['analytic_majority_wrong'], 2)}（平 {pct(c['analytic_tie'], 2)}） "
                 f"| {pct(m['all_speak_analytic_last_wrong'], 2)} |")
    L += ['', '## 锁死', '',
          '| p | 平局 | 第 3 人就锁死 | 解析 | 第 5 人前锁死 | 平均第几人锁死 | 解析 | 锁死前用了自己信号的人（平均） |',
          '|---|---|---|---|---|---|---|---|']
    for name, m in s['base'].items():
        _, tie, p = name.split('_')
        k = m['lock']
        L.append(f"| {p} | {'听自己' if tie == 'own' else '抛硬币'} | {pct(k['p_at_3'])} | {pct(k['analytic_p_at_3'])} | {pct(k['p_le_5'])} "
                 f"| {k['mean']:.2f} | {k['analytic_mean']:.2f} | {m['informative_people']['mean']:.2f} |")
    L += ['', '## 锁死以后', '',
          '| p | 平局 | 锁死后的人（平均） | 其中信号说隔壁好（全都跟着排了） | 占比 | 排错的队里占比 | 排对的队里占比 |',
          '|---|---|---|---|---|---|---|']
    for name, m in s['base'].items():
        _, tie, p = name.split('_')
        a = m['after_lock']
        L.append(f"| {p} | {'听自己' if tie == 'own' else '抛硬币'} | {a['locked_people_mean']:.1f} | {a['contrary_mean']:.1f} "
                 f"| {pct(a['contrary_share_of_locked'])} | {pct(a['in_wrong_queues']['contrary_share'])} "
                 f"| {pct(a['in_right_queues']['contrary_share'])} |")
    L += ['', '## 排错的队（第 100 人在错店）里，朋友其实说对了的人', '',
          '| p | 平局 | 100 人里信号其实对的（平均，10–90%） | 其中站在错店的 | 这种队里多数人信号是对的 | 排错的队里 100 人全错的占比 |',
          '|---|---|---|---|---|---|']
    for name, m in s['base'].items():
        _, tie, p = name.split('_')
        wq = m['wrong_queue_people_with_right_signal']
        L.append(f"| {p} | {'听自己' if tie == 'own' else '抛硬币'} | {wq['mean']:.1f}（{wq['q10_50_90'][0]:.0f}–{wq['q10_50_90'][2]:.0f}） "
                 f"| {wq['right_signal_but_at_wrong_shop_mean']:.1f} | {pct(wq['share_queues_where_majority_had_right_signal'])} "
                 f"| {pct(wq['queues_all_100_wrong_share_of_wrong'])} |")
    y = s['you_decision']
    L += ['', f"## “你”排第 {y['pos']} 个，队已锁死，你的信号说隔壁好（p={y['p']}，精确递推；后面还有 {y['behind']} 人）", '',
          '| 做法 | 你自己吃对 | 你后面的人平均几人吃对 | 第 100 人排错 |', '|---|---|---|---|']
    for k, lab in (('A_silent', '闷声跟着排'), ('B_speak_and_queue', '跟着排，但把朋友的话说出来'),
                   ('C_go_empty_visible', '走到空的那家（大家知道你不看队）')):
        L.append(f"| {lab} | {pct(y[k]['you_right'])} | {y[k]['behind_right_mean']:.1f} | {pct(y[k]['last_wrong'])} |")
    L += ['', f"- 仿真复核（40 万条队里挑出符合条件的）：闷声 第 100 人排错 {ci(y['mc_silent']['last_wrong'])}，后面平均 {y['mc_silent']['behind_right_mean']:.1f} 人吃对；"
          f"说出来 {ci(y['mc_speak']['last_wrong'])}，{y['mc_speak']['behind_right_mean']:.1f} 人。",
          f"- 如果这条队真的排错了：闷声时第 100 人 100% 错；你说出来，降到 {pct(y['if_queue_really_wrong']['speak_last_wrong'])}（有 {pct(1 - y['if_queue_really_wrong']['speak_last_wrong'])} 的机会被掰回来）。",
          f"- 如果这条队其实是对的：你说出来，有 {pct(y['if_queue_really_right']['speak_last_wrong'])} 的机会把它带偏。"]
    L += ['', '## 队有多长 vs 可不可信（平局听自己）', '',
          '| p | 前 1 人 | 前 2 人同一家 | 前 3 人 | 前 10 人 | 前 100 人 |', '|---|---|---|---|---|---|']
    for p in ('0.6', '0.7', '0.8'):
        rel = s['base'][f'base_own_{p}']['first_k_same_reliability']
        L.append(f"| {p} | " + ' | '.join(pct(rel[k]['p_right']) for k in ('1', '2', '3', '10', '100')) + ' |')
    L += ['', '## 能不能打破（第 100 人永远是看队的人）', '']
    for p, rows in s['breaking'].items():
        L += [f'### p = {p}', '',
              '| 做法 | 第 100 人排错 | 精确递推 | 多数人排错 | 看队的人平均选错 | 那些特别的人自己选错 |',
              '|---|---|---|---|---|---|']
        for r_ in rows:
            an = pct(r_['analytic_last_wrong']) if 'analytic_last_wrong' in r_ else '—'
            sp = pct(r_['mean_wrong_special']) if r_['mean_wrong_special'] is not None else '—'
            L.append(f"| {r_['label']} | {ci(r_['last_wrong'])} | {an} | {ci(r_['majority_wrong'])} "
                     f"| {pct(r_['mean_wrong_herders'])} | {sp} |")
        L.append('')
    L += ['### 更长的队（p=0.6，4 万条队）', '', '| 做法 | 第 100 人排错 | 第 1000 人排错 |', '|---|---|---|']
    for r_ in s['long_queue_0.6']:
        L.append(f"| {r_['label']} | {ci(r_['wrong_at_100'])} | {ci(r_['wrong_at_1000'])} |")
    b = s['batches_of_20_p0.6']
    L += ['', '## 20 条队一组（p=0.6）', '',
          f"- 平均 {b['mean']:.1f} 条排错；10%/50%/90% 分位：{b['q10_50_90']}；4–8 条的概率 {pct(b['p_between_4_and_8'])}。"]
    with open(os.path.join(RES, '结果表.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
