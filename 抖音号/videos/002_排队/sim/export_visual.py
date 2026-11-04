"""给画面用的数据（p=0.6，平局听自己，100 人一条队）。

输出（visual/ 目录）：
  queue_排错.json   一次排错店的完整队列（含“你”= 第 7 人）
  queue_排对.json   一次排对的完整队列（同样挑第 7 人当“你”，信号同样说隔壁好）
  you.json          “你”那一段：你前面的人、你的信号、你怎么算的、你后面的人、三种做法的后果
  queues_20.json    20 条队：每条每人的信号和选择、最后排在哪家、对错
  summary.json      画面要用的汇总数（从 results/summary.json 摘出来）

挑选规则（写死在代码里，不按好看挑）：
  排错的队：在 2 万条队里，找“第 3 人就锁死（最常见）、第 7 人的信号说隔壁好、最后排错”的队；
            再按“第 3–6 人里信号说隔壁好的人数”和“100 人里信号其实对的人数”离这组队的平均最近来挑，
            并列取种子顺序第一条。
  排对的队：同样的条件，只是最后排对。
  20 条队：从第 0 组起，每组 20 条（种子不同），取第一组“排错条数 = 中位数 6”的。
"""
import json
import math
import os

import numpy as np

from sim import simulate, lam_of, dp_from
from experiments import seed_of

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'visual')
P, N, YOU = 0.6, 100, 7
NAMES = ['A', 'B']
COLORS = {  # 配色：好吃的那家 / 不好吃的那家（plots.py 里校验过对比度）
    'right_shop': {'light': '#2a78d6', 'dark': '#3987e5'},
    'wrong_shop': {'light': '#eb6834', 'dark': '#d95926'},
}


def queue_record(r, j):
    T = int(r['T'][j])
    sig, ch, lk, L = r['sig'][j], r['choice'][j], r['locked'][j], r['L'][j].astype(float)
    lam = lam_of(P)
    people = []
    for i in range(N):
        d = int(round(L[i] / lam))  # 公开的净信号数（正 = A 多）
        own = 1 if sig[i] == 0 else -1
        post_A = 1 / (1 + math.exp(-(L[i] + own * lam)))
        people.append({
            'i': i + 1,
            'signal': NAMES[sig[i]],                  # 朋友说哪家好吃
            'choice': NAMES[ch[i]],                   # 他排了哪家
            'signal_right': bool(sig[i] == T),        # 朋友说对了没有
            'choice_right': bool(ch[i] == T),
            'locked': bool(lk[i]),                    # 他来的时候队已锁死（他的信号改变不了他的选择）
            'used_own_signal': bool(not lk[i]),       # 他的选择透露了他的信号
            'signal_vs_choice': 'same' if sig[i] == ch[i] else 'other',
            'public_net_signals_before': d,           # 他来之前，前面人的选择透露出的净信号数（A 为正）
            'his_belief_A_better': round(post_A, 4),  # 他按自己知道的，算出 A 更好吃的概率
        })
    lock_at = next((p['i'] for p in people if p['locked']), None)
    return {
        'p': P, 'tie_rule': '平局听自己', 'n': N,
        'better_shop': NAMES[T], 'final_shop': NAMES[ch[-1]], 'final_right': bool(ch[-1] == T),
        'lock_at': lock_at,
        'n_used_own_signal': int((~lk).sum()),
        'n_signal_right': int((sig == T).sum()),
        'n_at_right_shop': int((ch == T).sum()),
        'n_signal_right_but_at_wrong_shop': int(((sig == T) & (ch != T)).sum()),
        'n_locked_signal_other': int((lk & (sig != ch)).sum()),
        'people': people,
    }


def pick(r, final_right):
    T, sig, ch, lk = r['T'], r['sig'], r['choice'], r['locked']
    lock = np.where(lk.any(1), lk.argmax(1) + 1, N + 1)
    ok = (lock == 3) & (sig[:, YOU - 1] != ch[:, YOU - 1]) & ((ch[:, -1] == T) == final_right)
    other_36 = (sig[:, 2:6] != ch[:, 2:6]).sum(1)          # 第 3–6 人里信号说隔壁好的
    right_sig = (sig == T[:, None]).sum(1)                   # 100 人里信号其实对的
    idx = np.flatnonzero(ok)
    m1, m2 = other_36[idx].mean(), right_sig[idx].mean()
    dist = np.abs(other_36[idx] - m1) / max(other_36[idx].std(), 1e-9) + np.abs(right_sig[idx] - m2) / max(right_sig[idx].std(), 1e-9)
    j = int(idx[np.argmin(dist)])
    return j, {'candidates': int(idx.size), 'mean_other_3to6': float(m1), 'mean_right_signal': float(m2),
               'picked_other_3to6': int(other_36[j]), 'picked_right_signal': int(right_sig[j])}


def counterfactual_you_speak(rec):
    """同样的信号，如果第 7 人把朋友的话说出来（或者走到空的那家、大家知道他不看队），后面会怎样。"""
    sig = [0 if p['signal'] == 'A' else 1 for p in rec['people']]
    d = 0
    ch = []
    for i, s in enumerate(sig):
        own = 1 if s == 0 else -1
        if i == YOU - 1:
            c = 0 if d + own > 0 else (1 if d + own < 0 else s)  # 他自己照样理性地选
            ch.append(c)
            d += own                                              # 他的信号公开了
            continue
        if abs(d) >= 2:
            c = 0 if d > 0 else 1
        else:
            c = s                                                 # |d|<=1：按自己信号（平局听自己）
            d += own
        ch.append(c)
    better = 0 if rec['better_shop'] == 'A' else 1
    return {'choices': [NAMES[c] for c in ch],
            'final_shop': NAMES[ch[-1]], 'final_right': ch[-1] == better,
            'n_at_right_shop_after_you': sum(1 for c in ch[YOU:] if c == better)}


def counterfactual_all_speak(rec):
    """同样的信号，如果每个人都把朋友的话说出来：第 t 人按前 t 条信号的多数选（平局听自己）。"""
    sig = [0 if p['signal'] == 'A' else 1 for p in rec['people']]
    d = 0
    ch = []
    for s in sig:
        own = 1 if s == 0 else -1
        d += own
        ch.append(0 if d > 0 else (1 if d < 0 else s))
    better = 0 if rec['better_shop'] == 'A' else 1
    return {'choices': [NAMES[c] for c in ch], 'final_shop': NAMES[ch[-1]],
            'final_right': ch[-1] == better, 'n_at_right_shop': sum(1 for c in ch if c == better)}


def you_story(rec, res):
    pp = rec['people']
    you = pp[YOU - 1]
    q = rec['final_shop']
    other = 'B' if q == 'A' else 'A'
    ahead = pp[:YOU - 1]
    behind = pp[YOU:]
    y = res['you_decision']
    return {
        'position': YOU,
        'queue_shop': q, 'other_shop': other, 'better_shop': rec['better_shop'],
        'ahead': [{'i': p['i'], 'choice': p['choice'], 'signal': p['signal'],
                   'used_own_signal': p['used_own_signal']} for p in ahead],
        'ahead_all_chose_queue_shop': all(p['choice'] == q for p in ahead),
        'ahead_used_own_signal': [p['i'] for p in ahead if p['used_own_signal']],
        'ahead_signal_said_other_but_queued': [p['i'] for p in ahead if p['locked'] and p['signal'] == other],
        'your_signal': you['signal'],
        'your_choice': you['choice'],
        'reasoning': [
            f"前面 {YOU - 1} 个人都排在 {q}。",
            f"但只有前 {len([p for p in ahead if p['used_own_signal']])} 个人是凭自己朋友的话选的；"
            f"从第 {rec['lock_at']} 个人起，队已经锁死，后来的人选 {q} 不管朋友说什么。",
            f"所以这条队等于：{q} 那边多 {abs(pp[YOU - 1]['public_net_signals_before'])} 条朋友的话。",
            f"你朋友说 {other} 好吃，抵掉 1 条，{q} 还多 1 条。",
            f"按你知道的，{q} 更好吃的概率 = {round(y['your_belief_queue_right'] * 100)}%。你排了 {q}。",
        ],
        'your_belief_queue_shop_better': y['your_belief_queue_right'],
        'behind_count': len(behind),
        'behind_signal_said_other_but_queued': sum(1 for p in behind if p['locked'] and p['signal'] == other),
        'whole_queue_signal_said_other': sum(1 for p in pp if p['signal'] == other),
        'whole_queue_signal_said_other_but_at_queue_shop': sum(1 for p in pp if p['signal'] == other and p['choice'] == q),
        'options_given_what_you_know': {
            '闷声跟着排': y['A_silent'],
            '跟着排，但把朋友的话说出来': y['B_speak_and_queue'],
            '走到空的那家（大家知道你不看队）': y['C_go_empty_visible'],
        },
        'if_this_queue_is_really_wrong': y['if_queue_really_wrong'],
        'counterfactual_same_signals_you_speak': counterfactual_you_speak(rec),
        'counterfactual_same_signals_everyone_speaks': counterfactual_all_speak(rec),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    res = json.load(open(os.path.join(HERE, 'results', 'summary.json')))

    pool = simulate(P, N, 20_000, seed_of('visual_pool'), record_L=True)
    jw, info_w = pick(pool, final_right=False)
    jr, info_r = pick(pool, final_right=True)
    wrong_q = queue_record(pool, jw)
    right_q = queue_record(pool, jr)
    wrong_q['picked'] = dict(info_w, pool_index=jw, pool_seed_name='visual_pool')
    right_q['picked'] = dict(info_r, pool_index=jr, pool_seed_name='visual_pool')
    wrong_q['you'] = YOU
    right_q['you'] = YOU
    wrong_q['counterfactual_everyone_speaks'] = counterfactual_all_speak(wrong_q)
    for name, q in (('queue_排错.json', wrong_q), ('queue_排对.json', right_q)):
        with open(os.path.join(OUT, name), 'w') as f:
            json.dump(q, f, ensure_ascii=False, indent=1)

    you = you_story(wrong_q, res)
    you['mirror_in_right_queue'] = you_story(right_q, res)
    with open(os.path.join(OUT, 'you.json'), 'w') as f:
        json.dump(you, f, ensure_ascii=False, indent=1)

    # 20 条队
    b = 0
    while True:
        r = simulate(P, N, 20, seed_of(f'visual_20_{b}'), record_L=True)
        nw = int((r['choice'][:, -1] != r['T']).sum())
        if nw == 6:
            break
        b += 1
    qs = []
    for j in range(20):
        rec = queue_record(r, j)
        qs.append({'k': j + 1, 'better_shop': rec['better_shop'], 'final_shop': rec['final_shop'],
                   'final_right': rec['final_right'], 'lock_at': rec['lock_at'],
                   'n_at_right_shop': rec['n_at_right_shop'], 'n_signal_right': rec['n_signal_right'],
                   'signals': ''.join(p['signal'] for p in rec['people']),
                   'choices': ''.join(p['choice'] for p in rec['people'])})
    with open(os.path.join(OUT, 'queues_20.json'), 'w') as f:
        json.dump({'p': P, 'n': N, 'batch_seed_name': f'visual_20_{b}', 'batches_tried': b + 1,
                   'n_wrong': sum(1 for q in qs if not q['final_right']),
                   'note': 'signals/choices 是长度 100 的字符串，第 k 个字符是第 k 个人。'
                           '挑法：从第 0 组起，取第一组"排错条数 = 中位数 6"的 20 条。',
                   'queues': qs}, f, ensure_ascii=False, indent=1)

    base = res['base']['base_own_0.6']
    vis = {
        'p': P, 'n': N, 'colors': COLORS,
        'wrong_rate_last': base['last_wrong'], 'wrong_rate_analytic': base['analytic_last_wrong'],
        'control_independent_majority_right': base['control_independent']['analytic_majority_right'],
        'all_speak_last_wrong': base['all_speak_analytic_last_wrong'],
        'mean_right_per_person_watching_queue': 1 - base['mean_wrong_per_person'],
        'mean_right_per_person_alone': P,
        'lock': base['lock'],
        'queue_reliability_first_k_same': base['first_k_same_reliability'],
        'wrong_queue_people_with_right_signal': base['wrong_queue_people_with_right_signal'],
        'after_lock': base['after_lock'],
        'batches_of_20': res['batches_of_20_p0.6'],
        'breaking': res['breaking']['0.6'],
        'you_decision': res['you_decision'],
    }
    with open(os.path.join(OUT, 'summary.json'), 'w') as f:
        json.dump(vis, f, ensure_ascii=False, indent=1)

    # 打印给说明.md 用
    print('排错的队：', {k: wrong_q[k] for k in ('better_shop', 'final_shop', 'lock_at', 'n_used_own_signal', 'n_signal_right',
                                             'n_signal_right_but_at_wrong_shop', 'n_locked_signal_other')}, wrong_q['picked'])
    print('  信号：', ''.join(p['signal'] for p in wrong_q['people'][:30]), '…')
    print('  选择：', ''.join(p['choice'] for p in wrong_q['people'][:30]), '…')
    print('  都说出来：', wrong_q['counterfactual_everyone_speaks']['final_shop'], wrong_q['counterfactual_everyone_speaks']['n_at_right_shop'])
    print('排对的队：', {k: right_q[k] for k in ('better_shop', 'final_shop', 'lock_at', 'n_signal_right', 'n_locked_signal_other')}, right_q['picked'])
    print('你：', json.dumps({k: you[k] for k in ('queue_shop', 'other_shop', 'ahead', 'ahead_signal_said_other_but_queued',
                                                 'behind_signal_said_other_but_queued', 'whole_queue_signal_said_other',
                                                 'whole_queue_signal_said_other_but_at_queue_shop')}, ensure_ascii=False))
    print('  理由：', ' '.join(you['reasoning']))
    print('  同样信号你说出来：', {k: v for k, v in you['counterfactual_same_signals_you_speak'].items() if k != 'choices'})
    print('  对照队里的你：', you['mirror_in_right_queue']['ahead_signal_said_other_but_queued'], you['mirror_in_right_queue']['your_signal'],
          you['mirror_in_right_queue']['queue_shop'], you['mirror_in_right_queue']['better_shop'])
    print('20 条队：试了', b + 1, '组；', [('错' if not q['final_right'] else '对', q['lock_at']) for q in qs])


if __name__ == '__main__':
    main()
