import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, math, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_呈交版V2_版式库 import *
from an_呈交版V2_版式库 import _font, _cell_border
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from PIL import Image

# V4（疏排版）：按「现状 → 目标 → 原因 → 做法 → 分期 → 验证」排；内容取自阶段 1–5 产出
# 版面规则：每页最多 3 块；块间距 ≥ 0.3 英寸；正文、表格 ≥ 12 号；放大数字 ≥ 28 号；
# 表格每页 ≤ 6 行（含表头）、行高 ≥ 0.48 英寸；底注 ≤ 1 行；卡片正文 ≤ 3 行
BASE = _ROOT + '/'
OUT = sys.argv[1] if len(sys.argv) > 1 else BASE + '弹窗标签推送方案_V4.pptx'
FIG = BASE + '分析/示意图_V4/'
SHOT = BASE + '来源资料/后台截图_1010/'

GREEN = '2F6B52'; GREEN_W = 'E2EFE8'; RED_W = 'F5E1DD'; BLUE_L = 'C6D9F1'; STONE = 'F1EFEA'
KIND = {'white': ('FFFFFF', BLUE), 'blue': (BLUE_W, BLUE), 'amber': (AMBER_W, AMBER), 'gray': (GRAY_W, GRAY),
        'red': (RED_W, RED), 'green': (GREEN_W, GREEN)}
TIER = {'现有功能可做': 'green', '小改动': 'blue', '较大开发': 'amber', '核实后定': 'gray', '中期建议': 'gray', '现有功能·替代办法': 'green'}
TIER_C = {'现有功能可做': GREEN, '小改动': BLUE, '较大开发': AMBER, '核实后定': GRAY, '中期建议': GRAY, '现有功能·替代办法': GREEN}
MID = MSO_ANCHOR.MIDDLE
X0 = 0.9; W = 11.53; XR = X0 + W; Y0 = 1.78; GAP = 0.35

prs = new_prs()
N = [0]


def S():
    N[0] += 1
    return new_slide(prs), N[0]


# ───────── 工具 ─────────
def cw(ch):
    return 1.0 if unicodedata.east_asian_width(ch) in ('W', 'F') else 0.55


def tw(t, size):
    return sum(cw(c) for c in t) * size / 72


def nlines(t, size, w):
    return max(1, math.ceil(tw(t, size) / w - 1e-6))


def lh(size, line=1.15):
    return size / 72 * 1.2 * line


def hdr(s, kicker, title, kcolor, n):
    text(s, X0, 0.78, 11.5, 0.3, kicker, size=12, color=kcolor, bold=True, spc=100, name='kicker')
    text(s, X0, 1.07, 11.85, 0.55, title, size=24, color=NAVY, bold=True, line=1.05, name='title')
    text(s, X0, 6.88, 6, 0.3, FOOT + '　·　' + str(n), size=12, color=GRAY, name='footer')


def chip_w(label, size=12, pad=0.2):
    return tw(label, size) + pad


def tag(s, x, y, label, kind='blue', size=12, h=0.3, bold=True, outline=None, pad=0.2):
    f, c = KIND[kind]
    w = chip_w(label, size, pad)
    box(s, x, y, w, h, fill=f, line=outline, radius=0.18, lw=1.5 if outline else 0.5)
    text(s, x, y, w, h, label, size=size, color=c, bold=bold, align=PP_ALIGN.CENTER, anchor=MID, line=1.0)
    return w


def ffd(items, width, size=12, gap=0.06, pad=0.18):
    """按宽度从大到小装箱，返回各行"""
    lines = []
    for it in sorted(items, key=lambda i: -chip_w(i[0], size, pad)):
        w = chip_w(it[0], size, pad)
        for ln in lines:
            used = sum(chip_w(i[0], size, pad) for i in ln) + gap * len(ln)
            if used + w <= width + 1e-6:
                ln.append(it); break
        else:
            lines.append([it])
    return lines


def pic(s, path, x, y, w=None, h=None, crop=(0, 0, 0, 0), border=LINE):
    Wp, Hp = Image.open(path).size
    l, t, r, b = crop
    ar = (Wp * (1 - l - r)) / (Hp * (1 - t - b))
    if w is None:
        w = h * ar
    if h is None:
        h = w / ar
    p = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    p.crop_left, p.crop_top, p.crop_right, p.crop_bottom = l, t, r, b
    if border:
        p.line.color.rgb = rgb(border); p.line.width = Pt(0.75)
    return w, h


def mark(s, cx, cy, n, d=0.3, fill=BLUE, fcolor='FFFFFF'):
    sp = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2), Inches(cy - d / 2), Inches(d), Inches(d))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    sp.line.color.rgb = rgb('FFFFFF'); sp.line.width = Pt(1.75)
    sp.shadow.inherit = False
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MID
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = str(n); _font(r, 12, fcolor, True)
    return sp


def cell_lines(val, size, w):
    paras = val if isinstance(val, list) else [val]
    n = 0
    for p in paras:
        t = p if isinstance(p, str) else ''.join(x[0] for x in p)
        sz = size if isinstance(p, str) else max([x[1].get('size', size) for x in p] or [size])
        n += nlines(t, sz, w)
    return n


def tbl(s, x, y, widths, rows, size=12, row_h=0.5, head_fill='EDEAE3', fills=None, colors=None,
        bold_first=True, line=1.1, mt=0.07, mb=0.06, head_colors=None, ml=0.12):
    """单元格：str 或段落列表；段落：str 或 [(文字, 选项)]；返回估算底边"""
    nr, nc = len(rows), len(widths)
    assert nr <= 6, '表格每页最多 6 行'
    gf = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * nr))
    tb = gf.table
    tblPr = gf._element.graphic.graphicData.tbl.tblPr
    tblPr.set('firstRow', '0'); tblPr.set('bandRow', '0')
    sid = tblPr.find(qn('a:tableStyleId'))
    if sid is None:
        sid = etree.SubElement(tblPr, qn('a:tableStyleId'))
    sid.text = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'
    for i, w in enumerate(widths):
        tb.columns[i].width = Inches(w)
    total = 0
    for r in range(nr):
        tb.rows[r].height = Inches(row_h)
        need = row_h
        for c in range(nc):
            cell = tb.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(ml)
            cell.margin_top = Inches(mt); cell.margin_bottom = Inches(mb)
            cell.vertical_anchor = MID
            f = (fills or {}).get((r, c), head_fill if r == 0 else CARD)
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb(f)
            tf = cell.text_frame; tf.word_wrap = True
            val = rows[r][c]
            paras = val if isinstance(val, list) else [val]
            for pi, p in enumerate(paras):
                para = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
                para.line_spacing = line
                runs = p if isinstance(p, list) else [(p, {})]
                for t, o in runs:
                    rr = para.add_run(); rr.text = t
                    if r == 0:
                        hc = (head_colors or {}).get(c, NAVY)
                        _font(rr, o.get('size', size), o.get('color', hc), o.get('bold', True))
                    else:
                        fb = (c == 0 and bold_first)
                        dc = NAVY if fb else (colors or {}).get(c, INK)
                        _font(rr, o.get('size', size), o.get('color', dc), o.get('bold', fb))
            _cell_border(cell)
            need = max(need, cell_lines(val, size, widths[c] - 2 * ml) * lh(size, line) + mt + mb + 0.04)
        total += need
    return y + total


def label(s, x, y, w, t, sub=None, size=14):
    runs = [(t, {'bold': True, 'color': NAVY})]
    if sub:
        runs.append(('　' + sub, {'color': GRAY, 'size': 12}))
    text(s, x, y, w, 0.32, [runs], size=size, anchor=MID)
    return y + 0.32


def fnote(s, y, t, color=GRAY):
    text(s, X0, y, W, 0.28, t, size=12, color=color, anchor=MID)


def card(s, x, y, w, title=None, lines=(), chip=None, place=None, gap=None, h=None, fill=CARD, line=LINE,
         tsize=14, bsize=12, tcolor=NAVY, bcolor=INK, pad=0.2, draw=True, radius=0.04, lw=0.5):
    """卡片：标题（＋开发量标签＋位置）＋正文若干行（str 自动折行或 list 显式分行）＋对应差距；返回底边"""
    iw = w - 2 * pad
    hh = pad
    if title:
        hh += 0.34 + 0.08
    blocks = []
    for b in lines:
        k = len(b) if isinstance(b, list) else nlines(b if isinstance(b, str) else ''.join(x[0] for x in b), bsize, iw)
        blocks.append((b, k))
        hh += k * lh(bsize) + 0.05
    if gap:
        hh += lh(12) + 0.07
    hh += pad - 0.05
    H = h or hh
    if not draw:
        return y + H
    box(s, x, y, w, H, fill=fill, line=line, radius=radius, lw=lw)
    yy = y + pad
    if title:
        tl = tw(title, tsize)
        text(s, x + pad, yy, tl + 0.15, 0.34, title, size=tsize, bold=True, color=tcolor, anchor=MID)
        tx = x + pad + tl + 0.2
        if chip:
            tx += tag(s, tx, yy + 0.03, chip, TIER.get(chip, 'blue'), h=0.28) + 0.12
        if place:
            text(s, tx, yy, max(x + w - pad - tx, 0.5), 0.34, place, size=12, color=GRAY, anchor=MID)
        yy += 0.42
    for b, k in blocks:
        hb = k * lh(bsize)
        if isinstance(b, list) and b and isinstance(b[0], tuple):
            text(s, x + pad, yy, iw, hb + 0.05, [b], size=bsize, color=bcolor, line=1.15)
        else:
            text(s, x + pad, yy, iw, hb + 0.05, b, size=bsize, color=bcolor, line=1.15)
        yy += hb + 0.05
    if gap:
        text(s, x + pad, yy + 0.02, iw, lh(12) + 0.05, [[('对应差距　', {'bold': True, 'color': GRAY}), (gap, {'color': GRAY})]], size=12, line=1.15)
    return y + H


def nbox(s, x, y, w, h, main, sub=None, lab=None, fill=STONE, line_c=LINE, mcolor=NAVY, msize=13, new=None):
    box(s, x, y, w, h, fill=fill, line=line_c, radius=0.08)
    paras = []
    if lab:
        paras.append([(lab, {'size': 12, 'color': GRAY, 'bold': True})])
    for m in (main if isinstance(main, list) else [main]):
        paras.append([(m, {'size': msize, 'color': mcolor, 'bold': True})])
    for t in (sub if isinstance(sub, list) else ([sub] if sub else [])):
        paras.append([(t, {'size': 12, 'color': INK})])
    text(s, x + 0.15, y, w - 0.3, h, paras, anchor=MID, line=1.1)
    if new:
        cwd = chip_w(new, 12, 0.18)
        tag(s, x + w - cwd - 0.1, y - 0.14, new, 'blue', h=0.28, pad=0.18)


def popup(s, x, y, w, h, n, name, kind, dashed=False):
    c = {'a': '5B6BD8', 'p': 'D98A1C', 'n': '1F8579'}[kind]
    sp = box(s, x, y, w, h, fill='FFFFFF', line=('8A909B' if dashed else 'D6D9DE'), radius=0.08, lw=(1.25 if dashed else 0.75))
    if dashed:
        sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    box(s, x + 0.06, y + 0.06, w - 0.12, 0.38, fill=c, line=None, radius=0.12)
    if n:
        sh = mark(s, x + 0.26, y + 0.25, n, d=0.28, fill='FFFFFF', fcolor=NAVY)
        sh.line.fill.background()
    text(s, x, y + 0.46, w, h - 0.5, name, size=12.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER, anchor=MID, line=1.0)


def arr(s, x, y, w=0.26):
    arrow(s, x, y, w, 0.18)


def span_rows(s, y, rows, L, R, lab=None, note=None, lfill='FFFFFF', lline=RED, rfill=BLUE_W, rline=BLUE,
              lsize=12.5, rsize=13, gap=0.15, minh=0.6, rbold=True, ls=13, lpad=0.26):
    """跨度行：左框 → 右框（可带左侧行名、右侧注）；rows: (行名段落, 左行, 右行, 注行)"""
    for lb, lt, rt, nt in rows:
        nl = max(len(lt), len(rt), len(lb or []), len(nt or []))
        h = max(minh, nl * lh(ls, 1.1) + lpad)
        if lab and lb:
            text(s, lab[0], y, lab[1], h, lb, size=12, color=NAVY, anchor=MID, line=1.08)
        box(s, L[0], y, L[1], h, fill=lfill, line=lline, lw=1.0, radius=0.06)
        text(s, L[0] + 0.18, y, L[1] - 0.3, h, lt, size=lsize, color=INK, anchor=MID, line=1.1)
        ax = L[0] + L[1] + 0.06
        arrow(s, ax, y + h / 2 - 0.09, R[0] - ax - 0.06, 0.18)
        box(s, R[0], y, R[1], h, fill=rfill, line=rline, lw=1.0, radius=0.06)
        text(s, R[0] + 0.18, y, R[1] - 0.3, h, rt, size=rsize, color=NAVY, bold=rbold, anchor=MID, line=1.1)
        if note and nt:
            text(s, note[0], y, note[1], h, nt, size=12, color=GRAY, anchor=MID, line=1.08)
        y += h + gap
    return y - gap




# ═════════ 1 封面 ═════════
s, n = S()
rect(s, 1.15, 2.42, 0.82, 0.07, BLUE)
text(s, 1.15, 2.72, 8, 0.4, '弹窗 · 推送 · 标签', size=18, color=BLUE, bold=True, spc=200)
text(s, 1.15, 3.15, 11, 1.2, '精细化运营能力方案', size=60, color=NAVY, bold=True, line=1.0)
text(s, 1.15, 4.6, 9, 0.4, '现状、目标、原因与做法', size=20, color=INK)

# ═════════ 2 结论 ═════════
s, n = S()
hdr(s, '结论', '弹窗分人群现有后台就能配，推送统一、每日上限与交集需新建', BLUE, n)
XN, WN = 1.8, 2.95
XM, WM = 5.15, 3.85
XT = 9.4; WT = XR - XT
hy = Y0 - 0.05
for x, w, t, c in ((XN, WN, '现在', RED), (XM, WM, '缺什么 → 怎么补', GRAY), (XT, WT, '目标', BLUE)):
    text(s, x, hy, w, 0.3, t, size=13, bold=True, color=c, anchor=MID)
CFG = ('缺配置 → 现有后台配置', GREEN, GREEN_W)
DEV = ('缺功能 → 新建能力', AMBER, AMBER_W)
items = [('弹窗', ['62,292 人看同一套弹窗'], [(CFG, '按五类人群分组配置'), (DEV, '每人每日上限、新手弹窗接入后台')],
          ['五类人群各看一套；', '每人每次、每日最多几个', '事前读得出']),
         ('推送', ['五种推送分在三处；', '40,117 人只能靠推送'], [(DEV, '推送统一后台')],
          ['一处配置、按人群发送，', '效果按人群可查']),
         ('标签', ['两类目标人群没有标签；', '群组不能取交集'], [(CFG, '新建两类标签'), (DEV, '群组交集')],
          ['五类人群都能圈出，', '可取交集'])]
ry = Y0 + 0.32; rh = 1.0; LH = 0.46
for nm, now, lanes, goal in items:
    text(s, X0, ry, 0.8, rh, nm, size=16, bold=True, color=NAVY, anchor=MID)
    sp = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(XN + WN - 0.2), Inches(ry + rh / 2 - 0.3), Inches(XT - XN - WN + 0.32), Inches(0.6))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb('E9E5DC'); sp.line.fill.background(); sp.shadow.inherit = False
    box(s, XN, ry, WN, rh, fill='FFFFFF', line=RED, lw=1.25, radius=0.06)
    text(s, XN + 0.2, ry, WN - 0.4, rh, now, size=13, bold=True, color=NAVY, anchor=MID, line=1.15)
    ly = ry + (rh - (len(lanes) * LH + (len(lanes) - 1) * 0.06)) / 2
    for (hd, col, fill), body in lanes:
        box(s, XM, ly, WM, LH, fill=fill, line=None, radius=0.1)
        text(s, XM + 0.15, ly, WM - 0.3, LH, [[(hd, {'bold': True, 'color': col})], [(body, {'color': NAVY})]], size=12, anchor=MID, line=0.95)
        ly += LH + 0.06
    box(s, XT, ry, WT, rh, fill='FFFFFF', line=BLUE, lw=1.25, radius=0.06)
    text(s, XT + 0.2, ry, WT - 0.4, rh, goal, size=13, bold=True, color=BLUE, anchor=MID, line=1.12)
    ry += rh + 0.16
by = ry - 0.16 + GAP
segs = [('缺配置 10', 10, GREEN), ('缺功能 6', 6, AMBER), ('待核实 7', 7, BAR_G), ('1', 1, 'B9C3D3')]
bx0 = 2.45; bw = 11.6 - bx0; unit = bw / 24
xs_ = [bx0]
for _, k, _c in segs:
    xs_.append(xs_[-1] + k * unit)
text(s, xs_[1], by, 4.5, 0.3, '需新建的能力集中在 6 项', size=13, bold=True, color=AMBER, anchor=MID)
by += 0.06
text(s, X0, by + 0.36, 1.5, 0.42, '24 个目标项', size=13, bold=True, color=NAVY, anchor=MID)
for (t, k, c), x in zip(segs, xs_):
    rect(s, x, by + 0.36, k * unit - 0.03, 0.42, c)
    text(s, x, by + 0.36, k * unit - 0.03, 0.42, t, size=12.5, bold=True, color='FFFFFF', align=PP_ALIGN.CENTER, anchor=MID)
text(s, xs_[-1] + 0.06, by + 0.36, XR - xs_[-1] - 0.06, 0.42, '已做到', size=12, bold=True, color=GRAY, anchor=MID)

# ═════════ 3 现状 · 弹窗规则 ═════════
s, n = S()
hdr(s, '现状 · 弹窗', '现状：上架的 3 条弹窗规则都面向全部玩家，所有人看同一套弹窗', RED, n)
SW, SH = 1630, 680
cx0, cx1, cy0, cy1 = 620, 1390, 155, 350
iw, ih = pic(s, SHOT + '弹窗顺序设定_规则列表.png', X0, Y0, w=W, crop=(cx0 / SW, cy0 / SH, 1 - cx1 / SW, 1 - cy1 / SH))
for k, px in enumerate([727, 1076, 1226, 1359]):
    mark(s, X0 + (px - cx0) / (cx1 - cx0) * iw, Y0 + (178 - cy0) / (cy1 - cy0) * ih, k + 1, d=0.34)
leg = [('弹窗排序', ['排在前面的弹不了', '就往下取']), ('弹出数量', ['每次最多弹几个']), ('弹窗位置', ['大厅自动弹窗、', '游戏破产弹窗']),
       ('对象', ['全部玩家或标签；', '3 条都是全部玩家']), ('玩家弹窗顺序查询', ['输入玩家，', '看完整弹窗顺序'])]
ly = Y0 + ih + GAP
lw_ = W / 5
for k, (a, b) in enumerate(leg):
    x = X0 + k * lw_
    if k < 4:
        mark(s, x + 0.15, ly + 0.16, k + 1, d=0.3)
    else:
        rect(s, x + 0.09, ly + 0.1, 0.12, 0.12, GRAY)
    text(s, x + 0.4, ly, lw_ - 0.45, 0.8, [[(a, {'bold': True, 'color': NAVY, 'size': 13})]] + [[(t, {'color': INK})] for t in b], size=12, line=1.1)

# ═════════ 4 现状 · 一位玩家看到什么 ═════════
s, n = S()
hdr(s, '现状 · 弹窗', '现状：每位玩家每次进大厅最多弹出 4 个，新增另有新手弹窗 2 个', RED, n)
bh = 2.7
box(s, X0, Y0, W, bh)
text(s, 1.15, Y0 + 0.22, 10.5, 0.34, [[('一位玩家每次进大厅看到什么', {'bold': True, 'color': NAVY, 'size': 14}),
                                     ('　从未储值的普卡玩家，活动均在开放期；蓝色为弹出', {'color': GRAY})]], size=12, anchor=MID)
lanes = [('活动类 14 项', [('热门资讯', 1), ('发信送奖', 1), ('月月抽', 0), ('卡别直升活动', 1), ('限时挑战', 0), ('天天敲蛋礼', 0), ('…共 14 项', 0)],
          '取前 3 个可弹的', '普卡跳过月月抽（金卡起）'),
         ('储值类 7 项', [('首储礼包', 1), ('独享礼包', 0), ('惊喜三选一', 0), ('限时加码礼包', 0), ('…共 7 项', 0)],
          '取第 1 个可买的', '从未储值者先取首储礼包')]
yy = Y0 + 0.78
for lab, chs, r1, r2 in lanes:
    text(s, 1.15, yy, 1.4, 0.32, lab, size=13, bold=True, color=NAVY, anchor=MID)
    xx = 2.6
    for c, on in chs:
        xx += tag(s, xx, yy + 0.01, c, 'blue' if on else 'gray', h=0.3, bold=bool(on)) + 0.07
    text(s, 9.85, yy - 0.08, 2.45, 0.5, [[(r1, {'bold': True, 'color': NAVY, 'size': 13})], [(r2, {'color': GRAY})]], size=12, line=1.0)
    yy += 0.62
hline(s, 1.15, Y0 + bh - 0.72, W - 0.5)
text(s, 1.15, Y0 + bh - 0.66, W - 0.5, 0.52, [[('合计　', {'bold': True, 'color': NAVY, 'size': 13}), ('后台规则下每次最多 ', {'color': NAVY, 'size': 13}),
                                             ('4 个', {'bold': True, 'color': RED, 'size': 28}), ('，所有人相同；', {'color': NAVY, 'size': 13}),
                                             ('新增另有客户端新手弹窗 2 个，后台看不到', {'color': INK, 'size': 13})]], size=13, anchor=MID)
fy = Y0 + bh + GAP
facts = [('多条规则同时命中都会弹', ['顺序查询中活动类在前、', '储值类在后']),
         ('每项每日 1 次', ['进大厅次数多的玩家，', '一天最多 14 个活动弹窗']),
         ('新手弹窗不在这套设定里', ['新手挑战、新手通行证', '写死在客户端'])]
fw = (W - 2 * 0.3) / 3
for k, (a, b) in enumerate(facts):
    card(s, X0 + k * (fw + 0.3), fy, fw, a, [b], fill=GRAY_W, line=None, tsize=13.5)

# ═════════ 5 现状 · 推送 ═════════
s, n = S()
hdr(s, '现状 · 推送', '现状：五种推送分在三处配置，40,117 人只能靠推送', RED, n)
C5 = [(X0, 2.45), (3.67, 2.75), (6.74, 2.45)]
for (x, w), t in zip(C5, ['推送方式', '在哪配置', '在哪看记录']):
    text(s, x, Y0, w, 0.28, t, size=12, bold=True, color=GRAY, anchor=MID)
rows5 = [(('推播', None), ('礼包后台', '只在限时加码礼包未购买时发送'), ('推播报表', '傳送、曝光、開啟')),
         (('快显', None), ('客户端', '写死，只有在线玩家收到'), ('记录位置待核实', None)),
         (('短信、Facebook、LINE', None), ('营销侧', '按名单发送'), ('短信数据在 BI', 'Facebook、LINE 待核实'))]
yy = Y0 + 0.36
for row in rows5:
    for k, ((x, w), (m, sub)) in enumerate(zip(C5, row)):
        nbox(s, x, yy, w, 0.66, m, sub, msize=13)
        if k < 2:
            arr(s, x + w + 0.04, yy + 0.24, 0.2)
    yy += 0.76
fb = yy - 0.1
xc = 9.55
box(s, xc, Y0 + 0.36, XR - xc, fb - Y0 - 0.36)
text(s, xc + 0.25, Y0 + 0.56, XR - xc - 0.5, 0.5, '3 处', size=32, color=RED, bold=True, line=1.0)
text(s, xc + 0.25, Y0 + 1.16, XR - xc - 0.5, 0.32, '五种推送的配置位置', size=14, color=NAVY, bold=True)
text(s, xc + 0.25, Y0 + 1.56, XR - xc - 0.5, 0.6, ['各自配置、各自记录；', '效果数据分在推播报表、', 'BI、营销侧'], size=12, color=INK, line=1.15)
y = fb + GAP
label(s, X0, y, W, '谁只能靠推送', '近一月活跃加八月已离开者共 74,480 人')
y += 0.4
w1 = W * 34363 / 74480
rect(s, X0, y, w1, 0.5, BAR_G); rect(s, X0 + w1, y, W - w1, 0.5, RED)
text(s, X0 + 0.15, y, w1 - 0.2, 0.5, '0–7 天内登录　34,363 人', size=13, color='FFFFFF', bold=True, anchor=MID)
text(s, X0 + w1 + 0.15, y, W - w1 - 0.3, 0.5, '8 天以上未登录　40,117 人（53.86%）', size=13, color='FFFFFF', bold=True, anchor=MID)
fnote(s, y + 0.6, '8 天以上未登录的玩家进不了大厅，弹窗够不到；其中新增 5,960 人、回流 8,542 人')

# ═════════ 6 现状 · 标签 ═════════
s, n = S()
hdr(s, '现状 · 标签', '现状：约 100 个标签支持且、排除、或，群组之间不能取交集', RED, n)
fw = (W - 2 * 0.35) / 3; cy = 2.55; ch6 = 2.1
xs6 = [X0 + k * (fw + 0.35) for k in range(3)]
card(s, xs6[0], cy, fw, '约 100 个标签，十大类', [['每个是独立的 BigQuery 脚本，', '最快 25 分钟刷新']], h=ch6, fill=GRAY_W, line=None, tsize=17, bsize=14, pad=0.32)
card(s, xs6[2], cy, fw, '弹窗对象可选标签', [['规则对象可选全部玩家', '或标签群组']], h=ch6, fill=GRAY_W, line=None, tsize=17, bsize=14, pad=0.32)
x = xs6[1]
box(s, x, cy, fw, ch6, fill=GRAY_W, line=None)
text(s, x + 0.32, cy + 0.32, fw - 0.64, 0.4, '组合：且、排除、或', size=17, bold=True, color=NAVY, anchor=MID)
xx = x + 0.32
for t in ['且 ✓', '排除 ✓', '或 ✓']:
    xx += tag(s, xx, cy + 0.9, t, 'green', size=13, h=0.34) + 0.1
tag(s, x + 0.32, cy + 1.4, '群组之间交集 ✗', 'red', size=13, h=0.34)
text(s, x + 0.32, cy + 1.4 + 0.34, fw - 0.64, 0.32, '尚未提供', size=13, color=INK, anchor=MID)

# ═════════ 7 目标 · 对谁 ═════════
s, n = S()
hdr(s, '目标 · 人群', '目标：五类人群都能圈出，三类沿用现有判定，两类按定义新建标签', BLUE, n)
lwc = 3.6; rxc = X0 + lwc + 0.35; rwc = XR - rxc
label(s, X0, Y0, lwc, '沿用现有判定', '3 类')
label(s, rxc, Y0, rwc, '按定义新建标签', '2 类')
cy = Y0 + 0.45
for g, how, l1, l2 in [('新增', '现有标签', '注册 30 天内', '10,749 人（17.26%）'),
                       ('回流', '现有标签', '会员身份为回流', '16,564 人（26.59%）'),
                       ('破产', '弹窗位置', '游戏中破产的时刻', '破产时触发，不形成名单')]:
    box(s, X0, cy, lwc, 1.0)
    text(s, X0 + 0.22, cy + 0.12, 1.5, 0.34, g, size=15, bold=True, color=NAVY, anchor=MID)
    pw = chip_w(how)
    tag(s, X0 + lwc - 0.22 - pw, cy + 0.14, how, 'gray', h=0.3, bold=False)
    text(s, X0 + 0.22, cy + 0.5, lwc - 0.44, 0.45, [[(l1, {'color': NAVY, 'size': 12.5})], [(l2, {'color': GRAY})]], size=12, line=1.05)
    cy += 1.0 + 0.22
rcy = Y0 + 0.45; rch = 1.61
for g, how, cnt, d, basis in [('潜在付费', '新建标签', '注册 7–14 天未付费玩家中占 25.24%', '从未储值，且近 14 天押注不低于 20,000',
                               ['依据：新玩家玩得越多，越可能首次付费（Optimove）；', '2 万约为注册 7–14 天未付费玩家押注的前 25%（528／2,092 人）']),
                              ('潜在流失', '新建标签 · 分两档', '按逐日登录计算，建标签时查看人数', '注册满 28 天、近 7 天内有登录；第 15–28 天登录不少于 4 天，近 14 天少于 4 天',
                               ['依据：近 30 天登录不到 9 天为登录天数下降（Game Developer），折成 14 天约 4 天；', '连续 7 天未登录算已流失（数数科技：3–7 天）'])]:
    box(s, rxc, rcy, rwc, rch, line=BLUE_L, lw=1.25)
    text(s, rxc + 0.22, rcy + 0.14, 1.3, 0.34, g, size=15, bold=True, color=NAVY, anchor=MID)
    cwd = tag(s, rxc + 1.45, rcy + 0.16, how, 'blue', h=0.3)
    text(s, rxc + 1.6 + cwd, rcy + 0.14, rwc - 1.85 - cwd, 0.34, cnt, size=12, color=GRAY, anchor=MID, align=PP_ALIGN.RIGHT)
    text(s, rxc + 0.22, rcy + 0.58, rwc - 0.44, 0.3, d, size=12.5, bold=True, color=NAVY, anchor=MID)
    text(s, rxc + 0.22, rcy + 0.94, rwc - 0.44, 0.5, basis, size=12, color=GRAY, line=1.08)
    rcy += rch + 0.22
fnote(s, max(cy - 0.22, rcy - 0.22) + GAP, '人数按近一月活跃 62,292 人计；五类以外的玩家沿用现有内容，VIP 108 人、黑名单 15 人单列')

# ═════════ 8 目标 · 每类先看什么 ═════════
s, n = S()
hdr(s, '目标 · 弹窗', '目标：五类人群各看一套弹窗，先看为该人群设的内容', BLUE, n)
gc = [('新增', '大厅自动弹窗', '先看新手挑战、新手通行证', ['为新玩家设的内容，客户端现另弹 2 个', '弹窗总数不多于其他玩家'], False),
      ('回流', '大厅自动弹窗', '活动弹窗先看回流任务', ['为回流玩家设的活动', '现排活动类第 7，取满 3 个就轮不到'], False),
      ('潜在付费', '大厅、破产弹窗', '储值弹窗先看首储礼包（沿用）', ['从未储值者的低门槛礼包，', '就是首储礼包（NT$50）'], True),
      ('潜在流失', '大厅自动弹窗', '一组先看每日补给计划，一组沿用', ['每日活动，对应登录天数减少的处境', '比较曝光、点击后定'], False),
      ('破产', '游戏破产弹窗', '一组破产礼包提到第 2，一组沿用', ['为破产时刻设的礼包', '与独享礼包谁先，对照后定'], False),
      ('其余', '全部位置', '沿用现有活动、储值、破产弹窗', ['现有排序本就按全部玩家设定'], True)]
cw3 = (W - 2 * 0.3) / 3; ch3 = 1.72
for k, (g, pos, see, why, keep) in enumerate(gc):
    x = X0 + (k % 3) * (cw3 + 0.3); y = Y0 + (k // 3) * (ch3 + 0.3)
    box(s, x, y, cw3, ch3, fill=(CARD if keep else CARD), line=(LINE if keep else BLUE_L), lw=(0.5 if keep else 1.25))
    text(s, x + 0.22, y + 0.18, 1.6, 0.34, g, size=15, bold=True, color=NAVY, anchor=MID)
    pw = chip_w(pos)
    tag(s, x + cw3 - 0.22 - pw, y + 0.2, pos, 'gray', h=0.3, bold=False)
    text(s, x + 0.22, y + 0.66, cw3 - 0.44, 0.32, see, size=13, bold=True, color=(GRAY if keep else BLUE), anchor=MID)
    text(s, x + 0.22, y + 1.04, cw3 - 0.44, 0.55, why, size=12, color=GRAY, line=1.12)
fnote(s, Y0 + 2 * ch3 + 0.3 + GAP, '蓝框、蓝字为要改的内容，灰字为沿用')

# ═════════ 9 目标 · 数量与顺序 ═════════
s, n = S()
hdr(s, '目标 · 弹窗', '目标：每人每次、每日最多几个事前读得出，各组顺序单独设定', BLUE, n)
LB = (X0, 5.35); RB = (6.85, XR - 6.85)
text(s, LB[0], Y0, LB[1], 0.3, '现在', size=13, bold=True, color=RED, anchor=MID)
text(s, RB[0], Y0, RB[1], 0.3, '目标', size=13, bold=True, color=BLUE, anchor=MID)
span_rows(s, Y0 + 0.42, [
    (None, ['新手挑战、新手通行证写死在客户端，后台读不到'], ['每人每次最多几个事前读得出；新手弹窗计入'], None),
    (None, ['只能逐项相加：活动类 14 项各每日 1 次，一天最多 14 个'], ['每人每日最多几个可设定、事前读得出'], None),
    (None, ['同一顺序给所有人，回流任务对回流玩家也排第 7'], ['各组顺序单独设定'], None),
    (None, ['多条规则同时命中都会弹，人群重叠时弹窗叠加'], ['同属两类的玩家只看一套'], None)], LB, RB, minh=0.66, gap=0.2)

# ═════════ 10 目标 · 推送 ═════════
s, n = S()
hdr(s, '目标 · 推送', '目标：五种推送一处配置、按人群发送，发送、到达、点击按人群可查', BLUE, n)
text(s, LB[0], Y0, LB[1], 0.3, '现在', size=13, bold=True, color=RED, anchor=MID)
text(s, RB[0], Y0, RB[1], 0.3, '目标', size=13, bold=True, color=BLUE, anchor=MID)
span_rows(s, Y0 + 0.42, [
    (None, ['分在礼包后台、客户端、营销侧三处，各自配置'], ['快显、推播、短信、Facebook、LINE 一处配置'], None),
    (None, ['40,117 人 8 天以上未登录，弹窗够不到，只能靠推送'], ['发送对象引用标签人群，与弹窗同一套五类人群'], None),
    (None, ['推播只在限时加码礼包未购买时发送；快显写死在客户端'], ['内容、点击跳转、触发条件（定时或按行为）运营自助'], None),
    (None, ['五种各自发送，一位玩家一天收到几条无处合计'], ['每人每日最多几条可设定、事前读得出'], None),
    (None, ['推播报表、短信 BI 数据、营销侧记录分在各处；', '玩家收到短信多直接打开 App 或网页，不点链接'],
     ['发送量、到达、点击按方式、按人群可查；', '短信另看发送后一定时间内登录人数'], None)], LB, RB, minh=0.62, gap=0.16)

# ═════════ 11 目标 · 标签 ═════════
s, n = S()
hdr(s, '目标 · 标签', '目标：新建两类标签、群组可取交集，改口径前看得到人数与影响', BLUE, n)
cw2 = (W - 0.3) / 2
yb = card(s, X0, Y0, cw2, '新建潜在付费、潜在流失标签', [['潜在流失分两档；两类没有现成标签，', '弹窗对象只能选全部玩家或标签']], line=BLUE_L, lw=1.25)
card(s, X0 + cw2 + 0.3, Y0, cw2, '群组之间可取交集', [['已建群组的重叠人群（如回流且潜在付费）', '可直接引用，不必拆回标签重建']], line=BLUE_L, lw=1.25)
y2 = yb + GAP
label(s, X0, y2, W, '改口径前看得到人数与影响', '四项标签工具')
tw4 = (W - 3 * 0.25) / 4
for k, (nm, what, why) in enumerate([('人数预览', '保存前看到人数', ['2 万押注、4 天登录等', '门槛要按人数调整']),
                                     ('口径说明', '每个标签写明圈法', ['部分标签名称看不出口径，', '如「目前，该卡比金卡更优越」']),
                                     ('变更记录', '谁在何时改了什么', ['口径一改，引用它的规则', '对象人数随之改变']),
                                     ('引用清单', '列出引用该标签的规则与推送', ['改口径前知道会影响', '哪些规则'])]):
    x = X0 + k * (tw4 + 0.25)
    card(s, x, y2 + 0.42, tw4, nm, [[(what, {'bold': True, 'color': BLUE, 'size': 12.5})], [(why[0], {'color': GRAY})], [(why[1], {'color': GRAY})]],
         h=1.62, fill=CARD, pad=0.2, tsize=14)

# ═════════ 12 原因 ═════════
s, n = S()
hdr(s, '原因', '原因：弹窗分人群只缺配置；新手弹窗、每日上限、推送统一后台、交集缺功能', RED, n)
cols = [('缺配置', '10 项', '后台截图或已确认的后台规则证明已有该能力', 'green'),
        ('缺功能', '6 项', '资料证明没有，需开发', 'red'),
        ('待核实', '7 项', '资料没写或未确认，不等于做不到', 'gray')]
mrows = [('弹窗', '11 项', [['新增少弹', '回流先看回流任务', '潜在流失一组先看补给计划', '破产礼包提到第 2', '其余沿用', '各组顺序单独设定', '同属两类只看一套', '曝光、点击按人群查'],
                           ['新手弹窗计入数量', '每人每日最多几个'], ['组内随机分两组']]),
         ('推送', '6 项', [['推播、短信效果按人群查'], ['五种推送一处配置', '内容、跳转、触发自助', '每人每日最多几条'], ['按标签人群发送', '快显、Facebook、LINE 效果']]),
         ('标签', '6 项', [['新建两类标签'], ['群组之间取交集'], ['人数预览', '口径说明', '变更记录', '引用清单']])]
lw7 = 0.66; g7 = 0.1
cwm = (W - lw7 - 3 * g7) / 3
xs = [X0 + lw7 + g7 + k * (cwm + g7) for k in range(3)]
y = Y0
DESC = {'缺配置': ['后台截图或已确认的后台', '规则证明已有该能力'], '缺功能': ['资料证明没有，', '需开发'], '待核实': ['资料没写或未确认，', '不等于做不到']}
HH = 0.8
for k, (nm, num, d, kind) in enumerate(cols):
    f, c = KIND[kind]
    box(s, xs[k], y, cwm, HH, fill=f, line=None)
    text(s, xs[k] + 0.14, y + 0.02, 1.2, 0.48, num, size=28, color=c, bold=True, line=1.0, anchor=MID)
    text(s, xs[k] + 0.14, y + 0.48, 1.2, 0.28, nm, size=14, color=c, bold=True, anchor=MID)
    text(s, xs[k] + 1.3, y, cwm - 1.38, HH, DESC[nm], size=12, color=INK, anchor=MID, line=1.08)
y += HH + g7
CHH = 0.28; CP = 0.36
for rn, rc, cells in mrows:
    packs = [ffd([(t, cols[k][3]) for t in cells[k]], cwm - 0.24) for k in range(3)]
    nl = max(len(p) for p in packs)
    rh = 0.26 + nl * CHH + (nl - 1) * (CP - CHH)
    box(s, X0, y, lw7, rh, fill=GRAY_W, line=None)
    text(s, X0, y, lw7, rh, [[(rn, {'bold': True, 'color': NAVY, 'size': 14})], [(rc, {'color': GRAY})]], size=12,
         align=PP_ALIGN.CENTER, anchor=MID, line=1.1)
    for k in range(3):
        box(s, xs[k], y, cwm, rh)
        yy = y + 0.13
        for ln in packs[k]:
            xx = xs[k] + 0.12
            for t, kind in ln:
                xx += tag(s, xx, yy, t, kind, h=CHH, pad=0.18) + 0.06
            yy += CP
    y += rh + g7

# ═════════ 13 做法 · 活动弹窗分四组 ═════════
s, n = S()
hdr(s, '做法 · 现有功能可做', '做法：现有后台把活动弹窗分四组，每人只命中本组一条规则', BLUE, n)
fh = 1.0
nbox(s, X0, Y0, 1.15, fh, '玩家', lab='起点', fill=CARD)
arr(s, 2.08, Y0 + 0.41)
box(s, 2.38, Y0, 5.85, fh, fill=BLUE_W, line=BLUE_L, radius=0.08)
text(s, 2.55, Y0 + 0.1, 5.5, 0.3, '按先后判定属于哪一组', size=12, bold=True, color=BLUE, anchor=MID)
xx = 2.55
for k, g in enumerate(['新增', '回流', '潜在流失·实验组', '其余（含对照组）']):
    xx += tag(s, xx, Y0 + 0.5, g, 'white', h=0.32, pad=0.18) + 0.04
    if k < 3:
        text(s, xx, Y0 + 0.5, 0.26, 0.32, '→', size=12, color=BLUE, bold=True, align=PP_ALIGN.CENTER, anchor=MID)
        xx += 0.3
arr(s, 8.3, Y0 + 0.41)
nbox(s, 8.62, Y0, 2.3, fh, '本组那一条活动类规则', '组间用排除互斥', lab='命中规则', fill=BLUE_W, line_c=BLUE_L, msize=13)
arr(s, 10.98, Y0 + 0.41)
nbox(s, 11.28, Y0, XR - 11.28, fh, ['看到本组', '内容'], lab='进大厅', fill=CARD, msize=13)
S_ = lambda t, c: [(t, {'bold': True, 'color': c})]
NM = lambda *ts: [[(t, {'bold': True, 'color': NAVY})] for t in ts]
rows = [['活动类规则', '排序前 3 项', '弹出', '对象'],
        [NM('活动类·新增'), '热门资讯、发信送奖、月月抽', '1', [S_('新建　', BLUE) + [('标签：新增', {})]]],
        [NM('活动类·回流'), '回流任务、热门资讯、发信送奖', '3', [S_('新建　', BLUE) + [('标签：回流；排除：新增', {})]]],
        [NM('活动类·潜在流失', '实验组'), '每日补给计划、热门资讯、发信送奖', '3', [S_('新建　', BLUE) + [('标签：潜在流失·实验组；排除：新增、回流', {})]]],
        [NM('活动类·其余'), '热门资讯、发信送奖、月月抽', '3', [S_('改　', AMBER) + [('全部玩家；排除：新增、回流、潜在流失·实验组', {})]]]]
tbl(s, X0, Y0 + fh + GAP, [2.15, 3.55, 0.8, 5.03], rows, row_h=0.56, colors={1: INK, 2: INK}, bold_first=False)

# ═════════ 14 做法 · 储值与破产规则 ═════════
s, n = S()
hdr(s, '做法 · 现有功能可做', '做法：储值类沿用，破产新建实验组规则；改后上架 7 条', BLUE, n)
label(s, X0, Y0, W, '改后上架 7 条', '活动类 4 条按人群互斥；储值类通用沿用；破产储值 2 条：实验组新建，原规则排除实验组')
rows = [['储值类规则', '排序前 3 项', '弹出', '对象'],
        [NM('储值类·通用'), '首储礼包、独享礼包、惊喜三选一', '1', [S_('沿用　', GRAY) + [('全部玩家', {})]]],
        [NM('破产储值·实验组'), '首储礼包、破产礼包、独享礼包', '1', [S_('新建　', BLUE) + [('标签：破产·实验组', {})]]],
        [NM('破产储值'), '首储礼包、独享礼包、破产礼包', '1', [S_('改　', AMBER) + [('全部玩家；排除：破产·实验组', {})]]]]
te = tbl(s, X0, Y0 + 0.45, [2.15, 3.55, 0.8, 5.03], rows, row_h=0.52, colors={1: INK, 2: INK}, bold_first=False)
cy = te + GAP
card(s, X0, cy, cw2, '活动弹窗分四组', ['同属两类按新增、回流、潜在流失实验组的先后只进一组', '对照组看到的与改前相同；配置后用顺序查询每组抽查'],
     chip='现有功能可做', gap='各组顺序单独设定 · 同属两类只看一套 · 其余沿用')
card(s, X0 + cw2 + 0.3, cy, cw2, '新建两类标签', ['按定义写 BigQuery 脚本，潜在流失分两档', '另按玩家 ID 尾数建潜在流失、破产实验组子标签'],
     chip='现有功能可做', gap='新建两类标签')

# ═════════ 15 做法 · 新增玩家改前改后 ═════════
s, n = S()
hdr(s, '做法 · 五类人群首版内容', '做法：新增玩家每次进大厅由 6 个减为 4 个，活动类由 3 个减为 1 个', BLUE, n)
PW, PH, PG = 1.15, 1.12, 0.1
GX = {'a': 2.45, 'p': 6.35, 'n': 7.85}
for t, x in (('活动类', GX['a']), ('储值类', GX['p']), ('新手弹窗', GX['n']), ('合计', 10.75)):
    text(s, x, Y0, 1.6, 0.28, t, size=12, bold=True, color=GRAY, anchor=MID)
fig = [('现在', STONE, LINE, GRAY,
        {'a': [(1, '热门资讯'), (2, '发信送奖'), (3, '卡别直升活动')], 'p': [(4, '首储礼包')], 'n': [(5, '新手挑战'), (6, '新手通行证')]},
        (['后台看不到'], RED), ('共 6 个', RED)),
       ('改后（首版）', BLUE_W, BLUE_L, BLUE,
        {'a': [(1, '热门资讯')], 'p': [(2, '首储礼包')], 'n': [(None, '新手挑战'), (None, '新手通行证')]},
        (['新手弹窗不变；', '接入后台后排最前（较大开发）'], BLUE), ('共 4 个', BLUE))]
ry = Y0 + 0.38; rh = 1.86
for nm, fill, lc, tc, groups, note, tot in fig:
    box(s, X0, ry, W, rh, fill=fill, line=lc, radius=0.05)
    nml = [nm] if '（' not in nm else [nm[:nm.index('（')], nm[nm.index('（'):]]
    text(s, 1.1, ry, 1.3, rh, nml, size=15, bold=True, color=tc, anchor=MID, line=1.05)
    for kind, cards_ in groups.items():
        for j, (num, name) in enumerate(cards_):
            popup(s, GX[kind] + j * (PW + PG), ry + 0.2, PW, PH, num, name, kind, dashed=(kind == 'n'))
    nt, nc = note
    text(s, GX['n'], ry + 0.2 + PH + 0.06, 2.75, 0.48, nt, size=12, bold=True, color=nc, line=1.05)
    text(s, 10.75, ry, 1.6, rh, tot[0], size=28, bold=True, color=tot[1], anchor=MID)
    ry += rh + 0.3

# ═════════ 16 做法 · 五类人群首版内容 ═════════
s, n = S()
hdr(s, '做法 · 五类人群首版内容', '做法：五类人群各看首版内容，潜在流失与破产组内对照', BLUE, n)
LAB = (X0, 1.15); L16 = (2.15, 3.2); R16 = (5.85, 4.15); N16 = (10.2, XR - 10.2)
for (x, w), t, c in ((LAB, '人群', NAVY), (L16, '改前', GRAY), (R16, '改后（首版内容 · 现有功能可做）', BLUE), (N16, '对应差距', GRAY)):
    text(s, x, Y0, w, 0.3, t, size=12.5, bold=True, color=c, anchor=MID)
G_ = lambda t: [(t, {'color': GRAY, 'bold': False})]
ye = span_rows(s, Y0 + 0.4, [
    ([[('新增', {'bold': True, 'size': 13})]], ['活动 3、储值 1、新手 2，共 6 个'], ['活动 1，储值与新手弹窗不变，共 4 个'], ['新增少弹']),
    ([[('回流', {'bold': True, 'size': 13})]], ['回流任务排活动类第 7，轮不到'], ['回流任务排第 1'], ['回流先看回流任务']),
    ([[('潜在付费', {'bold': True, 'size': 13})]], ['储值位、破产位先取首储礼包'], [G_('沿用，不另建规则')], ['现已做到']),
    ([[('潜在流失', {'bold': True, 'size': 13})]], ['每日补给计划排活动类第 8'], ['实验组：每日补给计划排第 1；对照组沿用'], ['潜在流失一组先看补给计划']),
    ([[('破产', {'bold': True, 'size': 13})]], ['已付费者先取独享礼包'], ['实验组：破产礼包提到第 2；对照组沿用'], ['破产礼包提到第 2'])],
    L16, R16, lab=LAB, note=N16, lfill=STONE, lline=LINE, minh=0.48, gap=0.08)
cy = ye + GAP
card(s, X0, cy, cw2, '其余', ['3 条规则面向全部玩家 → 内容沿用；潜在流失对照组也在此组'], gap='其余沿用')
card(s, X0 + cw2 + 0.3, cy, cw2, '组内对照', ['按玩家 ID 尾数分实验组、对照组，比较曝光、点击'], chip='现有功能·替代办法', gap='组内随机分两组')

# ═════════ 17 做法 · 推送统一后台 ═════════
s, n = S()
hdr(s, '做法 · 推送统一后台', '做法：五种推送合到推送统一后台，对象引用标签，效果一处查', BLUE, n)
fh = 0.95
text(s, X0, Y0, 2.4, 0.56, '3 处 → 1 个', size=28, color=BLUE, bold=True, anchor=MID, line=1.0)
text(s, X0, Y0 + 0.58, 2.4, 0.3, '五种推送的配置位置', size=12, color=GRAY, anchor=MID)
box(s, 3.45, Y0, 2.6, fh, fill=STONE, line=LINE, radius=0.08)
yy = Y0 + 0.13; xx = 3.6
for t in ['快显', '推播', '短信']:
    xx += tag(s, xx, yy, t, 'gray', h=0.3) + 0.07
yy += 0.38; xx = 3.6
for t in ['Facebook', 'LINE']:
    xx += tag(s, xx, yy, t, 'gray', h=0.3) + 0.07
arr(s, 6.11, Y0 + 0.39)
nbox(s, 6.43, Y0, 2.85, fh, '推送统一后台', '对象引用标签；跳转与触发自助', fill=BLUE_W, line_c=BLUE_L, mcolor=BLUE, new='新建')
arr(s, 9.34, Y0 + 0.39)
nbox(s, 9.66, Y0, XR - 9.66, fh, '一处查看', '发送量、到达、点击', fill=BLUE_W, line_c=BLUE_L, mcolor=BLUE, new='新建')
y2 = Y0 + fh + GAP
cwL = 6.3
label(s, X0, y2, cwL, '推送方式与发送对象', '推送统一后台示意')
_, h1 = pic(s, FIG + '推送_统一后台.png', X0, y2 + 0.36, w=cwL, crop=(30 / 1200, 180 / 750, 1 - 590 / 1200, 1 - 284 / 750))
y3 = y2 + 0.36 + h1 + 0.3
label(s, X0, y3, cwL, '每人每日上限', '每种推送分别设定')
pic(s, FIG + '推送_统一后台.png', X0, y3 + 0.36, w=cwL, crop=(600 / 1200, 280 / 750, 1 - 1150 / 1200, 1 - 376 / 750))
xr = X0 + cwL + 0.4; wr = XR - xr
label(s, xr, y2, wr, '发送记录', '按方式、按人群统计')
rows = [['推送名称', '方式', '对象', '发送量', '到达', '点击'],
        ['回流任务开启', '推播', '回流', '—', '—', '—'],
        ['回流任务开启', 'LINE', '回流', '—', '—', '—'],
        ['首储礼包提醒', '快显', '新增', '—', '—', '—']]
tbl(s, xr, y2 + 0.36, [1.32, 0.78, 0.7, 0.8, 0.62, 0.62], rows, row_h=0.5, colors={3: GRAY, 4: GRAY, 5: GRAY}, bold_first=False, ml=0.08)

# ═════════ 18 做法 · 推送改动 ═════════
s, n = S()
hdr(s, '做法 · 推送统一后台', '做法：推送统一后台等三项需开发，推播、短信可用替代办法按标签发送', BLUE, n)
lw18 = 5.2; rx18 = X0 + lw18 + 0.35; rw18 = XR - rx18
label(s, X0, Y0, lw18, '现有功能可做', '2 项')
label(s, rx18, Y0, rw18, '需开发 · 较大开发', '3 项')
yl = Y0 + 0.45
for t_, chip_, body, gp in [('推播、短信按标签发送', '现有功能·替代办法', '短信按标签导出名单交营销侧；推播能按标签则直接选', '按标签人群发送'),
                            ('效果按人群汇总', '现有功能可做', '推播傳送、曝光、開啟与短信登录人数按人群统计', '推播、短信效果按人群查')]:
    yl = card(s, X0, yl, lw18, t_, [body], chip=chip_, gap=gp, line=LINE, pad=0.16) + 0.2
card(s, X0, yl + 0.05, lw18, '较大开发的前置条件', [['短信、Facebook、LINE 需营销侧接入；', '限时加码礼包推播要迁移']], fill=AMBER_W, line=None, tcolor=AMBER)
yr = Y0 + 0.45
for t_, body, gp in [('推送统一后台', '五种推送一处配置，快显改由后台下发；效果一处查', '五种推送一处配置'),
                     ('跳转与触发自助', '文案、点击跳转自助；定时或按行为触发', '内容、跳转、触发自助'),
                     ('每种方式每日上限', '每种推送每人每日最多几条，相加即总条数', '每人每日最多几条')]:
    yr = card(s, rx18, yr, rw18, t_, [body], chip='较大开发', gap=gp, line=LINE, pad=0.16) + 0.2

# ═════════ 19 做法 · 每日上限与新手弹窗 ═════════
s, n = S()
hdr(s, '做法 · 需开发', '做法：弹窗后台加每人每日上限，新手弹窗接入后台计入数量', BLUE, n)
ch19 = 1.95
xt = 7.0; wt = XR - xt - 0.25
box(s, X0, Y0, W, ch19)
text(s, X0 + 0.25, Y0 + 0.2, 5.6, 0.3, '大厅弹窗顺序设定 · 新建一栏', size=12, bold=True, color=GRAY, anchor=MID)
pic(s, FIG + '弹窗_每日上限.png', X0 + 0.25, Y0 + 0.62, w=5.5, crop=(195 / 1280, 126 / 196, 1 - 650 / 1280, 1 - 194 / 196))
card(s, xt, Y0 + 0.05, wt, '每人每日弹窗上限', [['每人每日最多弹几个，含各时机；', '超出后当日不再弹，按排序截断'], '现在只能逐项相加：活动类一天最多 14 个'],
     chip='小改动', place='弹窗后台', gap='每人每日最多几个', fill=CARD, line=None, pad=0.15)
y2 = Y0 + ch19 + GAP
box(s, X0, y2, W, ch19)
fy2 = y2 + 0.42
nbox(s, X0 + 0.25, fy2, 1.6, 1.1, ['新手挑战、', '新手通行证'], '写死在客户端', fill=STONE)
arr(s, X0 + 1.9, fy2 + 0.46)
nbox(s, X0 + 2.2, fy2, 1.85, 1.1, '弹窗后台', '配时机、次数、先后', fill=BLUE_W, line_c=BLUE_L, mcolor=BLUE)
arr(s, X0 + 4.1, fy2 + 0.46)
nbox(s, X0 + 4.4, fy2, 1.5, 1.1, ['顺序查询', '读得出'], '计入新增组数量', fill=CARD)
text(s, X0 + 0.25, y2 + 0.08, 5.6, 0.3, '新手弹窗：客户端 → 弹窗后台', size=12, bold=True, color=GRAY, anchor=MID)
card(s, xt, y2 + 0.05, wt, '新手弹窗接入后台', [['新手挑战、新手通行证改由弹窗后台配置', '时机、次数、对象与先后'], '计入新增组弹出数量，接入后排最前'],
     chip='较大开发', place='客户端', gap='新手弹窗计入数量', fill=CARD, line=None, pad=0.15)

# ═════════ 20 做法 · 群组交集 ═════════
s, n = S()
hdr(s, '做法 · 需开发', '做法：群组条件可选另一群组取交集，已建群组不必拆回标签重建', BLUE, n)
label(s, X0, Y0, 7, '会员标签设定 · 标签群组条件', '交集为新建选项')
iw, ih = pic(s, FIG + '标签_群组交集.png', X0, Y0 + 0.4, w=6.9, crop=(165 / 1000, 190 / 588, 1 - 845 / 1000, 1 - 425 / 588))
xc = X0 + 6.9 + 0.4
card(s, xc, Y0 + 0.4, XR - xc, '群组交集', [['群组条件可选另一群组取交集；且、或、排除沿用', '如回流且潜在付费，不必拆回标签用「且」重建']],
     chip='小改动', place='会员标签设定', gap='群组之间取交集')

# ═════════ 21 改动分层 ═════════
s, n = S()
hdr(s, '改动分层', '改动分层：17 项改动中现有功能可做 6 项，需开发 6 项，5 项核实后定', BLUE, n)
segs = [('现有功能可做', 6, 'green', ['活动弹窗分四组', '五类人群首版内容', '推播、短信按标签发送', '新建两类标签', '效果按人群汇总', '组内随机对照'], ['只改配置与标签']),
        ('小改动', 2, 'blue', ['每人每日弹窗上限', '群组交集'], ['弹窗后台、', '会员标签设定']),
        ('较大开发', 4, 'amber', ['新手弹窗接入后台', '推送统一后台', '跳转与触发自助', '每种方式每日上限'], ['推送统一后台、', '客户端']),
        ('核实后定', 5, 'gray', ['标签人数预览', '口径说明', '变更记录', '引用清单', ['快显、Facebook、', 'LINE 效果记录']], ['可用 SQL、说明文档、', '营销侧导出代替']),
        ('后续建议', 2, 'gray', [['弹窗与推送', '按人合计上限'], '跨推送方式每日上限'], ['五种推送都在一个后台', '发送后才能合计'])]
ag = 0.3
sw = (W - ag * 4) / 5
xcol = [X0 + k * (sw + ag) for k in range(5)]
text(s, xcol[0], Y0, xcol[3] + sw - X0, 0.28, '本方案改动 17 项', size=12.5, color=NAVY, bold=True, anchor=MID)
rect(s, xcol[0], Y0 + 0.33, xcol[3] + sw - X0, 0.02, NAVY)
text(s, xcol[1], Y0 + 0.42, xcol[2] + sw - xcol[1], 0.28, '需开发 6 项', size=12.5, color=NAVY, bold=True, anchor=MID, align=PP_ALIGN.CENTER)
rect(s, xcol[1], Y0 + 0.74, xcol[2] + sw - xcol[1], 0.015, SAND)
text(s, xcol[4], Y0, sw, 0.28, '方案外的后续建议', size=12.5, color=GRAY, bold=True, anchor=MID)
rect(s, xcol[4], Y0 + 0.33, sw, 0.02, SAND)
sy = Y0 + 0.9; sh = 3.3
for k, (nm, cnt, kind, its, attr) in enumerate(segs):
    x = xcol[k]
    f, c = KIND[kind]
    box(s, x, sy, sw, sh, fill=(CARD if k < 4 else BG), line=LINE)
    rect(s, x, sy, sw, 1.12, f)
    rect(s, x, sy, sw, 0.05, c)
    text(s, x + 0.15, sy + 0.12, sw - 0.75, 0.44, nm, size=13, bold=True, color=c, anchor=MID)
    text(s, x + sw - 0.82, sy + 0.1, 0.7, 0.48, [[(str(cnt), {'size': 28, 'bold': True, 'color': c}), (' 项', {'size': 12, 'color': INK})]], align=PP_ALIGN.RIGHT, anchor=MID, line=1.0)
    text(s, x + 0.15, sy + 0.6, sw - 0.3, 0.48, attr, size=12, color=c, bold=True, anchor=MID, line=1.05)
    yy = sy + 1.22
    for j, it in enumerate(its):
        nl_ = len(it) if isinstance(it, list) else 1
        hh = nl_ * lh(12, 1.05) + 0.12
        text(s, x + 0.15, yy, sw - 0.3, hh, it, size=12, color=NAVY, line=1.05, anchor=MID)
        yy += hh
        if j < len(its) - 1:
            hline(s, x + 0.15, yy, sw - 0.3)
fnote(s, sy + sh + GAP, '现有功能可做 6 项中，组内随机对照、推播与短信按标签发送为替代办法：按玩家 ID 尾数建子标签；短信导出名单')

# ═════════ 23 验证 · 三条验收 ═════════
s, n = S()
hdr(s, '验证', '验证：三条验收中弹窗部分用现有功能即达到，推送需开发后达到', BLUE, n)
acc = [('新人群可单独配置', ['运营可为一类新人群单独配置弹窗与推送，', '不影响其他人群'], '如回流且潜在付费单设一套，其余人群不变'),
       ('每人上限事前读得出', ['每人每次、每日最多几个弹窗、几条推送，', '事前读得出'], '新手弹窗计入；同属两类只按一套计'),
       ('效果按人群查得到', ['弹窗曝光、点击，推送发送、到达、点击，', '按人群查得到'], '短信另看发送后一定时间内登录人数')]
cw3 = (W - 0.6) / 3
ye = Y0
for k, (a, b, c) in enumerate(acc):
    ye = card(s, X0 + k * (cw3 + 0.3), Y0, cw3, a, [b, [(c, {'color': GRAY})]], tcolor=BLUE, fill=BLUE_W, line=None, pad=0.18)
y2 = ye + GAP
label(s, X0, y2, W, '靠哪类改动达到')
rows = [['三条验收', '现有功能可做', '小改动', '较大开发'],
        ['新人群可单独配置', '弹窗：一类人群单设一条规则', '交集人群，如回流且潜在付费', '推送：按人群单独发送'],
        ['每人每次、每日最多几个', '弹窗每次：各组弹出数量相加', '弹窗每日：每人每日上限', '推送每日；新手弹窗计入每次'],
        ['效果按人群查得到', '弹窗曝光、点击；推播、短信', '—', '五种推送一处查（记录已有则无需开发）']]
fl = {(0, 1): GREEN_W, (0, 2): BLUE_W, (0, 3): AMBER_W}
tbl(s, X0, y2 + 0.4, [2.45, 2.85, 2.6, 3.63], rows, row_h=0.5, fills=fl, head_colors={1: GREEN, 2: BLUE, 3: AMBER})

# ═════════ 24 附录 · 五名玩家走查 ═════════
s, n = S()
hdr(s, '附录 · 验证', '验证：五名玩家改后各只命中本组规则，新增每次由 6 个降到 4 个', GRAY, n)
text(s, X0, Y0, W, 0.3, [[('共同假设　', {'bold': True, 'color': NAVY}),
                          ('普卡（月月抽金卡起，跳过）；活动均在开放期；除破产示例外均从未储值；同属两类按先后只进一组', {'color': INK})]], size=12, anchor=MID)
NB = lambda t: (t, {'bold': True, 'color': BLUE})
PL = lambda t: (t, {'bold': False, 'color': NAVY})
LAB = (X0, 1.75); L24 = (2.7, 3.85); R24 = (7.0, 3.85); N24 = (11.0, XR - 11.0)
for (x, w), t, c in ((LAB, '人群（示例玩家）', NAVY), (L24, '改前每次看到', GRAY), (R24, '改后每次看到', BLUE), (N24, '靠哪项', GRAY)):
    text(s, x, Y0 + 0.38, w, 0.28, t, size=12.5, bold=True, color=c, anchor=MID)
W4 = ['4 个：热门资讯、发信送奖、', '卡别直升活动、首储礼包']
WHO = lambda g, *ex: [[(g, {'bold': True, 'size': 12.5})]] + [[(e, {'color': GRAY})] for e in ex]
span_rows(s, Y0 + 0.72, [
    (WHO('新增', '注册第 5 天'), ['6 个：热门资讯、发信送奖、卡别直升活动、', '首储礼包、新手挑战、新手通行证'],
     [[PL('4 个：热门资讯、首储礼包、')], [PL('新手挑战、新手通行证')]], ['活动弹窗分四组', '新手弹窗接入后台']),
    (WHO('回流', '会员身份为回流'), W4, [[PL('4 个：'), NB('回流任务'), PL('、热门资讯、')], [PL('发信送奖、首储礼包')]], ['五类人群首版内容']),
    (WHO('潜在付费', '近 14 天押注 25,000'), W4, [[PL('4 个：不变')], [PL('归其余组')]], ['现已做到', '新建潜在付费标签']),
    (WHO('潜在流失', '近 14 天登录 2 天', '前 14 天登录 5 天'), W4,
     [[PL('实验组 4 个：'), NB('每日补给计划'), PL('、热门资讯、')], [PL('发信送奖、首储礼包；对照组同改前')]], ['新建潜在流失标签', '组内随机对照']),
    (WHO('破产', '曾储值，游戏中破产'), ['1 个：独享礼包'], [[PL('实验组 1 个：'), NB('破产礼包')], [PL('对照组 1 个：独享礼包')]], ['五类人群首版内容', '组内随机对照'])],
    L24, R24, lab=LAB, note=N24, lfill=STONE, lline=LINE, lsize=12, rsize=12, minh=0.58, gap=0.08, ls=12, lpad=0.2)

# ═════════ 25 附录 · 改动清单 ═════════
s, n = S()
hdr(s, '附录 · 改动清单', '改动清单：17 项改动，需开发 6 项，5 项核实后定', GRAY, n)
T_ = lambda t: [[(t, {'bold': True, 'color': TIER_C[t]})]]
P_ = lambda a, b: [[(a, {'bold': True, 'color': NAVY})], [(b, {'color': GRAY})]]
rows = [['位置', '改动', '开发量'],
        [P_('弹窗后台 · 会员标签设定', '各 1 项'), '每人每日弹窗上限；群组交集', T_('小改动')],
        [P_('推送统一后台', '新建 · 3 项'), ['推送统一后台（含发送量、到达、点击一处查）；', '跳转与触发自助；每种方式每日上限'], T_('较大开发')],
        [P_('客户端', '1 项'), ['新手弹窗接入后台；', '快显改由推送统一后台下发'], T_('较大开发')],
        [P_('数据 · 建议配置', '2 项 · 4 项'), ['新建两类标签；效果按人群汇总；活动弹窗分四组；', '五类人群首版内容；按标签发送、组内对照（替代办法）'], T_('现有功能可做')],
        [P_('核实后定', '5 项'), ['标签人数预览、口径说明、变更记录、引用清单；', '快显、Facebook、LINE 效果记录'], T_('核实后定')]]
te = tbl(s, X0, Y0, [3.0, 6.98, 1.55], rows, row_h=0.56, colors={1: INK}, bold_first=False)
fnote(s, te + GAP, '24 个目标项中 23 项有对应改动；另 1 项现已做到：潜在付费先看首储礼包')

# ═════════ 26 附录 · 待核实 ═════════
s, n = S()
hdr(s, '附录 · 待核实', '待核实 9 问：答案只改变做法与开发量', GRAY, n)
qs = [('回流身份的离开天数与保留期', ['保留期过长：加「回流后若干天内」；', '合适：沿用']),
      ('同属两类时顺序查询显示哪套', ['只显示一套：可不排除；', '都显示：按先后排除互斥']),
      ('弹窗内容能否由运营编辑', ['能：各组自行迭代；', '不能：加一项小改动']),
      ('推播、短信能否按标签发送', ['能：直接选标签；', '不能：短信导出名单，推播等推送统一后台']),
      ('实验分流能否直接配置', ['能：组内直接分两组；', '不能：按玩家 ID 尾数建子标签']),
      ('弹窗、推播、短信记录哪些不全', ['汇总时注明缺失时段；', '缺字段则补记录']),
      ('快显、Facebook、LINE 的记录在哪', ['已有：并入按人群汇总；', '没有：补记录，按小改动做']),
      ('标签四项工具哪些已有', ['已有的不做；没有的按小改动做，', '可用 SQL 与说明文档代替']),
      ('新手弹窗写死在客户端的原因', ['历史遗留：只改后台接入；', '客户端限制：需同时改客户端'])]
cw3 = (W - 0.6) / 3
for k, (q, a) in enumerate(qs):
    x = X0 + (k % 3) * (cw3 + 0.3); y = Y0 + (k // 3) * (1.3 + 0.3)
    card(s, x, y, cw3, None, [[(q, {'bold': True, 'color': NAVY, 'size': 13})], a], h=1.3, pad=0.18)

prs.save(OUT)
print('saved', OUT, N[0], 'slides')
