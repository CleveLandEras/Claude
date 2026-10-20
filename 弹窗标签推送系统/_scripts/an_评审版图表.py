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


CW = 744   # 外框内容区宽 887 ÷ 缩放 1.12 − 左右内边距 48：图表按这个宽排


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
def trend_svg(bars, num, events, *, den=None, W=CW, top_ticks, bar_ticks, top_fmt, avg_fmt,
              top_title, bar_title, top_h=176, bar_h=74):
    """上格：每日折线（浅）＋两条竖线之间的平均（深，标数字）；下格：每日柱；两格共用 x 轴，竖线贯穿两格。
    上格的值＝num/den（比率，段内平均＝段内 num 合计 ÷ den 合计），不给 den 时为 num 本身（段内平均＝日均）。
    events: [{'t': datetime, 'kind': 'chg'|'rel', 'tag': 竖线顶上的标签}]；平均只取段内完整的日（竖线当天不计）。
    返回 (svg, 各段 (首日, 末日, 平均) 列表，空段为 None)。"""
    n = len(bars)
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
    c_lo, c_hi = top_ticks[0], top_ticks[-1]
    Yc = lambda v: top + top_h - (v - c_lo) / (c_hi - c_lo) * top_h
    gap = 46
    e_top = top + top_h + gap                   # 下格顶
    e_max = bar_ticks[-1]
    Ye = lambda v: e_top + bar_h - v / e_max * bar_h
    base = e_top + bar_h
    H = base + 22
    s = [f'<svg class="ch-svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img">']
    for v in top_ticks:
        y = Yc(v)
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        s.append(txt(L - 8, y + 4, top_fmt(v), 11, MUTE, 'end'))
    for v in bar_ticks[1:]:
        y = Ye(v)
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        s.append(txt(L - 8, y + 4, fmt(v), 11, MUTE, 'end'))
    s.append(txt(L - 8, base + 4, '0', 11, MUTE, 'end'))
    s.append(txt(0, top - 16, top_title, 12, INK2, weight='600'))
    s.append(txt(0, e_top - 16, bar_title, 12, INK2, weight='600'))
    cw = min(16.0, bw * 0.6)
    for i, v in enumerate(bars):
        s.append(col_path(X(i + .5) - cw / 2, Ye(v), cw, base, 2.5, BAR))
    s.append(f'<line x1="{L}" x2="{W - R}" y1="{base}" y2="{base}" stroke="{AXIS}"/>')
    for i in list(range(0, n, 3)) + [n - 1]:
        if i == n - 1 and (n - 1) % 3 and (n - 1) % 3 < 2:
            continue
        s.append(txt(X(i + .5), base + 16, md(DAYS[i]), 11, MUTE, 'middle'))
    for e, x, x0, w, row in tags:
        y_tag = 6 + row * (TAG_H + 4)
        dash = ' stroke-dasharray="4 3"' if e['kind'] == 'rel' else ''
        s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y_tag + TAG_H:.1f}" y2="{base:.1f}" stroke="{REL if e["kind"] == "rel" else CHG}" stroke-width="1.5"{dash}/>')
    vals = [a / b for a, b in zip(num, den)] if den else list(num)
    pts = ' '.join(f'{X(i + .5):.1f},{Yc(v):.1f}' for i, v in enumerate(vals))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{ACC_LT}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>')
    avgs = []
    for sg in segments(events):
        if not sg:
            avgs.append(None)
            continue
        a, b = sg
        av = sum(num[a:b + 1]) / sum(den[a:b + 1]) if den else sum(num[a:b + 1]) / (b - a + 1)
        avgs.append((a, b, av))
        y = Yc(av)
        s.append(f'<line x1="{X(a) + 2:.1f}" x2="{X(b + 1) - 2:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{ACC}" stroke-width="3" stroke-linecap="round"/>')
        s.append(txt((X(a) + X(b + 1)) / 2, y - 8, avg_fmt(av), 12.5, INK, 'middle', '700', halo=True))
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


def legend_html(bar='每日曝光', line='每日点击率', avg='两条竖线之间的平均点击率（不含竖线当天）',
                chg='规则改动', rel=True):
    sw_bar = f'<svg width="10" height="12"><rect x="1" y="1" width="8" height="11" rx="1.5" fill="{BAR}"/></svg>'
    sw_ln = f'<svg width="20" height="10"><line x1="1" x2="19" y1="5" y2="5" stroke="{ACC_LT}" stroke-width="1.5"/></svg>'
    sw_av = f'<svg width="20" height="10"><line x1="2" x2="18" y1="5" y2="5" stroke="{ACC}" stroke-width="3" stroke-linecap="round"/></svg>'
    sw_c = f'<svg width="8" height="14"><line x1="4" x2="4" y1="0" y2="14" stroke="{CHG}" stroke-width="1.5"/></svg>'
    sw_r = f'<svg width="8" height="14"><line x1="4" x2="4" y1="0" y2="14" stroke="{REL}" stroke-width="1.5" stroke-dasharray="4 3"/></svg>'
    return ('<div class="ch-lg">'
            f'<span>{sw_bar}{E(bar)}</span><span>{sw_ln}{E(line)}</span><span>{sw_av}{E(avg)}</span>'
            f'<span>{sw_c}{E(chg)}</span>' + (f'<span>{sw_r}App 发版</span>' if rel else '') + '</div>')


def event_rows(events, with_rule=False):
    """图下的清单：每条竖线一行，按时间。"""
    cols = '24px 98px 214px minmax(0,1fr) 52px' if with_rule else '24px 98px minmax(0,1fr) 52px'
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
def funnel_svg(rows, W=CW, unit='人', unit2='次', BMAX=170, VW=150):
    """rows: [(步骤, 数量, 第二个数量或 None, 第一行说明, 第二行说明)]；横条长度＝数量。"""
    RH = 44
    LW, BX = 92, 96
    VX = BX + BMAX + 18
    NX = VX + VW
    H = RH * len(rows) + 4
    mx = rows[0][1]
    s = [f'<svg class="ch-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    for k, (name, ppl, times, l1, l2) in enumerate(rows):
        yc = k * RH + 14
        s.append(txt(0, yc + 5, name, 13, INK2))
        s.append(f'<line x1="{BX}" x2="{BX}" y1="{yc - 12}" y2="{yc + 12}" stroke="{AXIS}"/>')
        s.append(hbar_path(BX, yc, max(ppl / mx * BMAX, 2), 16, 3))
        s.append(f'<text x="{VX}" y="{yc + 5}" font-size="14" fill="{INK}" font-weight="700">{fmt(ppl)} {unit}'
                 + (f'<tspan dx="10" font-size="12" fill="{MUTE}" font-weight="400">{fmt(times)} {unit2}</tspan>' if times is not None else '')
                 + '</text>')
        if l1:
            s.append(txt(NX, yc + 5, l1, 13, INK if l2 else MUTE))
        if l2:
            s.append(txt(NX, yc + 24, l2, 12, MUTE))
    s.append('</svg>')
    return '\n'.join(s)


def hbars_svg(rows, *, vmax, W=CW, LW=150, BMAX=420, vfmt=None):
    """rows: [(名称, 值, 旁注)]；横条长＝值，条端标值（默认按百分比），旁注紧跟其后。"""
    vfmt = vfmt or pct
    RH = 32
    BX = LW
    H = RH * len(rows)
    s = [f'<svg class="ch-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    s.append(f'<line x1="{BX}" x2="{BX}" y1="2" y2="{H - 2}" stroke="{AXIS}"/>')
    for k, (name, v, right) in enumerate(rows):
        yc = k * RH + RH / 2
        s.append(txt(0, yc + 4.5, name, 13, INK2))
        ln = v / vmax * BMAX
        s.append(hbar_path(BX, yc, ln, 16, 3))
        s.append(f'<text x="{BX + ln + 7:.1f}" y="{yc + 4.5:.1f}" font-size="13" fill="{INK}" font-weight="700">{vfmt(v)}'
                 + (f'<tspan dx="10" font-size="12.5" fill="{MUTE}" font-weight="400">{E(right)}</tspan>' if right else '') + '</text>')
    s.append('</svg>')
    return '\n'.join(s)


def cols_svg(rows, *, vmax, W=335, H=212):
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


# 外框（_后台框.js）：数据页在「数据」分组下；单条推送、单条弹窗规则是数据明细的下一层；页内切换的层、位置画成子导航
FRAME = {'数据概览': dict(page='数据概览'),
         '数据明细': dict(page='数据明细', subnav='*游戏外推送|游戏内推送'),
         '单条推送数据': dict(page='数据明细', crumb='推送 46'),
         '单条弹窗规则数据': dict(page='数据明细', crumb='弹窗规则 15'),
         '弹窗与快显位置数据': dict(page='弹窗与快显位置数据', subnav='*大厅弹窗|破产弹窗|快显'),
         '每人每天推送量': dict(page='每人每天推送量', subnav='*游戏外推送|游戏内推送')}


def page(title, body):
    attrs = ' '.join(f'data-{k}="{E(v)}"' for k, v in FRAME[title].items())
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{E(title)}</title>
<link rel="stylesheet" href="../原型样式.css">
<link rel="stylesheet" href="_图表.css">
<link rel="stylesheet" href="_后台框.css">
</head>
<!-- 由 _scripts/an_评审版图表.py 生成，改数字请改脚本后重跑 -->
<body class="ch-page">
<div class="shot ch bk" {attrs}><div class="ch-z">
{body}
</div></div>
<script src="_后台框.js"></script>
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
    name='破产储值弹窗（实验组）', rid='弹窗规则 15',
    meta=['储值类弹窗', '破产弹窗', '权重 30', '每次最多弹出 1 个', '对象：破产储值实验·实验组'],
)
EV14 = [   # 取自操作纪录（本规则的每一次保存）＋客户端发版
    dict(t=dt.datetime(2026, 9, 18, 10, 5), kind='chg', what='关闭后冷却：无 → 30 分钟', who='运营01'),
    dict(t=dt.datetime(2026, 9, 24, 15, 20), kind='chg', what='弹窗次数：破产礼包 每日 2 次 → 每日 1 次', who='运营02'),
    dict(t=dt.datetime(2026, 10, 6, 10, 0), kind='rel', what='App 发版：3.8.2（iOS、Android）', who='—'),
    dict(t=dt.datetime(2026, 10, 9, 11, 30), kind='chg', what='弹窗排序：破产礼包 第 3 → 第 2', who='运营02'),
]
for e in EV14:
    e['tag'] = '发版' if e['kind'] == 'rel' else md(e['t'].date())
#                      段：  9/13–  9/18–  9/24–  10/06– 10/09–
EXPO14, CLK14 = gen_daily(EV14, 3150, [1.00, 0.91, 0.87, 0.88, 0.90],
                          [0.105, 0.117, 0.122, 0.119, 0.131],
                          wkend_expo=0.12, wkend_ctr=-0.002, sd_expo=0.035, sd_ctr=0.0025, seed=14)
F14 = dict(enter=15210, ok=14380, expo_ppl=14290, clk_ppl=4620,      # 人数
           cap_block=14200, cd_block=5300, all_skip=3200, fail_show=190, no_report=1280)  # 次数；请求次数由曝光倒推
ITEMS14 = [('第 1　首储礼包', 0.40, 0.101), ('第 2　破产礼包', 0.23, 0.159), ('第 3　独享礼包', 0.19, 0.110),
           ('第 4　限时加码礼包', 0.10, 0.126), ('其余 4 项（第 5–8）', 0.08, 0.084)]


def build_14():
    expo, clk = sum(EXPO14), sum(CLK14)
    f = F14
    ok_req = expo + f['fail_show'] + f['no_report']     # 符合条件（返回了排序项）的次数 = 曝光 + 显示失败 + 返回后未上报
    f['enter_req'] = ok_req + f['cap_block'] + f['cd_block'] + f['all_skip']   # 进入弹窗位置（请求）的次数
    no_report = f['no_report']
    rows = [
        ('进入弹窗位置', f['enter'], f['enter_req'], '对象群组里期间内破产过的玩家', ''),
        ('符合条件', f['ok'], ok_req, f'少 {fmt(f["enter"] - f["ok"])} 人、{fmt(f["enter_req"] - ok_req)} 次',
         f'上限拦下 {fmt(f["cap_block"])} · 关闭后冷却中 {fmt(f["cd_block"])} · 排序项都跳过 {fmt(f["all_skip"])}'),
        ('曝光', f['expo_ppl'], expo, f'少 {fmt(f["ok"] - f["expo_ppl"])} 人、{fmt(ok_req - expo)} 次',
         f'弹出失败 {fmt(f["fail_show"])} · 弹出后未确认显示 {fmt(no_report)}'),
        ('点击', f['clk_ppl'], clk, f'点击率 {pct(clk / expo)}', '点击次数 ÷ 曝光次数'),
    ]
    ppl = [r[1] for r in rows]
    tms = [r[2] for r in rows]
    check(all(a > b for a, b in zip(ppl, ppl[1:])), f'14 漏斗人数逐步递减 {ppl}')
    check(all(a > b for a, b in zip(tms, tms[1:])), f'14 漏斗次数逐步递减 {tms}')
    check(all(r[1] <= (r[2] or 10**9) for r in rows), '14 每步人数 ≤ 次数')
    check(no_report > 0, f'14 返回后未上报 {no_report} > 0')
    # 趋势图
    svg, avgs = trend_svg(EXPO14, CLK14, EV14, den=EXPO14, top_ticks=[0.09, 0.10, 0.11, 0.12, 0.13, 0.14],
                          bar_ticks=[0, 2000, 4000], top_fmt=lambda v: pct(v, 0), avg_fmt=pct,
                          top_title='点击率', bar_title='曝光')
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
  {funnel_svg(rows, BMAX=130)}
</div>
<div class="ch-sec">
  <div class="ch-h">按日趋势</div>
  {legend_html()}
  {svg}
  {event_rows(EV14)}
</div>
<div class="ch-sec">
  <div class="pd-tabs"><span class="pd-on">按排序项</span><span>按人群</span><span>按平台</span></div>
  <div class="ch-h" style="margin-bottom:6px">各排序项的点击率<span class="ch-m">排序项按现在的先后排列</span></div>
  {hbars_svg(item_rows, vmax=0.18)}
</div>'''
    return page('单条弹窗规则数据', body)


# ================================================================ 示例数据：13 游戏内推送数据（大厅弹窗）
EV13 = [   # 取自操作纪录（大厅弹窗上全部规则的保存）＋客户端发版
    dict(t=dt.datetime(2026, 9, 16, 14, 10), kind='chg', rule='5 活动类·其余', what='每次最多弹出：3 个 → 2 个', who='运营01'),
    dict(t=dt.datetime(2026, 9, 23, 11, 20), kind='chg', rule='12 活动类·新增玩家', what='弹窗排序：新手通行证 第 2 → 第 1', who='运营02'),
    dict(t=dt.datetime(2026, 9, 30, 16, 5), kind='chg', rule='14 活动类·潜在流失', what='关闭后冷却：无 → 60 分钟', who='运营01'),
    dict(t=dt.datetime(2026, 10, 6, 10, 0), kind='rel', rule='', what='App 发版：3.8.2（iOS、Android）', who='—'),
    dict(t=dt.datetime(2026, 10, 12, 14, 36), kind='chg', rule='13 活动类·回流', what='弹窗排序：回流任务 第 7 → 第 1', who='运营02'),
]
for e in EV13:
    e['tag'] = '发版' if e['kind'] == 'rel' else '弹窗规则 ' + e['rule'].split()[0]
    if e['rule']:
        e['rule'] = '弹窗规则 ' + e['rule']
#                      段：  9/13–  9/16–  9/23–  9/30–  10/06– 10/12–
EXPO13, CLK13 = gen_daily(EV13, 47000, [1.00, 0.91, 0.91, 0.90, 0.905, 0.91],
                          [0.066, 0.0725, 0.0738, 0.0752, 0.0731, 0.0745],
                          wkend_expo=0.14, wkend_ctr=-0.0015, sd_expo=0.025, sd_ctr=0.0009, seed=13)
PPL13, PREV13 = 71400, dict(ppl=69900, expo=1361800, clk=94100)
POS13 = [('第 1 个', 0.404, 0.096), ('第 2 个', 0.307, 0.068), ('第 3 个', 0.182, 0.054), ('第 4 个及以后', 0.107, 0.043)]
#            规则, 权重（越大越靠前，与 10a 弹窗列表一致）, 曝光份额, 预设点击率, 曝光人数（各规则各自去重；合计行按玩家去重＝PPL13，小于各行相加）
RULES13 = [('12 活动类·新增玩家', 40, 0.122, 0.112, 9860), ('13 活动类·回流', 35, 0.151, 0.087, 14620),
           ('14 活动类·潜在流失', 30, 0.040, 0.074, 4130), ('5 活动类·其余', 20, 0.472, 0.066, 52340),
           ('6 储值类', 10, 0.215, 0.060, 38950)]


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
    svg, avgs = trend_svg(EXPO13, CLK13, EV13, den=EXPO13, top_ticks=[0.060, 0.065, 0.070, 0.075, 0.080],
                          bar_ticks=[0, 30000, 60000], top_fmt=pct, avg_fmt=pct,
                          top_title='点击率', bar_title='曝光')
    dctr = [c / x for c, x in zip(CLK13, EXPO13)]
    check(min(dctr) > 0.06 and max(dctr) < 0.08, f'13 每日点击率 {pct(min(dctr))}–{pct(max(dctr))} 在纵轴内')
    check(max(EXPO13) < 60000, f'13 每日曝光 {fmt(min(EXPO13))}–{fmt(max(EXPO13))} 在纵轴内')
    check(True, '13 段内平均 ' + ' → '.join(pct(a[2]) if a else '—（竖线后不满 1 天）' for a in avgs))
    ex_pos = split_int(expo, [w for _, w, _ in POS13])
    ck_pos = split_clicks(clk, ex_pos, [c for _, _, c in POS13])
    check(sum(ex_pos) == expo and sum(ck_pos) == clk, '13 各位次曝光、点击相加等于合计')
    pos_rows = [(n, c / x, x) for (n, _, _), x, c in zip(POS13, ex_pos, ck_pos)]
    check(all(a[1] > b[1] for a, b in zip(pos_rows, pos_rows[1:])), '13 位次越后点击率越低 ' + '、'.join(pct(r[1]) for r in pos_rows))
    ex_r = split_int(expo, [r[2] for r in RULES13])
    ck_r = split_clicks(clk, ex_r, [r[3] for r in RULES13])
    check(sum(ex_r) == expo and sum(ck_r) == clk, '13 各规则曝光、点击相加等于合计')
    ppl_sum = sum(r[4] for r in RULES13)
    check(PPL13 < ppl_sum and max(r[4] for r in RULES13) <= PPL13, f'13 合计曝光人数 {fmt(PPL13)} < 各规则相加 {fmt(ppl_sum)}（按玩家去重），且不小于任一行')
    check(all(r[4] < x for r, x in zip(RULES13, ex_r)), '13 各规则曝光人数 < 曝光次数')
    card_html = ''.join(
        f'<div class="ch-card"><div class="l">{E(l)}</div><div class="v">{v}<small>{u}</small></div>'
        f'<div class="d">比前 30 天 <b>{E(d)}</b></div></div>' for l, v, u, d in cards)
    trs = ''.join(
        f'<tr><td><span class="pd-lk">{E(r[0].split(" ", 1)[1])}</span><span class="pd-s2">弹窗规则 {r[0].split()[0]}</span></td><td class="pd-r">{r[1]}</td><td class="pd-r">{fmt(r[4])}</td><td class="pd-r">{fmt(x)}</td><td class="pd-r">{pct(c / x)}</td></tr>'
        for r, x, c in zip(RULES13, ex_r, ck_r))
    trs += (f'<tr class="pd-tot"><td>合计（按玩家去重）</td><td class="pd-r">—</td><td class="pd-r">{fmt(PPL13)}</td><td class="pd-r">{fmt(expo)}</td>'
            f'<td class="pd-r">{pct(ctr)}</td></tr>')
    body = f'''<div class="ch-sec" style="padding-top:14px;padding-bottom:12px">
  <div class="ch-ptitle">弹窗与快显位置数据</div>
  <div class="ch-row">{seg_html(["今日", "近 7 天", "近 30 天", "自定义"], "近 30 天")}<span class="ch-m">{md(DAYS[0])}–{md(DAYS[-1])}，与前 30 天（{md(PREV[0])}–{md(PREV[1])}）比</span></div>
</div>
<div class="ch-sec">
  <div class="ch-cards">{card_html}</div>
</div>
<div class="ch-sec">
  <div class="ch-h">按日趋势</div>
  {legend_html()}
  {svg}
  {event_rows(EV13, with_rule=True)}
</div>
<div class="ch-sec">
  <div class="ch-2col">
    <div>
      <div class="ch-h">按位次<span class="ch-m">这次进入大厅时第几个看到，跨规则计</span></div>
      {cols_svg(pos_rows, vmax=0.11, W=297)}
    </div>
    <div>
      <div class="ch-h">规则<span class="ch-m">点规则名看这条规则的数据</span></div>
      <table class="pd-dt"><thead><tr><th>规则</th><th class="pd-r">权重</th><th class="pd-r">曝光人数</th><th class="pd-r">曝光</th><th class="pd-r">点击率</th></tr></thead>
      <tbody>{trs}</tbody></table>
    </div>
  </div>
</div>'''
    return page('弹窗与快显位置数据', body)


# ================================================================ 通用：数字卡走势小图、分布柱、页面外框
def spark_svg(vals, w, h=26):
    """所选期间的每日走势小图：浅色面积＋折线，最后一天标点。"""
    lo, hi = min(vals), max(vals)
    if hi == lo:
        hi, lo = hi + 1, lo - 1
    pad = 4
    X = lambda i: pad + i * (w - 2 * pad) / (len(vals) - 1)
    Y = lambda v: pad + (h - 2 * pad) * (1 - (v - lo) / (hi - lo))
    pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
    area = f'{X(0):.1f},{h} ' + pts + f' {X(len(vals) - 1):.1f},{h}'
    xe, ye = X(len(vals) - 1), Y(vals[-1])
    return (f'<svg class="ch-svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.0f} {h}">'
            f'<polygon points="{area}" fill="{ACC}" fill-opacity="0.10"/>'
            f'<polyline points="{pts}" fill="none" stroke="{ACC}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="3" fill="{ACC}" stroke="#fff" stroke-width="2"/></svg>')


def dist_svg(rows, cap_after, cap_label, *, vmax, W=351, H=180):
    """每人每天收到几条的分布：rows [(条数, 占比)]；在第 cap_after 根柱之后画上限线。"""
    top, bot = 30, 24
    ph = H - top - bot
    base = top + ph
    L = 6
    slot = (W - L) / len(rows)
    cw = 24
    s = [f'<svg class="ch-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    s.append(f'<line x1="0" x2="{W}" y1="{base}" y2="{base}" stroke="{AXIS}"/>')
    xc = L + slot * cap_after
    s.append(f'<line x1="{xc:.1f}" x2="{xc:.1f}" y1="14" y2="{base}" stroke="{CHG}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    s.append(txt(xc + 6, 14, cap_label, 12, INK, weight='600'))
    for k, (name, v) in enumerate(rows):
        cx = L + slot * k + slot / 2
        y = base - v / vmax * ph
        s.append(col_path(cx - cw / 2, y, cw, base, 4))
        s.append(txt(cx, y - 7, pct(v), 13, INK, 'middle', '700'))
        s.append(txt(cx, base + 18, name, 12.5, INK2, 'middle'))
    s.append('</svg>')
    return '\n'.join(s)


def delta_pp(cur, prev):
    d = (cur - prev) * 100
    return ('▲ ' if d >= 0 else '▼ ') + f'{abs(d):.1f} 个百分点'


# ================================================================ 示例数据：06b 每人每天收到几条（近 30 天）
EV6B = [   # 取自操作纪录：每人每天上限与勿扰页的改动
    dict(t=dt.datetime(2026, 9, 22, 15, 30), kind='chg', what='勿扰时段：00:00–08:00 → 22:00–08:00', who='运营01'),
    dict(t=dt.datetime(2026, 10, 5, 10, 10), kind='chg', what='勿扰时段：22:00–08:00 → 00:00–08:00', who='运营01'),
]
for e in EV6B:
    e['tag'] = md(e['t'].date())


def gen_series(events, base, levels, *, wkend, sd, seed, step=10):
    """按段生成每日数量；竖线当天按时刻把前后两段加权。"""
    rnd = random.Random(seed)
    ev_days = {(e['t'].date() - D0).days: i for i, e in enumerate(events)}
    out, seg = [], 0
    for i, d in enumerate(DAYS):
        if i in ev_days:
            k = ev_days[i]
            f = ev_pos(events[k]) - i
            lv = f * levels[k] + (1 - f) * levels[k + 1]
            seg = k + 1
        else:
            lv = levels[seg]
        x = base * lv * (1 + (wkend if d.weekday() >= 5 else 0)) * (1 + rnd.gauss(0, sd))
        out.append(int(round(x / step)) * step)
    return out


def seg_of_day(events, i):
    k = 0
    for e in sorted(events, key=ev_pos):
        if (e['t'].date() - D0).days <= i:
            k += 1
    return k


# 推播：每天收到至少 1 条的玩家、各段的条数分布（1、2、3、4 条及以上）
RECV_P = gen_series([], 5600, [1.0], wkend=0.10, sd=0.03, seed=61)
SHARE_P = [[0.596, 0.312, 0.070, 0.022], [0.585, 0.355, 0.047, 0.013], [0.598, 0.311, 0.069, 0.022]]
CAP_P = gen_series(EV6B, 5600, [0.295, 0.368, 0.298], wkend=0.10, sd=0.035, seed=62)        # 碰到上限的人数
BLOCK_P = gen_series(EV6B, 5600, [0.165, 0.272, 0.168], wkend=0.10, sd=0.05, seed=63)       # 上限拦下人次
RECV_S = gen_series([], 860, [1.0], wkend=0.05, sd=0.05, seed=64)
SHARE_S = [0.962, 0.034, 0.004]
FOUR_PLUS = 4.25        # 「4 条及以上」的平均条数


def mean_p(seg):
    sh = SHARE_P[seg]
    return sh[0] * 1 + sh[1] * 2 + sh[2] * 3 + sh[3] * FOUR_PLUS


MEAN_S = SHARE_S[0] * 1 + SHARE_S[1] * 2 + SHARE_S[2] * 3.1
SEND_P = [round(RECV_P[i] * mean_p(seg_of_day(EV6B, i))) for i in range(N)]     # 推播每天发出条数
SEND_S = [round(r * MEAN_S) for r in RECV_S]


def build_06b():
    tot_p = sum(RECV_P)
    w = [sum(RECV_P[i] * SHARE_P[seg_of_day(EV6B, i)][k] for i in range(N)) for k in range(4)]
    cnt_p = split_int(tot_p, w)
    tot_s = sum(RECV_S)
    cnt_s = split_int(tot_s, SHARE_S)
    rows_p = [(f'{k} 条' if k < 4 else '4 条及以上', c / tot_p) for k, c in zip(range(1, 5), cnt_p)]
    rows_s = [(f'{k} 条' if k < 3 else '3 条及以上', c / tot_s) for k, c in zip(range(1, 4), cnt_s)]
    avg_p = sum(SEND_P) / tot_p
    avg_s = sum(SEND_S) / tot_s
    check(sum(cnt_p) == tot_p and sum(cnt_s) == tot_s, f'06b 分布相加＝收到至少 1 条的玩家·天（推播 {fmt(tot_p)}、短信 {fmt(tot_s)}）')
    check(all(b < c for b, c in zip(BLOCK_P, CAP_P)) or True, '06b 每天拦下人次与碰到上限人数并列，量级 ' +
          f'{fmt(min(BLOCK_P))}–{fmt(max(BLOCK_P))} / {fmt(min(CAP_P))}–{fmt(max(CAP_P))}')
    check(all(c < r for c, r in zip(CAP_P, RECV_P)), '06b 每天碰到上限的人数 < 当天收到的人数')
    svg, avgs = trend_svg(BLOCK_P, CAP_P, EV6B, top_ticks=[0, 1000, 2000, 3000], bar_ticks=[0, 1000, 2000],
                          top_fmt=fmt, avg_fmt=lambda v: fmt(int(round(v / 10.0)) * 10),
                          top_title='碰到上限的人数', bar_title='上限拦下人次', top_h=150)
    check(max(CAP_P) < 3000 and max(BLOCK_P) < 2000, '06b 每日数值在纵轴内')
    check(True, '06b 碰到上限日均 ' + ' → '.join(fmt(round(a[2])) for a in avgs if a))
    body = f"""<div class="ch-sec" style="padding-top:14px;padding-bottom:12px">
  <div class="ch-ptitle">每人每天推送量</div>
  <div class="ch-row">{seg_html(["今日", "近 7 天", "近 30 天", "自定义"], "近 30 天")}<span class="ch-m">{md(DAYS[0])}–{md(DAYS[-1])}</span></div>
</div>
<div class="ch-sec">
  <div class="ch-h">每人每天计入上限几条<span class="ch-m">近 30 天平均</span></div>
  <div class="ch-2col eq">
    <div>
      <div class="ch-sub"><b>推播</b><span class="ch-m">占当天收到推播的玩家</span></div>
      {dist_svg(rows_p, 2, '每人每天上限 2 条', vmax=0.70)}
    </div>
    <div>
      <div class="ch-sub"><b>短信</b><span class="ch-m">占当天收到短信的玩家</span></div>
      {dist_svg(rows_s, 1, '每人每天上限 1 条', vmax=1.12)}
    </div>
  </div>
  <div class="ch-note">超过上限的是勾了「不受每人每天上限」、仍计入当天条数的推送；服务通知不计入，不在图里。</div>
</div>
<div class="ch-sec">
  <div class="ch-h">碰到上限</div>
  <div class="ch-row" style="margin:-2px 0 8px">{seg_html(["推播", "短信"], "推播")}</div>
  {legend_html(bar='每日上限拦下人次', line='每日碰到上限的人数', avg='两条竖线之间的日均人数（不含竖线当天）', chg='设置改动', rel=False)}
  {svg}
  {event_rows(EV6B)}
</div>"""
    return page('每人每天推送量', body)


# ================================================================ 示例数据：06 概览、00 后台首页（近 7 天 10/06–10/12，对比 9/29–10/05）
CUR7, PRV7 = range(23, 30), range(16, 23)
RULE7_EXPO = [round(x * 0.97 / 10) * 10 for x in EXPO14]             # 破产弹窗的另一条规则 7（对照组那一半）
RULE7_CLK = [round(x * (0.106 if i < 23 else 0.117)) for i, x in enumerate(RULE7_EXPO)]
QS_EXPO = gen_series([], 1980, [1.0], wkend=0.08, sd=0.04, seed=71)  # 快显
QS_CLK = [round(x * (0.098 if i < 23 else 0.128)) for i, x in enumerate(QS_EXPO)]   # 快显 10/06 起换了文案


def ov_data():
    """两层的数字：游戏外取 06b 的推播、短信每日数据，游戏内取 13（大厅弹窗）、14（破产弹窗）的每日数据加快显。"""
    rnd = random.Random(72)
    send = [SEND_P[i] + SEND_S[i] for i in range(N)]
    ios = [round(SEND_P[i] * 0.083) for i in range(N)]                       # iOS 未接入（不进到达率分母）
    arr = [round((send[i] - ios[i]) * (0.926 + rnd.gauss(0, 0.004))) for i in range(N)]
    clk = [round(send[i] * (0.0556 + rnd.gauss(0, 0.0012))) for i in range(N)]
    pdays = [RECV_P[i] + round(RECV_S[i] * 0.55) for i in range(N)]          # 当天收到至少 1 条的玩家
    arr_ppl = [round(pdays[i] * 0.93) for i in range(N)]
    pop = [EXPO13[i] + EXPO14[i] + RULE7_EXPO[i] for i in range(N)]           # 弹窗曝光（大厅＋破产）
    ex = [pop[i] + QS_EXPO[i] for i in range(N)]
    ck = [CLK13[i] + CLK14[i] + RULE7_CLK[i] + QS_CLK[i] for i in range(N)]
    viewers = [round(pop[i] / (4.86 + rnd.gauss(0, 0.05))) for i in range(N)]  # 当天看到至少 1 个弹窗的玩家
    ex_ppl = [v + 310 for v in viewers]
    S = lambda a, r: sum(a[i] for i in r)
    out = {}
    for key, r in (('cur', CUR7), ('prv', PRV7)):
        d = dict(send=S(send, r), arr=S(arr, r), ios=S(ios, r), clk=S(clk, r),
                 arr_ppl=round(S(arr_ppl, r) * (0.62 if key == 'cur' else 0.615)),
                 per=S(send, r) / S(pdays, r),
                 ex=S(ex, r), ck=S(ck, r), ex_ppl=round(S(ex_ppl, r) * (0.68 if key == 'cur' else 0.675)),
                 per_pop=S(pop, r) / S(viewers, r))
        d['arr_rate'] = d['arr'] / (d['send'] - d['ios'])
        d['ctr_out'] = d['clk'] / d['send']
        d['ctr_in'] = d['ck'] / d['ex']
        out[key] = d
    sp = lambda a: [a[i] for i in CUR7]
    out['spark'] = dict(send=sp(send), arr=sp(arr), clk=sp(clk), arr_ppl=sp(arr_ppl),
                        per=[send[i] / pdays[i] for i in CUR7], ex_ppl=sp(ex_ppl), ex=sp(ex), ck=sp(ck),
                        ctr_in=[ck[i] / ex[i] for i in CUR7], per_pop=[pop[i] / viewers[i] for i in CUR7])
    return out


_OV_CHECKED = []


def ov_cards(spark_w):
    d = ov_data()
    first = not _OV_CHECKED
    _OV_CHECKED.append(1)
    chk = check if first else (lambda *a: None)
    c, p, sp = d['cur'], d['prv'], d['spark']
    out_cards = [
        ('发送', fmt(c['send']), '', '', delta_pct(c['send'], p['send']), sp['send']),
        ('到达', fmt(c['arr']), '', f'另有 iOS 未接入 {fmt(c["ios"])}', delta_pct(c['arr'], p['arr']), sp['arr']),
        ('点击', fmt(c['clk']), '', '', delta_pct(c['clk'], p['clk']), sp['clk']),
        ('到达人数', fmt(c['arr_ppl']), '', '按玩家去重', delta_pct(c['arr_ppl'], p['arr_ppl']), sp['arr_ppl']),
        ('人均每天收到', f'{c["per"]:.1f}', ' 条', '按当天收到的玩家', delta_pct(c['per'], p['per']), sp['per']),
    ]
    in_cards = [
        ('曝光人数', fmt(c['ex_ppl']), '', '按玩家去重', delta_pct(c['ex_ppl'], p['ex_ppl']), sp['ex_ppl']),
        ('曝光', fmt(c['ex']), '', '', delta_pct(c['ex'], p['ex']), sp['ex']),
        ('点击', fmt(c['ck']), '', '', delta_pct(c['ck'], p['ck']), sp['ck']),
        ('点击率', f'{c["ctr_in"] * 100:.1f}', '%', '', delta_pp(c['ctr_in'], p['ctr_in']), sp['ctr_in']),
        ('人均每天弹窗曝光', f'{c["per_pop"]:.1f}', ' 个', '按当天看到的玩家', delta_pct(c['per_pop'], p['per_pop']), sp['per_pop']),
    ]
    chk(abs(c['arr'] / (c['send'] - c['ios']) - c['arr_rate']) < 1e-9, f'06 到达率可由卡上数字复算：{fmt(c["arr"])} ÷ ({fmt(c["send"])} − {fmt(c["ios"])}) = {pct(c["arr_rate"])}')
    chk(c['arr'] < c['send'] - c['ios'] and c['clk'] < c['send'], f'06 游戏外 发送 {fmt(c["send"])} > 到达 {fmt(c["arr"])}（另 iOS 未接入 {fmt(c["ios"])}）> 点击 {fmt(c["clk"])}')
    chk(c['arr_ppl'] < c['arr'], f'06 到达人数 {fmt(c["arr_ppl"])} < 到达条数')
    chk(c['ex_ppl'] < c['ex'] and c['ck'] < c['ex'], f'06 游戏内 曝光 {fmt(c["ex"])}、点击 {fmt(c["ck"])}、点击率 {pct(c["ctr_in"], 2)}、曝光人数 {fmt(c["ex_ppl"])}（13 的 30 天大厅曝光人数 {fmt(PPL13)}）')
    chk(True, f'06 到达率 {pct(c["arr_rate"])}、游戏外点击率 {pct(c["ctr_out"])}、人均每天收到 {c["per"]:.2f} 条、人均每天弹窗曝光 {c["per_pop"]:.2f} 个')

    def card(l, v, u, sub, dl, vals):
        return (f'<div class="ch-card"><div class="l">{E(l)}</div><div class="v">{v}<small>{E(u)}</small></div>'
                f'<div class="s">{"<br>".join(E(x) for x in sub.split(chr(10))) or "&nbsp;"}</div><div class="d"><b>{E(dl)}</b></div>{spark_svg(vals, spark_w)}</div>')
    return ''.join(card(*x) for x in out_cards), ''.join(card(*x) for x in in_cards)


def ov_parts(spark_w):
    oc, ic = ov_cards(spark_w)
    flt = (f'<div class="ch-row">{seg_html(["今日", "近 7 天", "近 30 天", "自定义"], "近 7 天")}'
           f'<span class="ch-m">{md(DAYS[CUR7[0]])}–{md(DAYS[CUR7[-1]])}，与前 7 天（{md(DAYS[PRV7[0]])}–{md(DAYS[PRV7[-1]])}）比</span></div>')
    # 游戏外跨推送方式只给数量，比率按推送方式给（需求文档 4.1.8 第 22、99 行）；按推送方式的数取 09 数据明细同期各行
    def by_way(w):
        rs = [r for r in ROWS09 if r[3] == w]
        sent, ios, arr, clk = (sum(r[k] or 0 for r in rs) for k in (9, 10, 11, 12))
        return f'<tr><td>{w}</td><td class="pd-r">{fmt(sent)}</td><td class="pd-r">{pct(arr / (sent - ios))}</td><td class="pd-r">{pct(clk / sent)}</td></tr>'
    way_tbl = ('<table class="pd-dt ch-tbl" style="margin-top:10px;width:auto"><thead><tr><th>按推送方式</th><th class="pd-r">发送</th>'
               '<th class="pd-r">到达率</th><th class="pd-r">点击率</th></tr></thead><tbody>' + by_way('推播') + by_way('短信') + '</tbody></table>')
    l1 = ('<div class="ch-lh"><b>游戏外推送</b><span>推播、短信</span><span class="ch-m">从发送算起；卡片只给数量，比率按推送方式看</span></div>'
          f'<div class="ch-cards c5">{oc}</div>{way_tbl}')
    l2 = ('<div class="ch-lh"><b>游戏内推送</b><span>弹窗、快显</span><span class="ch-m">从曝光算起，点击率＝点击 ÷ 曝光</span></div>'
          f'<div class="ch-cards c5">{ic}</div>')
    return flt, l1, l2


def build_06():
    flt, l1, l2 = ov_parts(124)
    body = f"""<div class="ch-sec" style="padding-top:14px;padding-bottom:12px">
  <div class="ch-ptitle">数据概览</div>
  {flt}
</div>
<div class="ch-sec">
  {l1}
</div>
<div class="ch-sec">
  {l2}
</div>"""
    return page('数据概览', body)


# 00 后台首页的左侧菜单、面包屑、页签由 需求评审版_原型/_后台框.js 统一画（全部截图共用一份菜单）




# ================================================================ 示例数据：02b 确认发送前的预计人数（第 1 页的推播：潜在流失两档）
F02B = [   # 与 02_新建推播 的预计人数一致；定时推送不预估每人每天上限拦下（到点按当时扣除），所以没有「预计发出」一层
    ('群组人数', 7880, '潜在流失（两档）', ''),
    ('受众', 7850, '少 30 人', '排除群组：VIP 名单 12 · 黑名单 3 · 机器人与测试账号 7 · 敏感状态账号 8'),
    ('能收到', 4310, '少 3,540 人', '收不到推播：没装 App 2,860 · 通知关闭 660 · 同一设备只发 1 条 20'),
]


def build_02b():
    v = [r[1] for r in F02B]
    check(all(a > b for a, b in zip(v, v[1:])), f'02b 逐层递减 {v}')
    check(v[0] - v[1] == 12 + 3 + 7 + 8 and v[1] - v[2] == 2860 + 660 + 20, '02b 每层少的人数＝各原因相加')
    rows = [(n, x, None, l1, l2) for n, x, l1, l2 in F02B]
    # 新建推播页的下半段「确认与测试」；外框由 _后台框.js 画（与 02_新建推播 同一页）
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>确认前的预计人数</title>
<link rel="stylesheet" href="../原型样式.css">
<link rel="stylesheet" href="_图表.css">
<link rel="stylesheet" href="_后台框.css">
</head>
<!-- 由 _scripts/an_评审版图表.py 生成，改数字请改脚本后重跑 -->
<body class="ch-page">
<div class="shot ch bk" data-page="推播" data-crumb="新建推播" data-tabs="*推播列表|操作纪录"><div class="ch-z">
<div class="ch-sec">
  <div class="ch-h">确认与测试<span class="ch-m">预计人数截至 10/12 15:25</span></div>
  {funnel_svg(rows, W=744, BMAX=170, VW=104)}
  <div class="ch-m" style="margin-top:2px">定时推送每次到点按当时的群组名单发，每人每天上限也按当时扣除</div>
</div>
<div class="ch-sec">
  <div class="ch-kv">
    <span>发送时间</span><span>定时 10/17 19:00 起每周六，重复至 12/26，共 11 次</span>
    <span>发送对象</span><span>潜在流失（两档）；排除 VIP 名单、黑名单、机器人与测试账号、敏感状态账号</span>
    <span>重要程度</span><span>重要：每次发送当天为 4,310 人预留推播 1 条，当天更早的普通推送预计多拦下约 260 人</span>
    <span>测试</span><span>上次测试 10/12 11:12 · 运营01 · 5 个测试账号：已发出 4，未送达 1（测试03 未开启通知）</span>
  </div>
  <div class="ch-row ch-btns"><span class="ch-m">取消</span><span class="ch-sp"></span><span class="btn2">存为草稿</span><span class="btn2">发送测试</span><span class="btn2 p">确认发送</span></div>
</div>
</div></div>
<script src="_后台框.js"></script>
</body>
</html>
'''


# ================================================================ 示例数据：07 单条推送数据（推送 46，定时推播，正常发完）
# 号码与第 12 页操作纪录里的 31、43、44 不同；所属活动「周末登录送金币」（09 数据明细里同一行）。
# 一次性推送，每人最多 1 条，漏斗全程按人。定时 19:00 不在勿扰时段，没有勿扰顺延。
P07 = dict(aud=16240, reject=41, bounce=22, no_receipt=310, ios=705, clk=612,
           login=3980)
NOTSENT07 = [('没装 App', 5410), ('通知关闭', 2130), ('每人每天上限拦下', 460)]
REJECT07 = [('设备已失效（App 卸载或重装）', 37), ('内容不符合服务商要求', 4)]


def build_07():
    f = P07
    sent = f['aud'] - sum(n for _, n in NOTSENT07) - f['reject']
    arr = sent - f['bounce'] - f['no_receipt'] - f['ios']
    arr_rate = arr / (sent - f['ios'])
    ctr = f['clk'] / sent
    pre = sum(n for nm, n in NOTSENT07 if nm in ('没装 App', '通知关闭'))
    check(f['aud'] - sent == sum(n for _, n in NOTSENT07) + f['reject'], '07 受众 − 发送＝未发出各原因＋服务商未受理')
    check(sum(n for _, n in REJECT07) == f['reject'], '07 服务商未受理分项相加')
    check(f['aud'] > sent > arr > f['clk'], f'07 漏斗（人）递减 {f["aud"]} → {sent} → {arr} → {f["clk"]}；到达率 {pct(arr_rate)}、点击率 {pct(ctr)}')
    check(f['login'] < sent, '07 24 小时内登录人数 < 发送人数')
    noapp, off, cap = (n for _, n in NOTSENT07)
    rows = [
        ('受众', f['aud'], None, '发送对象扣掉排除群组', ''),
        ('发送', sent, None, f'少 {fmt(f["aud"] - sent)} 人',
         f'收不到推播 {fmt(pre)} · 每人每天上限拦下 {cap} · 服务商未受理 {f["reject"]}'),
        ('到达', arr, None, f'少 {fmt(sent - arr)} 人 · 到达率 {pct(arr_rate)}',
         f'服务商退回 {f["bounce"]} · 结果不明 {f["no_receipt"]} · iOS 未接入 {f["ios"]}（不进分母）'),
        ('点击', f['clk'], None, f'点击率 {pct(ctr)}', '点击 ÷ 发送'),
    ]
    blk = sorted(NOTSENT07, key=lambda x: -x[1])
    body = f"""<div class="ch-sec">
  <div class="ch-row"><div class="ch-ttl">周末登录送金币提醒<span class="pd-st">已完成</span><span class="pd-st">推送 46</span></div></div>
  <div class="ch-meta">推播<i>|</i>定时 10/10 19:00<i>|</i>发送对象：回流；排除 VIP 名单、黑名单、机器人与测试账号、敏感状态账号</div>
</div>
<div class="ch-sec">
  <div class="ch-h">漏斗</div>
  {funnel_svg(rows, BMAX=120, VW=104)}
  <div class="ch-ref"><b>发送后 24 小时内</b><span class="ch-m">推播只作参考</span>登录 {fmt(f["login"])} 人</div>
</div>
<div class="ch-sec">
  <div class="ch-2col w07">
    <div>
      <div class="ch-h">未发出的原因<span class="ch-m">从多到少，单位：人</span><span class="ch-sp"></span><span class="btn2 sm">导出名单</span></div>
      {hbars_svg([(n, x, '') for n, x in blk], vmax=5600, W=396, LW=118, BMAX=220, vfmt=fmt)}
    </div>
    <div>
      <div class="ch-h">服务商未受理<span class="ch-m">{f["reject"]} 人</span></div>
      {hbars_svg([(n, x, '') for n, x in REJECT07], vmax=40, W=312, LW=196, BMAX=80, vfmt=fmt)}
    </div>
  </div>
</div>"""
    return page('单条推送数据', body)

# ================================================================ 示例数据：09 数据明细（游戏外推送一层，近 7 天 10/06–10/12，按发送时间倒序）
# 近 7 天游戏外推送共 11 条，一页列完；11 条的发送、到达、点击、iOS 未接入合计正好等于 06 数据概览的同期数字（表末合计行）。
# 推送 46 与 07 一致；43、44、31 与第 12 页操作纪录一致（43 在 15:04 停止，已发出 1,050；44 服务商未受理，发送失败；31 按行为）。
# 按行为的两条：发送时间写生效起始日，各数只算所选期间内的发送。
# 每行：编号、名称、状态、推送方式、所属活动、发送时间（方式）、发送时间（时刻）、发送对象、受众、发送、iOS 未接入、到达、点击（无点击链接为 None）
FIXED09 = {   # 由别处定死的行
    46: (8199, 705, 7162, 612),     # 07
    43: (1050, 92, 921, 84),        # 第 12 页：已发出 1,050 后停止
    44: (0, 0, 0, 0),               # 第 12 页：服务商未受理，发送失败
}
BASE09 = [   # 其余各行的相对大小（发送、iOS 未接入、到达、点击），按 06 的合计等比放大
    (47, '回流礼包 B 加码通知', '发送中', '推播', '回流礼包 B', '立即', '10/12 15:20', '回流', 16240, (8230, 708, 7190, 395)),
    (43, '月月抽开奖提醒', '已停止', '推播', '月月抽', '定时', '10/12 15:00', '月月抽本期参与者', 6820, None),
    (44, '限时挑战开启', '发送失败', '推播', '限时挑战', '定时', '10/12 14:00', '近 7 天登录', 14380, None),
    (45, '中秋排名赛结算倒数', '已完成', '推播', '中秋排名赛', '定时', '10/11 20:00', '中秋排名赛参与者', 9860, (5540, 470, 4980, 277)),
    (46, '周末登录送金币提醒', '已完成', '推播', '周末登录送金币', '定时', '10/10 19:00', '回流', 16240, None),
    (41, '回流礼包 B 限时上架', '已完成', '短信', '回流礼包 B', '定时', '10/10 12:00', '回流', 16240, (3410, 0, 3268, 150)),
    (39, '中秋排名赛冲榜提醒', '已完成', '短信', '中秋排名赛', '定时', '10/08 20:00', '中秋排名赛参与者', 9420, (2450, 0, 2371, 74)),
    (37, '周年庆预告', '已完成', '推播', '周年庆', '定时', '10/08 19:30', '近 30 天登录', 22310, (13920, 1180, 12410, 640)),
    (40, '账号安全验证通知', '已完成', '短信', '不属于活动', '立即', '10/07 16:20', '上传名单', 1720, (1248, 0, 1231, None)),
    (31, '限时加码礼包未购买提醒', '运行中', '推播', '限时加码礼包', '按行为', '9/20 起', '触发的玩家', 8652, (3617, 313, 3133, 290)),
    (33, '任务完成奖励提醒', '运行中', '推播', '每日任务', '按行为', '9/01 起', '触发的玩家', 12940, (6730, 520, 5960, 404)),
]


def rows09():
    oc = ov_data()['cur']
    target = (oc['send'], oc['ios'], oc['arr'], oc['clk'])
    free = [b for b in BASE09 if b[0] not in FIXED09]
    cols = []
    for k in range(4):
        need = target[k] - sum(v[k] for v in FIXED09.values())
        ws = [b[9][k] or 0 for b in free]
        cols.append(split_int(need, ws))
    scaled = {b[0]: tuple(cols[k][n] if b[9][k] is not None else None for k in range(4)) for n, b in enumerate(free)}
    out = []
    for b in BASE09:
        v = FIXED09.get(b[0]) or scaled[b[0]]
        out.append(b[:9] + v)
    return out


ROWS09 = rows09()


def sort_icon(active=False):
    up = '#C0C5CC'
    dn = INK if active else '#C0C5CC'
    return (f'<svg class="ch-si" width="8" height="11" viewBox="0 0 8 11"><path d="M4 0 L8 4 H0 Z" fill="{up}"/>'
            f'<path d="M4 11 L8 7 H0 Z" fill="{dn}"/></svg>')


def when_html(mode, when):
    """发送时间一格：立即／定时后跟时刻；按行为另起一行写最近一次。"""
    return f'{mode} {E(when)}'


def build_09():
    r46 = [r for r in ROWS09 if r[0] == 46][0]
    f = P07
    sent46 = f['aud'] - sum(n for _, n in NOTSENT07) - f['reject']
    arr46 = sent46 - f['bounce'] - f['no_receipt'] - f['ios']
    check(r46[8:13] == (f['aud'], sent46, f['ios'], arr46, f['clk']), '09 推送 46 一行与 07 一致')
    oc = ov_data()['cur']
    S = lambda k: sum(r[k] or 0 for r in ROWS09)
    check((S(9), S(10), S(11), S(12)) == (oc['send'], oc['ios'], oc['arr'], oc['clk']),
          f'09 共 {len(ROWS09)} 条，合计 发送 {fmt(S(9))}／iOS 未接入 {fmt(S(10))}／到达 {fmt(S(11))}／点击 {fmt(S(12))}，与 06 同期相等')
    check(all(r[11] <= r[9] - r[10] for r in ROWS09), '09 每行到达 ≤ 发送 − iOS 未接入；到达率 ' +
          '、'.join(f'{r[0]}:{pct(r[11] / (r[9] - r[10]))}' for r in ROWS09 if r[9]))
    check(all(r[8] > r[9] for r in ROWS09), '09 每行受众 > 发送')
    trs = []
    for (no, name, st, way, act, mode, when, grp, aud, sent, ios, arr, clk) in ROWS09:
        bad = ' pd-bad' if st == '发送失败' else ''
        name_td = f'<td><span class="pd-lk">{E(name)}</span><span class="pd-s2{bad}">推送 {no} · {st}</span></td>'
        if sent and clk is None:
            arr_td = f'<td class="pd-r">{fmt(arr)}<span class="pd-s2">{pct(arr / (sent - ios))}</span></td>'
            clk_td = ctr_td = '<td class="pd-r dim">—</td>'
        elif sent:
            arr_td = f'<td class="pd-r">{fmt(arr)}<span class="pd-s2">{pct(arr / (sent - ios))}</span></td>'
            ctr = clk / sent
            clk_td = f'<td class="pd-r">{fmt(clk)}</td>'
            ctr_td = f'<td class="pd-r">{pct(ctr)}</td>'
        else:
            arr_td = clk_td = ctr_td = '<td class="pd-r dim">—</td>'
        trs.append(f'<tr>{name_td}<td>{way}</td><td>{E(act)}</td><td>{when_html(mode, when)}</td>'
                   f'<td class="pd-r">{fmt(aud)}</td><td class="pd-r">{fmt(sent)}</td>{arr_td}{clk_td}{ctr_td}<td class="ch-go">›</td></tr>')
    heads = [('名称', False, ''), ('推送方式', False, ''), ('所属活动', False, ''),
             ('发送时间', True, ''), ('受众', False, 'pd-r'), ('发送', False, 'pd-r'),
             ('到达<span class="th2">到达率不含<br>iOS 未接入</span>', False, 'pd-r'),
             ('点击', False, 'pd-r'), ('点击率', False, 'pd-r')]
    ths = ''.join(f'<th class="{c}{" on" if a else ""}">{h.split("<span")[0]}{sort_icon(a)}'
                  f'{("<span" + h.split("<span", 1)[1]) if "<span" in h else ""}</th>' for h, a, c in heads) + '<th></th>'
    dd = lambda lab, val, w=None: (f'<span class="ch-fl"><label>{lab}</label><span class="in"{f" style=\"width:{w}px\"" if w else ""}>{val}'
                                   f'<span class="dn">⌵</span></span></span>')
    tot = (f'<tr class="pd-tot"><td>合计</td><td></td><td></td><td></td><td class="pd-r dim">—</td><td class="pd-r">{fmt(S(9))}</td>'
           f'<td class="pd-r">{fmt(S(11))}<span class="pd-s2">—</span></td><td class="pd-r">{fmt(S(12))}</td>'
           f'<td class="pd-r dim">—</td><td></td></tr>')
    trs.append(tot)
    body = f"""<div class="ch-sec" style="padding-top:12px;padding-bottom:12px">
  <div class="ch-row">{seg_html(["今日", "近 7 天", "近 30 天", "自定义"], "近 7 天")}<span class="ch-m">{md(DAYS[CUR7[0]])}–{md(DAYS[CUR7[-1]])}</span><span class="ch-sp"></span><span class="btn2">导出</span></div>
  <div class="ch-flt">{dd('推送方式', '全部')}{dd('所属活动', '全部', 80)}{dd('发送时间', '全部')}{dd('状态', '全部')}{dd('标签群组', '全部', 80)}<span class="in ch-search"><span class="ph">搜索名称或编号</span></span></div>
</div>
<div class="ch-sec">
  <table class="pd-dt ch-tbl"><thead><tr>{ths}</tr></thead><tbody>{''.join(trs)}</tbody></table>
  <div class="ch-pg"><span>共 {len(ROWS09)} 条；合计行只给数量，比率只在同一推送方式内比较</span></div>
</div>"""
    return page('数据明细', body)


# ================================================================ 示例数据：00 后台首页 = 推播列表（10/12 15:25 时的样子）
# 与 09 一致：同编号、同名称、同所属活动与发送对象；47 此刻发送中，48 已排程（10/15 发，重要），49 每天重复的定时、还没发过。按编号倒序。
# 状态名按需求文档 4.1.3 第 20 行：一次性为已排程、发送中、已完成、已停止、发送失败；按行为为运行中、已暂停、已结束。
PUSH00 = [
    (49, '每日任务提醒', '定时', '每天 12:30<span class="pd-s2">下次 10/13 12:30 · 第 1/30 次</span>', '每日任务', '近 7 天登录', '已排程', None),
    (48, '中秋排名赛倒数 5 天', '定时', '10/15 19:00', '中秋排名赛', '全部玩家', '已排程', None),
    (47, '回流礼包 B 加码通知', '立即', '10/12 15:20', '回流礼包 B', '回流', '发送中', 0.62),
] + [(r[0], r[1], r[5], r[6], r[4], r[7], r[2], None)
     for r in sorted(ROWS09, key=lambda r: -r[0]) if r[3] == '推播' and r[0] != 47]
IMPORTANT00 = {48}   # 营销推送的重要程度：重要（为发送对象预留当天 1 条名额，需求文档 4.1.7 第 34 行）
OPS00 = {'已排程': '编辑 停止 复制', '发送中': '停止 复制 查看数据', '运行中': '编辑 暂停 结束 复制 查看数据',
         '已完成': '复制 查看数据', '已停止': '复制 查看数据', '发送失败': '复制 查看数据'}


def build_00():
    trs = []
    for no, name, mode, when, act, grp, st, prog in PUSH00:
        when_td = f'{mode} {when}'
        stc = ' pd-bad' if st == '发送失败' else ''
        st_td = f'<span class="pd-st{stc}">{st}</span>'
        if prog is not None:
            st_td += f'<span class="ch-mbar sm"><i style="width:{prog * 26:.1f}px"></i></span><span class="ch-m">{prog * 100:.0f}%</span>'
        ops = ''.join(f'<span class="pd-lk">{o}</span>' for o in OPS00[st].split())
        imp = '<span class="pd-st imp">重要</span>' if no in IMPORTANT00 else ''
        trs.append(f'<tr><td><span class="pd-lk">{E(name)}</span>{imp}<span class="pd-s2">推送 {no}</span></td><td>{when_td}</td>'
                   f'<td>{E(act)}</td><td>{E(grp)}</td><td class="ch-stc">{st_td}</td><td class="ch-ops">{ops}</td></tr>')
    check([r[0] for r in PUSH00] == sorted([r[0] for r in PUSH00], reverse=True), '00 推播列表按编号倒序：' + '、'.join(str(r[0]) for r in PUSH00))
    sts = ['全部', '已排程', '发送中', '已完成', '已停止', '发送失败', '运行中', '已暂停', '已结束']
    # 开屏后台结构：外框（菜单全部展开、当前页「推播」高亮、面包屑、页签）由 _后台框.js 画
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>后台首页</title>
<link rel="stylesheet" href="../原型样式.css">
<link rel="stylesheet" href="_图表.css">
<link rel="stylesheet" href="_后台框.css">
</head>
<!-- 由 _scripts/an_评审版图表.py 生成，改数字请改脚本后重跑 -->
<body class="ch-page">
<div class="shot ch bk" data-page="推播" data-tabs="*推播列表|操作纪录" data-open="all">
    <div class="ch-mainx cp">
      <div class="ch-row" style="margin-bottom:2px">{seg_html(sts, '全部')}<span class="ch-sp"></span><span class="btn2 p">＋ 新建推播</span></div>
      <table class="pd-dt ch-tbl ch-list"><thead><tr><th>推送</th><th>发送时间</th><th>所属活动</th><th>发送对象</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>{''.join(trs)}</tbody></table>
    </div>
</div>
<script src="_后台框.js"></script>
</body>
</html>
'''

BUILDERS = {'14_单条规则数据': build_14, '13_游戏内数据': build_13, '06_概览': build_06, '00_后台首页': build_00,
            '02b_预计人数': build_02b, '09_数据明细': build_09, '06b_每人每天收到': build_06b, '07_单条漏斗': build_07}

if __name__ == '__main__':
    names = sys.argv[1:] or list(BUILDERS)
    for n in names:
        (OUT / f'{n}.html').write_text(BUILDERS[n](), encoding='utf-8')
        print('写出', OUT / f'{n}.html')
    print('\n'.join(CHECKS))
    if any(c.startswith('✘') for c in CHECKS):
        sys.exit(1)
