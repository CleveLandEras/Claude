# 呈交版 V4（设计版，10/12 重排）：弹窗 · 推送 · 标签 精细化运营能力方案
# 用法：python an_呈交版V4_设计版.py [输出.pptx]
# 版面系统：16:9；左右边距 0.9 英寸；页眉＝章节进度条＋章节标记（13 号）＋结论标题（32 号，约 20 字内）＋可选副标题（16 号一行）。
# 正文 15–17 号，说明 13–14 号，放大数字 54–140 号；块间距 0.3–0.5 英寸；每页先定密度级别（0 呼吸｜1 轻｜2 中｜3 重）。
# 颜色语义：红＝现状与影响、蓝＝目标与改后、绿＝现有功能可做、琥珀＝需开发、灰＝沿用与次要；章节分隔页为深色满版。
# 章节：一 目标｜二 弹窗｜三 推送｜四 标签｜附录（10/12 精简：工作进度汇报，正文只留目标与各项现状、做法；验收与细节页在附录，附录单独成节）。二至四每章按问题排：每个现状页后紧跟它的做法页（Dk 10/12：现状与解决方案要放在一块前后立刻看）。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, unicodedata
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.ns import qn
from lxml import etree

BASE = _ROOT + '/'
OUT = sys.argv[1] if len(sys.argv) > 1 else BASE + '弹窗标签推送方案/弹窗标签推送方案.pptx'   # 10/13 Dk 定名（此前误作「推送方」）
SHOT = BASE + '来源资料/后台截图_1010/弹窗顺序设定_规则列表.png'
FONT = 'Microsoft YaHei'
FOOT = '精细化运营能力方案'

# ───────── 颜色 ─────────
BG = 'F7F6F2'; CARD = 'FFFEFC'; LINE = 'E2DED5'; HEAD = 'EFEDE7'; STONE = 'F0EEE9'
NAVY = '1F2A44'; INK = '3A4254'; GRAY = '6A707C'; MUTE = '9A9FA8'; ARW = 'CFC9BD'
RED = 'B03A2E'; RED_W = 'F8E7E3'; RED_L = 'E6B9AF'
BLUE = '2A63A6'; BLUE_W = 'E7EEF8'; BLUE_L = 'BFD3EC'
GREEN = '2F6B52'; GREEN_W = 'E3EFE8'; GREEN_L = 'B7D4C4'
AMBER = '9A6212'; AMBER_W = 'F6ECD9'; AMBER_L = 'E2C795'
GRAY_W = 'ECEBE7'; GRAY_L = 'C9CCD2'
UI_LINE = 'CDD2DA'; UI_BLUE = '409EFF'; UI_TXT = '303133'; UI_SUB = '606266'

L, C, RT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM
X0 = 0.9; CW = 11.53; XR = X0 + CW
TS = 32          # 标题字号
Y1, Y1S = 1.95, 2.25   # 内容起点（无副标题／有副标题）

PEND = []   # (文本框, 目标页标题)：文中「第 {p} 页」在全稿生成后回填
prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
TITLES = []; WARN = []


def rgb(h):
    return RGBColor.from_string(h)


# ───────── 文字 ─────────
def cw(ch):
    if unicodedata.east_asian_width(ch) in ('W', 'F') or '①' <= ch <= '⑳':   # 圈号 ①–⑳ 按全角算
        return 1.0
    if ch == ' ':
        return 0.3
    if ch in '.,:;|':
        return 0.3
    if ch.isdigit():
        return 0.58
    if ch.isupper():
        return 0.68
    return 0.54


def tw(t, size):
    return sum(cw(c) for c in t) * size / 72


def _rf(r, size, color, bold):
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = rgb(color)
    rPr = r._r.get_or_add_rPr(); rPr.set('lang', 'zh-CN')
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)


def T(s, x, y, w, h, paras, size=15, color=INK, bold=False, align=L, anchor=TOP, ls=1.32, sa=0, spc=None, check=True):
    """paras: str | [para]；para: str | [(text, {size,color,bold})]"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    if isinstance(paras, str):
        paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        runs = p if isinstance(p, list) else [(p, {})]
        runs = [(r, {}) if isinstance(r, str) else r for r in runs]
        mx = max(o.get('size', size) for _, o in runs)
        para.line_spacing = Pt(mx * ls)
        if sa:
            para.space_after = Pt(sa)
        para.alignment = align
        width = 0
        for t, o in runs:
            r = para.add_run(); r.text = t
            _rf(r, o.get('size', size), o.get('color', color), o.get('bold', bold))
            if spc:
                r._r.get_or_add_rPr().set('spc', str(spc))
            width += tw(t, o.get('size', size)) * (1.04 if o.get('bold', bold) else 1.0)
        if check and width > w * 1.0:
            WARN.append('wrap p%d: %.2f>%.2f  %s' % (len(prs.slides), width, w, ''.join(t for t, _ in runs)[:30]))
    return tb


# ───────── 形状 ─────────
def R(s, x, y, w, h, fill=CARD, line=LINE, lw=0.75, r=0.08, dash=False, shape=None, alpha=None):
    shp = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE)
    sp = s.shapes.add_shape(shp, Inches(x), Inches(y), Inches(w), Inches(h))
    if shp in (MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.ROUND_2_SAME_RECTANGLE):
        sp.adjustments[0] = min(0.5, r / min(w, h))
        if shp == MSO_SHAPE.ROUND_2_SAME_RECTANGLE:
            sp.adjustments[1] = 0
    if fill:
        sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            clr = sp._element.spPr.find(qn('a:solidFill')).find(qn('a:srgbClr'))
            etree.SubElement(clr, qn('a:alpha')).set('val', str(int(alpha * 1000)))
    else:
        sp.fill.background()
    if line:
        sp.line.color.rgb = rgb(line); sp.line.width = Pt(lw)
        if dash:
            sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def LN(s, x1, y1, x2, y2, color=LINE, lw=1.0, dash=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    st = c._element.find(qn('p:style'))
    if st is not None:
        c._element.remove(st)
    c.line.color.rgb = rgb(color); c.line.width = Pt(lw)
    if dash:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return c


def ARR(s, x, y, w=0.36, h=0.28, color=ARW):
    sp = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(color); sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def CHEV(s, x, y, w=0.3, h=0.42, color=ARW):
    sp = s.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(color); sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def DARR(s, x, y, w=0.28, h=0.3, color=ARW):
    sp = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(color); sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def DOT(s, x, y, n, d=0.3, fill=BLUE, size=12):
    R(s, x, y, d, d, fill=fill, line=None, shape=MSO_SHAPE.OVAL)
    T(s, x - 0.05, y, d + 0.1, d, str(n), size, 'FFFFFF', True, align=C, anchor=MID, ls=1.0, check=False)


def chip(s, x, y, text, size=15, fill=STONE, color=NAVY, h=0.44, pad=0.22, bold=True, line=None):
    w = tw(text, size) * (1.04 if bold else 1) + 2 * pad
    R(s, x, y, w, h, fill=fill, line=line, r=h / 2)
    T(s, x, y, w, h, text, size, color, bold, align=C, anchor=MID, ls=1.0, check=False)
    return w


def donut(s, x, y, d, vals, colors, hole=66):
    cd = CategoryChartData(); cd.categories = [str(i) for i in range(len(vals))]; cd.add_series('s', vals)
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(d), Inches(d), cd)
    ch = gf.chart; ch.has_legend = False; ch.has_title = False
    pl = ch.plots[0]; pl.has_data_labels = False
    ser = pl.series[0]
    for i, c in enumerate(colors):
        pt = ser.points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(c)
        pt.format.line.color.rgb = rgb(CARD); pt.format.line.width = Pt(2)
    cs = ch._chartSpace
    dn = cs.find('.//' + qn('c:doughnutChart'))
    for tag, val in (('c:firstSliceAng', '0'), ('c:holeSize', str(hole))):
        el = dn.find(qn(tag))
        if el is None:
            el = etree.SubElement(dn, qn(tag))
        el.set('val', val)
    vc = dn.find(qn('c:varyColors'))
    if vc is not None:
        vc.set('val', '1')
    sp = etree.Element(qn('c:spPr'))
    etree.SubElement(sp, qn('a:noFill'))
    ln = etree.SubElement(sp, qn('a:ln')); etree.SubElement(ln, qn('a:noFill'))
    cs.find(qn('c:chart')).addnext(sp)
    return gf


CH = [('一', '目标', BLUE), ('二', '弹窗', NAVY), ('三', '推送', NAVY), ('四', '标签', NAVY), ('附录', '改动清单', GRAY)]
NCH = len(CH)
DARK_ACC = {0: '82B1E8', 1: 'DADEE7', 2: 'DADEE7', 3: 'DADEE7', 4: 'DADEE7'}
CH_PAGE = {}


def chapter_of(kicker):
    for i, (num, _, _) in enumerate(CH):
        if kicker and kicker.startswith(num):
            return i
    return None


def progress(s, ci, dark=False):
    gap = 0.08; w = (CW - gap * (NCH - 1)) / NCH
    for i, (num, name, col) in enumerate(CH):
        x = X0 + i * (w + gap)
        on = i == ci
        if dark:
            lc = DARK_ACC[i] if on else '7D8699'; bc = DARK_ACC[i] if on else '39445E'
        else:
            lc = col if on else MUTE; bc = col if on else 'E2DED5'
        T(s, x, 0.17, w, 0.24, (num + ' ' + name) if num != '附录' else '附录', 10.5, lc, on, ls=1.0)
        R(s, x, 0.44, w, 0.055 if on else 0.035, fill=bc, line=None, r=0)


def badge(s, x, y, d, num, col, size, txt='FFFFFF'):
    R(s, x, y, d, d, fill=col, line=None, r=d * 0.16)
    T(s, x - 0.1, y, d + 0.2, d, num, size, txt, True, align=C, anchor=MID, ls=1.0, check=False)


def new_slide(bg=BG):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(bg)
    return s


def page(kicker, title, sub=None, lv=2, tier=None):
    s = new_slide()
    n = len(prs.slides)
    if kicker:
        ci = chapter_of(kicker)
        if ci is not None:
            progress(s, ci)
            kc = RED if '现状' in kicker else CH[ci][2]
            num = CH[ci][0]
            rest = kicker[len(num):].strip()
            if ci < NCH - 1:
                badge(s, X0, 0.64, 0.3, num, kc, 13)
                T(s, X0 + 0.42, 0.62, 10, 0.32, rest, 13, kc, True, anchor=MID, ls=1.0, spc=60)
                if tier:
                    tc, tf_ = (GREEN, GREEN_W) if tier.startswith('现有') else (AMBER, AMBER_W)
                    chip(s, X0 + 0.42 + tw(rest, 13) * 1.1 + 0.25, 0.645, tier, 11, fill=tf_, color=tc, h=0.29, pad=0.13)
            else:
                T(s, X0, 0.62, 10, 0.32, kicker, 13, kc, True, anchor=MID, ls=1.0, spc=60)
                if tier:
                    tc, tf_ = (GREEN, GREEN_W) if tier.startswith('现有') else (AMBER, AMBER_W)
                    chip(s, X0 + tw(kicker, 13) * 1.1 + 0.25, 0.645, tier, 11, fill=tf_, color=tc, h=0.29, pad=0.13)
        elif kicker != '目录':
            T(s, X0, 0.62, 10, 0.32, kicker, 13, NAVY, True, anchor=MID, ls=1.0, spc=100)
        T(s, X0, 0.98, CW, 0.62, title, TS, NAVY, True, ls=1.1)
        if sub:
            T(s, X0, 1.64, CW, 0.32, sub, 16, GRAY, ls=1.1)
        T(s, X0, 6.98, 6, 0.25, FOOT + '　·　第 ' + str(n) + ' 页', 11, MUTE)
        TITLES.append((n, lv, kicker, title, sub or ''))
        if tw(title, TS) * 1.04 > CW:
            WARN.append('title p%d too long %.2f' % (n, tw(title, TS)))
    else:
        TITLES.append((n, lv, '封面', title or '', ''))
    return s


def card(s, x, y, w, h, fill=CARD, line=LINE, lw=0.75):
    return R(s, x, y, w, h, fill=fill, line=line, lw=lw, r=0.1)


def impact(s, text, y=5.95, x=X0, w=CW):
    lines = [text] if isinstance(text, str) else text
    h = 0.34 * len(lines) + 0.18
    R(s, x, y, 0.07, h, fill=RED, line=None, r=0)
    T(s, x + 0.28, y + 0.09, 0.7, 0.34, '影响', 16, RED, True, ls=1.3)
    T(s, x + 0.95, y + 0.09, w - 0.95, 0.34 * len(lines), lines, 17, NAVY, ls=1.3)


def divider(ci, lines, size=20, gap=0.62):
    s = new_slide(NAVY)
    n = len(prs.slides)
    num, name, col = CH[ci]
    acc = DARK_ACC[ci]
    progress(s, ci, dark=True)
    badge(s, X0, 2.45, 1.55, num, acc, 70, txt=NAVY)
    T(s, X0 + 2.0, 2.4, 9, 0.95, name, 50, 'FFFFFF', True, anchor=MID, ls=1.0)
    extra = 0
    for k, ln in enumerate(lines):
        y = 3.62 + k * gap + extra
        if isinstance(ln, str) and ln.startswith('§'):   # 分层小标题：不加圆点，用强调色
            T(s, X0 + 2.0, y, 9.4, 0.4, ln[1:], 17, acc, True, anchor=MID, ls=1.0)
            continue
        R(s, X0 + 2.36, y + 0.135, 0.12, 0.12, fill=acc, line=None, shape=MSO_SHAPE.OVAL) if any(isinstance(l_, str) and l_.startswith('§') for l_ in lines) else R(s, X0 + 2.06, y + 0.135, 0.12, 0.12, fill=acc, line=None, shape=MSO_SHAPE.OVAL)
        runs = [[(ln[0], {'color': 'B9C0CE'}), ('  →  ', {'color': '7D8699'}), (ln[1], {'color': 'FFFFFF', 'bold': True})]] if isinstance(ln, tuple) else ln
        xo = 2.7 if any(isinstance(l_, str) and l_.startswith('§') for l_ in lines) else 2.4
        T(s, X0 + xo, y, 11.53 - xo + 0.0, 0.4, runs, size, 'B9C0CE', anchor=MID, ls=1.0)
        if isinstance(ln, tuple) and len(ln) > 2:   # 小字注：属于改后，放在箭头右侧、与做法文字左对齐
            nx_ = X0 + xo + tw(ln[0], size) + 2.2 * size / 72 - (0.09 if ln[2].startswith('（') else 0)   # 「  →  」实际约 2.2 个字宽；全角左括号字形偏右，左移对齐
            T(s, nx_, y + 0.4, X0 + CW - nx_, 0.3, ln[2], 14, '8E97AA', anchor=MID, ls=1.0)
            extra += 0.34
    T(s, X0, 6.98, 6, 0.25, FOOT + '　·　第 ' + str(n) + ' 页', 11, '7D8699')
    CH_PAGE[ci] = n
    TITLES.append((n, 0, '分隔页', num + ' ' + name, '｜'.join(ln.lstrip('§') if isinstance(ln, str) else ln[0] + '→' + ln[1] for ln in lines)))
    return s


# ───────── 示意用的后台控件 ─────────
def ui_input(s, x, y, w, h, text, drop=False, focus=False, size=13):
    R(s, x, y, w, h, fill='FFFFFF', line=(UI_BLUE if focus else UI_LINE), lw=0.9, r=0.05)
    if w < 0.8:
        T(s, x, y, w, h, text, size, UI_TXT, align=C, anchor=MID, ls=1.0)
    else:
        T(s, x + 0.12, y, w - 0.4, h, text, size, UI_TXT, anchor=MID, ls=1.0)
    if drop:
        T(s, x + w - 0.3, y, 0.22, h, '▾', size, '9AA0AA', anchor=MID, ls=1.0, check=False)


def ui_check(s, x, y, label, on, size=13, h=0.32):
    d = 0.17
    R(s, x, y + (h - d) / 2, d, d, fill=(UI_BLUE if on else 'FFFFFF'), line=(UI_BLUE if on else UI_LINE), lw=0.9, r=0.03)
    if on:
        T(s, x - 0.02, y + (h - d) / 2 - 0.02, d + 0.04, d + 0.04, '✓', 10, 'FFFFFF', True, align=C, anchor=MID, ls=1.0, check=False)
    T(s, x + d + 0.08, y, tw(label, size) + 0.1, h, label, size, (UI_BLUE if on else UI_SUB), anchor=MID, ls=1.0)
    return d + 0.08 + tw(label, size) + 0.24


def ui_radio(s, x, y, label, on, size=13, h=0.32):
    d = 0.17
    R(s, x, y + (h - d) / 2, d, d, fill=(UI_BLUE if on else 'FFFFFF'), line=(UI_BLUE if on else UI_LINE), lw=0.9, shape=MSO_SHAPE.OVAL)
    if on:
        R(s, x + 0.055, y + (h - d) / 2 + 0.055, 0.06, 0.06, fill='FFFFFF', line=None, shape=MSO_SHAPE.OVAL)
    T(s, x + d + 0.08, y, tw(label, size) + 0.1, h, label, size, (UI_BLUE if on else UI_SUB), anchor=MID, ls=1.0)
    return d + 0.08 + tw(label, size) + 0.24


def ui_btn(s, x, y, label, primary=True, size=13, h=0.34):
    w = tw(label, size) + 0.4
    R(s, x, y, w, h, fill=(UI_BLUE if primary else 'FFFFFF'), line=(None if primary else UI_LINE), lw=0.9, r=0.05)
    T(s, x, y, w, h, label, size, ('FFFFFF' if primary else UI_SUB), True, align=C, anchor=MID, ls=1.0)
    return w


def ui_new(s, x, y, label='新加', size=11, h=0.24):
    w = tw(label, size) + 0.18
    R(s, x, y, w, h, fill='2B5EA8', line=None, r=0.04)
    T(s, x, y, w, h, label, size, 'FFFFFF', True, align=C, anchor=MID, ls=1.0)
    return w


def tile(s, x, y, w, h, name, dashed=False, size=15, faded=False):
    if faded:
        R(s, x, y, w, h, fill='F3F2EE', line='DDD9D0', lw=0.75, r=0.1, dash=True)
        T(s, x, y, w, h, name, 13, MUTE, align=C, anchor=MID, ls=1.0)
        return
    R(s, x, y, w, h, fill='FFFFFF', line=('8E949E' if dashed else 'D5D1C8'), lw=(1.25 if dashed else 0.9), dash=dashed, r=0.1)
    R(s, x + (0.06 if dashed else 0), y + (0.06 if dashed else 0), w - (0.12 if dashed else 0), 0.14, fill='8C93A8', line=None,
      r=0.07, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
    T(s, x + 0.06, y + 0.14, w - 0.12, h - 0.14, name, size, NAVY, True, align=C, anchor=MID, ls=1.15)


def bracket(s, x1, x2, y, color=GRAY_L, down=True):
    LN(s, x1, y, x2, y, color, 1.25)
    d = 0.09 if down else -0.09
    LN(s, x1, y, x1, y + d, color, 1.25); LN(s, x2, y, x2, y + d, color, 1.25)


# ══════════════════════ 1 封面（0） ══════════════════════
s = page(None, '精细化运营能力方案', lv=0)
R(s, X0, 2.6, 0.85, 0.08, fill=BLUE, line=None, r=0.04)
T(s, X0, 2.9, 7, 0.4, '弹窗 · 推送 · 标签', 20, BLUE, True, spc=200)
T(s, X0, 3.4, 7.2, 1.1, '精细化运营能力方案', 52, NAVY, True, ls=1.1)
T(s, X0, 4.7, 7, 0.45, [[('所有玩家用同一套弹窗规则', {'color': GRAY}), (' → ', {'color': MUTE}), ('按五类人群分别配置', {'color': NAVY, 'bold': True})]], 19)
cd_ = 2.2; ccx, ccy = 8.05, 2.62
R(s, ccx, ccy, cd_, cd_, fill='E9E7E1', line=None, shape=MSO_SHAPE.OVAL)
T(s, ccx, ccy, cd_, cd_, [[('近一月登录', {'size': 12, 'color': GRAY})], [('62,292 人', {'size': 24, 'bold': True, 'color': NAVY})], [('用同一套弹窗规则', {'size': 12, 'color': GRAY})]], 14, align=C, anchor=MID, ls=1.3)
CHEV(s, ccx + cd_ + 0.18, ccy + cd_ / 2 - 0.2, 0.24, 0.4)
for k, (nm, f_) in enumerate([('新增', '9DBCE3'), ('回流', '7FA8DA'), ('破产', '5F91CE'), ('潜在付费', '3F78C0'), ('潜在流失', BLUE)]):
    yy = 1.7 + k * 0.7
    R(s, 10.7, yy, 0.54, 0.54, fill=f_, line=None, shape=MSO_SHAPE.OVAL)
    T(s, 11.36, yy, 1.07, 0.54, nm, 15, NAVY, True, anchor=MID, ls=1.0)
yy = 1.7 + 5 * 0.7   # 五类以外：灰色虚线圈，表示沿用现有规则
R(s, 10.7, yy, 0.54, 0.54, fill=None, line=GRAY_L, lw=1.25, dash=True, shape=MSO_SHAPE.OVAL)
T(s, 11.36, yy - 0.04, 1.07, 0.62, [[('其余玩家', {'size': 15, 'bold': True, 'color': GRAY})], [('沿用现有规则', {'size': 12, 'color': GRAY})]], 15, anchor=MID, ls=1.15)

# ══════════════════════ 2 结论（1） ══════════════════════
s = page('结论', '弹窗与推送改为按五类人群分别配置', lv=1)
gap = 0.5; pw = (CW - 2 * gap) / 3; P = 0.38; iw = pw - 2 * P
py, ph = 2.05, 4.2
for i, (lab, col) in enumerate([('现在 · 近一月登录', RED), ('目标', BLUE), ('做法', NAVY)]):
    x = X0 + i * (pw + gap)
    card(s, x, py, pw, ph)
    T(s, x + P, py + 0.38, iw, 0.3, lab, 15, col, True, spc=200)
    LN(s, x + P, py + 2.95, x + pw - P, py + 2.95, LINE)
    if i < 2:
        CHEV(s, x + pw + 0.13, py + ph / 2 - 0.21, 0.24, 0.42)
x = X0
T(s, x + P, py + 0.8, iw, 1.0, [[('62,292', {}), (' 人', {'size': 24})]], 46, RED, True, anchor=MID, ls=1.0)
T(s, x + P, py + 1.95, iw, 0.4, '用同一套弹窗规则', 19, NAVY, True)
T(s, x + P, py + 3.08, iw, 1.05, ['推送分散在不同地方配置', '不能统一按人群发送', '潜在付费、潜在流失没有标签'], 15, INK, ls=1.45)
x = X0 + pw + gap
T(s, x + P, py + 0.8, iw, 1.0, [[('5', {}), (' 类', {'size': 24})]], 46, BLUE, True, anchor=MID, ls=1.0)
T(s, x + P, py + 1.95, iw, 0.4, '目标人群', 19, NAVY, True)
T(s, x + P, py + 2.4, iw, 0.5, ['新增、回流、破产、', '潜在付费、潜在流失'], 14, BLUE, True, ls=1.3)
T(s, x + P, py + 3.08, iw, 1.05, ['弹窗、推送按人群配置', '每人收到的弹窗、推送有上限', '数据按人群可查'], 15, INK, ls=1.45)
x = X0 + 2 * (pw + gap)
T(s, x + P, py + 0.8, iw, 1.0, [[('17', {}), (' 项', {'size': 24})]], 46, NAVY, True, anchor=MID, ls=1.0)
T(s, x + P, py + 1.82, iw, 0.9, [[('现有功能可做 6 项', {'color': GREEN})], [('需开发 11 项', {'color': AMBER})]], 17, NAVY, True, ls=1.35)
CONC_TB = T(s, x + P, py + 3.08, iw, 1.05, ['需开发的 11 项中：', '较大开发 4 项、小改动 7 项', '17 项清单见第 ? 页'], 15, INK, ls=1.45)
T(s, X0, py + ph + 0.2, CW, 0.3, '人数均取自 9/16 的数据；近一月登录指 8/16–9/16 登录过的玩家', 12.5, GRAY)

TOC_SLIDE = page('目录', '目录', '本方案对应产品计划里「短期计划」的三项：弹窗、推送、标签（第二至四章）', lv=0)


# ══════════════════════ 一 目标 ══════════════════════
divider(0, ['五类人群：四类按标签选出；破产玩家在破产时弹出破产弹窗', '弹窗、推送按人群配置', '每人收到的弹窗与推送有上限，可在后台设定', '弹窗与推送的数据都能按人群查'])

# ── 一·0 规则组成（10/15 新增，Dk 认可的框架：规则＝事件＋状态＋内容＋频次）
# 放在人群页之前：读者在人群页第一次遇到「四类按标签、破产按破产时触发」，先有这个概念才看得懂。
# 版面：三列＝事件 → 状态 → 内容（下半是频次约束）；三行＝一条规则的组成、破产的例子、本方案补的地方，逐列对齐。
s = page('一 目标 · 规则组成', '弹窗与推送：事件发生时查玩家状态，符合就给内容', lv=2)
LB, gx = 0.95, 0.42
W1, W2 = 2.85, 4.2
W3 = XR - (X0 + LB) - W1 - W2 - 2 * gx
CX = [X0 + LB, X0 + LB + W1 + gx, X0 + LB + W1 + W2 + 2 * gx]; CWS = [W1, W2, W3]; P_ = 0.22
ry1, rh1 = 1.95, 2.62
ry2, rh2 = ry1 + rh1 + 0.16, 0.92
ry3, rh3 = ry2 + rh2 + 0.16, 0.82
for ry_, rh_, lab_, col_ in [(ry1, rh1, '一条规则', NAVY), (ry2, rh2, '例：破产', NAVY), (ry3, rh3, '本方案补', BLUE)]:
    T(s, X0, ry_, LB - 0.1, rh_, lab_, 14.5, col_, True, anchor=MID, ls=1.0)


def rhead(x, y, w, nm, q):
    T(s, x, y, w, 0.4, [[(nm, {'size': 20, 'bold': True, 'color': NAVY}), ('　' + q, {'size': 14, 'color': GRAY})]], 20, anchor=MID, ls=1.0)


# 第一行：一条规则的四部分
for k in range(3):
    card(s, CX[k], ry1, CWS[k], rh1)
    if k < 2:
        CHEV(s, CX[k] + CWS[k] + (gx - 0.2) / 2, ry1 + rh1 / 2 - 0.2, 0.2, 0.4)
x, w = CX[0] + P_, W1 - 2 * P_
rhead(x, ry1 + 0.18, w, '事件', '什么时候动手')
T(s, x, ry1 + 0.7, w, 0.5, ['某个时刻发生的一件事，', '常是状态的一次变化'], 14, INK, ls=1.3)
T(s, x, ry1 + 1.32, w, 0.75, [[('游戏里　', {'bold': True, 'color': NAVY}), ('进大厅、破产、升级', {})], [('按时间　', {'bold': True, 'color': NAVY}), ('每天定时', {})],
                             [('状态变化　', {'bold': True, 'color': NAVY}), ('刚变成潜在流失', {})]], 13, INK, ls=1.4)
T(s, x, ry1 + 2.1, w, 0.3, '状态变化最适合触发推送', 13, BLUE, True)
x, w = CX[1] + P_, W2 - 2 * P_
rhead(x, ry1 + 0.18, w, '状态', '那一刻谁符合')
T(s, x, ry1 + 0.7, w, 0.5, ['一段时间里一直成立，会变；', '随时都能问「这个玩家现在是不是」'], 14, INK, ls=1.3)
for j, (lab, how, ex) in enumerate([('变得慢的', '事先算好，存成标签，定时更新', '新增、回流、卡别、潜在流失（需新建）'),
                                    ('变得快的', '事件发生时当场查', '当前余额、本局输赢、今天已弹几个')]):
    by = ry1 + 1.32 + j * 0.6
    R(s, x - 0.08, by, w + 0.16, 0.54, fill=STONE, line=None, r=0.06)
    T(s, x + 0.08, by, w - 0.16, 0.54, [[(lab + '　', {'bold': True, 'color': NAVY}), (how, {'color': INK})], [(ex, {'color': GRAY, 'size': 12.5})]], 13, anchor=MID, ls=1.3)
x, w = CX[2] + P_, W3 - 2 * P_
rhead(x, ry1 + 0.18, w, '内容', '给他看什么')
T(s, x, ry1 + 0.7, w, 0.3, '例：破产礼包、首储礼包', 13.5, GRAY)
R(s, CX[2] + 0.08, ry1 + 1.16, W3 - 0.16, rh1 - 1.24, fill=STONE, line=None, r=0.06)
rhead(x, ry1 + 1.26, w, '频次', '最多几次')
T(s, x, ry1 + 1.74, w, 0.72, [['按人统一计数，'], ['各条规则合在一起算'], [('弹窗、每种推送各有上限', {'color': GRAY, 'size': 12.5})]], 13.5, INK, ls=1.3)

# 第二行：破产套进同一条流程
for k, paras in enumerate([[[('「刚破产」', {'bold': True, 'color': NAVY, 'size': 14})], '破产弹窗由这个事件触发'],
                           ['「余额不足」是变得快的状态，当场查', '不另建破产标签：提前算成标签会过时', '金卡、普卡要看不同礼包时，再加卡别标签'],
                           [[('破产礼包', {'bold': True, 'color': NAVY, 'size': 14})], '不超过每人每天弹窗上限']]):
    R(s, CX[k], ry2, CWS[k], rh2, fill=STONE, line=None, r=0.08)
    T(s, CX[k] + P_, ry2, CWS[k] - 2 * P_, rh2, paras, 13, INK, anchor=MID, ls=1.3)
    if k < 2:
        CHEV(s, CX[k] + CWS[k] + (gx - 0.14) / 2, ry2 + rh2 / 2 - 0.14, 0.14, 0.28)

# 第三行：本方案在事件、状态、频次三处补什么（名称同附录改动清单）
for k, items in enumerate([['推送跳转与触发自助', '新手弹窗接入后台'],
                           ['新建潜在付费、潜在流失标签', '群组交集：标签组成的群组之间可取交集'],
                           ['每人每天弹窗上限', '每种推送每人每天上限']]):
    R(s, CX[k], ry3, CWS[k], rh3, fill=BLUE_W, line=None, r=0.08)
    for j, it in enumerate(items):
        iy = ry3 + rh3 / 2 - 0.29 + j * 0.3
        R(s, CX[k] + P_, iy + 0.11, 0.07, 0.07, fill=BLUE, line=None, shape=MSO_SHAPE.OVAL)
        T(s, CX[k] + P_ + 0.18, iy, CWS[k] - 2 * P_ - 0.18, 0.28, it, 13.5, NAVY, anchor=MID, ls=1.0)

# ── 二·1 五类人群（1）
s = page('一 目标 · 人群', '五类目标人群中，潜在付费、潜在流失要新建标签', lv=1)
g5 = 0.22; w5 = (CW - 4 * g5) / 5; y5, h5 = 2.05, 2.85
people = [('新增', ['注册 30 天内'], ('现有标签', '近一月登录中', '10,749 人'), False), ('回流', ['后台会员身份', '为「回流」'], ('现有标签', '近一月登录中', '16,564 人'), False),
          ('破产', ['游戏中破产的', '玩家（破产时）'], ('不另建标签', '破产那一刻', '触发破产弹窗'), False),
          ('潜在付费', ['从未储值，', '且近期押注偏高'], ('需新建标签',), True), ('潜在流失', ['登录天数下降，', '但尚未流失'], ('需新建标签',), True)]
for i, (nm, d_, cnt, new) in enumerate(people):
    x = X0 + i * (w5 + g5)
    card(s, x, y5, w5, h5, fill=(BLUE_W if new else CARD), line=(BLUE_L if new else LINE), lw=(1.25 if new else 0.75))
    T(s, x + 0.22, y5 + 0.32, w5 - 0.44, 0.45, nm, 24, NAVY, True, ls=1.0)
    T(s, x + 0.22, y5 + 0.92, w5 - 0.44, 0.7, d_, 14, GRAY, ls=1.4)
    LN(s, x + 0.22, y5 + 1.8, x + w5 - 0.22, y5 + 1.8, (BLUE_L if new else LINE))
    T(s, x + 0.22, y5 + 1.9, w5 - 0.44, 0.85, [[(cnt[0], {'bold': True, 'color': (BLUE if new else NAVY), 'size': 17})]] + [[(c_, {'color': GRAY, 'size': 14})] for c_ in cnt[1:]], 17, anchor=MID, ls=1.3)
T(s, X0, 5.45, CW, 0.75, [[('为什么要标签　', {'bold': True, 'color': NAVY}), ('弹窗按标签选择发给谁，改后推送也一样；破产以外的四类，没有标签就不能单独配置', {'color': INK})],
                          [('破产玩家不用另建标签　', {'bold': True, 'color': NAVY}), ('破产弹窗在玩家破产那一刻触发，余额变得快，提前算成标签会过时', {'color': INK})]], 17, ls=1.32, sa=6)

# ── 二·2 三项目标（2）
s = page('一 目标 · 弹窗与推送', '改完后要达到的三项目标', lv=2)
g3 = 0.4; w3 = (CW - 2 * g3) / 3; y3, h3 = 1.95, 3.36
goals = [('弹窗、推送按人群配置', ['每类人群的弹窗可以单独设置', '同属两类的玩家只看一类的', '所有推送在一处按人群发'], ['现在所有人用同一套弹窗规则', '推送分散，不能统一按人群发']),
         ('每人收到的数量有上限', ['弹窗每次、每天各有上限', '新手挑战、新手通行证也计入', '推送每种每人每天有上限'], ['新手弹窗不在后台，算不进上限', '没有每天总上限']),
         ('数据按人群可查', ['游戏内：曝光、点击', '游戏外：发送、到达、点击', [('（iOS 推播没有到达，', {'size': 12.5, 'color': GRAY})], [('LINE 到达只有按日总数）', {'size': 12.5, 'color': GRAY})], '所有推送的数据在一处看'], ['推送数据分在不同报表', '部分推送的数据不在后台报表里'])]
for i, (goal, det, why) in enumerate(goals):
    x = X0 + i * (w3 + g3); P = 0.35
    card(s, x, y3, w3, h3)
    T(s, x + P, y3 + 0.28, w3 - 2 * P, 0.45, goal, 19, BLUE, True, anchor=MID, ls=1.0)
    T(s, x + P, y3 + 0.8, w3 - 2 * P, 1.4, det, 15, NAVY, ls=1.4)
    LN(s, x + P, y3 + 2.26, x + w3 - P, y3 + 2.26, LINE)
    T(s, x + P, y3 + 2.36, w3 - 2 * P, 0.95, [[('为什么', {'bold': True, 'color': NAVY, 'size': 13})]] + [[(w_, {})] for w_ in why], 14, GRAY, ls=1.4)
T(s, X0, 5.42, CW, 0.3, [[('游戏内', {'bold': True, 'color': NAVY}), ('：弹窗、快显，玩家在游戏里才看得到　　', {}), ('游戏外推送', {'bold': True, 'color': NAVY}), ('：推播、短信、Facebook、LINE，不在游戏里也收得到', {})]], 13, GRAY)
R(s, X0, 5.8, 0.07, 0.62, fill=BLUE, line=None, r=0)
T(s, X0 + 0.25, 5.8, CW - 0.25, 0.62, [[('游戏外推送还要覆盖 8 天以上未登录的新增、回流玩家', {'color': BLUE, 'bold': True}), ('：他们只收得到游戏外推送', {'color': INK})],
                                       [('8/1–9/16 登录过的 74,480 人中，8 天以上未登录 40,117 人，其中新增、回流 ', {'color': GRAY, 'size': 14}), ('14,502 人', {'color': NAVY, 'bold': True, 'size': 14})]], 15, anchor=MID, ls=1.35)
T(s, X0, 6.52, CW, 0.3, '五类以外的玩家沿用现有弹窗与推送', 12.5, GRAY)

# ══════════════════════ 二 弹窗：每个现状后紧跟它的做法 ══════════════════════
divider(1, [('所有玩家用同一套弹窗规则', '活动类弹窗按人群拆成四条规则'), ('每人每天弹几个没有总上限', '加每人每天弹窗上限'), ('新手挑战、新手通行证固定在客户端', '改由弹窗后台配置')])

# ── 一·1（1）：大数字＋真实后台截图
s = page('二 弹窗 · 现状', '现在所有玩家用同一套弹窗规则', lv=1)
iw_, ih_ = 7.0, 7.0 * 517 / 920
ix, iy = XR - iw_, 2.72
lw_ = ix - X0 - 0.45
T(s, X0, 2.3, lw_, 0.35, '近一月登录的玩家', 16, GRAY)
T(s, X0, 2.7, lw_, 1.1, [[('62,292', {}), (' 人', {'size': 30})]], 66, RED, True, anchor=MID, ls=1.0)
T(s, X0, 3.85, lw_, 0.4, '全部按同一顺序弹出', 18, NAVY, True)
LN(s, X0, 4.65, X0 + lw_, 4.65, LINE)
T(s, X0, 4.85, lw_, 0.8, [[('其中新增与回流玩家 ', {'color': GRAY}), ('27,313 人（43.85%）', {'color': NAVY, 'bold': True})], [('也按这一套弹出', {'color': GRAY})]], 15, ls=1.5)
T(s, ix, 1.98, iw_, 0.65, [[('上架的 3 条弹窗规则，对象都是「全部玩家」', {'color': RED, 'bold': True})], [('大厅活动类、大厅储值类（即图中「通用弹窗」）、破产储值类；截图为后两条', {'color': GRAY, 'size': 13})]], 14, ls=1.3)
pic = s.shapes.add_picture(SHOT, Inches(ix), Inches(iy), Inches(iw_), Inches(ih_))
pic.crop_left = 468 / 1630; pic.crop_right = (1630 - 1388) / 1630; pic.crop_top = 155 / 680; pic.crop_bottom = 8 / 680
pic.line.color.rgb = rgb(UI_LINE); pic.line.width = Pt(0.75)
hx = ix + (1238 - 468) / 920 * iw_
R(s, hx - 0.02, iy - 0.04, 150 / 920 * iw_ + 0.04, ih_ + 0.08, fill=None, line=RED, lw=2.5, r=0.06)

# ── 三·3 活动弹窗分四组（2）
s = page('二 弹窗 · 做法', '活动类弹窗按人群拆成四条规则，每名玩家只符合一条', lv=2, tier='现有功能可做')
lx, lw_ = X0, 2.7
rx = X0 + lw_ + 0.55; rw = 3.95
rungs = [('是新增？', '活动类 · 新增', '对象：标签「新增」', '首版：活动类弹窗每次由 3 个减为 1 个'),
         ('是回流？', '活动类 · 回流', '对象：标签「回流」，排除新增', '首版：回流任务排第 1 个'),
         ('是潜在流失实验组？', '活动类 · 潜在流失', '对象：潜在流失实验组，排除新增、回流', '首版：每日补给计划排第 1 个'),
         ('其余玩家', '活动类 · 其余', '对象：全部玩家，排除以上三组', '首版：沿用现有排序')]
rh_, rg = 0.8, 0.2
for i, (q, nm, obj, first) in enumerate(rungs):
    y = 1.95 + i * (rh_ + rg)
    last = i == 3
    R(s, lx, y, lw_, rh_, fill=(STONE if last else GREEN_W), line=None, r=0.1)
    sub_q = {'是潜在流失实验组？': '按 ID 尾数分出一半', '其余玩家': '含潜在流失另一半（对照组）'}.get(q)
    qp = [[(q, {})]] + ([[(sub_q, {'size': 12.5, 'bold': False, 'color': GRAY})]] if sub_q else [])
    T(s, lx + 0.22, y, lw_ - 0.36, rh_, qp, 16, NAVY, True, anchor=MID, ls=1.2)
    ARR(s, lx + lw_ + 0.1, y + rh_ / 2 - 0.13, 0.35, 0.26)
    card(s, rx, y, rw, rh_)
    T(s, rx + 0.25, y, rw - 0.4, rh_, [[(nm, {'bold': True, 'color': NAVY, 'size': 15})], [(obj, {'color': INK, 'size': 13.5})],
                                       [(first, {'color': (GRAY if last else BLUE), 'size': 13.5, 'bold': not last})]], 15, anchor=MID, ls=1.22)
    if not last:
        DARR(s, lx + lw_ / 2 - 0.11, y + rh_ + 0.02, 0.22, rg - 0.04)
        T(s, lx + lw_ / 2 + 0.17, y + rh_, 0.5, rg, '否', 12, GRAY, anchor=MID, ls=1.0)
# 另外两类人群：放在四条规则下方，与上面一起凑齐五类
by_ = 1.95 + 4 * rh_ + 3 * rg + 0.17; bw_ = rx + rw - lx
card(s, lx, by_, bw_, 0.78, fill=STONE, line=None)
T(s, lx + 0.25, by_, 1.2, 0.78, [[('破产', {})], [('潜在付费', {})]], 15, NAVY, True, anchor=MID, ls=1.45)
T(s, lx + 1.45, by_, bw_ - 1.6, 0.78, ['破产弹窗：实验组中已储值的玩家先看破产礼包，对照组不变', '储值类弹窗本就先给首储礼包，所以首版不另建规则'], 14, INK, anchor=MID, ls=1.55)
nx = rx + rw + 0.35; nw = XR - nx
for by, bh, k, lines in [(1.95, 2.45, '首版：上线后的第一版弹窗内容', ['每日补给计划排第 1 个', '已储值玩家先看破产礼包', '这两种排法都没有现成依据', '所以潜在流失、破产玩家各分一半：', '实验组用上面的新排法，对照组不变', '比较两组人均点击，再定用哪种排法']),
                         (4.6, by_ + 0.78 - 4.6, '为什么这样排', ['玩家符合几条规则，每条都会弹', '排除前几条后，每人只符合一条', '先认身份（新增、回流），', '再看行为（潜在流失）'])]:
    card(s, nx, by, nw, bh, fill=STONE, line=None)
    T(s, nx + 0.3, by + 0.22, nw - 0.6, 0.3, k, 16, NAVY, True)
    T(s, nx + 0.3, by + 0.62, nw - 0.6, bh - 0.75, lines, 14, INK, ls=1.4)

# ── 三·6 弹窗两项开发（2）
s = page('二 弹窗 · 做法', '要限制每人收到的弹窗数，还需开发两项', lv=2, tier='需开发')
pw = (CW - 0.4) / 2
for i in range(2):
    card(s, X0 + i * (pw + 0.4), 1.95, pw, 4.6)
x = X0; P = 0.4
T(s, x + P, 2.22, pw - 2 * P, 0.4, [[('每人每天弹窗上限', {'bold': True, 'color': NAVY, 'size': 20}), ('　小改动 · 弹窗后台', {'color': AMBER, 'size': 13, 'bold': True})]], 20)
mx, my, mw = x + P, 2.9, pw - 2 * P
R(s, mx, my, mw, 1.25, fill='FFFFFF', line=UI_LINE, lw=0.9, r=0.04)
T(s, mx + 0.18, my + 0.08, 3, 0.3, '大厅弹窗顺序设定（示意）', 12, UI_BLUE, anchor=MID)
LN(s, mx, my + 0.45, mx + mw, my + 0.45, 'E4E7ED', 0.75)
R(s, mx + 0.15, my + 0.6, mw - 0.3, 0.5, fill='EAF1FB', line='C6D9F1', lw=0.75, r=0.04)
xx = mx + 0.28
xx += ui_new(s, xx, my + 0.73) + 0.12
T(s, xx, my + 0.6, 1.3, 0.5, '每人每天上限', 13, UI_TXT, True, anchor=MID, ls=1.0); xx += 1.2
ui_input(s, xx, my + 0.68, 0.55, 0.34, ''); xx += 0.65
T(s, xx, my + 0.6, 1.9, 0.5, '个（大厅与破产合计）', 13, UI_SUB, anchor=MID, ls=1.0)
T(s, x + P, 4.3, pw - 2 * P, 2.15, [[('每人每天最多弹几个，大厅与破产弹窗合计', {'color': NAVY, 'bold': True})],
                                    [('先在弹窗后台设；推送统一后台建成后，', {'color': INK, 'size': 14})],
                                    [('移到「频率上限」页，与其他推送上限一起设', {'color': INK, 'size': 14})],
                                    [('按弹出先后计数', {'color': INK, 'size': 15})],
                                    [('达到上限后，当天大厅、破产都不再弹', {'color': INK, 'size': 15})],
                                    [('剩余额度不够时，按排序只弹前面的', {'color': INK, 'size': 15})],
                                    [('现在　', {'color': RED, 'bold': True, 'size': 14}), ('没有每天总上限', {'color': GRAY, 'size': 14})],
                                    [('活动类 14 项各每天弹 1 次，一天就可能弹 14 个', {'color': GRAY, 'size': 14})]], 16, ls=1.32)
x = X0 + pw + 0.4
T(s, x + P, 2.22, pw - 2 * P, 0.4, [[('新手弹窗改由后台配置', {'bold': True, 'color': NAVY, 'size': 20}), ('　较大开发 · 客户端', {'color': AMBER, 'size': 13, 'bold': True})]], 20)
fw2 = (pw - 2 * P - 0.6) / 2
for j, (k_, v, f, c) in enumerate([('现在 · 客户端', ['固定在程序里', '后台查不到'], STONE, GRAY), ('改后 · 弹窗后台', ['设何时弹、给谁', '计入弹出个数'], BLUE_W, BLUE)]):
    xx = x + P + j * (fw2 + 0.6)
    R(s, xx, 2.9, fw2, 1.25, fill=f, line=None, r=0.08)
    T(s, xx + 0.05, 2.9, fw2 - 0.1, 1.25, [[(k_, {'bold': True, 'color': c, 'size': 15})]] + [[(t, {'color': INK, 'size': 13})] for t in v], 14, align=C, anchor=MID, ls=1.35)
    if j < 1:
        ARR(s, xx + fw2 + 0.14, 3.4, 0.32, 0.26)
T(s, x + P, 4.5, pw - 2 * P, 1.9, [[('新手挑战、新手通行证两个弹窗改由后台配置', {'color': NAVY, 'bold': True})], [('计入新增玩家每次、每天的弹出个数，排在最前', {'color': INK})]], 16, ls=1.45)

# ══════════════════════ 三 推送 ══════════════════════
divider(2, ['§游戏外推送：推播、短信、Facebook、LINE，不在游戏里也收得到', ('配置分散，不能统一按人群发', '先按标签发短信，再建推送统一后台'), ('数据分散，部分无后台报表', '推送统一后台查发送、到达、点击', '（建成后 iOS 推播仍没有到达，LINE 到达只有按日总数）'),
           
            '§游戏内推送：快显（游戏内的即时提示），只有在线玩家看得到；弹窗见第二章', ('快显固定在客户端，不能按人群显示', '改由推送统一后台配置，按人群显示')], size=18, gap=0.58)

# ── 游戏外推送现状
s = page('三 推送 · 现状', '游戏外推送分在礼包后台、营销侧，不能统一按人群发', lv=2)
PEND.append((T(s, X0, 1.95, CW, 0.32, [[('游戏外推送', {'bold': True, 'color': NAVY}), ('：玩家不在游戏里也收得到。游戏内的快显另见第 {p} 页', {'color': GRAY})]], 14), '快显改由推送统一后台配置，按人群显示并记曝光、点击'))
w2 = (CW - 0.4) / 2
cols = [('礼包后台', ['推播'], ['手机 App 通知，现在用于限时加码礼包，', '发给触发后未购买的玩家'], '装了 App 并授权的玩家', ['推播报表']),
        ('营销侧', ['短信', 'Facebook', 'LINE'], ['短信：营销人员按名单发送', 'Facebook、LINE：由营销侧发送'], '短信：名单上的玩家', ['短信：数据平台', 'Facebook、LINE：', '现有后台没有报表'])]
x = X0
cy_, ch_ = 2.38, 3.0
for i, (place, chs, how, who, data) in enumerate(cols):
    card(s, x, cy_, w2, ch_)
    T(s, x + 0.4, cy_ + 0.2, w2 - 0.8, 0.3, place, 14, GRAY, True, spc=150)
    cx = x + 0.4
    for c_ in chs:
        cx += chip(s, cx, cy_ + 0.56, c_, 17, h=0.5, pad=0.2) + 0.1
    T(s, x + 0.4, cy_ + 1.13, w2 - 0.8, 0.6, how, 14, INK, ls=1.4)
    LN(s, x + 0.4, cy_ + 1.78, x + w2 - 0.4, cy_ + 1.78, LINE)
    T(s, x + 0.4, cy_ + 1.88, w2 - 0.8, 0.5, [[('谁收到', {'color': GRAY, 'bold': True, 'size': 12.5})], [(who, {'color': NAVY, 'bold': True})]], 14, ls=1.25)
    T(s, x + 2.6, cy_ + 1.88, w2 - 3.0, 1.0, [[('数据', {'color': GRAY, 'bold': True, 'size': 12.5})]] + [[(d_, {'color': NAVY, 'bold': True})] for d_ in data], 14, ls=1.25)
    x += w2 + 0.4
impact(s, ['8/1–9/16 登录过的 74,480 人中，8 天以上未登录的有 40,117 人', '他们只能靠这四种推送联系，现在却不能统一按人群发', '没有一处能看到一名玩家一天收到几条，发送、到达、点击也查不全'], y=5.56)

# ── 推送·做法（现有功能）：开发前，短信先按标签发；推播看礼包后台能否选标签
s = page('三 推送 · 做法', '开发前，短信先按标签选发送对象', '礼包后台能选标签时，推播也一样', lv=2, tier='现有功能可做')
cw2 = (CW - 0.5) / 2
for i, (nm, lines, data) in enumerate([('短信', ['按标签导出玩家名单，交营销侧发送'], ['发送对象中，发送后一段时间内登录的人数，', '按人群统计']),
                                      ('推播', ['礼包后台能按标签选对象时，先按标签发；', '不能时，改在推送统一后台按标签发', [('需开发，见第 {p} 页', {'size': 14, 'color': AMBER, 'bold': True})]], ['推播报表里的发送、曝光、开启数，按人群统计', '报表没有到达', '推送统一后台建成后，Android 补上到达；', 'iOS 仍没有到达，只有发送、点击'])]):
    x = X0 + i * (cw2 + 0.5)
    card(s, x, 2.3, cw2, 3.78)
    chip(s, x + 0.45, 2.6, nm, 17, h=0.5, pad=0.2)
    tb_ = T(s, x + 0.45, 3.26, cw2 - 0.9, 1.0, lines, 16, NAVY, ls=1.45)
    if nm == '推播':
        PEND.append((tb_, '新建推送统一后台，所有推送从一个入口配置和查数据'))
    LN(s, x + 0.45, 4.37, x + cw2 - 0.45, 4.37, LINE)
    T(s, x + 0.45, 4.48, cw2 - 0.9, 1.45, [[('数据', {'color': GRAY, 'bold': True, 'size': 13})]] + [[(d_, {'color': INK})] for d_ in data], 15, ls=1.4)
T(s, X0, 6.3, CW, 0.35, 'Facebook、LINE 要等推送统一后台建成后，才能按标签发', 14, GRAY)

# ── 推送统一后台（需开发）：一个入口，每种推送一页，游戏内、游戏外分开
s = page('三 推送 · 做法', '新建推送统一后台，所有推送从一个入口配置和查数据', lv=3, tier='需开发')
mx, my, mw, mh = X0, 1.98, 6.1, 4.4
R(s, mx, my, mw, mh, fill='FFFFFF', line=UI_LINE, lw=0.9, r=0.04)
R(s, mx, my, mw, 0.42, fill='F5F7FA', line=None, r=0.04, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
T(s, mx + 0.25, my, 2.3, 0.42, '推送统一后台（示意）', 14, UI_TXT, True, anchor=MID, ls=1.0)
LN(s, mx, my + 0.42, mx + mw, my + 0.42, 'E4E7ED', 0.75)
nvw = 1.4
R(s, mx, my + 0.42, nvw, mh - 0.42, fill='F7F8FA', line=None, r=0)
ny = my + 0.55
for grp, items_, sel in [('游戏内', ['弹窗', '快显'], None), ('游戏外', ['推播', '短信', 'Facebook', 'LINE'], '推播'), ('设置', ['频率上限'], None)]:
    T(s, mx + 0.18, ny, nvw - 0.3, 0.3, grp, 11.5, UI_SUB, True, anchor=MID, ls=1.0)
    ny += 0.32
    for it in items_:
        if it == sel:
            R(s, mx + 0.08, ny, nvw - 0.16, 0.32, fill='EAF1FB', line=None, r=0.04)
        T(s, mx + 0.3, ny, nvw - 0.4, 0.32, it, 12.5, (UI_BLUE if it == sel else UI_TXT), it == sel, anchor=MID, ls=1.0)
        ny += 0.34
    ny += 0.12
fx0 = mx + nvw + 0.2; fw = mw - nvw - 0.35
T(s, fx0, my + 0.52, fw, 0.32, '推播 · 新建推送', 13, UI_TXT, True, anchor=MID, ls=1.0)
lx_, fx_, iw14 = fx0, fx0 + 1.12, 2.4
rowsy = [my + 0.98 + k * 0.45 for k in range(4)]
for k, lab in enumerate(['发送对象', '点击跳转', '触发条件']):
    T(s, lx_, rowsy[k], 1.05, 0.34, lab, 12, UI_TXT, align=RT, anchor=MID, ls=1.0)
ui_input(s, fx_, rowsy[0], iw14, 0.34, '标签群组：回流', drop=True, size=12)
ui_input(s, fx_, rowsy[1], iw14, 0.34, '活动页面：回流任务', drop=True, size=12)
xx = fx_
xx += ui_radio(s, xx, rowsy[2] + 0.01, '定时', True, size=12)
ui_radio(s, xx, rowsy[2] + 0.01, '按行为', False, size=12)
# 上限在「频率上限」页按推送方式统一设定，新建表单里只读显示
R(s, lx_, rowsy[3], fx_ + iw14 - lx_, 0.34, fill='F5F7FA', line='E4E7ED', lw=0.75, r=0.05)
T(s, lx_ + 0.1, rowsy[3], fx_ + iw14 - lx_ - 0.12, 0.34, '推播每人每天上限（在频率上限页统一设定）', 12, UI_SUB, anchor=MID, ls=1.0)
ry = my + 2.92
LN(s, fx0, ry - 0.08, mx + mw - 0.15, ry - 0.08, 'E4E7ED', 0.75)
T(s, fx0, ry, 3, 0.3, '发送记录', 12.5, UI_TXT, True, anchor=MID, ls=1.0)
cws = [1.6, 0.5, 0.6, 0.6, 0.5]
for r_, row in enumerate([['推送名称', '对象', '发送量', '到达', '点击'], ['回流任务 · Android', '回流', '—', '—', '—'], ['回流任务 · iOS', '回流', '—', '不回传', '—']]):
    yy = ry + 0.34 + r_ * 0.28
    if r_ == 0:
        R(s, fx0, yy, sum(cws), 0.28, fill='F5F7FA', line=None, r=0)
    xx = fx0
    for w_, t_ in zip(cws, row):
        T(s, xx + 0.06, yy, w_ - 0.08, 0.28, t_, 11.5, (UI_SUB if r_ == 0 else UI_TXT), r_ == 0, anchor=MID, ls=1.0)
        xx += w_
# 编号：① 标在窗口标题旁（整个后台）；②③④ 放在表单对应行的右侧
dx_ = fx_ + iw14 + 0.16
DOT(s, mx + 2.42, my + 0.06, 1, d=0.3)
DOT(s, dx_, (rowsy[1] + rowsy[2] + 0.34) / 2 - 0.15, 2, d=0.3)
DOT(s, dx_, rowsy[3] + 0.02, 3, d=0.3)
DOT(s, dx_, ry, 4, d=0.3)
nx = mx + mw + 0.4; nw = XR - nx
yy = 1.96
for k, (nm, tier, desc) in enumerate([('推送统一后台', '较大开发', ['一个入口下，每种推送各一页', '游戏内（弹窗、快显）与游戏外分开列', '现有弹窗后台整页移入，规则原样生效，另加投放条件', '短信、Facebook、LINE 从营销侧接入']),
                                      ('推送跳转与触发自助', '较大开发', ['游戏外推送：运营自设文案、跳转，可定时或按行为发', '快显：运营自设文案、跳转，可按行为发，不能定时']),
                                      ('每种推送每人每天上限', '较大开发', ['在「频率上限」页设快显和四种游戏外推送', '每人每天最多几条；弹窗上限见第 {q} 页', '各种上限相加，即每人每天最多收到几条', '合计上限列为后续建议（附录第 {p} 页）']),
                                      ('快显与 Facebook、LINE 数据记录', '小改动', ['快显补记曝光、点击', 'Facebook 补记发送、到达、点击', 'LINE 补记发送、点击；到达只有按日汇总'])]):
    DOT(s, nx, yy + 0.02, k + 1, d=0.3)
    T(s, nx + 0.42, yy, nw - 0.42, 0.34, [[(nm, {'bold': True, 'color': NAVY, 'size': 15}), ('　' + tier, {'color': AMBER, 'size': 12, 'bold': True})]], 15, ls=1.1)
    tb_ = T(s, nx + 0.42, yy + 0.36, nw - 0.42, 0.225 * len(desc), desc, 13.5, INK, ls=1.2)
    if k == 2:
        PEND.append((tb_, '需开发的 11 项里，9 项在会员标签设定与推送'))
        PEND.append((tb_, '要限制每人收到的弹窗数，还需开发两项', '{q}'))
    yy += 0.36 + 0.225 * len(desc) + 0.1

# ── 游戏内推送（需开发）：快显 现在｜改后
n14 = [n for n, lv, k, ti, sb in TITLES if ti == '新建推送统一后台，所有推送从一个入口配置和查数据'][0]
s = page('三 推送 · 做法', '快显改由推送统一后台配置，按人群显示并记曝光、点击', lv=2, tier='需开发 · 含在第 %d 页 ①③④ 里，不另计' % n14)
T(s, X0, 1.95, CW, 0.35, [[('快显', {'bold': True, 'color': NAVY}), ('：游戏内的即时提示，如中奖播报、新手通行证升级提示；只有在线玩家看得到', {'color': GRAY})]], 14)
cq = [1.9, (CW - 1.9) / 2, (CW - 1.9) / 2]
hy = 2.55
R(s, X0, hy, CW, 0.42, fill=HEAD, line=None, r=0.06)
T(s, X0 + 0.25, hy, cq[0], 0.42, '项目', 13, GRAY, True, anchor=MID, ls=1.0)
T(s, X0 + cq[0], hy, cq[1], 0.42, '现在', 13, RED, True, anchor=MID, ls=1.0)
T(s, X0 + cq[0] + cq[1], hy, cq[2], 0.42, '改后', 13, BLUE, True, anchor=MID, ls=1.0)
for k, (nm, now, after, core) in enumerate([('配置', '固定在客户端程序里，后台改不了', '现有快显改在推送统一后台「快显」页设置', False),
                                            ('显示给谁', '当时在线的玩家，不能选人群', '按标签选人群，仍只对在线玩家', True),
                                            ('每人每天上限', '没有', '每人每天最多显示几条，现有快显都计入', False),
                                            ('数据', '没有后台页面可查', '记录曝光、点击', True)]):
    y = hy + 0.5 + k * 0.78
    if core:
        R(s, X0 + cq[0] + cq[1] - 0.15, y + 0.08, cq[2] + 0.15, 0.62, fill=BLUE_W, line=None, r=0.06)
    T(s, X0 + 0.25, y, cq[0] - 0.3, 0.78, nm, 16, NAVY, True, anchor=MID, ls=1.0)
    T(s, X0 + cq[0], y, cq[1] - 0.35, 0.78, now, 15, INK, anchor=MID, ls=1.3)
    T(s, X0 + cq[0] + cq[1], y, cq[2] - 0.2, 0.78, after, 15, NAVY, anchor=MID, ls=1.3)
    LN(s, X0, y + 0.78, XR, y + 0.78, LINE)

# ══════════════════════ 四 标签 ══════════════════════
divider(3, [('潜在付费、潜在流失没有标签', '按附录的定义新建这两个标签'), ('几个标签组成的群组，彼此不能取交集', '加群组交集'), ('保存前看不到人数和影响', '加人数预览、引用清单'), ('标签条件不清楚，改动没有记录', '加条件说明、变更记录')])

# ── 一·6 标签（2）
s = page('四 标签 · 现状', '现有标签都选不出潜在付费、潜在流失两类玩家', lv=2)
cw7 = (CW - 0.5) / 2
for i, (nm, d_, why) in enumerate([('潜在付费', '从未储值，且近期押注偏高', '现有付费标签只按储值金额分档'),
                                    ('潜在流失', '登录天数下降，但尚未流失', '现有「衰减」标签按储值变化，不看登录')]):
    x = X0 + i * (cw7 + 0.5)
    card(s, x, 2.05, cw7, 2.7, fill=RED_W, line=RED_L, lw=1.0)
    T(s, x + 0.45, 2.32, cw7 - 0.9, 0.5, nm, 24, NAVY, True, ls=1.0)
    T(s, x + 0.45, 2.9, cw7 - 0.9, 0.35, d_, 15, GRAY)
    T(s, x + 0.45, 3.45, cw7 - 0.9, 0.38, '没有对应标签', 18, RED, True, ls=1.0)
    T(s, x + 0.45, 3.98, cw7 - 0.9, 0.4, why, 15, INK)
T(s, X0, 4.98, CW, 0.35, '新增玩家、回流玩家已有标签；破产玩家不用另建标签，破产弹窗在玩家破产那一刻触发', 14, GRAY)
impact(s, '弹窗、推送不能只发给潜在付费或潜在流失玩家', y=5.75)

# ── 三·5 同一套人群标签（2）：中心辐射图
s = page('四 标签 · 做法', '新建潜在付费、潜在流失标签，五类人群都能单独配置', lv=2, tier='现有功能可做')
lw6 = 4.9
card(s, X0, 2.05, lw6, 4.25, fill=GREEN_W, line=GREEN_L, lw=1.0)
T(s, X0 + 0.45, 2.3, lw6 - 0.9, 0.4, '怎么建', 15, GREEN, True)
T(s, X0 + 0.45, 2.8, lw6 - 0.9, 3.3, [[('按附录的定义写标签条件', {'color': NAVY, 'bold': True})], [('用逐日的登录、押注数据计算', {'color': INK})], [('', {'size': 8})],
                                    [('潜在流失分两档', {'color': NAVY, 'bold': True})], [('近 14 天登录 2–3 天', {'color': INK})], [('近 14 天只登录 1 天', {'color': INK})],
                                    [('两档可分开选，也可合并；首版合并用', {'color': INK})]], 16, ls=1.45)
ARR(s, X0 + lw6 + 0.15, 4.0, 0.4, 0.3)
rx = X0 + lw6 + 0.75; rw = XR - rx
T(s, rx, 2.05, rw, 0.35, '建好后用在', 15, GRAY, True)
for k, (nm, d) in enumerate([('弹窗', '活动类弹窗按标签拆成四条规则（第 {p} 页）'),
                             ('推送', ['短信按标签选发送对象（第 {p} 页）', '礼包后台能选标签时，推播也一样']),
                             ('数据', ['弹窗曝光、点击按五类人群统计', '破产看破产弹窗的数据'])]):
    y = 2.55 + k * 1.27
    card(s, rx, y, rw, 1.05)
    T(s, rx + 0.35, y, 1.0, 1.05, nm, 18, NAVY, True, anchor=MID, ls=1.0)
    tb_ = T(s, rx + 1.3, y, rw - 1.55, 1.05, d, 15, INK, anchor=MID, ls=1.35)
    if k == 0: PEND.append((tb_, '活动类弹窗按人群拆成四条规则，每名玩家只符合一条'))
    if k == 1: PEND.append((tb_, '开发前，短信先按标签选发送对象'))

# ── 二·3 标签（2）
s = page('四 标签 · 做法', '标签条件保存前，就能看到人数和受影响的弹窗、推送', lv=2, tier='需开发')
T(s, X0, 1.95, CW, 0.35, '「会员标签设定」页的 5 项小改动', 15, NAVY, True)
cw_ = [1.75, (CW - 1.75) / 2, (CW - 1.75) / 2]
hy = 2.35
R(s, X0, hy, CW, 0.42, fill=HEAD, line=None, r=0.06)
T(s, X0 + 0.25, hy, cw_[0], 0.42, '改动', 13, GRAY, True, anchor=MID, ls=1.0)
T(s, X0 + cw_[0], hy, cw_[1], 0.42, '现在', 13, RED, True, anchor=MID, ls=1.0)
T(s, X0 + cw_[0] + cw_[1], hy, cw_[2], 0.42, '改后', 13, BLUE, True, anchor=MID, ls=1.0)
rows17 = [('人数预览', '保存前看不到符合条件的人数', ['保存前显示人数，', '押注金额、登录天数这类门槛可按人数调'], True),
          ('引用清单', '保存前不知道哪些弹窗、推送在用这个标签', '列出用到这个标签的弹窗和推送', True),
          ('变更记录', '标签表单没有变更记录，人数突然变化时无从对照', '记录谁在什么时候改了哪个条件', False),
          ('条件说明', '部分标签从名称看不出条件', '标签旁写明数据来源、统计天数、门槛', False),
          ('群组交集', ['标签群组之间不能取交集，', '要选交叉人群得另建一个群组'], '两个已建好的群组可直接取交集', False)]
rh = 0.66
for k, (nm, now, after, core) in enumerate(rows17):
    y = hy + 0.5 + k * rh
    if core:   # 支撑标题的两项：改后一栏浅蓝底
        R(s, X0 + cw_[0] + cw_[1] - 0.15, y + 0.06, cw_[2] + 0.15, rh - 0.12, fill=BLUE_W, line=None, r=0.06)
    T(s, X0 + 0.25, y, cw_[0] - 0.3, rh, nm, 16, NAVY, True, anchor=MID, ls=1.0)
    T(s, X0 + cw_[0], y, cw_[1] - 0.35, rh, now, 14.5, INK, anchor=MID, ls=1.3)
    T(s, X0 + cw_[0] + cw_[1], y, cw_[2] - 0.2, rh, after, 14.5, NAVY, anchor=MID, ls=1.3)
    LN(s, X0, y + rh, XR, y + rh, LINE)
T(s, X0 + cw_[0], y + rh + 0.08, CW - cw_[0], 0.56, ['标签群组：用几个标签组合出的玩家群；标签之间能用「且」「排除」，产品计划要新增的「或」也已上线',
                                                    '群组交集：产品计划把「交集」列为后续，本方案则提前到本轮'], 12.5, GRAY, ls=1.4)

# ══════════════════════ 附录（精简版：正文只留现状与做法，细节放附录，附录在 PowerPoint 里单独成节、可折叠） ══════════════════════
CH_PAGE[NCH - 1] = len(prs.slides) + 1
APP_TOC = page('附录', '目录', lv=0)
s = page('附录 · 改动清单', '需开发的 11 项里，9 项在会员标签设定与推送', lv=3)
wd = [2.6, CW - 2.6 - 1.75, 1.75]
groupsA = [(GREEN, GREEN_W, '现有功能可做 6 项', [('弹窗后台', ['活动类弹窗分四条规则', '五类人群首版内容', '实验组与对照组'], '3 项'),
                                              ('会员标签设定', ['新建两类标签'], '1 项'),
                                              ('礼包后台、营销侧', ['短信按标签发送（推播能选标签时也一样）'], '1 项'),
                                              ('弹窗与推送报表', ['发送数据按人群统计'], '1 项')]),
           (AMBER, AMBER_W, '需开发 11 项', [('会员标签设定', ['群组交集', '人数预览', '条件说明', '变更记录', '引用清单'], '小改动 5 项'),
                                         ('推送统一后台（新建）', ['推送统一后台（含数据查看）', '推送跳转与触发自助', '每种推送每人每天上限'], '较大开发 3 项'),
                                         ('快显客户端、营销侧', ['快显与 Facebook、LINE 数据记录'], '小改动 1 项'),
                                         ('弹窗后台', ['每人每天弹窗上限'], '小改动 1 项'),
                                         ('客户端、弹窗后台', ['新手弹窗接入后台'], '较大开发 1 项')])]
y = 1.98
for col, wash, gname, rws in groupsA:
    R(s, X0, y, 0.07, 0.32, fill=col, line=None, r=0)
    T(s, X0 + 0.22, y, 5, 0.32, gname, 15, col, True, anchor=MID, ls=1.0)
    y += 0.4
    for loc, items, n_ in rws:
        T(s, X0 + 0.22, y, wd[0] - 0.3, 0.4, loc, 14.5, NAVY, True, anchor=MID, ls=1.0)
        cx = X0 + wd[0]
        for it in items:
            cx += chip(s, cx, y + 0.06, it, 13, fill=wash, color=INK, h=0.28, pad=0.12, bold=False) + 0.1
        T(s, X0 + wd[0] + wd[1], y, wd[2], 0.4, n_, 14, col, True, align=RT, anchor=MID, ls=1.0)
        LN(s, X0, y + 0.38, XR, y + 0.38, LINE)
        y += 0.38
    y += 0.2
T(s, X0, 6.45, CW, 0.3, '方案外的后续建议：弹窗与推送合计的每人每天上限、五种推送合计的每人每天上限（等五种推送都在推送统一后台发送后才能做）', 12.5, GRAY)

# ── 四·1 三项验收（1）：清单式
s = page('附录 · 验收', '按三项目标逐项验收', lv=1)
crit3 = [('弹窗、推送按人群配置', ['用「玩家弹窗顺序查询」逐类抽查，', '每名玩家看到的弹窗只来自本类规则']),
         ('每人收到的数量有上限', ['后台设好上限后抽查，', '玩家当天收到的弹窗、推送不超过上限']),
         ('数据按人群可查', ['后台能按五类人群查到弹窗、快显的曝光、点击，', '以及游戏外推送的发送、到达、点击', [('（iOS 推播没有到达，LINE 到达只有按日总数）', {'size': 14, 'color': GRAY})]])]
T(s, X0 + 0.95, 1.95, 5.2, 0.3, '目标', 13, GRAY, True)
T(s, X0 + 6.3, 1.95, CW - 6.3, 0.3, '怎么验收', 13, GRAY, True)
for i, (k_, sub_) in enumerate(crit3):
    y = 2.4 + i * 1.25
    R(s, X0, y + 0.13, 0.6, 0.6, fill=GREEN_W, line=GREEN_L, lw=1.25, r=0.1)
    T(s, X0, y + 0.13, 0.6, 0.6, str(i + 1), 22, GREEN, True, align=C, anchor=MID, ls=1.0)
    T(s, X0 + 0.95, y, 5.2, 0.86, k_, 24, NAVY, True, anchor=MID, ls=1.0)
    T(s, X0 + 6.3, y - 0.07, CW - 6.3, 1.0, sub_, 16, INK, anchor=MID, ls=1.35)
    if i < 2:
        LN(s, X0, y + 1.1, XR, y + 1.1, LINE)

s = page('附录 · 验收与改动', '三项验收分别靠哪些改动', '弹窗分人群用现有功能就能做；每天上限和推送统一后台要开发', lv=3)
lw25 = 3.25; cw25 = (CW - lw25) / 3
for j, (h_, c_, w_) in enumerate([('现有功能可做', GREEN, GREEN_W), ('小改动', AMBER, AMBER_W), ('较大开发', AMBER, AMBER_W)]):
    x = X0 + lw25 + j * cw25
    R(s, x + 0.06, 2.25, cw25 - 0.12, 0.46, fill=w_, line=None, r=0.08)
    T(s, x + 0.06, 2.25, cw25 - 0.12, 0.46, h_, 15, c_, True, align=C, anchor=MID, ls=1.0)
crit = [('弹窗、推送按人群配置', ['改一类，其他类不变'], ['弹窗：每类人群一条规则', '短信：按标签导出名单'], ['两个标签群组的重叠玩家', '如回流且潜在付费'], ['五种推送按人群发送']),
        ('每人收到的数量有上限', ['弹窗与推送的每次、每天上限'], ['每次进大厅：', '各条规则的弹出数量'], ['每天：每人弹窗上限'], ['新手弹窗计入', '每次进大厅的上限', '每种推送每人每天上限']),
        ('数据按人群可查', ['弹窗：曝光、点击', '推送：发送量、到达、点击', ('（iOS 推播没有到达，', {'color': GRAY, 'size': 12.5}), ('LINE 到达只有按日总数）', {'color': GRAY, 'size': 12.5})], ['弹窗曝光、点击', '推播、短信的发送数据'], ['快显与 Facebook、LINE', '补数据记录'], ['五种推送在一处查看'])]
for i, (k_, sub_, a_, b_, c_) in enumerate(crit):
    y = 2.85 + i * 1.2; rh25 = 1.3 if i == 2 else 1.05
    T(s, X0, y, lw25 - 0.2, rh25, [[(k_, {'bold': True, 'color': NAVY, 'size': 17})]] + [[(t_, {'color': GRAY, 'size': 13})] if isinstance(t_, str) else [t_] for t_ in sub_], 17, anchor=MID, ls=1.35)
    for j, cell in enumerate([a_, b_, c_]):
        x = X0 + lw25 + j * cw25
        T(s, x + 0.25, y, cw25 - 0.4, rh25, cell, 14.5, INK, anchor=MID, ls=1.4)
    LN(s, X0, y + rh25 + 0.07, XR, y + rh25 + 0.07, LINE)

# ── 四·2 五类玩家走一遍（3）
s = page('附录 · 验收', '五类玩家走一遍，各看为本类设的内容', '示例玩家：活动均在开放期；除破产外均从未储值', lv=3)
g5 = 0.22; w5 = (CW - 4 * g5) / 5; y5, h5 = 2.3, 4.3
walk = [('新增', '注册第 5 天', '6', '4', ['活动类弹窗', '由 3 个减为 1 个'], ['活动类弹窗', '分四条规则', '新增规则只弹 1 个']),
        ('回流', '会员身份为「回流」', '4', '4', ['回流任务由轮不到', '变为第 1 个'], ['五类人群首版内容']),
        ('潜在付费', '近 14 天押注 25,000', '4', '4', ['弹窗不变：', '储值类本就先给', '首储礼包', '推送可按此人群发'], ['新建潜在付费标签']),
        ('潜在流失', '近 14 天登录 2 天', '4', '4', ['实验组：', '先看每日补给计划', '对照组：不变'], ['新建潜在流失标签', '实验组与对照组']),
        ('破产', '曾储值，游戏中破产', '1', '1', ['实验组：', '先看破产礼包', '对照组：不变'], ['五类人群首版内容', '实验组与对照组'])]
for i, (nm, ex, a_, b_, chg, how) in enumerate(walk):
    x = X0 + i * (w5 + g5); P = 0.25; iw = w5 - 2 * P
    changed = a_ != b_
    card(s, x, y5, w5, h5, fill=(BLUE_W if changed else CARD), line=(BLUE_L if changed else LINE), lw=(1.25 if changed else 0.75))
    T(s, x + P, y5 + 0.25, iw, 0.4, nm, 21, NAVY, True, ls=1.0)
    T(s, x + P, y5 + 0.7, iw, 0.3, ex, 12, GRAY, ls=1.0)
    T(s, x + P, y5 + 1.1, iw, 0.28, ('破产时看到' if nm == '破产' else ('每次进大厅最多看到' if nm == '新增' else '每次进大厅看到')), 12, GRAY, ls=1.0)
    T(s, x + P, y5 + 1.38, iw, 0.6, [[(a_, {'color': GRAY}), (' 个', {'color': GRAY, 'size': 15}), (' → ', {'color': MUTE, 'size': 17}), (b_, {'color': BLUE if changed else GRAY}), (' 个', {'color': BLUE if changed else GRAY, 'size': 15})]], 28, NAVY, True, anchor=MID, ls=1.0)
    LN(s, x + P, y5 + 2.12, x + w5 - P, y5 + 2.12, (BLUE_L if changed else LINE))
    T(s, x + P, y5 + 2.25, iw, 1.0, chg, 14, INK, ls=1.38)
    T(s, x + P, y5 + 3.3, iw, 0.9, [[('靠哪项改动', {'color': MUTE})]] + [[(h_, {})] for h_ in how], 12.5, GRAY, ls=1.3)

s = page('附录 · 人群定义', '两类新标签的门槛与依据', lv=3)
cw2 = (CW - 0.4) / 2; y0 = 1.95
for i in range(2):
    card(s, X0 + i * (cw2 + 0.4), y0, cw2, 4.45)
P = 0.4; iw = cw2 - 2 * P
for i, (nm, d) in enumerate([('潜在付费', ['从未储值', '且近 14 天押注不低于 20,000']), ('潜在流失', ['注册满 28 天、近 7 天内有登录', '且登录天数下降'])]):
    x = X0 + i * (cw2 + 0.4)
    T(s, x + P, y0 + 0.2, iw, 0.4, nm, 20, BLUE, True)
    R(s, x + P, y0 + 0.68, iw, 0.85, fill=BLUE_W, line=None, r=0.08)
    T(s, x + P + 0.22, y0 + 0.68, iw - 0.44, 0.85, d, 16, NAVY, True, anchor=MID, ls=1.35)
    LN(s, x + P, y0 + 2.95, x + P + iw, y0 + 2.95, LINE)
x = X0
T(s, x + P, y0 + 1.72, iw, 0.3, '门槛怎么定：注册 7–14 天的未储值玩家 2,092 人中', 14, GRAY)
R(s, x + P, y0 + 2.08, iw, 0.48, fill=GRAY_W, line=None, r=0)
R(s, x + P, y0 + 2.08, iw * 0.2524, 0.48, fill=BLUE, line=None, r=0)
T(s, x + P + 0.12, y0 + 2.08, 1.2, 0.48, '528 人', 14, 'FFFFFF', True, anchor=MID)
T(s, x + P + iw * 0.2524 + 0.15, y0 + 2.08, 3.5, 0.48, '押注达 20,000，占 25.24%', 14, NAVY, True, anchor=MID)
T(s, x + P, y0 + 3.1, iw, 1.1, [[('依据', {'bold': True, 'color': NAVY})], [('新玩家玩得越多，越可能首次付费（Optimove）', {})],
                               [('20,000 约为这批玩家押注的前 25%', {})]], 13.5, INK, ls=1.4)
x = X0 + cw2 + 0.4
T(s, x + P, y0 + 1.72, iw, 0.3, '按逐日登录计算', 14, GRAY)
T(s, x + P + iw / 2 - 0.6, y0 + 1.72, iw / 2 + 0.6, 0.3, '近 14 天分两档：2–3 天、1 天', 13, BLUE, True, align=RT)
half = iw / 2
R(s, x + P, y0 + 2.08, half - 0.04, 0.48, fill=GRAY_W, line=None, r=0)
R(s, x + P + half + 0.04, y0 + 2.08, half - 0.04, 0.48, fill=BLUE, line=None, r=0)
T(s, x + P, y0 + 2.08, half - 0.04, 0.48, '第 15–28 天：登录 ≥ 4 天', 13, NAVY, True, align=C, anchor=MID)
T(s, x + P + half + 0.04, y0 + 2.08, half - 0.04, 0.48, '近 14 天：登录 < 4 天', 14, 'FFFFFF', True, align=C, anchor=MID)
T(s, x + P, y0 + 2.58, 0.9, 0.16, '28 天前', 10.5, GRAY, ls=1.0)
T(s, x + P + half - 0.45, y0 + 2.58, 0.9, 0.16, '14 天前', 10.5, GRAY, align=C, ls=1.0)
T(s, x + P + iw - 0.8, y0 + 2.58, 0.8, 0.16, '今天', 10.5, GRAY, align=RT, ls=1.0)
T(s, x + P, y0 + 3.1, iw, 1.2, [[('依据', {'bold': True, 'color': NAVY})], [('近 30 天登录不足 9 天为下降（Game Developer），', {})],
                               [('折成 14 天约 4 天', {})], [('连续 7 天未登录算已流失（数数科技：3–7 天）', {})]], 13.5, INK, ls=1.4)

s = page('附录 · 人群定义', '人群人数与统计范围', lv=3)
cw2 = (CW - 0.4) / 2; y0 = 1.95; h0 = 3.4
blocks = [('近一月登录', '62,292 人', [('新增', '10,749 人（17.26%）'), ('回流', '16,564 人（26.59%）')]),
          ('8 天以上未登录的统计范围', '74,480 人', [('近一月登录', '62,292 人'), ('八月登录过、近一月未再登录', '12,188 人'),
                                         ('按最近登录：0–7 天内', '34,363 人'), ('按最近登录：8 天以上', '40,117 人（53.86%）')])]
for i, (head, big, rows_) in enumerate(blocks):
    x = X0 + i * (cw2 + 0.4); P = 0.4; iw = cw2 - 2 * P
    card(s, x, y0, cw2, h0)
    T(s, x + P, y0 + 0.25, iw, 0.3, head, 14, GRAY, True)
    T(s, x + P, y0 + 0.6, iw, 0.6, big, 30, NAVY, True, anchor=MID, ls=1.0)
    LN(s, x + P, y0 + 1.35, x + cw2 - P, y0 + 1.35, LINE)
    for k, (lab, val) in enumerate(rows_):
        yy = y0 + 1.45 + k * 0.46
        if k == 2:   # 第二种拆法（按最近登录）与上面的来源拆法分开
            LN(s, x + P, yy - 0.02, x + cw2 - P, yy - 0.02, LINE)
        T(s, x + P, yy, iw * 0.6, 0.42, lab, 15, INK, anchor=MID, ls=1.0)
        T(s, x + P + iw * 0.4, yy, iw * 0.6, 0.42, val, 15, NAVY, True, align=RT, anchor=MID, ls=1.0)
T(s, X0, 5.5, CW, 1.1, ['潜在付费、潜在流失要新建标签后才能统计人数；破产在破产时触发，没有固定人数', '五类以外的玩家沿用现有弹窗与推送', 'VIP 108 人、黑名单 15 人不进五类，单独列出'], 14, GRAY, ls=1.45)


# ── 一·2 每次 4 / 6（2）
s = page('附录 · 弹窗 · 现状', '现在每次进大厅弹 4 个，新增玩家最多 6 个', '示例：从未储值、会员等级为普卡的玩家；活动均在开放期', lv=2)
tw6, th6, g_in, g_out = 1.62, 1.35, 0.16, 0.42
tot = 6 * tw6 + 3 * g_in + 2 * g_out
x = X0 + (CW - tot) / 2
xs = []
for gi, n_ in enumerate([3, 1, 2]):
    for k in range(n_):
        xs.append(x); x += tw6 + (g_in if k < n_ - 1 else g_out)
ty = 3.55
for j, nm in enumerate(['热门资讯', '发信送奖', '卡别直升活动', '首储礼包', '新手挑战', '新手通行证']):
    tile(s, xs[j], ty, tw6, th6, nm, dashed=(j >= 4))
bracket(s, xs[0], xs[3] + tw6, 3.3)
T(s, xs[0], 2.6, xs[3] + tw6 - xs[0], 0.6, [[('4 个', {'size': 30, 'color': NAVY}), ('　所有人同一套规则', {'size': 16, 'color': GRAY, 'bold': False})]], 16, NAVY, True, align=C, anchor=MID, ls=1.0)
bracket(s, xs[4], xs[5] + tw6, 3.3, RED_L)
T(s, xs[4] - 0.3, 2.6, xs[5] + tw6 - xs[4] + 0.6, 0.6, [[('+2 个', {'size': 30, 'color': RED}), ('　仅新增玩家', {'size': 16, 'color': GRAY, 'bold': False})]], 16, NAVY, True, align=C, anchor=MID, ls=1.0)
by = ty + th6 + 0.25
for a, b, l1, l2, c_ in [(0, 2, '活动类 14 项', '按排序取前 3 个可弹的', NAVY), (3, 3, '储值类 7 项', '取第 1 个可购买的', NAVY), (4, 5, '新手弹窗', '固定在客户端，后台看不到', RED)]:
    LN(s, xs[a], by, xs[b] + tw6, by, (RED_L if c_ == RED else GRAY_L), 1.5)
    T(s, xs[a], by + 0.14, xs[b] + tw6 - xs[a] + 0.2, 0.7, [[(l1, {'bold': True, 'color': NAVY})], [(l2, {'color': c_ if c_ == RED else GRAY, 'size': 14, 'bold': c_ == RED})]], 15, ls=1.4)

# ── 三·2 新增 6→4（1）
s = page('附录 · 弹窗 · 做法', '新增玩家每次最多由 6 个减为 4 个', '活动类弹窗由 3 个减为 1 个，弹窗总数不多于其他玩家', lv=1, tier='现有功能可做')
lab_w = 1.1; tx0 = X0 + lab_w + 0.2
tw6, tg6 = 1.32, 0.1
slot_x = [tx0, tx0 + (tw6 + tg6), tx0 + 2 * (tw6 + tg6), tx0 + 3 * (tw6 + tg6) + 0.25, tx0 + 4 * (tw6 + tg6) + 0.5, tx0 + 5 * (tw6 + tg6) + 0.5]
for a, b, nm in [(0, 2, '活动类'), (3, 3, '储值类'), (4, 5, '新手弹窗（客户端）')]:
    T(s, slot_x[a], 2.3, slot_x[b] + tw6 - slot_x[a], 0.3, nm, 13, GRAY, True, align=C)
    LN(s, slot_x[a], 2.66, slot_x[b] + tw6, 2.66, LINE, 1.0)
lanes = [('现在', GRAY_W, RED, '6 个', ['热门资讯', '发信送奖', '卡别直升活动', '首储礼包', '新手挑战', '新手通行证']),
         ('改后', BLUE_W, BLUE, '4 个', ['热门资讯', None, None, '首储礼包', '新手挑战', '新手通行证'])]
for li, (lab, wash, col, tot, nm6) in enumerate(lanes):
    y = 2.85 + li * 1.9
    R(s, X0, y, CW, 1.6, fill=wash, line=None, r=0.1)
    T(s, X0 + 0.32, y, lab_w, 1.6, lab, 20, col, True, anchor=MID)
    for j in range(6):
        if nm6[j]:
            tile(s, slot_x[j], y + 0.22, tw6, 1.16, nm6[j], dashed=(j >= 4), size=13)
        else:
            tile(s, slot_x[j], y + 0.22, tw6, 1.16, '不弹', faded=True)
    T(s, slot_x[5] + tw6 + 0.15, y, XR - slot_x[5] - tw6 - 0.25, 1.6, tot, 30, col, True, align=C, anchor=MID, ls=1.0)
T(s, slot_x[4] - 0.2, 6.48, 2 * tw6 + tg6 + 0.4, 0.3, '新手弹窗接入后台前，仍由客户端弹出', 13, GRAY, align=C)

# ── 三·4 各组先看到首选弹窗（2）
s = page('附录 · 弹窗 · 做法', '四类人群先看到各自的首选弹窗', '潜在流失、破产只有实验组这样排，对照组不变', lv=2, tier='现有功能可做')
wd = [1.75, 3.0, 2.85, CW - 7.6]
y0 = 2.35; rh20 = 0.88
rows20 = [('回流', '回流任务', '活动类弹窗', '第 7 个', '第 1 个', ['为回流玩家设的活动', '改前，前 3 个取满后就轮不到']),
          ('潜在流失', '每日补给计划', '活动类弹窗', '第 8 个', '第 1 个', ['针对登录天数下降的每日活动']),
          ('破产', '破产礼包', '破产储值弹窗', '第 3 个', '第 2 个', ['排在首储礼包之后、独享礼包之前', '已储值者首储礼包不可买，', '实际第 1 个看到']),
          ('潜在付费', '首储礼包', '大厅与破产储值弹窗', '第 1 个', '第 1 个', ['从未储值者的低门槛礼包 NT$50', '现有排序已如此，沿用'])]
LN(s, X0, y0, XR, y0, LINE)
for i, (nm, item, pos, a, b, why) in enumerate(rows20):
    y = y0 + i * rh20
    same = a == b
    R(s, X0, y + 0.21, 1.45, 0.46, fill=BLUE_W, line=None, r=0.23)
    T(s, X0, y + 0.21, 1.45, 0.46, nm, 15, BLUE, True, align=C, anchor=MID, ls=1.0)
    T(s, X0 + wd[0], y, wd[1] - 0.2, rh20, [[(item, {'bold': True, 'color': NAVY, 'size': 18})], [(pos, {'color': GRAY, 'size': 13})]], 18, anchor=MID, ls=1.3)
    xm = X0 + wd[0] + wd[1]
    T(s, xm, y, wd[2] / 2 - 0.22, rh20, a, 22, GRAY, True, align=RT, anchor=MID, ls=1.0)
    ARR(s, xm + wd[2] / 2 - 0.17, y + rh20 / 2 - 0.13, 0.34, 0.26, color=(ARW if same else BLUE_L))
    T(s, xm + wd[2] / 2 + 0.22, y, wd[2] / 2 - 0.22, rh20, b, 22, (GRAY if same else BLUE), True, anchor=MID, ls=1.0)
    T(s, X0 + sum(wd[:3]) + 0.25, y, wd[3] - 0.25, rh20, why, 14, INK, anchor=MID, ls=1.35)
    LN(s, X0, y + rh20, XR, y + rh20, LINE)
T(s, X0, 6.1, CW, 0.3, '其余玩家沿用现有排序', 14, GRAY)

# ── 一·3 每天 14（1）：手机上叠满弹窗
s = page('附录 · 弹窗 · 现状', '每人每天弹窗没有总上限，活动类最多 14 个', lv=1)
T(s, X0, 1.95, 6.5, 2.1, [[('14', {}), (' 个', {'size': 36})]], 150, RED, True, anchor=MID, ls=1.0)
T(s, X0, 4.15, 7.0, 1.4, [[('活动类 14 项，每项每天 1 次', {'bold': True, 'color': NAVY, 'size': 18})],
                         [('进大厅次数多的玩家，最多可看到 14 个', {'color': INK})],
                         [('后台只能设每一项的次数和冷却时间，不能设每人每天一共弹几个', {'color': GRAY, 'size': 14})]], 16, ls=1.55)
T(s, X0, 5.75, 7.0, 0.45, [[('加上储值类与破产弹窗，', {'color': NAVY}), ('合计还会更多', {'color': RED, 'bold': True})]], 18, anchor=MID)
PEND.append((T(s, X0, 6.35, 7.0, 0.3, '对应做法见第 {p} 页：弹窗后台加每人每天弹窗上限', 13, GRAY), '要限制每人收到的弹窗数，还需开发两项'))
px, py_, pw_, ph_ = 8.95, 1.85, 2.75, 4.85
R(s, px, py_, pw_, ph_, fill=NAVY, line=None, r=0.38)
sx, sy, sw, sh = px + 0.13, py_ + 0.34, pw_ - 0.26, ph_ - 0.56
R(s, sx, sy, sw, sh, fill='EDEEF1', line=None, r=0.2)
R(s, px + pw_ / 2 - 0.32, py_ + 0.14, 0.64, 0.07, fill='46526E', line=None, r=0.035)
cwp, chp = sw - 0.36, 1.2
for k in range(14):
    xx = sx + 0.18; yy = sy + 0.22 + k * 0.205
    R(s, xx, yy, cwp, chp, fill='FFFFFF', line='E3B5AE', lw=0.75, r=0.08)
    R(s, xx + 0.12, yy + 0.07, 0.42, 0.07, fill=(RED if k == 13 else 'E8A39A'), line=None, r=0.035)
T(s, sx + 0.18, sy + 0.22 + 13 * 0.205 + 0.12, cwp, chp - 0.12, [[('活动类弹窗', {'size': 13, 'color': GRAY})], [('第 14 个', {'size': 18, 'bold': True, 'color': RED})]], 14, align=C, anchor=MID, ls=1.3)

# ── 一·5 过半玩家只能靠推送（2）
s = page('附录 · 推送 · 现状', '8 天以上未登录的人只收得到游戏外推送', lv=2)
dd = 3.1; dx, dy = X0 + 0.25, 1.95
donut(s, dx, dy, dd, (40117, 34363), (RED, 'E4E1DA'))
T(s, dx, dy + dd / 2 - 0.45, dd, 0.55, [[('40,117', {}), (' 人', {'size': 16})]], 30, RED, True, align=C, anchor=MID, ls=1.0)
T(s, dx, dy + dd / 2 + 0.12, dd, 0.3, '8 天以上未登录', 13, GRAY, align=C, ls=1.0)
T(s, X0 - 0.1, dy + dd + 0.15, 3.8, 0.85, [[('占 74,480 人的 53.86%', {'color': NAVY, 'bold': True, 'size': 14})], [('近一月登录 62,292 人，', {})], [('加上八月登录过、近一月未再登录的 12,188 人', {})]], 12, GRAY, align=C, ls=1.35)
rx = X0 + 4.3; rw = XR - rx
T(s, rx, 2.05, rw, 0.5, '不登录就看不到游戏内的弹窗、快显', 24, NAVY, True, anchor=MID, ls=1.0)
T(s, rx, 2.65, rw, 0.35, '游戏外推送（推播、短信、Facebook、LINE）不进游戏也收得到', 16, GRAY)
LN(s, rx, 3.3, XR, 3.3, LINE)
T(s, rx, 3.5, rw, 0.3, '其中新增、回流', 15, GRAY)
T(s, rx, 3.85, rw, 0.75, [[('14,502', {}), (' 人', {'size': 20})]], 44, NAVY, True, anchor=MID, ls=1.0)
T(s, rx, 4.68, rw, 0.6, ['新增 5,960 人＋回流 8,542 人', '其他 25,615 人'], 14, GRAY, ls=1.35)
impact(s, ['游戏外推送现在不能统一按人群发'], y=5.45, x=rx, w=rw)
PEND.append((T(s, rx, 6.4, rw, 0.3, '对应做法见第 {p} 页起：先按标签发短信，再建推送统一后台', 13, GRAY), '开发前，短信先按标签选发送对象'))

# ── 三·7 标签开发（2）
s = page('附录 · 标签 · 做法', '「会员标签设定」改后的样子（示意）', lv=2, tier='需开发')
mx, my, mw, mh = X0 + 0.45, 2.05, 6.6, 3.95
R(s, mx, my, mw, mh, fill='FFFFFF', line=UI_LINE, lw=0.9, r=0.04)
T(s, mx + 0.25, my + 0.05, 1.3, 0.4, '标签设定', 13, UI_SUB, anchor=MID, ls=1.0)
T(s, mx + 1.45, my + 0.05, 2.6, 0.4, '标签群组设定（示意）', 13, UI_BLUE, anchor=MID, ls=1.0)
LN(s, mx, my + 0.5, mx + mw, my + 0.5, 'E4E7ED', 0.75)
R(s, mx + 0.2, my + 0.68, mw - 0.4, 0.42, fill='F5F7FA', line=None, r=0.03)
T(s, mx + 0.38, my + 0.68, 3, 0.42, '编辑标签群组', 13, UI_TXT, True, anchor=MID, ls=1.0)
ry_ = [my + 1.35, my + 2.0, my + 2.7, my + 3.35]
T(s, mx + 0.2, ry_[0], 1.05, 0.38, '群组名称', 13, UI_TXT, align=RT, anchor=MID, ls=1.0)
ui_input(s, mx + 1.4, ry_[0], 3.0, 0.38, '回流且潜在付费')
T(s, mx + 0.2, ry_[1], 1.05, 0.38, '条件', 13, UI_TXT, align=RT, anchor=MID, ls=1.0)
ui_input(s, mx + 1.4, ry_[1], 1.35, 0.38, '回流', drop=True)
ui_input(s, mx + 2.88, ry_[1], 1.5, 0.38, '交集', drop=True, focus=True)
ui_new(s, mx + 3.42, ry_[1] + 0.08, size=10, h=0.22)
ui_input(s, mx + 4.5, ry_[1], 1.7, 0.38, '潜在付费', drop=True)
R(s, mx + 0.2, ry_[2] - 0.05, mw - 0.4, 0.48, fill='EAF1FB', line='C6D9F1', lw=0.75, r=0.04)
xx = mx + 0.35
xx += ui_new(s, xx, ry_[2] + 0.07) + 0.12
T(s, xx, ry_[2] - 0.05, 4.8, 0.48, '当前人数：— 人（已剔除机器人、测试账号）', 13, UI_TXT, anchor=MID, ls=1.0)
ui_btn(s, mx + 1.4, ry_[3], '保存', h=0.36)
ui_btn(s, mx + 2.25, ry_[3], '取消', primary=False, h=0.36)
DOT(s, X0, ry_[1] + 0.04, 1); DOT(s, X0, ry_[2] + 0.04, 2)
nx = mx + mw + 0.5; nw = XR - nx
yy = 2.2
for k, (nm, desc) in enumerate([('群组交集', ['可选另一个群组取交集', '标签之间的且、或、排除照旧']), ('人数预览', ['标签、群组保存前显示人数'])]):
    DOT(s, nx, yy + 0.03, k + 1, d=0.3)
    T(s, nx + 0.42, yy, nw - 0.42, 0.36, [[(nm, {'bold': True, 'color': NAVY, 'size': 18}), ('　小改动', {'color': AMBER, 'size': 13, 'bold': True})]], 18, ls=1.1)
    T(s, nx + 0.42, yy + 0.45, nw - 0.42, 0.7, desc, 15, INK, ls=1.4)
    yy += 1.35
LN(s, nx, yy - 0.05, XR, yy - 0.05, LINE)
T(s, nx, yy + 0.1, nw, 0.3, '「会员标签设定」页另加（小改动）', 13, GRAY, True)
T(s, nx, yy + 0.5, nw, 1.0, [[('条件说明：', {'bold': True, 'color': NAVY}), ('写明数据来源、统计天数、门槛', {})], [('变更记录：', {'bold': True, 'color': NAVY}), ('记录谁在什么时候改了哪个条件', {})], [('引用清单：', {'bold': True, 'color': NAVY}), ('列出用到这个标签的弹窗和推送', {})]], 13, INK, ls=1.4)

# ══════════════════════ 目录内容（页码在全稿生成后回填） ══════════════════════
s = TOC_SLIDE
for i, ci in enumerate(range(NCH)):
    num, name, col = CH[ci]
    y = 2.2 + i * 0.76
    if ci < NCH - 1:
        badge(s, X0, y + 0.12, 0.52, num, col, 20)
    T(s, X0 + 0.9, y, 8, 0.76, [[(name if ci < NCH - 1 else '附录', {'size': 22, 'bold': True, 'color': NAVY}), ('　第 %d 页' % CH_PAGE[ci], {'size': 14, 'color': MUTE})]], 22, anchor=MID, ls=1.0)
    LN(s, X0, y + 0.76, XR, y + 0.76, LINE)

# ══════════════════════ 附录目录（按主题分组，页码回填） ══════════════════════
s = APP_TOC
groups = [[('改动', ['改动清单']), ('验收', ['验收', '验收与改动']), ('人群定义', ['人群定义'])], [('弹窗细节', ['弹窗']), ('推送细节', ['推送']), ('标签细节', ['标签'])]]
colw = (CW - 0.8) / 2
for c, grp in enumerate(groups):
    x = X0 + c * (colw + 0.8); y = 1.95
    for gname, keys in grp:
        T(s, x, y, colw, 0.34, gname, 13, GRAY, True, anchor=MID, ls=1.0)
        y += 0.4
        for n, lv, k, title_, sub_ in TITLES:
            if k and k.startswith('附录 · ') and k.split(' · ')[1] in keys:
                tag = k.split(' · ')[2] if k.count(' · ') == 2 else ''
                runs = ([(tag + '　', {'color': RED if tag == '现状' else NAVY, 'bold': True, 'size': 13})] if tag else []) + [(title_, {'color': NAVY})]
                T(s, x, y, colw - 1.0, 0.44, [runs], 13, NAVY, anchor=MID, ls=1.0)
                T(s, x + colw - 1.0, y, 1.0, 0.44, '第 %d 页' % n, 13, MUTE, align=RT, anchor=MID, ls=1.0)
                LN(s, x, y + 0.44, x + colw, y + 0.44, LINE)
                y += 0.44
        y += 0.22

for pe_ in PEND:
    tb_, ti_ = pe_[0], pe_[1]; ph_ = pe_[2] if len(pe_) > 2 else '{p}'
    n_ = [n for n, lv, k, ti, sb in TITLES if ti == ti_][0]
    for para in tb_.text_frame.paragraphs:
        for r in para.runs:
            r.text = r.text.replace(ph_, str(n_))

# 结论页「17 项清单见第 N 页」回填
for r in CONC_TB.text_frame.paragraphs[2].runs:
    r.text = r.text.replace('?', str([n for n, lv, k, ti, sb in TITLES if k == '附录 · 改动清单'][0]))

# ══════════════════════ PowerPoint 节：每章一节，附录单独一节（缩略图栏可折叠） ══════════════════════
import uuid
starts = [(1, '封面与结论')] + [(CH_PAGE[i], (CH[i][0] + ' ' + CH[i][1]) if i < NCH - 1 else '附录') for i in range(NCH)]
ids = [sid.get('id') for sid in prs.slides._sldIdLst]
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
sec_lst = etree.Element('{%s}sectionLst' % P14, nsmap={'p14': P14})
for k, (st, nm) in enumerate(starts):
    en = starts[k + 1][0] if k + 1 < len(starts) else len(ids) + 1
    sec = etree.SubElement(sec_lst, '{%s}section' % P14, name=nm, id='{%s}' % str(uuid.uuid4()).upper())
    sl = etree.SubElement(sec, '{%s}sldIdLst' % P14)
    for j in range(st, en):
        etree.SubElement(sl, '{%s}sldId' % P14, id=ids[j - 1])
pres_el = prs.part._element
ext_lst = pres_el.find(qn('p:extLst'))
if ext_lst is None:
    ext_lst = etree.SubElement(pres_el, qn('p:extLst'))
etree.SubElement(ext_lst, qn('p:ext'), uri='{521415D9-36F7-43E2-AB2F-B90AF26B5E84}').append(sec_lst)

prs.save(OUT)
print('saved', OUT, len(prs.slides), 'slides')
for n, lv, k, t, sub in TITLES:
    print('%2d  L%d  %-22s %s%s' % (n, lv, k, t, ('  ｜' + sub) if sub else ''))
if WARN:
    print('--- warnings')
    for w in WARN:
        print(w)
