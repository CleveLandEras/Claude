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

def table(slide, data, x, y, colw, rowh, head=14, body=15):
    tbl = slide.shapes.add_table(len(data), len(colw), Inches(x), Inches(y), Inches(sum(colw)), Inches(sum(rowh))).table
    for j, w in enumerate(colw): tbl.columns[j].width = Inches(w)
    for i, h in enumerate(rowh): tbl.rows[i].height = Inches(h)
    for i, row in enumerate(data):
        for j, v in enumerate(row):
            c = tbl.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = CARD if i == 0 else WHITE
            c.margin_left = c.margin_right = Inches(0.15); c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame; tf.word_wrap = True; tf.paragraphs[0].text = ''
            r = tf.paragraphs[0].add_run(); r.text = v
            if i == 0: set_font(r, head, INK, True)
            elif j == 0: set_font(r, max(body - 1, 14), INK2, True)
            else: set_font(r, body, INK)
    return tbl

def note_landscape(slide):
    text(slide, M, 6.78, 8.5, 0.3, [P(('本页及以下客户端界面图均为横版；竖版同样要适配，版式与美术一起定', False, MUTE, 12))])

# ---------- 1 ----------
s = new_slide('总览', '建议：储值、商城类活动后台配置上线；好康改为银行入口', 1)
rows = [('问题一　好康和限时活动', '好康改为银行，活动并入一个入口；名称、储值活动放哪待讨论'),
        ('问题二　运营后台', '选工具、填规则、审核后定时上线'),
        ('问题三　公告', '分官方、活动、其他三类'),
        ('问题四　节庆', '6 个每次都开发的模块，初步改法待研发评估')]
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
         ('2', '重复配置', '同一活动要在好康、限时活动两个后台各配一次'),
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
for i, (h, rel, d) in enumerate([('A  银行加「储值活动」页签', '需求评审材料_图/01_商城_储值活动页签.jpg', '付款时就看到优惠|不开银行的玩家靠角标、Banner、弹窗看到|要和银行改版对齐页签'),
                                 ('B  活动入口加第三个页签', '需求评审材料_图/p02c_活动_储值活动页签_方案B.jpg', '豪神在活动汇总窗口单设付费页签|不付费的玩家也能看到|页签从两个变三个')]):
    xx = M + i * (cw2 + 0.4)
    text(s, xx + 0.25, cy + 0.2, cw2 - 0.5, 0.45, [P(B(h, INK, 18), (('（倾向）', True, GREEN, 18) if i == 0 else ('', False, None, 18)))])
    _, _, _, hh = image(s, rel, xx + 0.25, cy + 0.75, cw2 - 0.5, 3.0)
    text(s, xx + 0.25, cy + 0.75 + hh + 0.15, cw2 - 0.5, 0.95, [P((ln, False, INK2, 14)) for ln in d.split('|')])

# ---------- 8 ----------
s = new_slide('问题二 · 运营后台', '现在很多活动上线要排开发，同类内容反复做', 8)
text(s, M, 2.3, 5.4, 1.3, [P(('52', True, PURPLE, 72), (' / 148 张', False, MUTE, 26))], anchor=MSO_ANCHOR.BOTTOM)
text(s, M, 3.75, 5.4, 1.6, [P(('近一年储值、商城类开发需求中，按标题归为同类、又动用研发的', False, INK2, 16)), P(('', False, None, 8)), P(('逐张核过、确认只换内容却要研发的至少 29 张，另有入口下拉、科目代码等单，见下页', False, INK, 16))])
x3 = M + 6.0; w3 = W - M - x3
card(s, x3, 2.3, w3, 3.3)
text(s, x3 + 0.35, 2.3, w3 - 0.7, 3.3, [P(B('原因', INK, 18)), P(('', False, None, 8)),
    P(('每种玩法各有一套设定页，分散在活动管理的 21 个子菜单里', False, INK2, 15)), P(('', False, None, 6)),
    P(('同一种页面、同一份卡别设置，各个活动各做各的', False, INK2, 15)), P(('', False, None, 6)),
    P(('新活动类型要研发补进入口下拉（如「至尊回归」上线时，好康、限时活动、大厅弹窗都选不到它）', False, INK2, 15))], anchor=MSO_ANCHOR.MIDDLE)
text(s, M, 6.55, W - 2 * M, 0.3, [P(('数据：Jira 2025-11 至 2026-10 的长篇故事，按需求张数算，不是工时；只配置、不开单的看不到，是下限', False, MUTE, 14))])

# ---------- 9 只换内容却要研发（请主管确认） ----------
s = new_slide('问题二 · 运营后台', '请确认：这些只换了内容，却每次都要研发', 9)
text(s, M, 1.5, W - 2 * M, 0.35, [P(('美术出新图、运营写文案是正常的；重复的是研发每次重做同一种东西', False, MUTE, 14))])
table(s, [('只换了内容的事', '为什么还要研发', '统一后怎么做', '近一年'),
          ('超值礼包活动页（如马上有钱包、老子翻倍包）：版式固定，只换图、字、价格', '没有礼包页模板，版式一样也要网页开发套一遍', '礼包页模板，运营传图即上线（本期）', '8 张'),
          ('「10 月庆典」「16 周年庆」的活动大页、储值优惠页：换主题和内容', '没有专题页模板，每次庆典网页重写', '庆典专题页模板（尽量本期）', '3 张'),
          ('两次庆典的换装、导航弹窗、敲蛋外观：换素材和日期', '素材、日期写在客户端；敲蛋和导航弹窗还动了服务器', '后台换素材、自动列排期（待研发评估）', '6 张'),
          ('卡别从 6 级加到 7 级（新增至尊卡）：只多一个卡别', '卡别写在每个活动的程序里', '共用一份卡别设置，改一处（现有玩法要改成读它，研发评审时提）', '12 张'),
          ('入口下拉（如至尊回归）、科目代码', '下拉、科目代码写死在程序里', '工具建的活动自动进下拉、科目代码自动生成（本期）', '2 张以上')],
      M, 1.95, [4.1, 3.0, 3.83, 1.2], [0.42, 0.68, 0.68, 0.68, 0.68, 0.68], head=14, body=14)
card(s, M, 6.07, W - 2 * M, 0.8)
text(s, M + 0.25, 6.07, W - 2 * M - 0.5, 0.8, [P(B('请确认：', GOLD, 14), ('① 以上是否属实，有没有漏掉的（抽奖大厅两轮规则不同、集卡这类新玩法，要开发是正常的，没算进来）；② 庆典这样做是每年都有，还是今年第一次（去年 8–10 月 Jira 里没有同类单）；③ 以后每个新超值礼包还要单独做活动页吗', False, INK2, 14))], anchor=MSO_ANCHOR.MIDDLE)

# ---------- 9 ----------
# ---------- 9 ----------
# ---------- 9 ----------
s = new_slide('问题二 · 运营后台', '储值、商城类活动改为选工具、填规则、审核后定时上线', 10)
steps = ['选工具', '填规则', '审核', '定时上线']
gap = 0.6; bw = (W - 2 * M - 3 * gap) / 4; x0 = M
for i, t in enumerate(steps):
    xx = x0 + i * (bw + gap)
    c = card(s, xx, 2.0, bw, 0.85, fill=CARD)
    text(s, xx, 2.0, bw, 0.85, [P(B(t, PURPLE, 22))], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if i < 3:
        text(s, xx + bw, 2.0, gap, 0.85, [P(('→', False, MUTE, 24))], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tools = ['礼包', '累充', '满减', '折扣', '抽奖', '团购', '一元夺宝']
tx = M; ty = 3.35
text(s, M, 3.0, 6, 0.35, [P(('七个工具（前四个先做）', False, MUTE, 13))])
for t in tools:
    tw = 0.45 + 0.24 * len(t)
    card(s, tx, ty, tw, 0.55, fill=WHITE, line=LINE, lw=1)
    text(s, tx, ty, tw, 0.55, [P((t, False, INK, 16))], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    tx += tw + 0.2
text(s, M, 4.05, W - 2 * M, 0.7, [P(('上线前由另一人审核规则和成本上限；成本预警沿用现有「奖励成本预警设定」', False, MUTE, 14)), P(('满减＝单笔满额加赠，折扣＝指定面额加赠；三款竞品录屏中都没有直接减价', False, MUTE, 14))])
_, _, iw, ih = image(s, '需求评审材料_图/04_活动列表.jpg', M, 4.85, 4.6, 2.05, align='left')
text(s, M + iw + 0.3, 4.85, W - 2 * M - iw - 0.3, 1.2, [P(B('活动配置列表', INK, 15)), P(('工具、主入口、状态、储值金额、成本进度（示意数据）', False, INK2, 14))])

# ---------- 10（改为第 11 页） ----------
s = new_slide('问题二 · 运营后台', '储值、商城类活动在「活动配置」建一次，入口自动挂', 11)
text(s, M, 1.58, W - 2 * M, 0.35, [P(('现在一个活动要在 3 个一级菜单、约 8 个配置页各配一次（10/28 后台实看）', False, MUTE, 14))])
table(s, [('', '现在', '本期之后'),
          ('活动本身', '每个玩法各有一套设定页（分散在活动管理的 21 个子菜单里），新玩法要开发', '在「活动管理」新增的「活动配置」里选工具、填规则建；现有子菜单照常用，不迁移'),
          ('主入口', '大厅限时活动入口、好康活动列表各配一次；新活动类型要研发补进下拉（如至尊回归）', '系统按规则自动放进银行或活动入口（本期四个工具都是储值类）'),
          ('热门资讯、Banner、悬浮按钮、推播、弹窗', '5 处各配一次', '照旧在各页配，但下拉里直接选得到这个活动'),
          ('看效果', '没有统一的按活动储值、成本数据', '活动列表看状态、储值金额、成本进度')],
      M, 2.15, [2.6, 4.75, 4.78], [0.5, 0.95, 0.95, 0.75, 0.7])
text(s, M, 6.25, W - 2 * M, 0.35, [P(B('尽量本期做（看研发工期）：', INK2, 14), ('在活动里勾选曝光位就自动生成，不用再去各页配', False, INK2, 14))])

# ---------- 11 ----------
s = new_slide('问题三 · 公告', '公告分官方、活动、其他三类，只放按日期发的通知', 12)
hc = pair(s, '截图/最新活动与公告弹层.webp', '需求评审材料_图/p03c_公告_活动页签_带大图.jpg', 2.05, cw2, 3.9)
text(s, M, 2.05 + hc + 0.12, cw2, 0.6, [P(('改前：「最新活动」「公告讯息」两个页签，不分类', False, INK2, 15))])
text(s, M + cw2 + 0.4, 2.05 + hc + 0.12, cw2, 0.9, [P(('改后：官方、活动、其他三类', False, INK2, 15)), P(('活动类是开跑通知，保留大图，点「前往活动」进活动入口', False, MUTE, 13))])

# ---------- 12 ----------
s = new_slide('问题四 · 节庆', '节庆 6 个每次都开发的模块：初步改法，待研发评估', 13)
text(s, M, 2.9, 3.6, 1.3, [P(('11', True, PURPLE, 72), (' 张', False, MUTE, 26))], anchor=MSO_ANCHOR.BOTTOM)
text(s, M, 4.35, 3.6, 1.6, [P(('两次庆典这 6 个模块动用研发的', False, INK2, 16)), P(('其中抽奖大厅 2 张规则不同，属新做法', False, MUTE, 14))])
rows = [('每次都开发的模块', '初步思路'),
        ('活动大页（官网大广页）', '可否做成网页模板，读活动配置'),
        ('储值优惠页', '并进专题页；优惠用折扣、累充工具'),
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
