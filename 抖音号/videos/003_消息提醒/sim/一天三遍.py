"""第三条《消息提醒》仿真：同一个你，把同一天过三遍（全开／全关／分批加例外）。

时间单位：分钟。一天从 7:00 到 23:00（0–960）。
专注时段：9–12 点、14–18 点、20–22 点（看书、陪孩子），只在这三段里算“带宽”和“最长连续专注”。

每条消息有三种来源：群、私聊、App 推送。少数是“要紧的事”。
三种设置：
  全开：每条都响一下（横幅或声音），算一次打断；要紧的事立刻看到。
  分批：只在 9:00、15:00、21:00 一次推送（Fitz 2019 的时间点），每次算一次打断；
        白名单里的人私聊、群里 @你 的消息照常立刻响。
  全关：一条都不响；要紧的事要等你下次自己拿起手机才看到。
三种设置下都有“自己拿起手机”的次数（不是通知叫的），用 Fitz 2019 各组的每天解锁数减去通知叫起来的那几次。

带宽：每次打断后，带宽掉到 FLOOR，接下来 RECOVER 分钟里线性回到 100%。
这是模型里的定义（借《稀缺》的“带宽”一词），不是测出来的；RECOVER 取“二十分钟左右”（Iqbal & Horvitz 2007）。
参数里凡是标“设定”的，都没有现成数据，要写进简介。
"""
import json, math, random, sys

P = dict(
    msgs_per_day=56,            # Pielot, Vradi & Park 2018：每人每天中位数 56 条
    share=dict(group=0.31, private=0.44, app=0.25),   # Pielot 2018 表 1 推算：私聊约 44%、群聊约 31%，其余（邮件、社交、其他）约 25%
    urgent_per_day=3.0,         # 设定：一天里真正要紧的事
    urgent_src=dict(private_white=0.5, group_at=0.2, group_noat=0.2, app=0.1),  # 设定：要紧的事从哪来
    white_private_share=0.3,    # 设定：私聊里来自白名单的人（家人、领导）占几成
    group_at_share=0.05,        # 设定：群消息里 @你 的占几成
    unlocks=dict(全开=57.3, 分批=37.2, 全关=46.0),  # Fitz 等 2019 表 2：照常／一天三批／完全不推，每天解锁次数（四组整体 p = .059）
    alert_unlock_share=0.11,    # Heitmayer & Lahlou 2021：11% 的拿起手机是通知叫的（89% 是自己拿的）
    see_on_pickup=0.5,          # 设定：自己拿起手机时，顺手看到一条压着的要紧消息的概率
    floor=0.4, recover=20.0,    # 带宽模型：打断后掉到 40%，20 分钟回满（“二十分钟左右”，Iqbal & Horvitz 2007）
    batch_times=[120, 480, 840],  # 9:00, 15:00, 21:00（Fitz 2019 的三个时间点）
    focus=[(120, 300), (420, 660), (780, 900)],
)
DAY = 960
ACTIVE = (60, 960)  # 8:00 以后才来消息

def gen_day(rng, p):
    n = rng.poisson(p['msgs_per_day']) if hasattr(rng, 'poisson') else poisson(rng, p['msgs_per_day'])
    msgs = []
    for _ in range(n):
        t = rng.uniform(*ACTIVE)
        r = rng.random(); s = p['share']
        src = 'group' if r < s['group'] else ('private' if r < s['group'] + s['private'] else 'app')
        white = src == 'private' and rng.random() < p['white_private_share']
        at = src == 'group' and rng.random() < p['group_at_share']
        msgs.append(dict(t=t, src=src, white=white, at=at, urgent=False))
    # 要紧的事单独放进来（不占 56 条之外的名额太多：从对应来源里挑）
    nu = poisson(rng, p['urgent_per_day'])
    for _ in range(nu):
        r = rng.random(); acc = 0
        for k, v in p['urgent_src'].items():
            acc += v
            if r < acc: break
        t = rng.uniform(*ACTIVE)
        if k == 'private_white': m = dict(t=t, src='private', white=True, at=False)
        elif k == 'group_at': m = dict(t=t, src='group', white=False, at=True)
        elif k == 'group_noat': m = dict(t=t, src='group', white=False, at=False)
        else: m = dict(t=t, src='app', white=False, at=False)
        m['urgent'] = True
        msgs.append(m)
    msgs.sort(key=lambda m: m['t'])
    return msgs

def poisson(rng, lam):
    L = math.exp(-lam); k = 0; q = 1.0
    while True:
        q *= rng.random()
        if q < L: return k
        k += 1

def pickups(rng, rate_per_day):
    ts = []; t = 0.0
    lam = rate_per_day / DAY
    while True:
        t += rng.expovariate(lam)
        if t >= DAY: return ts
        ts.append(t)

def run(policy, rng, p):
    msgs = gen_day(rng, p)
    # 自己拿起手机的次数 = 这种设置下每天解锁次数 − 通知叫起来的那几次（那几次和“响一下”算同一次打断）
    q = p['alert_unlock_share'] * p['unlocks']['全开'] / p['msgs_per_day']   # 每响一下，引出一次解锁的概率
    n_alerts_expected = dict(全开=p['msgs_per_day'],
                             分批=len(p['batch_times']) + p['msgs_per_day'] * (p['share']['private'] * p['white_private_share'] + p['share']['group'] * p['group_at_share']),
                             全关=0.0)[policy]
    rate = max(0.0, p['unlocks'][policy] - q * n_alerts_expected)
    picks = pickups(rng, rate)
    events = list(picks)  # 打断时刻
    delays = []
    if policy == '全开':
        events += [m['t'] for m in msgs]
        delays = [0.0 for m in msgs if m['urgent']]
    elif policy == '分批':
        events += [b for b in p['batch_times']]
        for m in msgs:
            through = (m['src'] == 'private' and m['white']) or (m['src'] == 'group' and m['at'])
            if through:
                events.append(m['t'])
                if m['urgent']: delays.append(0.0)
            elif m['urgent']:
                nxt = [b for b in p['batch_times'] if b >= m['t']]
                nxt_pick = [x for x in picks if x >= m['t'] and rng.random() < p['see_on_pickup']]
                cand = (nxt[:1] + nxt_pick[:1]) or [DAY + 480]  # 当天看不到：算到第二天 9 点
                delays.append(min(cand) - m['t'])
    else:  # 全关
        for m in msgs:
            if m['urgent']:
                nxt_pick = [x for x in picks if x >= m['t'] and rng.random() < p['see_on_pickup']]
                delays.append((nxt_pick[0] if nxt_pick else DAY + 480) - m['t'])
    events.sort()
    # 带宽：逐分钟
    bw = [1.0] * DAY
    for e in events:
        i0 = int(e)
        for i in range(i0, min(DAY, i0 + int(p['recover']) + 1)):
            v = p['floor'] + (1 - p['floor']) * (i - e) / p['recover']
            bw[i] = min(bw[i], max(p['floor'], min(1.0, v)))
    focus_min = [i for a, b in p['focus'] for i in range(a, b)]
    avg_bw = sum(bw[i] for i in focus_min) / len(focus_min)
    # 最长连续“满带宽”（没被打断、也缓过来了）
    longest = 0; cur = 0
    for a, b in p['focus']:
        cur = 0
        for i in range(a, b):
            cur = cur + 1 if bw[i] >= 0.999 else 0
            longest = max(longest, cur)
    n_focus = sum(1 for e in events if any(a <= e < b for a, b in p['focus']))
    return dict(n_all=len(events), n_focus=n_focus, avg_bw=avg_bw, longest=longest,
                urgent=len(delays), late=sum(1 for d in delays if d > 60), delay_mean=(sum(delays) / len(delays) if delays else 0.0),
                delay_max=max(delays) if delays else 0.0, bw=bw if False else None)

def summarize(p, days=2000, seed=1):
    out = {}
    for pol in ['全开', '全关', '分批']:
        rng = random.Random(seed)
        rs = [run(pol, rng, p) for _ in range(days)]
        def avg(k): return sum(r[k] for r in rs) / len(rs)
        tot_u = sum(r['urgent'] for r in rs); late = sum(r['late'] for r in rs)
        dl = [r['delay_mean'] for r in rs if r['urgent']]
        out[pol] = dict(打断_全天=round(avg('n_all'), 1), 打断_专注时段=round(avg('n_focus'), 1),
                        平均带宽=round(avg('avg_bw') * 100, 1), 最长连续专注_分=round(avg('longest'), 1),
                        要紧的事_晚1小时以上占比=round(100 * late / max(tot_u, 1), 1),
                        要紧的事_平均晚到_分=round(sum(dl) / max(len(dl), 1), 1))
    return out

if __name__ == '__main__':
    res = summarize(P)
    for k, v in res.items(): print(k, v)
