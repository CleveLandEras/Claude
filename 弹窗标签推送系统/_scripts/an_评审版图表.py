#!/usr/bin/env python3
"""需求评审版的数据截图：示例数据 → 内联 SVG 图表 → 推送系统后台集成需求/需求评审版_原型/<名>.html。

用法：python3 _scripts/an_评审版图表.py [名 …]      不给名则生成全部
然后：node _scripts/pl_评审版截图.mjs <名 …>         截成 需求评审版_图/<名>.jpg

示例数据都写在本文件「示例数据」各段，改数字只改这里；漏斗、各段平均、合计、比率都由每日数据算出，
生成时打印自洽检查（漏斗逐步递减、各拆分相加等于合计、比率=分子/分母）。
趋势图 trend_svg() 可复用：按日柱（下格）＋比率线（上格，同一条 x 轴），竖线标改动与发版，竖线之间画段内平均。
不用双 y 轴（dataviz：两种量纲分两格，共用 x 轴与竖线）。时间为台湾时间。
"""
import datetime as dt
import html
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '推送系统后台集成需求' / '需求评审版_原型'

# ---------------------------------------------------------------- 配色（服从原型样式.css 的后台观感）
INK, INK2, MUTE = '#1F2329', '#4E5560', '#6B7280'
GRID, AXIS = '#EDEFF2', '#C9CED6'
ACC = '#1F63E0'          # 主数据：段内平均、漏斗、拆分、位次（原型样式 --acc）
ACC_LT = '#7FA3EA'       # 每日比率线（背景信息，比平均线浅）
BAR = '#BAC1CA'          # 每日曝光柱（背景信息）
CHG = '#4E5560'          # 规则改动竖线（实线）
REL, REL_BG, REL_TX = '#B26B00', '#FFF3DC', '#7A4A00'   # 客户端发版竖线（虚线）

E = html.escape


def tw(s, size):
    """估算文字宽度（px）：中文与全角 1em，数字约 0.6em。只用来排布，最终以渲染为准。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80 or ch in '：（），、；':
            w += size
        elif ch in ' ,.:·|':
            w += size * 0.3
        elif ch == '%':
            w += size * 0.85
        elif ch in '→▲▼':
            w += size * 0.9
        elif ch.isdigit():
            w += size * 0.62
        elif ch.isupper():
            w += size * 0.68
        else:
            w += size * 0.56
    return w


def fmt(n):
    return f'{n:,}'


def pct(x, d=1):
    return f'{x * 100:.{d}f}%'


def txt(x, y, s, size=12, fill=INK2, anchor='start', weight=None, halo=False, extra=''):
    a = f' font-size="{size}" fill="{fill}"'
    if anchor != 'start':
        a += f' text-anchor="{anchor}"'
    if weight:
        a += f' font-weight="{weight}"'
    if halo:
        a += ' stroke="#fff" stroke-width="4" stroke-linejoin="round" paint-order="stroke"'
    return f'<text x="{x:.1f}" y="{y:.1f}"{a}{extra}>{E(s)}</text>'


def col_path(x, y_top, w, y_base, r=3, fill=ACC):
    """柱：顶端 r 圆角，底端方角。"""
    h = y_base - y_top
    if h <= 0:
        return ''
    r = min(r, h, w / 2)
    return (f'<path d="M{x:.1f},{y_base:.1f} V{y_top + r:.1f} Q{x:.1f},{y_top:.1f} {x + r:.1f},{y_top:.1f} '
            f'H{x + w - r:.1f} Q{x + w:.1f},{y_top:.1f} {x + w:.1f},{y_top + r:.1f} V{y_base:.1f} Z" fill="{fill}"/>')


def hbar_path(x0, yc, length, th, r=3, fill=ACC):
    """横条：右端 r 圆角，左端（基线）方角。"""
    if length <= 0:
        return ''
    r = min(r, length, th / 2)
    y0, y1 = yc - th / 2, yc + th / 2
    x1 = x0 + length
    return (f'<path d="M{x0:.1f},{y0:.1f} H{x1 - r:.1f} Q{x1:.1f},{y0:.1f} {x1:.1f},{y0 + r:.1f} '
            f'V{y1 - r:.1f} Q{x1:.1f},{y1:.1f} {x1 - r:.1f},{y1:.1f} H{x0:.1f} Z" fill="{fill}"/>')


# ---------------------------------------------------------------- 时间与每日数据
D0 = dt.date(2026, 9, 13)          # 近 30 天：9/13–10/12（台湾时间）
N = 30
DAYS = [D0 + dt.timedelta(i) for i in range(N)]
PREV = (D0 - dt.timedelta(30), D0 - dt.timedelta(1))   # 前一个同样长度的周期：8/14–9/12


def md(d):
    return f'{d.month}/{d.day:02d}'


def ev_pos(e):
    """事件在 x 轴上的位置（以 D0 零点为 0，单位：天）。"""
    t = e['t']
    return (t.date() - D0).days + (t.hour + t.minute / 60) / 24


def gen_daily(events, base, levels, ctrs, *, wkend_expo, wkend_ctr, sd_expo, sd_ctr, seed):
    """按段生成每日曝光与点击。levels、ctrs 各有 len(events)+1 段；改动当天按改动时刻把前后两段加权。"""
    rnd = random.Random(seed)
    ev_days = {(e['t'].date() - D0).days: i for i, e in enumerate(events)}
    expo, clk = [], []
    seg = 0
    for i, d in enumerate(DAYS):
        if i in ev_days:
            k = ev_days[i]
            f = (ev_pos(events[k]) - i)
            lv = f * levels[k] + (1 - f) * levels[k + 1]
            ct = f * ctrs[k] + (1 - f) * ctrs[k + 1]
            seg = k + 1
        else:
            lv, ct = levels[seg], ctrs[seg]
        wk = d.weekday() >= 5
        x = base * lv * (1 + (wkend_expo if wk else 0)) * (1 + rnd.gauss(0, sd_expo))
        c = ct + (wkend_ctr if wk else 0) + rnd.gauss(0, sd_ctr)
        x = int(round(x / 10.0)) * 10
        expo.append(x)
        clk.append(int(round(x * c)))
    return expo, clk


def segments(events):
    """竖线之间的段：只取段内完整的日（改动、发版当天不计）。返回 [(首日序号, 末日序号)]，空段为 None。"""
    cuts = sorted((e['t'].date() - D0).days for e in events)
    out, start = [], 0
    for c in cuts + [N]:
        a, b = start, c - 1
        out.append((a, b) if b >= a else None)
        start = c + 1
    return out


# ---------------------------------------------------------------- 可复用：趋势图
def trend_svg(expo, clk, events, *, W=827, ctr_ticks, expo_ticks, ctr_h=176, expo_h=74, ctr_dec=1):
    """上格：每日比率线（浅）＋段内平均（深，标数字）；下格：每日曝光柱；竖线贯穿两格。
    events: [{'t': datetime, 'kind': 'chg'|'rel', 'tag': 竖线顶上的标签}]。返回 (svg, 各段平均列表)。"""
    n = len(expo)
    L, R = 52, 14
    pw = W - L - R
    bw = pw / n
    X = lambda v: L + v * bw
    # 竖线顶上的标签：重叠时错到第二行
    tags = []
    rows_end = [-1e9, -1e9]
    for e in sorted(events, key=ev_pos):
        x = X(ev_pos(e))
        w = max(tw(e['tag'], 11.5) + 14, 40)
        x0 = min(max(x - w / 2, L), W - R - w)
        row = 0 if x0 > rows_end[0] + 4 else 1
        rows_end[row] = x0 + w
        tags.append((e, x, x0, w, row))
    nrow = 1 + max((t[4] for t in tags), default=0)
    TAG_H = 18
    top = 6 + nrow * (TAG_H + 4) + 18           # 上格顶（留出纵轴名的一行）
    c_lo, c_hi = ctr_ticks[0], ctr_ticks[-1]
    Yc = lambda v: top + ctr_h - (v - c_lo) / (c_hi - c_lo) * ctr_h
    gap = 40
    e_top = top + ctr_h + gap                   # 下格顶
    e_max = expo_ticks[-1]
    Ye = lambda v: e_top + expo_h - v / e_max * expo_h
    base = e_top + expo_h
    H = base + 22
    s = [f'<svg class="ch-svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img">']
    # 格线与刻度
    for v in ctr_ticks:
        y = Yc(v)
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        s.append(txt(L - 8, y + 4, pct(v, ctr_dec), 11, MUTE, 'end'))
    for v in expo_ticks[1:]:
        y = Ye(v)
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        s.append(txt(L - 8, y + 4, fmt(v), 11, MUTE, 'end'))
    s.append(txt(L - 8, base + 4, '0', 11, MUTE, 'end'))
    s.append(txt(0, top - 16, '点击率', 12, INK2, weight='600'))
    s.append(txt(0, e_top - 16, '曝光', 12, INK2, weight='600'))
    # 下格：每日曝光柱
    cw = min(16.0, bw * 0.6)
    for i, v in enumerate(expo):
        s.append(col_path(X(i + .5) - cw / 2, Ye(v), cw, base, 2.5, BAR))
    s.append(f'<line x1="{L}" x2="{W - R}" y1="{base}" y2="{base}" stroke="{AXIS}"/>')
    # x 轴日期：每 3 天一个，再加最后一天
    for i in list(range(0, n, 3)) + [n - 1]:
        if i == n - 1 and (n - 1) % 3 and (n - 1) % 3 < 2:
            continue
        s.append(txt(X(i + .5), base + 16, md(DAYS[i]), 11, MUTE, 'middle'))
    # 竖线（先画，压在折线下面）
    for e, x, x0, w, row in tags:
        y_tag = 6 + row * (TAG_H + 4)
        if e['kind'] == 'rel':
            s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y_tag + TAG_H:.1f}" y2="{base:.1f}" stroke="{REL}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        else:
            s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y_tag + TAG_H:.1f}" y2="{base:.1f}" stroke="{CHG}" stroke-width="1.5"/>')
    # 上格：每日点击率（浅）
    ctr = [c / x for c, x in zip(clk, expo)]
    pts = ' '.join(f'{X(i + .5):.1f},{Yc(v):.1f}' for i, v in enumerate(ctr))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{ACC_LT}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>')
    # 段内平均（深，标数字）
    avgs = []
    for sg in segments(events):
        if not sg:
            avgs.append(None)
            continue
        a, b = sg
        av = sum(clk[a:b + 1]) / sum(expo[a:b + 1])
        avgs.append((a, b, av))
        y = Yc(av)
        s.append(f'<line x1="{X(a) + 2:.1f}" x2="{X(b + 1) - 2:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{ACC}" stroke-width="3" stroke-linecap="round"/>')
        s.append(txt((X(a) + X(b + 1)) / 2, y - 8, pct(av, ctr_dec + 0 if ctr_dec else 1), 12.5, INK, 'middle', '700', halo=True))
    # 标签（最上层）
    for e, x, x0, w, row in tags:
        y_tag = 6 + row * (TAG_H + 4)
        if e['kind'] == 'rel':
            s.append(f'<rect x="{x0:.1f}" y="{y_tag}" width="{w:.1f}" height="{TAG_H}" rx="9" fill="{REL_BG}" stroke="{REL}"/>')
            s.append(txt(x0 + w / 2, y_tag + 13, e['tag'], 11.5, REL_TX, 'middle', '600'))
        else:
            s.append(f'<rect x="{x0:.1f}" y="{y_tag}" width="{w:.1f}" height="{TAG_H}" rx="9" fill="{CHG}"/>')
            s.append(txt(x0 + w / 2, y_tag + 13, e['tag'], 11.5, '#fff', 'middle', '600'))
    s.append('</svg>')
    return '\n'.join(s), avgs


def legend_html():
    sw_bar = f'<svg width="10" height="12"><rect x="1" y="1" width="8" height="11" rx="1.5" fill="{BAR}"/></svg>'
    sw_ln = f'<svg width="20" height="10"><line x1="1" x2="19" y1="5" y2="5" stroke="{ACC_LT}" stroke-width="1.5"/></svg>'
    sw_av = f'<svg width="20" height="10"><line x1="2" x2="18" y1="5" y2="5" stroke="{ACC}" stroke-width="3" stroke-linecap="round"/></svg>'
    sw_c = f'<svg width="8" height="14"><line x1="4" x2="4" y1="0" y2="14" stroke="{CHG}" stroke-width="1.5"/></svg>'
    sw_r = f'<svg width="8" height="14"><line x1="4" x2="4" y1="0" y2="14" stroke="{REL}" stroke-width="1.5" stroke-dasharray="4 3"/></svg>'
    return ('<div class="ch-lg">'
            f'<span>{sw_bar}每日曝光</span><span>{sw_ln}每日点击率</span>'
            f'<span>{sw_av}两条竖线之间的平均点击率（不含竖线当天）</span>'
            f'<span>{sw_c}规则改动</span><span>{sw_r}客户端发版</span></div>')


def event_rows(events, with_rule=False):
    """图下的清单：每条竖线一行，按时间。"""
    cols = '10px 84px 136px minmax(0,1fr) 52px' if with_rule else '10px 84px minmax(0,1fr) 52px'
    out = [f'<div class="ch-ev" style="grid-template-columns:{cols}">']
    for e in sorted(events, key=ev_pos):
        pill = (f'<svg width="10" height="16"><line x1="5" x2="5" y1="0" y2="16" stroke="{REL}" stroke-width="1.5" stroke-dasharray="4 3"/></svg>'
                if e['kind'] == 'rel' else
                f'<svg width="10" height="16"><line x1="5" x2="5" y1="0" y2="16" stroke="{CHG}" stroke-width="1.5"/></svg>')
        t = f'{md(e["t"].date())} {e["t"]:%H:%M}'
        cells = [f'<span>{pill}</span>', f'<span class="t">{t}</span>']
        if with_rule:
            cells.append(f'<span>{E(e.get("rule", ""))}</span>')
        cells.append(f'<span>{E(e["what"])}</span>')
        cells.append(f'<span class="p">{E(e["who"])}</span>')
        out.append('<div>' + ''.join(cells) + '</div>')
    out.append('</div>')
    return '\n'.join(out)


# ---------------------------------------------------------------- 横条（漏斗、拆分）与柱形（位次）
def funnel_svg(rows, W=827):
    """rows: [(步骤, 人数, 次数或 None, 第一行说明, 第二行说明)]；横条长度＝人数。"""
    RH = 44
    LW, BX, BMAX = 92, 96, 170
    VX = BX + BMAX + 18
    NX = VX + 150
    H = RH * len(rows) + 4
    mx = rows[0][1]
    s = [f'<svg class="ch-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    for k, (name, ppl, times, l1, l2) in enumerate(rows):
        yc = k * RH + 14
        s.append(txt(0, yc + 5, name, 13, INK2))
        s.append(f'<line x1="{BX}" x2="{BX}" y1="{yc - 12}" y2="{yc + 12}" stroke="{AXIS}"/>')
        s.append(hbar_path(BX, yc, max(ppl / mx * BMAX, 2), 16, 3))
        s.append(txt(VX, yc + 5, f'{fmt(ppl)} 人', 14, INK, weight='700'))
        if times is not None:
            s.append(txt(VX + tw(f'{fmt(ppl)} 人', 14) + 10, yc + 5, f'{fmt(times)} 次', 12, MUTE))
        if l1:
            s.append(txt(NX, yc + 5, l1, 13, INK))
        if l2:
            s.append(txt(NX, yc + 24, l2, 12, MUTE))
    s.append('</svg>')
    return '\n'.join(s)


def hbars_svg(rows, *, vmax, W=827, LW=150, BMAX=420):
    """rows: [(名称, 比率, 右侧说明)]；按比率画横条，条端标比率，右栏标曝光。"""
    RH = 32
    BX = LW
    RX = W
    H = RH * len(rows)
    s = [f'<svg class="ch-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    s.append(f'<line x1="{BX}" x2="{BX}" y1="2" y2="{H - 2}" stroke="{AXIS}"/>')
    for k, (name, v, right) in enumerate(rows):
        yc = k * RH + RH / 2
        s.append(txt(0, yc + 4.5, name, 13, INK2))
        ln = v / vmax * BMAX
        s.append(hbar_path(BX, yc, ln, 16, 3))
        s.append(txt(BX + ln + 7, yc + 4.5, pct(v), 13, INK, weight='700'))
        s.append(txt(RX, yc + 4.5, right, 12.5, MUTE, 'end'))
    s.append('</svg>')
    return '\n'.join(s)


def cols_svg(rows, *, vmax, W=372, H=212):
    """rows: [(位次, 比率, 曝光)]；柱上标比率，柱下标位次与曝光。"""
    top, bot = 26, 44
    ph = H - top - bot
    base = top + ph
    slot = W / len(rows)
    cw = 24
    s = [f'<svg class="ch-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    s.append(f'<line x1="0" x2="{W}" y1="{base}" y2="{base}" stroke="{AXIS}"/>')
    for k, (name, v, ex) in enumerate(rows):
        cx = slot * k + slot / 2
        y = base - v / vmax * ph
        s.append(col_path(cx - cw / 2, y, cw, base, 4))
        s.append(txt(cx, y - 7, pct(v), 13, INK, 'middle', '700'))
        s.append(txt(cx, base + 18, name, 12.5, INK2, 'middle'))
        s.append(txt(cx, base + 35, f'曝光 {fmt(ex)}', 11.5, MUTE, 'middle'))
    s.append('</svg>')
    return '\n'.join(s)


def seg_html(items, on):
    return '<span class="seg">' + ''.join(
        f'<span{" class=\"on\"" if x == on else ""}>{E(x)}</span>' for x in items) + '</span>'


def page(title, body):
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{E(title)}</title>
<link rel="stylesheet" href="../原型样式.css">
<link rel="stylesheet" href="_图表.css">
</head>
<!-- 由 _scripts/an_评审版图表.py 生成，改数字请改脚本后重跑 -->
<body class="ch-page">
<div class="shot ch" style="width:980px"><div class="ch-z">
{body}
</div></div>
</body>
</html>
'''


def split_int(total, weights):
    """按权重把整数 total 分开，和恰好等于 total。"""
    raw = [total * w / sum(weights) for w in weights]
    out = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - out[i], reverse=True)[:total - sum(out)]:
        out[i] += 1
    return out


def split_clicks(total_clk, expos, ctrs):
    """按各项曝光×预设点击率分配点击，再整体缩放，使相加恰好等于合计点击。"""
    w = [e * c for e, c in zip(expos, ctrs)]
    return split_int(total_clk, w)


CHECKS = []


def check(cond, msg):
    CHECKS.append(('✔' if cond else '✘') + ' ' + msg)


# ================================================================ 示例数据：14 单条弹窗规则数据
R14 = dict(
    name='破产储值弹窗（实验组）', rid='ID 15',
    meta=['储值类弹窗', '破产弹窗', '优先级 1', '每次最多弹出 1 个', '对象：破产储值实验·实验组'],
)
EV14 = [   # 取自操作纪录（本规则的每一次保存）＋客户端发版
    dict(t=dt.datetime(2026, 9, 18, 10, 5), kind='chg', what='关闭后冷却：无 → 30 分钟', who='运营01'),
    dict(t=dt.datetime(2026, 9, 24, 15, 20), kind='chg', what='弹窗次数：破产礼包 每日 2 次 → 每日 1 次', who='运营02'),
    dict(t=dt.datetime(2026, 10, 6, 10, 0), kind='rel', what='客户端发版：App 3.8.2（iOS、Android）', who='—'),
    dict(t=dt.datetime(2026, 10, 9, 11, 30), kind='chg', what='弹窗排序：破产礼包 第 3 → 第 2', who='运营02'),
]
for e in EV14:
    e['tag'] = '发版' if e['kind'] == 'rel' else md(e['t'].date())
#                      段：  9/13–  9/18–  9/24–  10/06– 10/09–
EXPO14, CLK14 = gen_daily(EV14, 3150, [1.00, 0.91, 0.87, 0.88, 0.90],
                          [0.105, 0.117, 0.122, 0.119, 0.131],
                          wkend_expo=0.12, wkend_ctr=-0.002, sd_expo=0.035, sd_ctr=0.0025, seed=14)
F14 = dict(target=38600, enter=15210, ok=14380, expo_ppl=14290, clk_ppl=4620,      # 人数
           cap_block=14200, cd_block=5300, all_skip=3200, fail_show=190, no_report=1280)  # 次数；请求次数由曝光倒推
ITEMS14 = [('第 1　首储礼包', 0.40, 0.101), ('第 2　破产礼包', 0.23, 0.159), ('第 3　独享礼包', 0.19, 0.110),
           ('第 4　限时加码礼包', 0.10, 0.126), ('其余 4 项（第 5–8）', 0.08, 0.084)]
AFTER14 = '领取 980 人、1,020 次　·　购买 1,240 人、1,330 笔、NT$386,700'


def build_14():
    expo, clk = sum(EXPO14), sum(CLK14)
    f = F14
    ok_req = expo + f['fail_show'] + f['no_report']     # 符合条件（返回了排序项）的次数 = 曝光 + 显示失败 + 返回后未上报
    f['enter_req'] = ok_req + f['cap_block'] + f['cd_block'] + f['all_skip']   # 进入弹窗位置（请求）的次数
    no_report = f['no_report']
    rows = [
        ('目标人数', f['target'], None, '期间内属于对象群组的玩家', ''),
        ('进入弹窗位置', f['enter'], f['enter_req'], f'少 {fmt(f["target"] - f["enter"])} 人', '期间内没有破产'),
        ('符合条件', f['ok'], ok_req, f'少 {fmt(f["enter"] - f["ok"])} 人、{fmt(f["enter_req"] - ok_req)} 次',
         f'每人每天弹窗上限拦下 {fmt(f["cap_block"])} · 关闭后冷却中 {fmt(f["cd_block"])} · 排序项全部跳过 {fmt(f["all_skip"])}'),
        ('曝光', f['expo_ppl'], expo, f'少 {fmt(f["ok"] - f["expo_ppl"])} 人、{fmt(ok_req - expo)} 次',
         f'显示失败 {fmt(f["fail_show"])} · 返回后未上报 {fmt(no_report)}'),
        ('点击', f['clk_ppl'], clk, f'点击率 {pct(clk / expo)}', '点击次数 ÷ 曝光次数'),
    ]
    ppl = [r[1] for r in rows]
    tms = [r[2] for r in rows[1:]]
    check(all(a > b for a, b in zip(ppl, ppl[1:])), f'14 漏斗人数逐步递减 {ppl}')
    check(all(a > b for a, b in zip(tms, tms[1:])), f'14 漏斗次数逐步递减 {tms}')
    check(all(r[1] <= (r[2] or 10**9) for r in rows), '14 每步人数 ≤ 次数')
    check(no_report > 0, f'14 返回后未上报 {no_report} > 0')
    # 趋势图
    svg, avgs = trend_svg(EXPO14, CLK14, EV14, ctr_ticks=[0.09, 0.10, 0.11, 0.12, 0.13, 0.14],
                          expo_ticks=[0, 2000, 4000], ctr_dec=0)
    check(min(c / x for c, x in zip(CLK14, EXPO14)) > 0.09 and max(c / x for c, x in zip(CLK14, EXPO14)) < 0.14,
          '14 每日点击率都在纵轴 9%–14% 内')
    check(max(EXPO14) < 4000, f'14 每日曝光 {min(EXPO14)}–{max(EXPO14)} 在纵轴内')
    seg_txt = ' → '.join(pct(a[2]) if a else '—' for a in avgs)
    check(True, f'14 段内平均点击率 {seg_txt}（段内点击合计 ÷ 曝光合计）')
    # 按排序项
    ex_items = split_int(expo, [w for _, w, _ in ITEMS14])
    ck_items = split_clicks(clk, ex_items, [c for _, _, c in ITEMS14])
    check(sum(ex_items) == expo and sum(ck_items) == clk, '14 各排序项曝光、点击相加等于合计')
    item_rows = [(n, c / x, f'曝光 {fmt(x)}') for (n, _, _), x, c in zip(ITEMS14, ex_items, ck_items)]
    check(True, '14 各排序项点击率 ' + '、'.join(f'{n.split("　")[-1]} {pct(v)}' for n, v, _ in item_rows))
    meta = '<i>|</i>'.join(E(m) for m in R14['meta'])
    body = f'''<div class="ch-sec">
  <div class="ch-row"><div class="ch-ttl">{E(R14["name"])}<span class="pd-st">上架中</span><span class="pd-st">{R14["rid"]}</span></div><span class="ch-sp"></span><span class="btn2">编辑规则</span></div>
  <div class="ch-meta">{meta}</div>
</div>
<div class="ch-sec" style="padding-top:12px;padding-bottom:12px">
  <div class="ch-row">{seg_html(["今日", "近 7 天", "近 30 天", "自定义"], "近 30 天")}<span class="ch-m">{md(DAYS[0])}–{md(DAYS[-1])}</span></div>
</div>
<div class="ch-sec">
  <div class="ch-h">漏斗</div>
  {funnel_svg(rows)}
  <div class="ch-ref"><b>点击后 24 小时内</b><span class="ch-m">按来源弹窗规则计，只作参考</span>{E(AFTER14)}</div>
</div>
<div class="ch-sec">
  <div class="ch-h">按日趋势</div>
  {legend_html()}
  {svg}
  {event_rows(EV14)}
</div>
<div class="ch-sec">
  <div class="pd-tabs"><span class="pd-on">按排序项</span><span>按人群</span><span>按平台</span><span>实验组与对照组</span></div>
  <div class="ch-h" style="margin-bottom:6px">各排序项的点击率<span class="ch-m">排序项按现在的先后排列</span></div>
  {hbars_svg(item_rows, vmax=0.18)}
</div>'''
    return page('单条弹窗规则数据', body)


# ================================================================ 示例数据：13 游戏内推送数据（大厅弹窗）
EV13 = [   # 取自操作纪录（大厅弹窗上全部规则的保存）＋客户端发版
    dict(t=dt.datetime(2026, 9, 16, 14, 10), kind='chg', rule='5 活动类·其余', what='每次最多弹出：3 个 → 2 个', who='运营01'),
    dict(t=dt.datetime(2026, 9, 23, 11, 20), kind='chg', rule='12 活动类·新增玩家', what='弹窗排序：新手通行证 第 2 → 第 1', who='运营02'),
    dict(t=dt.datetime(2026, 9, 30, 16, 5), kind='chg', rule='14 活动类·潜在流失', what='关闭后冷却：无 → 60 分钟', who='运营01'),
    dict(t=dt.datetime(2026, 10, 6, 10, 0), kind='rel', rule='', what='客户端发版：App 3.8.2（iOS、Android）', who='—'),
    dict(t=dt.datetime(2026, 10, 12, 14, 36), kind='chg', rule='13 活动类·回流', what='弹窗排序：回流任务 第 7 → 第 1', who='运营02'),
]
for e in EV13:
    e['tag'] = '发版' if e['kind'] == 'rel' else '规则 ' + e['rule'].split()[0]
#                      段：  9/13–  9/16–  9/23–  9/30–  10/06– 10/12–
EXPO13, CLK13 = gen_daily(EV13, 47000, [1.00, 0.91, 0.91, 0.90, 0.905, 0.91],
                          [0.066, 0.0725, 0.0738, 0.0752, 0.0731, 0.0745],
                          wkend_expo=0.14, wkend_ctr=-0.0015, sd_expo=0.025, sd_ctr=0.0009, seed=13)
PPL13, PREV13 = 71400, dict(ppl=69900, expo=1361800, clk=94100)
POS13 = [('第 1 个', 0.404, 0.096), ('第 2 个', 0.307, 0.068), ('第 3 个', 0.182, 0.054), ('第 4 个及以后', 0.107, 0.043)]
RULES13 = [('12 活动类·新增玩家', 1, 0.122, 0.112), ('13 活动类·回流', 2, 0.151, 0.087), ('14 活动类·潜在流失', 3, 0.040, 0.074),
           ('5 活动类·其余', 4, 0.472, 0.066), ('6 通用弹窗', 5, 0.215, 0.060)]


def delta_pct(cur, prev):
    d = (cur - prev) / prev
    return ('▲ ' if d >= 0 else '▼ ') + f'{abs(d) * 100:.1f}%'


def build_13():
    expo, clk = sum(EXPO13), sum(CLK13)
    ctr, pctr = clk / expo, PREV13['clk'] / PREV13['expo']
    dpp = (ctr - pctr) * 100
    cards = [
        ('曝光人数', fmt(PPL13), '', delta_pct(PPL13, PREV13['ppl'])),
        ('曝光', fmt(expo), '', delta_pct(expo, PREV13['expo'])),
        ('点击', fmt(clk), '', delta_pct(clk, PREV13['clk'])),
        ('点击率', f'{ctr * 100:.1f}', '%', ('▲ ' if dpp >= 0 else '▼ ') + f'{abs(dpp):.1f} 个百分点'),
    ]
    check(PPL13 < expo, '13 曝光人数 < 曝光次数')
    check(True, f'13 合计 曝光 {fmt(expo)}、点击 {fmt(clk)}、点击率 {pct(ctr, 2)}；前 30 天 {pct(pctr, 2)}，差 {dpp:+.2f} 个百分点')
    svg, avgs = trend_svg(EXPO13, CLK13, EV13, ctr_ticks=[0.060, 0.065, 0.070, 0.075, 0.080, 0.085],
                          expo_ticks=[0, 30000, 60000])
    dctr = [c / x for c, x in zip(CLK13, EXPO13)]
    check(min(dctr) > 0.06 and max(dctr) < 0.085, f'13 每日点击率 {pct(min(dctr))}–{pct(max(dctr))} 在纵轴内')
    check(max(EXPO13) < 60000, f'13 每日曝光 {fmt(min(EXPO13))}–{fmt(max(EXPO13))} 在纵轴内')
    check(True, '13 段内平均 ' + ' → '.join(pct(a[2]) if a else '—（竖线后不满 1 天）' for a in avgs))
    ex_pos = split_int(expo, [w for _, w, _ in POS13])
    ck_pos = split_clicks(clk, ex_pos, [c for _, _, c in POS13])
    check(sum(ex_pos) == expo and sum(ck_pos) == clk, '13 各位次曝光、点击相加等于合计')
    pos_rows = [(n, c / x, x) for (n, _, _), x, c in zip(POS13, ex_pos, ck_pos)]
    check(all(a[1] > b[1] for a, b in zip(pos_rows, pos_rows[1:])), '13 位次越后点击率越低 ' + '、'.join(pct(r[1]) for r in pos_rows))
    ex_r = split_int(expo, [w for _, _, w, _ in RULES13])
    ck_r = split_clicks(clk, ex_r, [c for _, _, _, c in RULES13])
    check(sum(ex_r) == expo and sum(ck_r) == clk, '13 各规则曝光、点击相加等于合计')
    card_html = ''.join(
        f'<div class="ch-card"><div class="l">{E(l)}</div><div class="v">{v}<small>{u}</small></div>'
        f'<div class="d">比前 30 天 <b>{E(d)}</b></div></div>' for l, v, u, d in cards)
    trs = ''.join(
        f'<tr><td>{E(n)}</td><td class="pd-r">{p}</td><td class="pd-r">{fmt(x)}</td><td class="pd-r">{pct(c / x)}</td><td><span class="pd-lk">查看数据</span></td></tr>'
        for (n, p, _, _), x, c in zip(RULES13, ex_r, ck_r))
    body = f'''<div class="ch-sec" style="padding-top:12px;padding-bottom:12px">
  <div class="ch-row">{seg_html(["大厅弹窗", "破产弹窗", "快显"], "大厅弹窗")}<span style="width:14px"></span>{seg_html(["今日", "近 7 天", "近 30 天", "自定义"], "近 30 天")}<span class="ch-m">{md(DAYS[0])}–{md(DAYS[-1])}，与前 30 天（{md(PREV[0])}–{md(PREV[1])}）比</span></div>
</div>
<div class="ch-sec">
  <div class="ch-cards">{card_html}</div>
</div>
<div class="ch-sec">
  <div class="ch-h">按日趋势<span class="ch-m">竖线标出大厅弹窗上全部规则的改动与客户端发版</span></div>
  {legend_html()}
  {svg}
  {event_rows(EV13, with_rule=True)}
</div>
<div class="ch-sec">
  <div class="ch-2col">
    <div>
      <div class="ch-h">按位次<span class="ch-m">这次进入大厅时第几个看到，跨规则计</span></div>
      {cols_svg(pos_rows, vmax=0.11)}
    </div>
    <div>
      <div class="ch-h">规则</div>
      <table class="pd-dt"><thead><tr><th>规则</th><th class="pd-r">优先级</th><th class="pd-r">曝光</th><th class="pd-r">点击率</th><th></th></tr></thead>
      <tbody>{trs}</tbody></table>
    </div>
  </div>
</div>'''
    return page('游戏内推送数据', body)


BUILDERS = {'14_单条规则数据': build_14, '13_游戏内数据': build_13}

if __name__ == '__main__':
    names = sys.argv[1:] or list(BUILDERS)
    for n in names:
        (OUT / f'{n}.html').write_text(BUILDERS[n](), encoding='utf-8')
        print('写出', OUT / f'{n}.html')
    print('\n'.join(CHECKS))
    if any(c.startswith('✘') for c in CHECKS):
        sys.exit(1)
