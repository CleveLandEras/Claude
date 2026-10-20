from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.ns import qn
from lxml import etree

BG = 'F7F6F2'; CARD = 'FFFEFB'; LINE = 'E1DED6'
NAVY = '1F2A44'; INK = '3F4859'; GRAY = '5F6673'; MUTE = '8A909B'
RED = 'B03A2E'; RED_L = 'E5B3A3'; BLUE = '2A63A6'; BLUE_W = 'E3ECF6'
AMBER = '9A6212'; AMBER_W = 'F6EBD6'; GRAY_W = 'ECEBE7'; SAND = 'DDD8CD'; BAR_G = '9AA3B2'
FOOT = '精细化运营能力方案'
FONT = 'Arial'


def rgb(h):
    return RGBColor.from_string(h)


def new_prs():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def new_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    f = s.background.fill
    f.solid(); f.fore_color.rgb = rgb(BG)
    return s


def _font(run, size, color=NAVY, bold=False, spc=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(color)
    rPr = run._r.get_or_add_rPr()
    rPr.set('lang', 'zh-CN')
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)
    if spc is not None:
        rPr.set('spc', str(spc))


def text(slide, x, y, w, h, paras, size=12, color=NAVY, bold=False, align=None,
         anchor=MSO_ANCHOR.TOP, line=1.25, space_after=0, name=None, spc=None):
    """paras: str | list of str | list of list of (text, opts) runs"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    if isinstance(paras, str):
        paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.line_spacing = line
        if space_after:
            para.space_after = Pt(space_after)
        if align:
            para.alignment = align
        runs = p if isinstance(p, list) else [(p, {})]
        for t, o in runs:
            r = para.add_run(); r.text = t
            _font(r, o.get('size', size), o.get('color', color), o.get('bold', bold), o.get('spc', spc))
    return tb


def box(slide, x, y, w, h, fill=CARD, line=LINE, radius=0.04, lw=0.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sp.adjustments[0] = radius
    if fill:
        sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    else:
        sp.fill.background()
    if line:
        sp.line.color.rgb = rgb(line); sp.line.width = Pt(lw)
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    sp.text_frame.text = ''
    return sp


def rect(slide, x, y, w, h, fill, line=None):
    return box(slide, x, y, w, h, fill=fill, line=line, shape=MSO_SHAPE.RECTANGLE)


def chip(slide, x, y, label, kind='blue', size=11, h=0.27):
    fill, col = {'blue': (BLUE_W, BLUE), 'amber': (AMBER_W, AMBER), 'gray': (GRAY_W, GRAY), 'red': ('F5E1DD', RED)}[kind]
    w = 0.16 * size / 11 * len(label) + 0.24
    box(slide, x, y, w, h, fill=fill, line=None, radius=0.18)
    text(slide, x, y, w, h, label, size=size, color=col, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line=1.0)
    return w


def arrow(slide, x, y, w=0.32, h=0.2, color='C9C3B6'):
    sp = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(color); sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def header(slide, kicker, title, kcolor=BLUE, n=None):
    text(slide, 0.9, 0.78, 11.5, 0.3, kicker, size=12, color=kcolor, bold=True, spc=100, name='kicker')
    text(slide, 0.9, 1.05, 11.6, 0.6, title, size=26, color=NAVY, bold=True, line=1.1, name='title')
    if n:
        text(slide, 0.9, 6.88, 6, 0.3, FOOT + '　·　' + str(n), size=12, color=GRAY, name='footer')


def hline(slide, x, y, w, color=LINE):
    return rect(slide, x, y, w, 0.012, fill=color)


def donut(slide, x, y, d, pct, color=RED, rest=SAND, label=None, lsize=None, hole=62):
    cd = CategoryChartData(); cd.categories = ['a', 'b']; cd.add_series('s', (pct, 100 - pct))
    gf = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(d), Inches(d), cd)
    ch = gf.chart
    ch.has_legend = False; ch.has_title = False
    plot = ch.plots[0]
    for i, c in enumerate((color, rest)):
        pt = plot.series[0].points[i]
        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(c)
        pt.format.line.fill.background()
    cs = ch._chartSpace
    dn = cs.find('.//' + qn('c:doughnutChart'))
    for tag, val in (('c:firstSliceAng', '0'), ('c:holeSize', str(hole))):
        el = dn.find(qn(tag))
        if el is None:
            el = etree.SubElement(dn, qn(tag))
        el.set('val', val)
    # 去掉图表区与绘图区的底色和边框
    for parent in (cs.find(qn('c:chart')).find(qn('c:plotArea')), cs):
        sp = parent.find(qn('c:spPr'))
        if sp is None:
            sp = etree.SubElement(parent, qn('c:spPr'))
        for ch_ in list(sp):
            sp.remove(ch_)
        etree.SubElement(sp, qn('a:noFill'))
        ln = etree.SubElement(sp, qn('a:ln')); etree.SubElement(ln, qn('a:noFill'))
    # chartSpace 的 spPr 必须在 txPr 之前、externalData 之前：移到 c:chart 之后
    sp = cs.find(qn('c:spPr')); cs.remove(sp); cs.find(qn('c:chart')).addnext(sp)
    if label:
        text(slide, x, y, d, d, label, size=lsize or 11, color=color, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line=1.0)
    return gf


def _cell_border(cell, color=LINE, w=6350):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB'):
        old = tcPr.find(qn(tag))
        if old is not None:
            tcPr.remove(old)
        ln = etree.SubElement(tcPr, qn(tag), w=str(w), cap='flat', cmpd='sng', algn='ctr')
        sf = etree.SubElement(ln, qn('a:solidFill')); c = etree.SubElement(sf, qn('a:srgbClr')); c.set('val', color)
        etree.SubElement(ln, qn('a:prstDash'), val='solid')
    # 边框元素须在填充之前
    fill = tcPr.find(qn('a:solidFill'))
    if fill is not None:
        tcPr.remove(fill); tcPr.append(fill)


def table(slide, x, y, widths, rows, size=12, head_fill='EDEAE3', row_h=0.36, col_colors=None, first_bold=True, fills=None):
    """rows[0] 为表头；col_colors: {col: color}；fills: {(r,c): hex}"""
    nr, nc = len(rows), len(widths)
    gf = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * nr))
    tbl = gf.table
    tblPr = gf._element.graphic.graphicData.tbl.tblPr
    tblPr.set('firstRow', '0'); tblPr.set('bandRow', '0')
    sid = tblPr.find(qn('a:tableStyleId'))
    if sid is None:
        sid = etree.SubElement(tblPr, qn('a:tableStyleId'))
    sid.text = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'
    for i, w in enumerate(widths):
        tbl.columns[i].width = Inches(w)
    for r in range(nr):
        tbl.rows[r].height = Inches(row_h)
        for c in range(nc):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.1)
            cell.margin_top = Inches(0.06); cell.margin_bottom = Inches(0.05)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE if r == 0 else MSO_ANCHOR.TOP
            f = (fills or {}).get((r, c), head_fill if r == 0 else CARD)
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb(f)
            tf = cell.text_frame; tf.word_wrap = True
            val = rows[r][c]
            para = tf.paragraphs[0]; para.line_spacing = 1.15
            r_ = para.add_run(); r_.text = val
            if r == 0:
                _font(r_, size, NAVY, True)
            else:
                col = (col_colors or {}).get(c, INK)
                _font(r_, size, NAVY if (c == 0 and first_bold) else col, c == 0 and first_bold)
            _cell_border(cell)
    return gf


def band(slide, y, label, body, fill=BLUE_W, color=BLUE, h=0.42):
    box(slide, 0.9, y, 11.53, h, fill=fill, line=None, radius=0.12)
    text(slide, 1.05, y, 11.3, h, [[(label + '　', {'bold': True}), (body, {'bold': False})]], size=12.5, color=color, anchor=MSO_ANCHOR.MIDDLE, line=1.0)


def items_card(slide, x, y, w, h, head, items, size=12.5):
    """右侧机制事实卡：小标题 + 若干（加粗短语, 说明）；各项等分高度"""
    box(slide, x, y, w, h)
    text(slide, x + 0.28, y + 0.24, w - 0.56, 0.3, head, size=13, bold=True)
    y0 = y + 0.68
    slot = (y + h - 0.12 - y0) / len(items)
    for i, (k, v) in enumerate(items):
        yy = y0 + i * slot
        text(slide, x + 0.28, yy, w - 0.56, slot - 0.1, [[(k, {'bold': True, 'color': NAVY})], [(v, {'color': INK})]], size=size, line=1.28)
        if i < len(items) - 1:
            hline(slide, x + 0.28, yy + slot - 0.09, w - 0.56)


def change_card(slide, x, y, w, h, title, chip_label, chip_kind, bullets, basis, size=12):
    box(slide, x, y, w, h)
    text(slide, x + 0.24, y + 0.22, w - 0.48, 0.32, title, size=14, bold=True)
    chip(slide, x + 0.24, y + 0.6, chip_label, chip_kind)
    yy = y + 1.0
    cpl = int((w - 0.66) / (size / 72 * 1.12))
    paras = []
    for b in bullets:
        paras.append([('•  ', {'color': GRAY}), (b, {'color': INK})])
    bl = sum(max(1, -(-(len(b) + 2) // cpl)) for b in bullets)
    bh = bl * size / 72 * 1.35 + 0.06 * len(bullets)
    text(slide, x + 0.24, yy, w - 0.48, bh, paras, size=size, line=1.3, space_after=3)
    yb = y + h - 0.98
    hline(slide, x + 0.24, yb, w - 0.48)
    text(slide, x + 0.24, yb + 0.13, w - 0.48, 0.8, [[('依据　', {'bold': True, 'color': NAVY}), (basis, {'color': INK})]], size=size, line=1.3)


def flow(slide, y, head, steps, h=1.22):
    """steps: [(num_label, text, style)] style: plain/blue/gray"""
    box(slide, 0.9, y, 11.53, h)
    text(slide, 1.1, y + 0.14, 8, 0.28, head, size=12, bold=True)
    n = len(steps); aw = 0.42
    sw = (11.53 - 0.4 - aw * (n - 1)) / n
    xx = 1.1
    for i, (lab, body, st) in enumerate(steps):
        fill = {'plain': None, 'blue': BLUE_W, 'gray': GRAY_W}[st]
        lcol = {'plain': NAVY, 'blue': BLUE, 'gray': GRAY}[st]
        if fill:
            box(slide, xx, y + 0.48, sw - 0.1, 0.6, fill=fill, line=None, radius=0.1)
        text(slide, xx + 0.1, y + 0.52, sw - 0.3, 0.24, lab, size=11, color=lcol, bold=True)
        text(slide, xx + 0.1, y + 0.76, sw - 0.3, 0.3, body, size=12, color=NAVY)
        xx += sw
        if i < n - 1:
            arrow(slide, xx - 0.02, y + 0.7, 0.32, 0.18)
            xx += aw
