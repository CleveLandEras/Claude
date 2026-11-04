import os, sys
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

ROOT = sys.argv[1]          # 商城 folder
OUT = sys.argv[2]
TMP = sys.argv[3]           # scratch dir for converted images
FONT = "Microsoft YaHei"

INK = RGBColor(0x1B, 0x1D, 0x21)
INK2 = RGBColor(0x4B, 0x50, 0x58)
MUTE = RGBColor(0x80, 0x85, 0x8C)
GOLD = RGBColor(0xB0, 0x82, 0x2A)
PURPLE = RGBColor(0x2A, 0x1D, 0x5C)
LAV = RGBColor(0xD9, 0xD2, 0xF2)
CARD = RGBColor(0xF5, 0xF3, 0xFA)
LINE = RGBColor(0xE1, 0xDE, 0xEA)
GREEN = RGBColor(0x2F, 0x6B, 0x52)
GREENBG = RGBColor(0xE6, 0xF1, 0xEA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
AMBER = RGBColor(0x8A, 0x5A, 0x00)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
TITLE_ONLY = prs.slide_layouts[5]
W = 13.333
M = 0.6

def img_path(rel):
    p = os.path.join(ROOT, rel)
    if p.lower().endswith('.webp'):
        q = os.path.join(TMP, os.path.basename(p)[:-5] + '.png')
        if not os.path.exists(q):
            Image.open(p).convert('RGB').save(q)
        return q
    return p

def set_font(run, size, color=INK, bold=False):
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = color
    run.font.name = FONT
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {}); rPr.append(el)
        el.set('typeface', FONT)

def text(slide, x, y, w, h, parts, size=18, color=INK2, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=0, name=None):
    """parts: list of paragraphs; each paragraph is list of (text, bold, color|None, size|None)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name: tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate(parts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if space_after: p.space_after = Pt(space_after)
        for (t, b, c, s) in para:
            r = p.add_run(); r.text = t
            set_font(r, s or size, c or color, b)
    return tb

def P(*runs):
    out = []
    for r in runs:
        if isinstance(r, str): out.append((r, False, None, None))
        else: out.append(r)
    return out

def B(t, color=INK, size=None): return (t, True, color, size)

def card(slide, x, y, w, h, fill=CARD, line=None, lw=0, name=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = 0.08
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None: s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(lw)
    s.shadow.inherit = False
    s.text_frame.text = ''
    if name: s.name = name
    return s

def image(slide, rel, x, y, w, h, align='center', name=None):
    p = img_path(rel)
    iw, ih = Image.open(p).size
    r = iw / ih
    bw, bh = w, w / r
    if bh > h: bh = h; bw = h * r
    ox = x + (w - bw) / 2 if align == 'center' else x
    oy = y
    pic = slide.shapes.add_picture(p, Inches(ox), Inches(oy), Inches(bw), Inches(bh))
    pic.name = name or os.path.basename(rel)
    ln = pic.line; ln.color.rgb = LINE; ln.width = Pt(0.75)
    return ox, oy, bw, bh

def new_slide(tag, title, n, dark=False):
    s = prs.slides.add_slide(TITLE_ONLY)
    if dark:
        bg = s.background.fill; bg.solid(); bg.fore_color.rgb = PURPLE
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(M), Inches(0.95), Inches(W - 2 * M), Inches(0.95)
    tf = t.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    r = p.add_run(); r.text = title
    set_font(r, 30, WHITE if dark else INK, True)
    text(s, M, 0.5, 8, 0.35, [P(B(tag, GOLD if not dark else RGBColor(0xE9, 0xC2, 0x6A), 13))], name='tag')
    text(s, W - M - 1, 7.0, 1, 0.3, [P((str(n), False, MUTE if not dark else LAV, 11))], align=PP_ALIGN.RIGHT, name='page number')
    return s

def pair(slide, ra, rb, y, cw, hmax):
    pa, pb = img_path(ra), img_path(rb)
    wa, ha_ = Image.open(pa).size; wb, hb_ = Image.open(pb).size
    h = min(cw * ha_ / wa, cw * hb_ / wb, hmax)
    image(slide, ra, M, y, cw, h, align='left'); image(slide, rb, M + cw + 0.4, y, cw, h, align='left')
    return h

def note_landscape(slide):
    text(slide, M, 6.78, 8.5, 0.3, [P(('本页及以下客户端界面图均为横版；竖版同样要适配，版式与美术一起定', False, MUTE, 12))])

# ---------- 1 ----------
s = new_slide('总览', '建议：储值、商城类活动后台配置上线；好康改为银行入口', 1)
rows = [('问题一　好康和限时活动', '好康改为银行，活动并入一个入口；名称、储值活动放哪待讨论'),
        ('问题二　运营后台', '选工具、填规则、审核后定时上线'),
        ('问题三　公告', '分官方、活动、其他三类'),
        ('问题四　节庆', '6 个重复模块的初步改法，待研发评估')]
y = 2.55
for a, b in rows:
    text(s, M, y, 3.15, 0.6, [P((a, False, MUTE, 18))], anchor=MSO_ANCHOR.MIDDLE)
    text(s, M + 3.25, y, W - 2 * M - 3.25, 0.6, [P((b, True, INK, 22))], anchor=MSO_ANCHOR.MIDDLE)
    ln = s.shapes.add_connector(1, Inches(M), Inches(y + 0.85), Inches(W - M), Inches(y + 0.85))
    ln.line.color.rgb = LINE; ln.line.width = Pt(0.75)
    y += 1.0

# ---------- 2 ----------
s = new_slide('问题一 · 好康和限时活动', '两个入口内容重叠，同一活动两边都挂', 2)
data = [('', '好康（左下）', '限时活动（右下）'),
        ('现在放什么', '排行、外赠、庆典、抽奖大厅等', '月月抽、新手挑战、抽奖大厅等'),
        ('版式长处', '左列表＋右大图', '图标入口；剩余天数')]
tbl = s.shapes.add_table(3, 3, Inches(M), Inches(2.4), Inches(W - 2 * M), Inches(2.6)).table
tbl.columns[0].width = Inches(2.5); tbl.columns[1].width = Inches(4.8); tbl.columns[2].width = Inches(4.83)
for i, row in enumerate(data):
    for j, v in enumerate(row):
        c = tbl.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = CARD if i == 0 else WHITE
        c.margin_left = c.margin_right = Inches(0.2); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = c.text_frame; tf.paragraphs[0].text = ''
        r = tf.paragraphs[0].add_run(); r.text = v
        if i == 0: set_font(r, 15, INK, True)
        elif j == 0: set_font(r, 16, MUTE)
        else: set_font(r, 20, INK)
text(s, M, 5.3, 12, 0.4, [P(('例：「祈福财神庙」在好康、限时活动两边都挂', False, MUTE, 12))])

# ---------- 3 ----------
s = new_slide('问题一 · 好康和限时活动', '竞品三款都有活动汇总窗口', 3)
cw3 = (W - 2 * M - 0.6) / 3
caps = ['金好运「活动公告」', '星城「活动快讯」', '豪神「最新活动」']
imgs = ['竞品参考图/竞品_活动中心结构_金好运_t0006.0.jpg', '竞品参考图/竞品_活动中心结构_星城_t0003.5.jpg', '竞品参考图/竞品_付费活动位置_豪神_t0042.0.jpg']
hmax = 0
for i in range(3):
    xx = M + i * (cw3 + 0.3)
    _, _, _, hh = image(s, imgs[i], xx, 2.4, cw3, 3.0)
    hmax = max(hmax, hh)
    text(s, xx, 2.4 + hh + 0.12, cw3, 0.35, [P((caps[i], False, INK2, 15))])
cy = 2.4 + hmax + 0.8; cw2 = (W - 2 * M - 0.3) / 2
card(s, M, cy, W - 2 * M, 0.95)
text(s, M + 0.2, cy, W - 2 * M - 0.4, 0.95, [P(B('共同做法', INK, 16)), P(('一个活动汇总窗口；分类页签；左列表、右大图（10/09 新账号录屏所见）', False, INK2, 15))], anchor=MSO_ANCHOR.MIDDLE)

# ---------- 4 ----------
s = new_slide('问题一 · 好康和限时活动', '可以合并为一个活动入口：四条依据', 4)
cards = [('1', '内容重叠', '同一活动两边都挂，例：祈福财神庙'),
         ('2', '重复配置', '一个活动要在约 8 个后台页各配一次'),
         ('3', '竞品', '三款都有活动汇总窗口'),
         ('4', '长处可保留', '好康的列表和大图、限时活动的剩余天数'),]
cw2 = (W - 2 * M - 0.4) / 2; chh = 1.95
for i, (n, h, d) in enumerate(cards):
    xx = M + (i % 2) * (cw2 + 0.4); yy = 2.15 + (i // 2) * (chh + 0.35)
    card(s, xx, yy, cw2, chh)
    text(s, xx + 0.35, yy + 0.3, 0.8, 1.0, [P((n, True, GOLD, 40))])
    text(s, xx + 1.15, yy + 0.38, cw2 - 1.5, 1.4, [P(B(h, INK, 21)), P(('', False, None, 6)), P((d, False, INK2, 17))])
# ---------- 5 ----------
s = new_slide('问题一 · 好康和限时活动', '待讨论：合并后右下入口叫什么（左下好康改为银行）', 5)
note_landscape(s)
text(s, M, 1.58, W - 2 * M, 0.35, [P(B('需求：', GOLD, 15), ('「限时活动：活动（游戏活动和平台活动的区分）」', False, INK2, 15))])
cw = (W - 2 * M - 0.4) / 2
h1 = pair(s, '截图/大厅首页.webp', '需求评审材料_图/p01b_大厅_活动入口.jpg', 2.0, cw, 3.0)
text(s, M, 2.0 + h1 + 0.12, cw, 0.35, [P(('改前：好康、限时活动', False, INK2, 15))])
text(s, M + cw + 0.4, 2.0 + h1 + 0.12, cw, 0.35, [P(('示意：左下银行，右下若改名「活动」', False, INK2, 15))])
ry = 2.0 + h1 + 0.6; rw = (W - 2 * M - 0.6) / 3
for i, (h, d) in enumerate([('保留「限时活动」', '玩家熟悉|但合并后含签到等常驻活动'),
                            ('改为「活动」', '能涵盖常驻和限时活动|竞品窗口名都含「活动」'),
                            ('左下放「银行」', '需求：好康改为金流／商城|沿用游戏内已有名称')]):
    xx = M + i * (rw + 0.3)
    card(s, xx, ry, rw, 0.95)
    hp = P(B(h, INK, 16), (('（倾向）', True, GREEN, 16) if i == 1 else ('', False, None, 16)))
    text(s, xx + 0.2, ry + 0.1, rw - 0.4, 0.85, [hp] + [P((ln, False, INK2, 14)) for ln in d.split('|')])

# ---------- 6 ----------
s = new_slide('问题一 · 好康和限时活动', '合并后的入口照竞品版式：左列表、右大图', 6)
image(s, '需求评审材料_图/p02c_活动_平台活动_竞品版式.jpg', M, 2.15, 6.9, 4.6, align='left')
x2 = M + 7.3
text(s, x2, 2.3, W - M - x2, 4.6, [
    P(B('页签', INK, 20)), P(('指定游戏的活动放「游戏活动」', False, INK2, 17)), P(('其余放「平台活动」', False, INK2, 17)), P(('', False, None, 10)),
    P(B('左侧列表', INK, 20)), P(('名称、角标、红点', False, INK2, 17)), P(('', False, None, 10)),
    P(B('右侧大图', INK, 20)), P(('主视觉、活动期间和剩余天数、立即前往', False, INK2, 17)),
], space_after=4)

# ---------- 7 ----------
s = new_slide('问题一 · 好康和限时活动', '待讨论：累充、满减等储值活动放银行还是活动入口', 7)
text(s, M, 1.58, W - 2 * M, 0.35, [P(B('需求：', GOLD, 15), ('「好康：改为金流／商城（入口载体）」', False, INK2, 15))])
cw2 = (W - 2 * M - 0.4) / 2; cy = 2.0; ch = 4.85
card(s, M, cy, cw2, ch, fill=WHITE, line=LINE, lw=1)
card(s, M + cw2 + 0.4, cy, cw2, ch, fill=WHITE, line=LINE, lw=1)
for i, (h, rel, d) in enumerate([('A  银行加「储值活动」页签', '需求评审材料_图/01_商城_储值活动页签.jpg', '付款时就看到优惠|不开银行的玩家靠角标、Banner、弹窗看到|需银行改版配合加页签'),
                                 ('B  活动入口加第三个页签', '需求评审材料_图/p02c_活动_储值活动页签_方案B.jpg', '豪神在活动汇总窗口单设付费页签|不付费的玩家也能看到|页签从两个变三个')]):
    xx = M + i * (cw2 + 0.4)
    text(s, xx + 0.25, cy + 0.2, cw2 - 0.5, 0.45, [P(B(h, INK, 18), (('（倾向）', True, GREEN, 18) if i == 0 else ('', False, None, 18)))])
    _, _, _, hh = image(s, rel, xx + 0.25, cy + 0.75, cw2 - 0.5, 3.0)
    text(s, xx + 0.25, cy + 0.75 + hh + 0.15, cw2 - 0.5, 0.95, [P((ln, False, INK2, 14)) for ln in d.split('|')])

# ---------- 8 ----------
s = new_slide('问题二 · 运营后台', '现在很多活动上线要排开发，同类内容反复做', 8)
text(s, M, 2.5, 5.2, 1.3, [P(('52', True, PURPLE, 72), (' / 148 个', False, MUTE, 26))], anchor=MSO_ANCHOR.BOTTOM)
text(s, M, 3.95, 5.2, 1.0, [P(('近一年储值、商城类（含庆典）开发需求中', False, INK2, 16)), P(('动用研发的重复开发', False, INK2, 16))])
x3 = M + 5.8; w3 = W - M - x3
card(s, x3, 2.5, w3, 1.1); card(s, x3, 3.85, w3, 1.1)
text(s, x3 + 0.3, 2.5, w3 - 0.6, 1.1, [P(B('每期重做 34 个', INK, 18)), P(('庆典 22 个、礼包 12 个', False, INK2, 15))], anchor=MSO_ANCHOR.MIDDLE)
text(s, x3 + 0.3, 3.85, w3 - 0.6, 1.1, [P(B('一个改动拆给多个活动 18 个', INK, 18)), P(('如新增至尊卡，拆成 12 个需求', False, INK2, 15))], anchor=MSO_ANCHOR.MIDDLE)
text(s, M, 5.45, W - 2 * M, 0.9, [P(B('原因：', INK, 15), ('每种玩法一套后台（活动管理下 21 个子菜单，一个玩法一个页签）；一个活动要在约 8 个后台页各配一次', False, INK2, 15)), P(('入口选项写死（如「至尊回归」上线时，好康、限时活动、大厅弹窗都选不到它）；活动页每次单独做', False, INK2, 15))])
text(s, M, 6.65, W - 2 * M, 0.3, [P(('数据：Jira 2025-11 至 2026-10，按标题归类后逐个核对子任务，为下限', False, MUTE, 12))])

# ---------- 9 ----------
s = new_slide('问题二 · 运营后台', '储值、商城类活动改为选工具、填规则、审核后定时上线', 9)
steps = ['选工具', '填规则', '审核', '定时上线']
gap = 0.6; bw = (W - 2 * M - 3 * gap) / 4; x0 = M
for i, t in enumerate(steps):
    xx = x0 + i * (bw + gap)
    c = card(s, xx, 2.9, bw, 1.0, fill=CARD)
    text(s, xx, 2.9, bw, 1.0, [P(B(t, PURPLE, 22))], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if i < 3:
        text(s, xx + bw, 2.9, gap, 1.0, [P(('→', False, MUTE, 24))], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tools = ['礼包', '累充', '满减', '折扣', '抽奖', '团购', '一元夺宝']
tx = M; ty = 4.65
text(s, M, 4.25, 5, 0.35, [P(('七个工具', False, MUTE, 13))])
for t in tools:
    tw = 0.45 + 0.24 * len(t)
    card(s, tx, ty, tw, 0.6, fill=WHITE, line=LINE, lw=1)
    text(s, tx, ty, tw, 0.6, [P((t, False, INK, 16))], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    tx += tw + 0.2
text(s, M, 5.35, W - 2 * M, 1.5, [P(('后台位置：「活动管理」下新增「活动配置」；现有 21 个子菜单照常用，不迁移', False, MUTE, 14)), P(('上线前由另一人审核规则和成本上限；成本预警沿用现有「奖励成本预警设定」', False, MUTE, 14)), P(('一个活动只有一个主入口；Banner、弹窗、推播（手机通知）、公告只引流', False, MUTE, 14)), P(('满减＝单笔满额加赠，折扣＝指定面额加赠；三款竞品录屏中都没有直接减价', False, MUTE, 14))])

# ---------- 10 ----------
s = new_slide('问题二 · 运营后台', '新增「活动配置」，用工具配置的活动在一张列表里管理', 10)
cw2 = (W - 2 * M - 0.4) / 2
_, _, iw, ih = image(s, '需求评审材料_图/04_活动列表.jpg', M, 2.0, W - 2 * M, 4.4)
text(s, M + (W - 2 * M - iw) / 2, 2.0 + ih + 0.12, iw, 0.35, [P(('活动列表：工具、主入口、状态、储值金额、成本（示意数据）', False, INK2, 15))])

# ---------- 11 ----------
s = new_slide('问题三 · 公告', '公告分官方、活动、其他三类，只放按日期发的通知', 11)
hc = pair(s, '截图/最新活动与公告弹层.webp', '需求评审材料_图/p03c_公告_活动页签_带大图.jpg', 2.05, cw2, 3.9)
text(s, M, 2.05 + hc + 0.12, cw2, 0.6, [P(('改前：「最新活动」「公告讯息」两个页签，不分类', False, INK2, 15))])
text(s, M + cw2 + 0.4, 2.05 + hc + 0.12, cw2, 0.9, [P(('改后：官方、活动、其他三类', False, INK2, 15)), P(('活动类是开跑通知，保留大图，点「前往活动」进活动入口', False, MUTE, 13))])

# ---------- 12 ----------
s = new_slide('问题四 · 节庆', '节庆 6 个重复模块：初步改法，待研发评估', 12)
text(s, M, 2.9, 3.6, 1.3, [P(('22', True, PURPLE, 72), (' 个', False, MUTE, 26))], anchor=MSO_ANCHOR.BOTTOM)
text(s, M, 4.35, 3.6, 1.6, [P(('两次庆典中需研发重做的需求', False, INK2, 16)), P(('两次庆典各做一遍同样的 6 个模块', False, MUTE, 14))])
rows = [('每次重做的模块', '初步思路'),
        ('活动大页（官网大广页）', '可否做成网页模板，读活动配置'),
        ('储值优惠页', '折扣、累充工具'),
        ('抽奖大厅', '抽奖工具，以现有抽奖大厅后台为基础'),
        ('人数活动（天天敲蛋礼）', '活动页素材、文案在后台换'),
        ('大厅换装', '大厅主题包：后台换素材'),
        ('导航弹窗（活动日历）', '版式不变；排好期的活动自动列出开启时间')]
tx = M + 4.0; tw = W - M - tx
tbl = s.shapes.add_table(len(rows), 2, Inches(tx), Inches(2.2), Inches(tw), Inches(0.58 * len(rows))).table
for rw in tbl.rows: rw.height = Inches(0.58)
tbl.columns[0].width = Inches(2.9); tbl.columns[1].width = Inches(tw - 2.9)
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        c = tbl.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = CARD if i == 0 else WHITE
        c.margin_left = c.margin_right = Inches(0.18); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = c.text_frame; tf.paragraphs[0].text = ''
        r = tf.paragraphs[0].add_run(); r.text = v
        if i == 0: set_font(r, 14, INK, True)
        elif j == 0: set_font(r, 16, INK2)
        else: set_font(r, 17, INK)
text(s, tx, 2.2 + 0.58 * len(rows) + 0.2, tw, 0.4, [P(('均为初步思路，可行性和工作量待研发评估；美术每次仍出素材', False, MUTE, 14))])
prs.save(OUT)
print('saved', OUT, len(prs.slides), 'slides')
