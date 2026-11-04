# 弹窗内容去留（给 Dk 审的决策稿）
# 用法：python3 _scripts/an_弹窗内容去留_PPT.py [输出.pptx]
# 版式沿用呈交版：16:9，左右边距 0.9 英寸，微软雅黑；标题 30 号，正文 15–16 号，说明 12–13 号。
# 颜色语义同呈交版：红＝现状与问题，蓝＝推荐与改后，琥珀＝要开发、要定，灰＝次要。
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.oxml.ns import qn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, '评审版_定稿改_1027', '推送系统后台集成需求', '弹窗内容去留.pptx')
FONT = 'Microsoft YaHei'

WHITE = 'FFFFFF'; NAVY = '1F2A44'; NAVY2 = '2C3A5C'; INK = '3A4254'; GRAY = '6A707C'; MUTE = '9A9FA8'
LINE = 'E2DED5'; STONE = 'F4F2EE'
RED = 'B03A2E'; RED_W = 'F8E7E3'
BLUE = '2A63A6'; BLUE_W = 'E7EEF8'
AMBER = '9A6212'; AMBER_W = 'F6ECD9'
L, C = PP_ALIGN.LEFT, PP_ALIGN.CENTER
TOP, MID = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE
X0 = 0.9; CW = 11.53

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
PAGE = [0]


def rgb(h):
    return RGBColor.from_string(h)


def font(run, size, color, bold=False):
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = rgb(color)
    rpr = run._r.get_or_add_rPr()
    rpr.set('lang', 'zh-CN'); rpr.set('altLang', 'en-US')
    ppr = run._r.getparent().get_or_add_pPr() if hasattr(run._r.getparent(), 'get_or_add_pPr') else None
    if ppr is not None:
        ppr.set('eaLnBrk', '1'); ppr.set('hangingPunct', '1')
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set('typeface', FONT)


def text(s, x, y, w, h, paras, size=15, color=INK, bold=False, align=L, anchor=TOP, gap=6, ls=1.15):
    """paras：字符串，或段落列表；段落是字符串，或 [(文字, {size,color,bold}) …]。"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = Inches(0); tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    if isinstance(paras, str):
        paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align; para.line_spacing = ls
        if i < len(paras) - 1:
            para.space_after = Pt(gap)
        runs = [(p, {})] if isinstance(p, str) else p
        for t, o in runs:
            r = para.add_run(); r.text = t
            font(r, o.get('size', size), o.get('color', color), o.get('bold', bold))
    return tb


def box(s, x, y, w, h, fill, line=None, rounded=True):
    sp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                            Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded:
        sp.adjustments[0] = 0.06
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    if line:
        sp.line.color.rgb = rgb(line); sp.line.width = Pt(1)
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def arrow(s, x1, y1, x2, y2, color=MUTE):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(2)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    ln.append(tail)


def slide(title, dark=False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(NAVY if dark else WHITE)
    PAGE[0] += 1
    if not dark:
        text(s, X0, 0.5, CW, 0.9, title, size=28, color=NAVY, bold=True, anchor=MID)
        text(s, X0, 7.0, CW, 0.3, [[('弹窗内容去留', {'color': MUTE}), (f'　{PAGE[0]}', {'color': MUTE})]],
             size=11, align=PP_ALIGN.RIGHT)
    return s


def table(s, x, y, widths, rows, size=13, head_fill=STONE, hl=None, row_h=None):
    nr, nc = len(rows), len(widths)
    shp = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(sum(widths)), Inches(0.4 * nr))
    tbl = shp.table
    tblpr = tbl._tbl.tblPr
    for k in ('firstRow', 'bandRow'):
        tblpr.set(k, '0')
    style = tblpr.find(qn('a:tableStyleId'))
    if style is not None:
        style.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'   # 无样式、细线
    for j, w in enumerate(widths):
        tbl.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        if row_h:
            tbl.rows[i].height = Inches(row_h[i])
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.1)
            cell.margin_top = cell.margin_bottom = Inches(0.06)
            cell.vertical_anchor = MID
            tcpr = cell._tc.get_or_add_tcPr()
            for side in ('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB'):
                ln = tcpr.makeelement(qn(side), {'w': '9525', 'cap': 'flat', 'cmpd': 'sng', 'algn': 'ctr'})
                sf = ln.makeelement(qn('a:solidFill'), {}); clr = sf.makeelement(qn('a:srgbClr'), {'val': LINE})
                sf.append(clr); ln.append(sf); tcpr.append(ln)
            fill = head_fill if i == 0 else (BLUE_W if hl is not None and i == hl else WHITE)
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb(fill)
            tf = cell.text_frame; tf.word_wrap = True
            runs = [(val, {})] if isinstance(val, str) else val
            p = tf.paragraphs[0]; p.line_spacing = 1.1
            for t, o in runs:
                r = p.add_run(); r.text = t
                font(r, o.get('size', size - 1 if i == 0 else size),
                     o.get('color', GRAY if i == 0 else INK), o.get('bold', i == 0 or (j == 0)))
    return shp


# ───────── 1 结论 ─────────
s = slide('', dark=True)
text(s, X0, 0.6, CW, 0.4, '推送统一后台 · 弹窗内容要不要保留 · 给 Dk 审', size=13, color='AEB6C8')
text(s, X0, 1.15, CW, 1.2, '弹窗内容保留：每个活动存一份设置，在规则里当场配', size=32, color=WHITE, bold=True)
cards = [
    ('存一份', '图、跳转、显示方式、什么时候弹、默认次数和冷却，每个活动或礼包一份；第一次在规则里配，别的规则选它时自动带出'),
    ('先不做列表', '找某个活动的设置，按活动筛出规则就行；图属于活动本身，以后活动配置能放图时，把图挪过去'),
    ('冷却要你重新定', '按数据，冷却跟着活动走；另加「同一位置两次弹出至少隔多久」，管住一会儿弹太多'),
]
cx = X0; cwid = (CW - 0.6) / 3
for i, (h, b) in enumerate(cards):
    box(s, cx, 2.75, cwid, 2.7, NAVY2)
    text(s, cx + 0.3, 2.98, cwid - 0.6, 0.5, h, size=20, color=WHITE if i < 2 else 'F2C46D', bold=True)
    text(s, cx + 0.3, 3.6, cwid - 0.6, 1.8, b, size=15, color='DDE2EC', ls=1.3)
    cx += cwid + 0.3
text(s, X0, 5.85, CW, 0.9, [
    '依据：运营同事的弹窗规则草稿、Jira 工单、Google Ad Manager 等官方文档；主管的两个问题在第 11 页回答，不当依据',
    '和 10/29 决策脑图比，推荐从「存一份并加列表」改为先不做列表；冷却由「放规则上」改为待你重新定'],
    size=13, color='AEB6C8', gap=8)

# ───────── 2 问题与标准 ─────────
s = slide('先回答三个问题，用运营要做成的五件事来判断')
text(s, X0, 1.6, 4.6, 0.4, '要回答的问题', size=16, color=GRAY, bold=True)
qs = ['① 要不要存一份：一个活动的图和弹窗设置，存一份让几条规则共用',
      '② 存一份的话，要不要单独一页：先去那一页建好，还是在规则里当场配',
      '③ 一个活动能存几份：比如给不同人群用不同的图']
y = 2.1
for q in qs:
    box(s, X0, y, 4.6, 1.0, STONE)
    text(s, X0 + 0.25, y, 4.1, 1.0, q, size=15, anchor=MID)
    y += 1.15
text(s, X0, y + 0.1, 4.6, 0.9, '主管问「新建弹窗内容有什么意义」「为什么要把弹窗规则和弹窗内容拆开」，当作要回答的问题，不当依据',
     size=12, color=GRAY)
x2 = X0 + 5.1; w2 = CW - 5.1
text(s, x2, 1.6, w2, 0.4, '运营配弹窗要做成的五件事', size=16, color=GRAY, bold=True)
goals = [
    ('新活动一上线就能加进弹窗', '活动下拉写死在代码里，上新活动要发版补，有过「急单」（RICH-19589 等）'),
    ('换图、改跳转不用找研发', '「弹窗显示的资源、跳转的 url 都需要可以通过后台配置」（RICH-24469）'),
    ('同一个活动不重复填，改时不漏', '草稿里 14 个活动和礼包在 14 条规则里一共填了 43 次'),
    ('同一个玩家不被同一个活动弹太多', '有过 A 平台弹过、换 B 平台登录又弹（RICH-22729）'),
    ('查得到某人会弹什么、为什么', '运营查某个玩家会看到哪些弹窗（RICH-19096、21302）'),
]
y = 2.1
for h, b in goals:
    text(s, x2, y, w2, 0.82, [[(h, {'bold': True, 'color': NAVY})], [(b, {'size': 12, 'color': GRAY})]], size=15, gap=2)
    y += 0.88

# ───────── 3 共用 ─────────
s = slide('同一个活动出现在好几条规则里：14 个活动和礼包共出现 43 次')
items = [('惊喜三选一', 5), ('独享礼包', 5), ('平台限量/专属礼包', 5), ('天天敲蛋礼 V2', 4), ('首储礼包', 4), ('每日礼包', 4),
         ('限时挑战', 3), ('卡别直升活动', 3), ('BOSS 战', 3), ('回流聚宝', 2), ('生涯限购', 2), ('发信送奖', 1),
         ('热门资讯', 1), ('限时加码礼包', 1)]
cd = CategoryChartData()
cd.categories = [n for n, _ in reversed(items)]
cd.add_series('出现在几条规则里', [v for _, v in reversed(items)])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(X0), Inches(1.5), Inches(6.6), Inches(4.95), cd)
ch = gf.chart
ch.has_legend = False; ch.has_title = True
ch.chart_title.text_frame.text = '每个活动或礼包出现在几条规则里'
tr = ch.chart_title.text_frame.paragraphs[0].runs[0]; font(tr, 13, GRAY, True)
pl = ch.plots[0]; pl.gap_width = 60; pl.has_data_labels = True
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.data_labels.font.size = Pt(11); pl.data_labels.font.color.rgb = rgb(INK)
ser = pl.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(BLUE)
ch.category_axis.tick_labels.font.size = Pt(11); ch.category_axis.tick_labels.font.color.rgb = rgb(INK)
ch.category_axis.format.line.color.rgb = rgb(LINE)
va = ch.value_axis; va.visible = False; va.has_major_gridlines = False; va.maximum_scale = 6
x2 = X0 + 7.0; w2 = CW - 7.0
stats = [('43 次', '14 个活动和礼包在 14 条规则里出现的次数（其中 1 条规则还没排内容）'),
         ('最多 5 条', '同一个活动出现在几条规则里；草稿只细排了计划中 12 个人群里的 7 个，所以是下限'),
         ('7 个礼包', '线上现在，大厅、破产两条储值规则共用的礼包数（10/10 截图）')]
y = 1.75
for n, d in stats:
    text(s, x2, y, w2, 0.7, n, size=34, color=BLUE, bold=True)
    text(s, x2, y + 0.72, w2, 0.8, d, size=13, color=GRAY)
    y += 1.65
text(s, X0, 6.62, CW, 0.3, '来源：运营同事的弹窗规则草稿工作表 2（线上没配置，代表运营打算怎么配）；三档卡别的规则逐格相同，合成一条的话最多 3 条',
     size=11, color=MUTE)

# ───────── 4 跟活动走还是跟人群走 ─────────
s = slide('显示方式和时机跟着活动走；次数和冷却只有 3 个礼包随人群变')
rows = [
    ['设置', '出现在 2 条以上规则的 11 个活动里', '所以'],
    ['显示方式（现有后台叫「弹窗形式」）', '11 个全都一样', [('存在活动上', {'color': BLUE, 'bold': True})]],
    ['什么时候弹', '11 个全都一样', [('存在活动上', {'color': BLUE, 'bold': True})]],
    ['每天几次、冷却', '8 个一样；惊喜三选一、独享礼包、平台限量/专属礼包对回流玩家不同：回流每天 1 次、冷却 0，其他人每天 2 次、冷却 30 分钟',
     [('活动上设默认，规则里可另设', {'color': BLUE, 'bold': True})]],
    ['图', '草稿里没有这一栏；先弹宣传图的只有天天敲蛋礼 V2、BOSS 战，其余直接打开、不弹图',
     [('存在活动上；要不要两套图问运营', {'color': AMBER, 'bold': True})]],
]
table(s, X0, 1.7, [3.2, 5.43, 2.9], rows, size=14, row_h=[0.5, 0.75, 0.75, 1.2, 1.1])
text(s, X0, 6.2, CW, 0.6, '另 3 个（发信送奖、热门资讯、限时加码礼包）只出现在 1 条规则里，没法比，不算在内。来源：运营同事的弹窗规则草稿工作表 2',
     size=12, color=MUTE)

# ───────── 5 顶尖做法 ─────────
s = slide('单独存一份的都有自己要编辑的东西；时机和冷却多设在投放那层')
rows = [
    ['产品', '单独存的那一份', '时机、冷却设在哪'],
    ['Google Ad Manager（广告投放）', '素材库：图、点击网址；投放计划里也能当场新建素材，或从库里选',
     '投放计划；挂素材时可单独改网址、起止时间'],
    ['Metaplay（游戏商城后端）', '商品：奖励、跨投放合计的每人购买上限；商品上没有图片字段', '投放（Offer Group）'],
    ['Balancy（游戏运营平台）', 'Game Offer：图标、界面、奖励', 'Game Event；一个 Event 只挂一个 Offer'],
    ['Appcharge（游戏网页商城）', '弹窗版式：背景图、标题样式，建弹窗时下拉选', '弹窗本身，一个弹窗就是一条规则'],
    ['Braze、Firebase、OneSignal 等营销弹窗', '不单独存，一条消息自带内容和投放设置', '单条消息'],
]
table(s, X0, 1.65, [3.3, 4.9, 3.33], rows, size=13, row_h=[0.45, 0.8, 0.8, 0.6, 0.7, 0.7])
box(s, X0, 5.95, CW, 0.75, AMBER_W)
text(s, X0 + 0.25, 5.95, CW - 0.5, 0.75,
     '和业界不同的一处：这些产品一条规则通常只挂一个内容；我们一条规则挂好几个活动，各项时机不同，所以时机、默认次数和冷却放在活动上',
     size=14, color=AMBER, anchor=MID)

# ───────── 6 五种做法 ─────────
s = slide('五种做法：推荐「存一份，在规则里当场配」')
rows = [
    ['做法', '好处', '代价'],
    ['A　不存，规则每一项各填', '最简单，所见即所弹', '43 处重复填；天天敲蛋礼 V2 要在 4 条规则里各传一次图，换图要逐条改'],
    ['B　单独一页，一个活动可存几份（10/28 评审版）', '集中管理；可以给不同人群配不同的图',
     '先去另一页建，再回规则里选；那版次数设在内容上，3 个礼包要各建第二份'],
    ['C　存一份，在规则里当场配（推荐）', '不用先去别处建；别的规则自动带出；改的入口只有一个',
     '找某个活动的设置要先按活动筛规则；在一条规则里改，会带动另外最多 4 条，要先提示'],
    ['D　存一份，再加一个按活动列的列表', '找得到、看得全', '多一页，两个入口改同一份数据；要不要列表，没有运营数据'],
    ['E　图放进活动、礼包自己的配置', '谁办活动谁配图；推播、快显以后能用同一张图', '要改活动配置和礼包后台，不在这次范围里'],
]
table(s, X0, 1.65, [3.6, 3.6, 4.33], rows, size=13, hl=3, row_h=[0.45, 0.8, 0.95, 0.95, 0.8, 0.8])

# ───────── 7 推荐做法怎么用 ─────────
s = slide('推荐做法：第一次在规则里配好，之后自动带出')
steps = [
    ('① 规则里加活动', '下拉从活动配置自动读取，新活动上线不用发版'),
    ('② 第一次当场配', '图、跳转、显示方式、什么时候弹、默认次数和冷却'),
    ('③ 别的规则再选它', '自动带出，不用重填'),
    ('④ 要改的时候', '先写出另有几条规则在用；某群人要不同，在这条规则里另设次数、冷却'),
]
bw = 2.55; gapx = (CW - 4 * bw) / 3; x = X0
for i, (h, b) in enumerate(steps):
    box(s, x, 2.1, bw, 2.6, BLUE_W)
    text(s, x + 0.22, 2.3, bw - 0.44, 0.55, h, size=17, color=BLUE, bold=True)
    text(s, x + 0.22, 2.95, bw - 0.44, 1.7, b, size=14, ls=1.3)
    if i < 3:
        arrow(s, x + bw + 0.05, 3.4, x + bw + gapx - 0.05, 3.4)
    x += bw + gapx
box(s, X0, 5.2, CW, 1.15, STONE)
text(s, X0 + 0.3, 5.2, CW - 0.6, 1.15, [
    [('次数和冷却按活动算：', {'bold': True, 'color': NAVY}), ('同一个活动在同一个位置、各条规则里弹过的次数合在一起，见第 9 页', {})],
    [('冷却还在规则上，还是改到活动上：', {'bold': True, 'color': AMBER}), ('要你重新定，见第 10 页', {})]],
    size=14, anchor=MID, gap=6)

# ───────── 8 列表和图的去向 ─────────
s = slide('列表先不做；图属于活动本身，以后放进活动配置')
hw = (CW - 0.4) / 2
box(s, X0, 1.7, hw, 4.6, STONE)
text(s, X0 + 0.3, 1.9, hw - 0.6, 0.5, '列表先不做', size=19, color=NAVY, bold=True)
text(s, X0 + 0.3, 2.55, hw - 0.6, 3.6, [
    '找某个活动的设置：规则列表按活动筛，打开一条就能改，几分钟内做完',
    '你定的标准：「人工几分钟能做完的事，不做成功能」',
    '要不要集中查漏、多久换一次图，没有运营数据；运营真要，再加列表'], size=15, gap=12, ls=1.3)
x2 = X0 + hw + 0.4
box(s, x2, 1.7, hw, 4.6, STONE)
text(s, x2 + 0.3, 1.9, hw - 0.6, 0.5, '图以后挪到活动配置', size=19, color=NAVY, bold=True)
text(s, x2 + 0.3, 2.55, hw - 0.6, 3.6, [
    '图是活动的东西：推播大图、快显、LINE 图卡以后都会用同一张',
    '项目里有先例：7 月快显定为随活动配置，不建独立的库（RICH-22042）',
    'Balancy 的商品也自带图标和界面',
    '这次要改活动配置和礼包后台，不在范围里，先存在推送后台'], size=15, gap=12, ls=1.3)

# ───────── 9 次数怎么算 ─────────
s = slide('次数按活动合计：同时符合两条规则，也不会多弹')
text(s, X0, 1.6, CW, 0.8, '例：新玩家同时符合「已首储」和「普卡、银卡」两条储值规则，两条里都有惊喜三选一，各每天 2 次；大厅轮流时，两条规则轮流弹',
     size=15)
hw = (CW - 0.4) / 2
box(s, X0, 2.6, hw, 1.9, RED_W)
text(s, X0 + 0.3, 2.75, hw - 0.6, 0.45, '按规则各算', size=16, color=RED, bold=True)
text(s, X0 + 0.3, 3.2, hw - 0.6, 0.8, '最多 4 次', size=36, color=RED, bold=True)
text(s, X0 + 0.3, 3.95, hw - 0.6, 0.45, '同一个礼包，一天里这个玩家可能看到 4 次', size=13, color=GRAY)
x2 = X0 + hw + 0.4
box(s, x2, 2.6, hw, 1.9, BLUE_W)
text(s, x2 + 0.3, 2.75, hw - 0.6, 0.45, '按活动合计', size=16, color=BLUE, bold=True)
text(s, x2 + 0.3, 3.2, hw - 0.6, 0.8, '最多 2 次', size=36, color=BLUE, bold=True)
text(s, x2 + 0.3, 3.95, hw - 0.6, 0.45, '两条规则弹过的次数合在一起，到了就不再弹', size=13, color=GRAY)
text(s, X0, 4.8, CW, 1.6, [
    [('规则里另设的次数怎么比：', {'bold': True, 'color': NAVY}),
     ('每条规则拿今天合计已弹的次数和自己的次数比。例：已首储规则每天 2 次、回流规则另设 1 次；今天已弹 1 次，回流规则不再弹，已首储规则还能弹 1 次', {})],
    [('先例：', {'bold': True, 'color': NAVY}),
     ('Metaplay 的商品上有跨投放合计的每人购买上限；Google Ad Manager 能给素材设跨投放计划的上限', {})],
    [('要查：', {'bold': True, 'color': AMBER}), ('两个群组实际重叠多少人，请数据同事算', {})]],
    size=14, gap=8, ls=1.25)

# ───────── 10 冷却 ─────────
s = slide('冷却要你重新定：按数据跟着活动走，另加同一位置的最小间隔')
text(s, X0, 1.55, CW, 0.45, '冷却要管两件事', size=16, color=GRAY, bold=True)
lw = 7.1
box(s, X0, 2.05, lw, 2.0, BLUE_W)
text(s, X0 + 0.3, 2.15, lw - 0.6, 1.85, [
    [('① 同一个活动别反复弹 → 跟着活动走', {'bold': True, 'color': BLUE, 'size': 16})],
    '草稿里每天 2 次的都配 30 分钟，每天 1 次的都是 0；同一条规则里两种都有。所以活动上设默认，规则里可另设'],
    size=14, gap=6, ls=1.25, anchor=MID)
box(s, X0, 4.2, lw, 2.0, BLUE_W)
text(s, X0 + 0.3, 4.3, lw - 0.6, 1.85, [
    [('② 一会儿别弹太多 → 位置设置里加「两次弹出至少隔多久」', {'bold': True, 'color': BLUE, 'size': 16})],
    '草稿总规则写了「弹出间隔 1800 秒，破产礼包、发财金除外」；原需求清单第 18 项也列了「同一位置两个弹窗的最小间隔」'],
    size=14, gap=6, ls=1.25, anchor=MID)
x2 = X0 + lw + 0.35; w2 = CW - lw - 0.35
box(s, x2, 2.05, w2, 4.15, RED_W)
text(s, x2 + 0.3, 2.2, w2 - 0.6, 3.9, [
    [('10/28 认可的「冷却放在规则上」', {'bold': True, 'color': RED, 'size': 16})],
    '管的是「这条规则弹过后隔多久」',
    '大厅轮流时，A 规则的冷却挡不住 B：同一个礼包可能 A 刚弹完，轮到 B 又弹',
    '上面两件事都没管准'], size=14, gap=8, ls=1.25)
text(s, X0, 6.35, CW, 0.45, '参照：Braze 全 App 两次触发默认至少隔 30 秒；Unity LevelPlay 按位置设两次之间的间隔；营销弹窗的再出现间隔设在单条消息上',
     size=12, color=MUTE)

# ───────── 11 回答主管 ─────────
s = slide('回答主管的两个问题')
qa = [('新建弹窗内容有什么意义？',
       '不用另外新建：在规则里第一次加某个活动时配好，存一份。存这一份是为了图能在后台换、同一个活动配一次各条规则共用、同一个活动的次数能跨规则合计'),
      ('为什么要把弹窗规则和弹窗内容拆开？',
       '规则管给谁、在哪个位置、弹哪几个、什么顺序；活动的弹窗设置管长什么样、点了去哪、默认弹几次。后者被好几条规则共用，所以存一份；但在规则这一页里就配完')]
y = 1.75
for q, a in qa:
    box(s, X0, y, CW, 1.75, STONE)
    text(s, X0 + 0.35, y + 0.2, CW - 0.7, 0.5, q, size=18, color=NAVY, bold=True)
    text(s, X0 + 0.35, y + 0.8, CW - 0.7, 0.9, a, size=15, ls=1.35)
    y += 2.0

# ───────── 12 还要查实的 ─────────
s = slide('还要查实的四件事')
rows = [['要查的事', '问谁', '影响什么'],
        ['图由谁换、多久换一次', '运营', '要不要加列表；图挪到活动配置有多急'],
        ['一个活动要不要两套图', '运营', '规则里要不要能另设图'],
        ['「已首储」和「普卡、银卡」两个群组重叠多少人', '数据同事', '次数按活动合计有多要紧'],
        ['后台配图要改客户端，开发量多大', '研发（待确认第 27 条）', '这次能不能做']]
table(s, X0, 1.75, [5.0, 2.6, 3.93], rows, size=15, row_h=[0.5, 0.85, 0.85, 0.85, 0.85])

prs.save(OUT)
print('已写出', OUT, '共', len(prs.slides), '页')
