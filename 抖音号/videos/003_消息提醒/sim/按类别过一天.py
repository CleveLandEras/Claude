"""第三条《消息提醒》仿真第二版：按消息类别过同一天（11/2 晚，依据 前置_消息分类与打扰.md）。

三种设置：
  全开：所有通知都响（系统通知本来就大多没声，不算）。
  全关：一条都不响；要紧的事要等你自己拿起手机时碰巧看到。
  先分开再处理：
    营销推送、内容推送 → 关掉；
    私聊、服务通知（验证码、快递、银行） → 照常响；
    群 → 普通群开免打扰，要紧的群（老师、领导那一两个）照常响并置顶；
    工作软件 → 上班时间照常，下班后勿扰；
    其余攒起来，一天看三次（9:00、15:00、21:00，Fitz 2019 的时间点）。
比三样：被打断几次、最长能专注多久、要紧的消息里有几条晚看到（超过 1 小时）或当天没看到。

每类消息给“一天几条”和“有多大可能是要紧的”。条数的出处写在 CATS 里；
“要紧的概率”没有现成研究，全是设定，靠换参数核结论。
带宽模型、自己拿起手机的次数和第一版相同。
"""
import copy, math, random

DAY = 960                       # 7:00–23:00
ACTIVE = (60, 960)              # 8:00 以后才来消息
WORK = (120, 660)               # 9:00–18:00 上班
FOCUS = [(120, 300), (420, 660), (780, 900)]
BATCH = [120, 480, 840]

# 类别：一天几条（出处）、要紧概率（设定）、全关时自己拿手机碰巧看到它的概率（设定）
CATS = dict(
    私聊=dict(n=18, p_urgent=0.08, see=0.6),      # 条数：Pielot 2018 中位数 18（西班牙 278 人）
    群聊=dict(n=27, p_urgent=0.04, see=0.25),     # 条数：Pielot 2018 均值 27（中位数 7，是下限；中国 73% 嫌群消息太多，取均值当“群多的你”）
    工作软件=dict(n=6, p_urgent=0.15, see=0.5),   # 条数：设定（中国手机端没数据；邮件中位数 2 条，Pielot 2018）
    服务通知=dict(n=3, p_urgent=0.3, see=0.8),    # 条数：设定（验证码、快递、银行，没查到条数）
    营销推送=dict(n=10, p_urgent=0.0, see=0.0),   # 条数：设定（中国媒体实测 21 个 App 9 小时 67–81 条，是全开上限；点开 6.5%）
    内容推送=dict(n=8, p_urgent=0.0, see=0.0),    # 条数：设定（资讯、短视频、热榜、点赞评论；重要性 2.24/5）
)
P = dict(
    cats=CATS,
    key_group_share=0.7,     # 设定：群里的要紧消息，有七成来自你会置顶、照常响的那一两个群（老师、领导）
    unlocks=dict(全开=57.3, 全关=46.0, 分开=37.2),  # Fitz 2019 表 2：照常／完全不推／一天三批，每天解锁次数
    alert_unlock_share=0.11,  # Heitmayer & Lahlou 2021：11% 的拿起手机是通知叫的
    floor=0.4, recover=20.0,  # 带宽：打断后掉到 40%，20 分钟回满（“二十分钟左右”，Iqbal & Horvitz 2007）
)

def poisson(rng, lam):
    L = math.exp(-lam); k = 0; q = 1.0
    while True:
        q *= rng.random()
        if q < L: return k
        k += 1

def gen_day(rng, p):
    msgs = []
    for cat, c in p['cats'].items():
        for _ in range(poisson(rng, c['n'])):
            t = rng.uniform(*ACTIVE)
            urgent = rng.random() < c['p_urgent']
            key_group = cat == '群聊' and (rng.random() < p['key_group_share'] if urgent else rng.random() < 0.15)
            msgs.append(dict(t=t, cat=cat, urgent=urgent, key=key_group))
    msgs.sort(key=lambda m: m['t'])
    return msgs

def alerts_through(m, policy):
    """这条消息在这种设置下会不会立刻响。"""
    if policy == '全开': return True
    if policy == '全关': return False
    c = m['cat']
    if c in ('私聊', '服务通知'): return True
    if c == '群聊': return m['key']
    if c == '工作软件': return WORK[0] <= m['t'] < WORK[1]
    return False   # 营销、内容推送关掉

def run(policy, rng, p):
    msgs = gen_day(rng, p)
    n_alert_exp = {'全开': sum(c['n'] for c in p['cats'].values()), '全关': 0.0}.get(policy)
    if n_alert_exp is None:
        cs = p['cats']
        n_alert_exp = cs['私聊']['n'] + cs['服务通知']['n'] + cs['群聊']['n'] * 0.15 + cs['工作软件']['n'] * (WORK[1] - WORK[0]) / (ACTIVE[1] - ACTIVE[0]) + len(BATCH)
    q = p['alert_unlock_share'] * p['unlocks']['全开'] / sum(c['n'] for c in p['cats'].values())
    rate = max(0.0, p['unlocks'][policy] - q * n_alert_exp)
    picks = []; t = 0.0
    while True:
        t += rng.expovariate(rate / DAY) if rate > 0 else DAY
        if t >= DAY: break
        picks.append(t)
    events = list(picks)
    if policy == '分开': events += BATCH
    late = missed = urgent = 0
    for m in msgs:
        through = alerts_through(m, policy)
        if through: events.append(m['t'])
        if not m['urgent']: continue
        urgent += 1
        if through: continue                      # 立刻看到
        seen = None
        if policy == '分开':
            nxt = [b for b in BATCH if b >= m['t']]
            seen = nxt[0] if nxt else None        # 攒着的那一批里会认真看（群里被 @ 会标红“有人@我”）
        see_p = p['cats'][m['cat']]['see']
        for x in picks:
            if x >= m['t'] and rng.random() < see_p:
                seen = x if seen is None else min(seen, x); break
        if seen is None: missed += 1
        elif seen - m['t'] > 60: late += 1
    events.sort()
    bw = [1.0] * DAY
    for e in events:
        i0 = int(e)
        for i in range(i0, min(DAY, i0 + int(p['recover']) + 1)):
            v = p['floor'] + (1 - p['floor']) * (i - e) / p['recover']
            bw[i] = min(bw[i], max(p['floor'], min(1.0, v)))
    longest = 0
    for a, b in FOCUS:
        cur = 0
        for i in range(a, b):
            cur = cur + 1 if bw[i] >= 0.999 else 0
            longest = max(longest, cur)
    focus_min = [i for a, b in FOCUS for i in range(a, b)]
    return dict(n=len(events), longest=longest, avg_bw=sum(bw[i] for i in focus_min) / len(focus_min),
                urgent=urgent, late=late, missed=missed)

def summarize(p, days=2000, seed=11):
    out = {}
    for pol in ['全开', '全关', '分开']:
        rng = random.Random(seed)
        rs = [run(pol, rng, p) for _ in range(days)]
        def avg(k): return sum(r[k] for r in rs) / len(rs)
        out[pol] = dict(打断=round(avg('n'), 1), 最长专注_分=round(avg('longest'), 1), 带宽=round(100 * avg('avg_bw'), 1),
                        要紧=round(avg('urgent'), 2), 晚1小时以上=round(avg('late'), 2), 当天没看到=round(avg('missed'), 2))
    return out

if __name__ == '__main__':
    for k, v in summarize(P).items(): print(k, v)
