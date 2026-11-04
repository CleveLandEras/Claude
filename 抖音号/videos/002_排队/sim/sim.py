"""信息瀑布（informational cascade）仿真。

基础模型照 Bikhchandani, Hirshleifer & Welch (1992, JPE) 的二元信号例子：
  - 两家店 A(=0)、B(=1)，其中一家真的更好吃（每条队随机定，各 1/2）。
  - n 个人依次到来。每人有一条私人信号（"朋友说哪家好吃"），说对的概率 p。
  - 每人看得到前面所有人选了哪家（看不到他们的信号），用贝叶斯规则算哪家更可能好吃，选更可能的那家。
  - 平局（两家一样可能）：
      tie='own'  听自己的信号（Anderson & Holt 1997 的主假设；主场景用这个）
      tie='coin' 抛硬币（BHW 1992 原文的假设）

“公开信念”L = log[P(A 好吃 | 前面所有人的选择) / P(B 好吃 | ...)]，所有人共享。
一个人自己的信号再加减 lam = log(p/(1-p))。

打破瀑布的几种人（schedule 里的类型）：
  H = 0  看队的人（理性跟队）
  I = 1  只听自己的人，而且大家知道他不看队（他的选择 = 他的信号，等于把信号公开了）
  S = 2  说出来的人：照样理性地选，但把自己的信号说出来
另外：
  q_hidden   每个看队的人以 q 的概率其实是“只听自己的人”，但别人认不出来（大家只知道比例 q）
  observer   'bayes'：看队的人按上面的贝叶斯规则；'naive'：把前面每个人的选择都当一票来数
"""
import math

import numpy as np

H, I, S = 0, 1, 2
EPS = 1e-9


def lam_of(p):
    return math.log(p / (1 - p))


def _pi0(post, sval, tie):
    """看队的人选 A 的概率。post = 公开信念 + 自己信号；sval = +1（信号说 A）或 -1。"""
    out = np.where(post > EPS, 1.0, 0.0)
    t = np.abs(post) <= EPS
    if tie == 'own':
        tv = 1.0 if sval > 0 else 0.0
    else:
        tv = 0.5
    return np.where(t, tv, out)


def simulate(p, n, R, seed, tie='own', schedule=None, q_hidden=0.0, observer='bayes',
             truth=None, record_L=False, probe=None):
    """跑 R 条独立的队，每条 n 人。返回 dict（全部是 numpy 数组）。

    schedule: 长度 n 的类型数组（H/I/S），默认全是 H。
    第 n 个人永远强制为 H（"队尾那个看队的人"），方便各场景比较。
    probe: 另外强制为 H（且不会是认不出的只听自己的人）的位置（0 起算），用来在长队中间量“看队的人”。
    """
    rng = np.random.default_rng(seed)
    lam = lam_of(p)
    sched = np.zeros(n, dtype=np.int8) if schedule is None else np.asarray(schedule, dtype=np.int8).copy()
    probes = [n - 1] + list(probe or [])
    sched[probes] = H

    T = rng.integers(0, 2, R).astype(np.int8) if truth is None else np.full(R, truth, np.int8)
    correct_sig = rng.random((R, n)) < p
    sig = np.where(correct_sig, T[:, None], 1 - T[:, None]).astype(np.int8)
    hidden = np.zeros((R, n), dtype=bool)
    if q_hidden > 0:
        hidden = rng.random((R, n)) < q_hidden
        hidden[:, sched != H] = False
        hidden[:, probes] = False
    coins = rng.integers(0, 2, (R, n)).astype(np.int8)

    choice = np.empty((R, n), dtype=np.int8)
    locked = np.zeros((R, n), dtype=bool)
    Lrec = np.empty((R, n), dtype=np.float32) if record_L else None
    L = np.zeros(R)
    cnt = np.zeros(R)  # naive：前面选 A 的人数 - 选 B 的人数

    for i in range(n):
        s = sig[:, i]
        sv = np.where(s == 0, 1.0, -1.0)
        typ = sched[i]
        if record_L:
            Lrec[:, i] = L if observer == 'bayes' else cnt * lam
        # ---- 看队的人怎么选 ----
        if observer == 'bayes':
            post = L + sv * lam
            locked[:, i] = np.abs(L) > lam + EPS
        else:
            post = (cnt + sv) * lam
            locked[:, i] = np.abs(cnt) >= 2 - EPS
        c_herd = np.where(post > EPS, 0, 1).astype(np.int8)
        tie_mask = np.abs(post) <= EPS
        if tie == 'own':
            c_herd = np.where(tie_mask, s, c_herd)
        else:
            c_herd = np.where(tie_mask, coins[:, i], c_herd)
        # ---- 实际选择 ----
        if typ == I:
            c = s.copy()
            locked[:, i] = False
        else:
            c = c_herd
        if q_hidden > 0:
            c = np.where(hidden[:, i], s, c)
            locked[:, i] &= ~hidden[:, i]
        choice[:, i] = c
        # ---- 后面的人怎么更新 ----
        if observer == 'naive':
            cnt += np.where(c == 0, 1.0, -1.0)
            continue
        if typ in (I, S):
            L = L + sv * lam
            continue
        q = q_hidden
        a_pos = _pi0(L + lam, +1, tie)   # 信号说 A 时选 A 的概率
        a_neg = _pi0(L - lam, -1, tie)   # 信号说 B 时选 A 的概率
        P0_A = q * p + (1 - q) * (p * a_pos + (1 - p) * a_neg)          # A 真好吃时，这人选 A 的概率
        P0_B = q * (1 - p) + (1 - q) * ((1 - p) * a_pos + p * a_neg)    # B 真好吃时，这人选 A 的概率
        num = np.where(c == 0, P0_A, 1 - P0_A)
        den = np.where(c == 0, P0_B, 1 - P0_B)
        ok = (num > 0) & (den > 0)
        L = L + np.where(ok, np.log(np.where(ok, num, 1) / np.where(ok, den, 1)), 0.0)

    out = dict(T=T, sig=sig, choice=choice, locked=locked, hidden=hidden, sched=sched, p=p, n=n, R=R)
    if record_L:
        out['L'] = Lrec
    return out


# ---------------------------------------------------------------- 解析解

def dp_basic(p, n, tie='own'):
    """标准模型（全是看队的人），A 真好吃（对称，不失一般性）。
    状态：0（两边信号抵消）、+1、-1（多一条 A / B 的信号）、UP（锁死在 A）、DOWN（锁死在 B）。
    返回：每个位置上的人选错的概率（长度 n），以及第 n 人之前已锁死在错店的概率。"""
    st = {'0': 1.0, '+1': 0.0, '-1': 0.0, 'UP': 0.0, 'DOWN': 0.0}
    wrong = []
    for _ in range(n):
        if tie == 'own':
            w = st['0'] * (1 - p) + st['+1'] * (1 - p) + st['-1'] * (1 - p) + st['DOWN']
            nxt = {
                '0': st['+1'] * (1 - p) + st['-1'] * p,
                '+1': st['0'] * p,
                '-1': st['0'] * (1 - p),
                'UP': st['UP'] + st['+1'] * p,
                'DOWN': st['DOWN'] + st['-1'] * (1 - p),
            }
        else:  # coin（BHW）
            w = st['0'] * (1 - p) + st['+1'] * (1 - p) / 2 + st['-1'] * ((1 - p) + p / 2) + st['DOWN']
            nxt = {
                '0': st['+1'] * (1 - p) / 2 + st['-1'] * p / 2,
                '+1': st['0'] * p,
                '-1': st['0'] * (1 - p),
                'UP': st['UP'] + st['+1'] * (p + (1 - p) / 2),
                'DOWN': st['DOWN'] + st['-1'] * ((1 - p) + p / 2),
            }
        wrong.append(w)
        st = nxt
    return np.array(wrong), st


def wrong_cascade_limit(p, tie='own'):
    """人数无穷多时，最后锁死在错店的概率。"""
    if tie == 'own':
        return (1 - p) ** 2 / (p ** 2 + (1 - p) ** 2)
    return (2 - p) * (1 - p) / (2 * (1 - p + p * p))


def bhw_eq3(p, n):
    """BHW 1992 式 (3)：A 真好吃时，n（偶数）人之后 对的瀑布 / 没瀑布 / 错的瀑布 的概率。"""
    x = (p - p * p) ** (n / 2)
    up = p * (p + 1) * (1 - x) / (2 * (1 - p + p * p))
    down = (p - 2) * (p - 1) * (1 - x) / (2 * (1 - p + p * p))
    return up, x, down


def dp_identified(p, n, sched):
    """平局听自己；schedule 里 I/S 的信号公开。状态 = 公开的净信号数 d（A 多为正），A 真好吃。
    看队的人：|d|>=2 锁死；|d|<=1 时按自己信号选（等于公开了信号）。
    返回每个位置上的人选错的概率。"""
    off = n + 2
    dist = np.zeros(2 * off + 1)
    dist[off] = 1.0
    wrong = []
    for i in range(n):
        typ = sched[i] if i < n - 1 else H
        d = np.arange(-off, off + 1)
        if typ == I:
            w = 1 - p
        elif typ == S:
            # 理性地选：d+自己信号 >0 选 A；=0 听自己；<0 选 B
            w = dist[d <= -2].sum() + dist[np.abs(d) <= 1].sum() * (1 - p)
        else:
            w = dist[d <= -2].sum() + dist[np.abs(d) <= 1].sum() * (1 - p)
        wrong.append(w)
        if typ in (I, S):
            new = np.zeros_like(dist)
            new[1:] += dist[:-1] * p
            new[:-1] += dist[1:] * (1 - p)
            dist = new
        else:
            move = np.abs(d) <= 1
            new = np.where(move, 0.0, dist)
            moved = np.where(move, dist, 0.0)
            new[1:] += moved[:-1] * p
            new[:-1] += moved[1:] * (1 - p)
            dist = new
    return np.array(wrong)


def binom_pmf(n, k, p):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def independent_majority(p, n):
    """每人只听自己：n 人里选对的人 > n/2、= n/2、< n/2 的概率。"""
    pm = [binom_pmf(n, k, p) for k in range(n + 1)]
    gt = sum(pm[k] for k in range(n + 1) if 2 * k > n)
    eq = sum(pm[k] for k in range(n + 1) if 2 * k == n)
    return gt, eq, 1 - gt - eq


def all_speak_last_wrong(p, n):
    """所有人都把信号说出来：第 n 人看到全部 n 条信号（含自己），按多数选；平局听自己（此时一半概率错）。"""
    gt, eq, lt = independent_majority(p, n)
    return lt + 0.5 * eq


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def dp_from(p, d0, m):
    """平局听自己、全是看队的人。A 真好吃，公开的净信号数从 d0 开始，后面还有 m 个人。
    返回 (这 m 人里平均几人选对, 第 m 人选错的概率)。"""
    off = m + 4
    dist = np.zeros(2 * off + 1)
    dist[off + d0] = 1.0
    d = np.arange(-off, off + 1)
    right = 0.0
    last_wrong = 0.0
    for j in range(m):
        w = dist[d <= -2].sum() + dist[np.abs(d) <= 1].sum() * (1 - p)
        right += 1 - w
        last_wrong = w
        move = np.abs(d) <= 1
        new = np.where(move, 0.0, dist)
        moved = np.where(move, dist, 0.0)
        new[1:] += moved[:-1] * p
        new[:-1] += moved[1:] * (1 - p)
        dist = new
    return right, last_wrong
