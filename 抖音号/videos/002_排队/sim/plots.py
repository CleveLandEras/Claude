"""用 Pillow 出图（项目里没有 matplotlib）。

fig_排错比例.png  朋友的话有多准（p） vs 一长串人最后排错店的比例：解析解 + 仿真点 + 对照
fig_20条队.png    20 条队，每条 100 人：排在哪家、谁的朋友其实说的是另一家、在第几个人锁死
fig_你.png        排错的队和排对的队，前 20 人：朋友说哪家 / 他排了哪家；“你”是第 7 个
fig_打破.png      几种打破办法：第 100 个人（看队的）排错的比例

配色：参考调色板第 1、2 号（蓝 #2a78d6 = 好吃的那家 / 只听自己；橙 #eb6834 = 不好吃的那家 / 看队），
第 3 号绿 #1baf7a = 都说出来。前三号相邻两两校验过（见 dataviz 参考调色板）。
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')
VIS = os.path.join(HERE, 'visual')
FIG = os.path.join(HERE, 'figs')
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
SURF = (252, 252, 251)
INK = (11, 11, 11)
INK2 = (82, 81, 78)
MUTED = (140, 139, 134)
GRID = (226, 225, 220)
BLUE = (42, 120, 214)
ORANGE = (235, 104, 52)
AQUA = (27, 175, 122)
SS = 2


def font(px, bold=False):
    return ImageFont.truetype(FONT, int(px * SS), index=1 if bold else 0)


def canvas(W, H):
    img = Image.new('RGB', (W * SS, H * SS), SURF)
    return img, ImageDraw.Draw(img)


def save(img, name):
    W, H = img.size
    img.resize((W // SS, H // SS), Image.LANCZOS).save(os.path.join(FIG, name))


def t(d, xy, s, px, fill=INK, bold=False, anchor='la'):
    d.text((xy[0] * SS, xy[1] * SS), s, font=font(px, bold), fill=fill, anchor=anchor)


def tw(d, s, px, bold=False):
    return d.textlength(s, font=font(px, bold)) / SS


def rrect(d, box, fill, r=4):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=fill)


def dashed(d, pts, fill, width, dash=10, gap=7):
    import math
    seg_left = dash
    on = True
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        pos = 0
        while pos < L:
            step = min(seg_left, L - pos)
            a = pos / L
            b = (pos + step) / L
            if on:
                d.line([((x0 + (x1 - x0) * a) * SS, (y0 + (y1 - y0) * a) * SS),
                        ((x0 + (x1 - x0) * b) * SS, (y0 + (y1 - y0) * b) * SS)], fill=fill, width=width * SS)
            pos += step
            seg_left -= step
            if seg_left <= 1e-9:
                on = not on
                seg_left = dash if on else gap


# ------------------------------------------------------------------ 图 1
def fig_rate(s):
    sw = s['sweep']
    W, H = 1600, 1000
    L, Rm, Tp, B = 120, 330, 230, 110
    img, d = canvas(W, H)
    pw, ph = W - L - Rm, H - Tp - B
    X = lambda p: L + pw * (p - 0.55) / 0.40
    ymax = 0.45
    Y = lambda v: Tp + ph * (1 - v / ymax)
    t(d, (L, 44), '朋友的话越不准，整条队排错店的机会越大', 40, bold=True)
    t(d, (L, 104), '一条 100 人的队，第 100 个人最后排在不好吃那家的比例。线 = 解析解；点 = 仿真（每个 p 5 万条队，竖线是 95% 区间，比点还小）', 22, INK2)
    t(d, (L, 138), '“看队”的人：看得见前面每个人排了哪家，看不见他们朋友说了什么，按贝叶斯规则选。', 22, INK2)
    # 网格
    for v in (0, .1, .2, .3, .4):
        d.line([(L * SS, Y(v) * SS), ((L + pw) * SS, Y(v) * SS)], fill=GRID, width=SS)
        t(d, (L - 14, Y(v)), f'{int(v * 100)}%', 20, INK2, anchor='rm')
    for p in (0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95):
        t(d, (X(p), Tp + ph + 20), f'{p:.2f}'.rstrip('0') if p * 100 % 10 else f'{p:.1f}', 20, INK2, anchor='mt')
    t(d, (L + pw / 2, H - 46), '朋友说对的概率 p', 22, INK2, anchor='mm')
    # 标出 0.6 / 0.7 / 0.8
    for p in (0.6, 0.7, 0.8):
        for yy in range(Tp, Tp + ph, 14):
            d.line([(X(p) * SS, yy * SS), (X(p) * SS, (yy + 6) * SS)], fill=GRID, width=SS)
    series = [
        ('analytic_own', ORANGE, False, '看队（平局听自己）'),
        ('analytic_coin', ORANGE, True, '看队（平局抛硬币，\nBHW 原文的设定）'),
        ('independent_majority_wrong_or_tie', BLUE, False, '不看队，各听各的：\n多数人选错（含 50:50）'),
        ('all_speak_last_wrong', AQUA, False, '看队，但每人都把\n朋友的话说出来'),
    ]
    for key, col, dash, lab in series:
        pts = [(X(r['p']), Y(r[key])) for r in sw]
        if dash:
            dashed(d, pts, col, 3)
        else:
            d.line([(x * SS, y * SS) for x, y in pts], fill=col, width=3 * SS, joint='curve')
    # 仿真点
    for key, col in (('sim_own', ORANGE), ('sim_coin', ORANGE)):
        for r in sw:
            x, y = X(r['p']), Y(r[key]['rate'])
            lo, hi = Y(r[key]['ci95'][0]), Y(r[key]['ci95'][1])
            d.line([(x * SS, lo * SS), (x * SS, hi * SS)], fill=INK2, width=SS)
            d.ellipse([(x - 6) * SS, (y - 6) * SS, (x + 6) * SS, (y + 6) * SS], fill=col, outline=SURF, width=2 * SS)
    # 直接标注（线尾）
    ends = {k: sw[-1][k] for k, *_ in series}
    t(d, (X(0.75) + 14, Y(sw[4]['analytic_coin']) - 14), '看队，平局抛硬币', 22, INK, anchor='lb')
    t(d, (X(0.75) - 14, Y(sw[4]['analytic_own']) + 14), '看队，平局听自己', 22, INK, anchor='rt')
    t(d, (X(0.553), Y(0.19)), '不看队、各听各的：多数人选错', 22, INK, anchor='lb')
    t(d, (X(0.607), Y(0.03)), '看队，但每人都把朋友的话说出来（和蓝线几乎重合）', 22, INK, anchor='lb')
    # 关键数
    rows = [(0.6, 1), (0.7, 3), (0.8, 5)]
    for p, idx in rows:
        r = sw[idx]
        x, y = X(p), Y(r['analytic_own'])
        t(d, (x + 12, y - 4), f"{r['analytic_own'] * 100:.1f}%", 22, INK, bold=True, anchor='lb')
    # 图例（右侧）
    lx, ly = L + pw + 40, Tp + 10
    t(d, (lx, ly), '图例', 22, INK, bold=True)
    ly += 44
    for key, col, dash, lab in series:
        if dash:
            dashed(d, [(lx, ly), (lx + 34, ly)], col, 3, dash=8, gap=5)
        else:
            d.line([(lx * SS, ly * SS), ((lx + 34) * SS, ly * SS)], fill=col, width=3 * SS)
        out = lab.split('\n')
        for k, ln in enumerate(out):
            t(d, (lx + 46, ly + k * 28), ln, 20, INK2, anchor='lm')
        ly += 28 * len(out) + 26
    d.ellipse([(lx + 11) * SS, (ly - 6) * SS, (lx + 23) * SS, (ly + 6) * SS], fill=ORANGE, outline=SURF, width=2 * SS)
    t(d, (lx + 46, ly), '仿真', 20, INK2, anchor='lm')
    save(img, 'fig_排错比例.png')


# ------------------------------------------------------------------ 图 2
def fig_20(q20):
    qs = q20['queues']
    n = q20['n']
    cell = 13
    W = 140 + n * cell + 120
    rowh = 34
    Tp = 250
    H = Tp + len(qs) * rowh + 110
    img, d = canvas(W, H)
    L = 110
    nw = q20['n_wrong']
    t(d, (L, 40), f'20 条队，{nw} 条排错了店', 40, bold=True)
    t(d, (L, 100), '每一行是一条队，从左到右是第 1 到第 100 个人。p = 0.6（朋友说对的概率）。', 22, INK2)
    t(d, (L, 134), '挑法：按种子顺序，取第一组“排错条数 = 中位数 6”的 20 条。20 万条队里，每 20 条平均 6.1 条排错。', 22, INK2)
    # 图例
    lx, ly = L, 190
    rrect(d, (lx, ly - 9, lx + 18, ly + 9), BLUE, 3)
    t(d, (lx + 26, ly), '排在好吃那家', 20, INK2, anchor='lm')
    lx += 26 + tw(d, '排在好吃那家', 20) + 30
    rrect(d, (lx, ly - 9, lx + 18, ly + 9), ORANGE, 3)
    t(d, (lx + 26, ly), '排在不好吃那家', 20, INK2, anchor='lm')
    lx += 26 + tw(d, '排在不好吃那家', 20) + 30
    rrect(d, (lx, ly - 9, lx + 18, ly + 9), MUTED, 3)
    d.ellipse([(lx + 6) * SS, (ly - 3) * SS, (lx + 12) * SS, (ly + 3) * SS], fill=SURF)
    t(d, (lx + 26, ly), '白点：他朋友说的是另一家，他还是跟着排了', 20, INK2, anchor='lm')
    lx += 26 + tw(d, '白点：他朋友说的是另一家，他还是跟着排了', 20) + 30
    d.line([(lx + 9) * SS, (ly - 12) * SS, (lx + 9) * SS, (ly + 12) * SS], fill=INK, width=2 * SS)
    t(d, (lx + 22, ly), '锁死的位置', 20, INK2, anchor='lm')
    for r, q in enumerate(qs):
        y = Tp + r * rowh
        t(d, (L - 14, y + rowh / 2 - 2), str(q['k']), 18, INK2, anchor='rm')
        better = q['better_shop']
        for i in range(n):
            x = L + i * cell
            ch = q['choices'][i]
            col = BLUE if ch == better else ORANGE
            rrect(d, (x + 1, y + 4, x + cell - 1, y + rowh - 6), col, 2)
            if q['signals'][i] != ch:
                cx, cy = x + cell / 2, y + (rowh - 2) / 2
                d.ellipse([(cx - 2.6) * SS, (cy - 2.6) * SS, (cx + 2.6) * SS, (cy + 2.6) * SS], fill=SURF)
        if q['lock_at']:
            x = L + (q['lock_at'] - 1) * cell - 1
            d.line([(x * SS, (y + 1) * SS), (x * SS, (y + rowh - 3) * SS)], fill=INK, width=2 * SS)
        lab = '对' if q['final_right'] else '错'
        t(d, (L + n * cell + 16, y + rowh / 2 - 2), lab, 22, INK, bold=not q['final_right'], anchor='lm')
    for i in (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        t(d, (L + (i - 0.5) * cell, Tp + len(qs) * rowh + 8), str(i), 16, INK2, anchor='mt')
    t(d, (L + n * cell / 2, Tp + len(qs) * rowh + 50), '第几个人', 20, INK2, anchor='mt')
    save(img, 'fig_20条队.png')


# ------------------------------------------------------------------ 图 3
def queue_panel(d, x0, y0, q, title, sub, show=20, you=7):
    t(d, (x0, y0), title, 30, bold=True)
    t(d, (x0, y0 + 46), sub, 21, INK2)
    better = q['better_shop']
    cw, ch_ = 52, 46
    gx = x0 + 150
    ry1, ry2 = y0 + 120, y0 + 120 + ch_ + 14
    t(d, (gx - 16, ry1 + ch_ / 2), '朋友说', 22, INK2, anchor='rm')
    t(d, (gx - 16, ry2 + ch_ / 2), '他排了', 22, INK2, anchor='rm')
    for i in range(show):
        p = q['people'][i]
        x = gx + i * cw
        for ry, key in ((ry1, 'signal'), (ry2, 'choice')):
            v = p[key]
            col = BLUE if v == better else ORANGE
            rrect(d, (x + 2, ry, x + cw - 2, ry + ch_), col, 4)
            t(d, (x + cw / 2, ry + ch_ / 2), v, 24, SURF, bold=True, anchor='mm')
        t(d, (x + cw / 2, ry2 + ch_ + 12), str(p['i']), 18, INK2, anchor='mt')
        if i + 1 == you:
            d.rounded_rectangle([(x - 2) * SS, (ry1 - 8) * SS, (x + cw + 2) * SS, (ry2 + ch_ + 40) * SS],
                                radius=8 * SS, outline=INK, width=3 * SS)
            t(d, (x + cw / 2, ry1 - 14), '你', 26, INK, bold=True, anchor='mb')
    lock = q['lock_at']
    if lock and lock <= show:
        x = gx + (lock - 1) * cw - 1
        d.line([(x * SS, (ry1 - 30) * SS), (x * SS, (ry2 + ch_ + 4) * SS)], fill=INK, width=3 * SS)
        t(d, (x - 8, ry1 - 30), '锁死', 20, INK, bold=True, anchor='rt')
    t(d, (gx + show * cw + 14, ry2 + ch_ / 2), f'… 一直到第 {q["n"]} 个', 20, INK2, anchor='lm')
    return ry2 + ch_ + 60


def fig_you(wrong_q, right_q, you):
    W, H = 1600, 1180
    img, d = canvas(W, H)
    x0 = 60
    t(d, (x0, 36), '同一个“你”，同一条朋友的话，同一个选择', 40, bold=True)
    t(d, (x0, 96), 'p = 0.6。字母是店名；蓝 = 好吃的那家，橙 = 不好吃的那家。两条队都在第 3 人锁死，你都排第 7，你朋友都说“隔壁好吃”。', 21, INK2)
    other = you['other_shop']
    y = 170
    y = queue_panel(d, x0, y, wrong_q,
                    f'这一次：排错了。好吃的是 {wrong_q["better_shop"]}，100 个人全排在 {wrong_q["final_shop"]}',
                    f'100 个人里，{wrong_q["n_signal_right"]} 个人的朋友说的是 {wrong_q["better_shop"]}（说对了）。'
                    f'凭自己朋友的话选的，只有前 {wrong_q["n_used_own_signal"]} 个，他俩的朋友都说错了。')
    y += 20
    y = queue_panel(d, x0, y, right_q,
                    f'另一次：排对了。好吃的是 {right_q["better_shop"]}，100 个人全排在 {right_q["final_shop"]}',
                    f'100 个人里，{right_q["n_locked_signal_other"]} 个人的朋友说的是隔壁（说错了），也都跟着排了。')
    # 你怎么算的
    y += 10
    t(d, (x0, y), '你在第 7 个。你怎么想：', 26, bold=True)
    lines = you['reasoning']
    for k, ln in enumerate(lines):
        t(d, (x0 + 20, y + 46 + k * 36), '· ' + ln, 22, INK)
    t(d, (x0, y + 46 + len(lines) * 36 + 16),
      '两次你算的都是 60%。你没算错，只是这一次落在了那 40% 里。', 22, INK2)
    save(img, 'fig_你.png')


# ------------------------------------------------------------------ 图 4
def fig_break(s):
    rows = s['breaking']['0.6']
    lab_short = {
        '基准：全是看队的人': '全是看队的人',
        '25% 的人只听自己；看队的人只数人头': '25% 只听自己，但别人只数人头',
        '10% 的人只听自己，但认不出是谁；看队的人会算': '10% 只听自己（认不出，别人会算）',
        '每 10 人有 1 个只听自己的人（大家知道他不看队）': '每 10 人 1 个只听自己（大家知道）',
        '每 10 人有 1 个把朋友的话说出来（照样跟队）': '每 10 人 1 个把朋友的话说出来',
        '25% 的人只听自己，但认不出是谁；看队的人会算': '25% 只听自己（认不出，别人会算）',
        '每 5 人有 1 个只听自己的人（大家知道他不看队）': '每 5 人 1 个只听自己（大家知道）',
        '每 5 人有 1 个把朋友的话说出来（照样跟队）': '每 5 人 1 个把朋友的话说出来',
        '每 2 人有 1 个只听自己的人（大家知道他不看队）': '每 2 人 1 个只听自己（大家知道）',
        '每个人都把朋友的话说出来': '每个人都把朋友的话说出来',
    }
    pick = [r for r in rows if r['label'] in lab_short]
    pick.sort(key=lambda r: -r['last_wrong']['rate'])
    W = 1600
    rowh = 62
    Tp = 270
    H = Tp + len(pick) * rowh + 150
    img, d = canvas(W, H)
    L = 470
    pw = 700
    xmax = 0.35
    X = lambda v: L + pw * v / xmax
    t(d, (60, 40), '怎么打破：让后面的人看得见“线索”，而不只是“人头”', 40, bold=True)
    t(d, (60, 100), 'p = 0.6，100 人一条队，每种做法 20 万条队。条 = 第 100 个人（看队的）排错店的比例；细线是 95% 区间。', 21, INK2)
    t(d, (60, 134), '右边两列：看队的人平均吃对的比例；“只听自己的人”或“说出来的人”自己吃对的比例。', 21, INK2)
    lx, ly = 60, 184
    for col, lab in ((ORANGE, '没有可用的新线索'), (BLUE, '有人只听自己，选择当线索'), (AQUA, '有人把朋友的话说出来，自己照样跟队')):
        rrect(d, (lx, ly - 9, lx + 18, ly + 9), col, 3)
        t(d, (lx + 26, ly), lab, 20, INK2, anchor='lm')
        lx += 26 + tw(d, lab, 20) + 34
    for v in (0, .1, .2, .3):
        d.line([(X(v) * SS, (Tp - 16) * SS), (X(v) * SS, (Tp + len(pick) * rowh) * SS)], fill=GRID, width=SS)
        t(d, (X(v), Tp + len(pick) * rowh + 12), f'{int(v * 100)}%', 20, INK2, anchor='mt')
    t(d, (L + pw / 2, Tp + len(pick) * rowh + 52), '第 100 个人排错店的比例', 21, INK2, anchor='mt')
    t(d, (L + pw + 70, Tp - 26), '看队的人', 20, INK2, anchor='mm')
    t(d, (L + pw + 70, Tp - 2), '吃对', 20, INK2, anchor='mm')
    t(d, (L + pw + 190, Tp - 26), '那些人', 20, INK2, anchor='mm')
    t(d, (L + pw + 190, Tp - 2), '自己吃对', 20, INK2, anchor='mm')
    for k, r in enumerate(pick):
        y = Tp + k * rowh
        base = r['label'].startswith('基准')
        col = ORANGE if base or '数人头' in r['label'] else (AQUA if '说出来' in r['label'] else BLUE)
        t(d, (L - 16, y + rowh / 2), lab_short[r['label']], 22, INK, bold=base, anchor='rm')
        v = r['last_wrong']['rate']
        rrect(d, (L, y + 14, X(v), y + rowh - 14), col, 4)
        lo, hi = r['last_wrong']['ci95']
        d.line([(X(lo) * SS, (y + rowh / 2) * SS), (X(hi) * SS, (y + rowh / 2) * SS)], fill=INK, width=2 * SS)
        t(d, (X(v) + 12, y + rowh / 2), f'{v * 100:.1f}%', 22, INK, bold=True, anchor='lm')
        t(d, (L + pw + 70, y + rowh / 2), f"{(1 - r['mean_wrong_herders']) * 100:.0f}%", 22, INK2, anchor='mm')
        sp = r['mean_wrong_special']
        t(d, (L + pw + 190, y + rowh / 2), f'{(1 - sp) * 100:.0f}%' if sp is not None else '—', 22, INK2, anchor='mm')
    yb = Tp + len(pick) * rowh + 96
    ctrl = s['base']['base_own_0.6']['control_independent']
    t(d, (60, yb), f"对照：100 个人谁也不看谁，各听各的朋友，多数人选错只有 {ctrl['analytic_majority_wrong'] * 100:.1f}%"
                   f"（另有 {ctrl['analytic_tie'] * 100:.1f}% 是 50:50）。", 21, INK2)
    save(img, 'fig_打破.png')


def main():
    os.makedirs(FIG, exist_ok=True)
    s = json.load(open(os.path.join(RES, 'summary.json')))
    fig_rate(s)
    fig_20(json.load(open(os.path.join(VIS, 'queues_20.json'))))
    fig_you(json.load(open(os.path.join(VIS, 'queue_排错.json'))), json.load(open(os.path.join(VIS, 'queue_排对.json'))),
            json.load(open(os.path.join(VIS, 'you.json'))))
    fig_break(s)


if __name__ == '__main__':
    main()
