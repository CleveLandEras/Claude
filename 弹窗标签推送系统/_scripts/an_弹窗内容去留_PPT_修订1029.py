# 弹窗内容去留（修订版，10/29 14:xx）：按思考笔记第二轮改，原版 an_弹窗内容去留_PPT.py 与 弹窗内容去留.pptx 不动
# 用法：python3 _scripts/an_弹窗内容去留_PPT_修订1029.py [输出.pptx]
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
    ROOT, '评审版_定稿改_1027', '推送系统后台集成需求', '弹窗内容去留_修订1029.pptx')
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
        text(s, X0, 7.0, CW, 0.3, [[('弹窗内容去留（修订）', {'color': MUTE}), (f'　{PAGE[0]}', {'color': MUTE})]],
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


# ───────── 1 审前须知 ─────────
s = slide('审前须知：这一版比 12:38 的原版收窄了结论，改了五处')
items = [
    ('结论收窄', '是否跳转、弹出时机、次数是活动上的默认值，规则里这三项都能另设、只在本条生效，宣传图和跳转页面不另设（10/29 已定）；还没定的只有共用多少，要等运营确认（第 2、8 页）'),
    ('依据补全', '补上线上现状：只有 3 条规则、全是默认值；补上第二个来源：10/12 方案把活动类拆成 4 条规则；写明草稿两张表之间的矛盾（第 4、5 页）'),
    ('次数合计降调', '只在大厅轮流时需要；重叠的约 1,046 人，占近一月活跃 1.7%（第 10 页）'),
    ('冷却分清三种，已定', '每一项的冷却、规则整体冷却、「弹出间隔：每人同一场景，弹完到下次再弹至少隔多久」；10/29 你已定：并进次数（活动上默认不设）、加弹出间隔、不要规则整体冷却（第 11 页）'),
    ('回答主管跟着改', '不再说「次数能跨规则合计」是存这一份的主要理由（第 12 页）'),
]
y = 1.65
for h, b in items:
    box(s, X0, y, CW, 0.88, STONE)
    text(s, X0 + 0.3, y, 2.4, 0.88, h, size=16, color=NAVY, bold=True, anchor=MID)
    text(s, X0 + 2.8, y, CW - 3.1, 0.88, b, size=14, anchor=MID, ls=1.25)
    y += 1.0
text(s, X0, 6.75, CW, 0.3, '原版 弹窗内容去留.pptx 没动；改的理由见 分析/思考笔记_弹窗设置跟着活动走_1029.md', size=11, color=MUTE)

# ───────── 2 结论 ─────────
s = slide('', dark=True)
text(s, X0, 0.6, CW, 0.4, '推送统一后台 · 弹窗内容要不要保留 · 给 Dk 审（修订）', size=13, color='AEB6C8')
text(s, X0, 1.15, CW, 1.2, '宣传图和跳转页面按活动存一份；其余是可覆盖的默认值', size=32, color=WHITE, bold=True)
cards = [
    ('定了的', '宣传图和跳转页面，每个活动或礼包一份，不在规则里另设。宣传图默认用活动或礼包自带的，要换再上传；以后活动配置能放图，就从那边读'),
    ('默认值，可在规则里另设', '是否跳转、弹出时机、次数按活动存一份，第一次在规则里配，别的规则自动带出；规则里这三项都能另设、只在本条生效（10/29 已定）；共用多少等运营确认'),
    ('冷却已定（10/29）', '设「每人同一场景，弹完到下次再弹至少隔多久」，管住「刚弹完又弹」；同一个活动的两次间隔并进次数、默认不设；不要规则整体冷却'),
]
cx = X0; cwid = (CW - 0.6) / 3
for i, (h, b) in enumerate(cards):
    box(s, cx, 2.55, cwid, 3.1, NAVY2)
    text(s, cx + 0.3, 2.78, cwid - 0.4, 0.5, h, size=20, color=WHITE if i < 2 else 'F2C46D', bold=True)
    text(s, cx + 0.3, 3.40, cwid - 0.6, 2.1, b, size=15, color='DDE2EC', ls=1.3)
    cx += cwid + 0.3
text(s, X0, 5.9, CW, 0.9, [
    '依据：Jira 工单、10/12 方案、运营同事的弹窗规则草稿、线上 10/10 截图、Google Ad Manager 等官方文档；主管的两个问题在第 12 页回答，不当依据',
    '还没验证、只能你去问的：运营的新规则计划会不会上线，研发第 24、25、27 条（第 13 页）'],
    size=13, color='AEB6C8', gap=8)

# ───────── 3 问题与标准 ─────────
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
    ('同一个活动不重复填，改时不漏', '同一批活动会出现在好几条规则里（见下一页）'),
    ('同一个玩家不被同一个活动弹太多', '有过 A 平台弹过、换 B 平台登录又弹（RICH-22729）'),
    ('查得到某人会弹什么、为什么', '运营查某个玩家会看到哪些弹窗（RICH-19096、21302）'),
]
y = 2.1
for h, b in goals:
    text(s, x2, y, w2, 0.82, [[(h, {'bold': True, 'color': NAVY})], [(b, {'size': 12, 'color': GRAY})]], size=15, gap=2)
    y += 0.88

# ───────── 4 共用 ─────────
s = slide('同一批活动会出现在好几条规则里：方案和运营草稿都是这样')
rows = [
    ['来源', '同一批活动出现在几条规则里', '可信度'],
    ['10/12 方案 17 项改动的第 1 项（已定事项第 22 条）', '活动类拆成 4 条规则，用排除让各组互斥：新增、回流、潜在流失实验组、其余；各组排的是同一批活动，只调顺序（如回流组把回流任务从第 7 调到第 1）',
     [('你确认过的方案', {'color': BLUE, 'bold': True})]],
    ['运营同事的弹窗规则草稿（工作表 2）', '14 个活动和礼包在 13 条有内容的规则里共出现 43 次，同一个最多 5 条；还没细排的人群可能再加',
     [('计划，线上没配置', {'color': AMBER, 'bold': True})]],
    ['线上现在（10/10 截图）', '只有 3 条规则；活动只在 1 条里，14 项全是 1 次、0 秒；大厅、破产两条储值规则共用 7 个礼包',
     [('现状，可能已变', {'color': GRAY, 'bold': True})]],
]
table(s, X0, 1.7, [3.4, 5.7, 2.43], rows, size=14, row_h=[0.5, 1.35, 1.0, 1.0])
box(s, X0, 5.85, CW, 0.75, AMBER_W)
text(s, X0 + 0.25, 5.85, CW - 0.5, 0.75, '所以：共用的需求来自按人群拆规则（方案和草稿都这样做），不是线上现状；运营的新规则计划会不会上线，决定共用值多少',
     size=14, color=AMBER, anchor=MID)

# ───────── 5 跟活动走还是跟人群走 ─────────
s = slide('一份计划里，弹窗形式和弹出时机跟着活动走；两份计划间会不同')
rows = [
    ['设置', '草稿工作表 2，出现在 2 条以上规则的 11 个活动', '所以'],
    ['弹窗形式（草稿的一栏；新设置改为是否跳转）', '11 个全都一样；回流聚宝表 1 是「活动广告页」、表 2 是「活动本身」，在各自的各条规则里都一致',
     [('活动上存默认，规则里可改', {'color': BLUE, 'bold': True})]],
    ['弹出时机', '11 个全都一样；回流聚宝在表 1、表 2 之间也不同', [('活动上存默认，规则里可改', {'color': BLUE, 'bold': True})]],
    ['每天几次、两次间隔', '只有两种组合：每天 2 次隔 30 分钟（24 处）、每天 1 次（19 处）；惊喜三选一、独享、平台限量对回流玩家不同',
     [('活动上存默认，规则里可改', {'color': BLUE, 'bold': True})]],
    ['宣传图', '草稿里弹窗形式为「活动广告页」的，表 2 有 2 个、表 1 有 4 个，暂按「要上传替换图」算（第 7 页传图次数按这个），确切意思待研发第 24 条',
     [('按活动存一份；要不要两套图问运营', {'color': AMBER, 'bold': True})]],
]
table(s, X0, 1.65, [2.9, 5.83, 2.8], rows, size=13, row_h=[0.5, 1.0, 0.75, 1.0, 1.0])
text(s, X0, 6.15, CW, 0.6, '另 3 个只出现在 1 条规则里，没法比。表 1、表 2 是同一位同事的两份草稿，未首储的活动类规则表 1 排了 10 项、表 2 全空，说明计划还在变',
     size=12, color=MUTE)

# ───────── 6 顶尖做法 ─────────
s = slide('单独存一份的都有要编辑的东西；弹出时机和冷却多设在投放层')
rows = [
    ['产品', '单独存的那一份', '弹出时机、冷却设在哪'],
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
     '和业界不同的一处：Metaplay 一组商品共用一个排期；我们同一条规则里各项弹出时机不同，同一个活动在各条规则里弹出时机一样，所以弹出时机放在活动上；把弹出时机、两次间隔设在共用的一份上，查到的产品都没有',
     size=14, color=AMBER, anchor=MID)

# ───────── 7 几种做法 ─────────
s = slide('几种做法比一比：推荐「存一份默认，在规则里当场配」')
rows = [
    ['做法', '好处', '代价（按草稿算；传图＝上传替换自带图；4 项＝是否跳转、弹出时机、每天几次、两次间隔）'],
    ['A　不存，规则每一项各填（可复制规则）', '最简单，所见即所弹；复制规则开发最少', '43 处 × 4 项＝172 项、传图 7 次；复制规则后约 100 项、传图 3 次；复制的不同步，换一次图改 4 处'],
    ['B　单独一页，一个活动可存几份（10/28 评审版）', '集中管理；可以给不同人群配不同的图',
     '17 份 × 4 项＝68 项、传图 2 次；要先去另一页建再回规则里选；回流那 3 个礼包要各建第二份'],
    ['C　存一份默认，在规则里当场配（推荐）', '14 个活动 × 4 项＋5 处另设 × 2 项＝66 项（这 5 处只有次数两格和默认不同，放开后仍是 10 格）、传图 2 次、换一次图改 1 处；不用先去别处建，别的规则自动带出',
     '改默认会带动用它的规则，要先提示另有几条在用；不单独建弹窗内容，少了一键下架，靠「在所有规则里暂停」开关补（第 8 页）'],
    ['D　存一份，再加一个按活动列的列表', '找得到、看得全', '填写、传图同 C；多一页，两个入口改同一份数据；要不要列表，没有运营数据'],
    ['E　图放进活动、礼包自己的配置', '谁办活动谁配图；推播、快显以后能用同一张图', '推送后台不传图，其余同 C；要改活动配置和礼包后台，不在这次范围里'],
]
table(s, X0, 1.65, [3.4, 3.6, 4.53], rows, size=13, hl=3, row_h=[0.5, 0.95, 0.95, 0.95, 0.8, 0.8])

# ───────── 8 推荐做法怎么用 ─────────
s = slide('推荐做法：第一次在规则里配好，之后自动带出')
steps = [
    ('① 规则里加活动', '下拉从活动配置自动读取，新活动上线不用发版'),
    ('② 第一次当场配', '宣传图（默认用自带的）、是否跳转和跳转页面、弹出时机、默认次数和两次间隔'),
    ('③ 别的规则再选它', '自动带出，不用重填'),
    ('④ 要改的时候', '改默认：先写出另有几条规则在用；某群人要不同：在这条规则里另设是否跳转、弹出时机或次数，只在本条生效；图和跳转页面不另设'),
]
bw = 2.55; gapx = (CW - 4 * bw) / 3; x = X0
for i, (h, b) in enumerate(steps):
    box(s, x, 2.0, bw, 2.75, BLUE_W)
    text(s, x + 0.22, 2.2, bw - 0.44, 0.55, h, size=17, color=BLUE, bold=True)
    text(s, x + 0.22, 2.85, bw - 0.44, 1.85, b, size=14, ls=1.3)
    if i < 3:
        arrow(s, x + bw + 0.05, 3.35, x + bw + gapx - 0.05, 3.35)
    x += bw + gapx
box(s, X0, 5.0, CW, 1.85, STONE)
text(s, X0 + 0.3, 5.0, CW - 0.6, 1.85, [
    [('配套：', {'bold': True, 'color': NAVY}), ('复制规则；草稿里三档卡别的规则逐格相同，像是复制出来的', {})],
    [('次数按活动合计：', {'bold': True, 'color': NAVY}), ('只在大厅轮流时需要，见第 10 页', {})],
    [('冷却：', {'bold': True, 'color': NAVY}), ('已定，并进次数（两次至少隔多久），另加「每人同一场景，弹完到下次再弹至少隔多久」，见第 11 页', {})],
    [('暂停开关：', {'bold': True, 'color': NAVY}), ('每个活动或礼包的弹窗设置里有「在所有规则里暂停」，默认关；打开前确认列出在用的规则；只停弹窗，活动照常。补上不单独建弹窗内容后少掉的「一键下架、所有规则跳过它」', {})]],
    size=14, anchor=MID, gap=5)

# ───────── 9 列表和图的去向 ─────────
s = slide('列表先不做；图属于活动本身，以后放进活动配置')
hw = (CW - 0.4) / 2
box(s, X0, 1.7, hw, 4.6, STONE)
text(s, X0 + 0.3, 1.9, hw - 0.6, 0.5, '列表先不做', size=19, color=NAVY, bold=True)
text(s, X0 + 0.3, 2.55, hw - 0.6, 3.6, [
    '找某个活动的设置：打开任一条用它的规则就能改',
    '要不要集中查漏、多久换一次图，没有运营数据；运营真要，再加列表'], size=15, gap=12, ls=1.3)
x2 = X0 + hw + 0.4
box(s, x2, 1.7, hw, 4.6, STONE)
text(s, x2 + 0.3, 1.9, hw - 0.6, 0.5, '图以后挪到活动配置', size=19, color=NAVY, bold=True)
text(s, x2 + 0.3, 2.55, hw - 0.6, 3.6, [
    '图是活动的东西：推播大图、快显、LINE 图卡以后都会用同一张',
    '项目里有先例：7 月快显定为随活动配置，不建独立的库（RICH-22042）',
    '现在先默认用活动或礼包自带的，要换再在推送后台上传',
    '这次要改活动配置和礼包后台，不在范围里'], size=15, gap=12, ls=1.3)

# ───────── 10 次数怎么算 ─────────
s = slide('次数按活动合计：只在大厅轮流时需要，影响的人不多')
text(s, X0, 1.6, CW, 0.8, '例：新玩家同时符合「已首储」和「普卡、银卡」两条储值规则，两条里都有惊喜三选一，各每天 2 次',
     size=15)
hw = (CW - 0.4) / 2
box(s, X0, 2.3, hw, 1.75, RED_W)
text(s, X0 + 0.3, 2.45, hw - 0.6, 0.45, '轮流，按规则各算', size=16, color=RED, bold=True)
text(s, X0 + 0.3, 2.9, hw - 0.6, 0.75, '最多 4 次', size=34, color=RED, bold=True)
text(s, X0 + 0.3, 3.6, hw - 0.6, 0.4, '两条规则轮流弹，各算各的', size=13, color=GRAY)
x2 = X0 + hw + 0.4
box(s, x2, 2.3, hw, 1.75, BLUE_W)
text(s, x2 + 0.3, 2.45, hw - 0.6, 0.45, '轮流，按活动合计；或只用优先级最高', size=16, color=BLUE, bold=True)
text(s, x2 + 0.3, 2.9, hw - 0.6, 0.75, '最多 2 次', size=34, color=BLUE, bold=True)
text(s, x2 + 0.3, 3.6, hw - 0.6, 0.4, '只用优先级最高时每次只命中一条，本来就不会多弹', size=13, color=GRAY)
text(s, X0, 4.35, CW, 2.2, [
    [('影响多少人：', {'bold': True, 'color': NAVY}),
     ('粗算，近一月新增玩家里已充值又是普卡或银卡的约 1,046 人，占近一月活跃玩家 1.7%（9/16 数据，口径是推断）', {})],
    [('另一种办法：', {'bold': True, 'color': NAVY}),
     ('10/12 方案用排除让各组互斥，同样不会多弹；规则多了以后，每条都要排除前面几条，按活动合计更省事', {})],
    [('规则里改过的次数怎么比：', {'bold': True, 'color': NAVY}),
     ('每条规则拿今天合计已弹的次数和自己的次数比；例：已首储规则 2 次、回流规则改成 1 次，今天已弹 1 次，回流规则不再弹，已首储规则还能弹 1 次', {})]],
    size=14, gap=8, ls=1.25)

# ───────── 11 冷却 ─────────
s = slide('冷却已定：并进次数、加弹出间隔，不要规则整体冷却')
rows = [
    ['含义', '现在有没有', '管什么', '推荐'],
    ['① 每一项自己的冷却', '线上活动类每一项都有（都是 0 秒）；草稿里每天 2 次的都配 30 分钟；策略总表写「每日 2 次，間隔 15 分鐘」',
     '同一个活动两次之间至少隔多久', [('并进次数：「每天 N 次，两次至少隔多久」，活动上默认不设、需要时再填', {'color': BLUE, 'bold': True})]],
    ['② 规则整体冷却', '线上、草稿都没有；10/28 按主管意见写进功能框架', '这条规则弹过后隔多久再弹',
     [('不要：轮流时挡不住别的规则，只用优先级最高时和 ③ 重复', {'color': RED, 'bold': True})]],
    ['③ 每人同一场景，弹完到下次再弹至少隔多久', '草稿总规则「弹出间隔 1800 秒，破产礼包、发财金除外」；原需求清单第 18 项', '一会儿别弹太多',
     [('加在场景设置里，可设例外', {'color': BLUE, 'bold': True})]],
]
table(s, X0, 1.6, [2.2, 3.9, 2.2, 3.23], rows, size=13, row_h=[0.45, 1.35, 1.0, 1.0])
box(s, X0, 5.65, CW, 1.05, AMBER_W)
text(s, X0 + 0.25, 5.65, CW - 0.5, 1.05, [
    [('10/29 你已按推荐定（已定事项第 25 条）。', {'bold': True}), ('草稿里 15 分钟和 1800 秒哪个对，还要问运营。', {})],
    '两种间隔都是 30 分钟时，弹出间隔已经管住，活动上的不起作用；只在弹出间隔更短、或这个活动不受弹出间隔（如破产礼包）时才起作用，所以活动上的默认不设（10/29 已定）'],
    size=13, color=AMBER, anchor=MID, gap=4)

# ───────── 12 回答主管 ─────────
s = slide('回答主管的两个问题')
qa = [('新建弹窗内容有什么意义？',
       '不用另外新建：在规则里第一次加某个活动时配好，系统按活动存一份。首先是为了图能在后台换；是否跳转、弹出时机、次数作为默认值带出，各条规则可以改，同一个活动不用每条规则重填'),
      ('为什么要把弹窗规则和弹窗内容拆开？',
       '规则管给谁、在哪个场景、弹哪几个、什么顺序；活动的弹窗设置管长什么样、点了去哪、默认弹几次。同一批活动会出现在好几条按人群拆开的规则里，所以存一份；但在规则这一页里就配完')]
y = 1.75
for q, a in qa:
    box(s, X0, y, CW, 1.85, STONE)
    text(s, X0 + 0.35, y + 0.2, CW - 0.7, 0.5, q, size=18, color=NAVY, bold=True)
    text(s, X0 + 0.35, y + 0.8, CW - 0.7, 1.0, a, size=15, ls=1.35)
    y += 2.1

# ───────── 13 还要查实的 ─────────
s = slide('还要查实的事，都要你去问')
rows = [['要查的事', '问谁', '影响什么'],
        ['按人群拆的新规则计划会不会上线、何时上线', '运营', '同一批活动共用多少，C 值不值'],
        ['图由谁换、多久换一次；要不要一个活动两套图', '运营', '要不要加列表；图现定不在规则里另设，要两套图再改'],
        ['草稿里「间隔 15 分钟」和「1800 秒」哪个对', '运营', '次数里默认的两次间隔'],
        ['「已首储」和「普卡、银卡」两个群组实际重叠多少', '数据同事', '次数按活动合计有多要紧'],
        ['「活动广告页」「活动本身」的确切意思；现在多条规则是不是同时弹', '研发（第 24、25 条）', '现有弹窗形式怎么对应到是否跳转；优先级还是轮流'],
        ['后台配图要改客户端，开发量多大', '研发（第 27 条）', '这次能不能做']]
table(s, X0, 1.65, [5.2, 2.4, 3.93], rows, size=14, row_h=[0.5, 0.72, 0.72, 0.72, 0.72, 0.72, 0.72])

prs.save(OUT)
print('已写出', OUT, '共', len(prs.slides), '页')
