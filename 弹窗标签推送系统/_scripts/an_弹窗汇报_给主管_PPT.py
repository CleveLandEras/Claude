# 给主管的弹窗汇报（构图 A 填句子）：标题＋上下两带（上带系统做的、青：组句一、两句各带括线、五道关连成一整块从左往右收窄的楔形（横躺漏斗）；下带运营做的、蓝：组句二、三张卡）＋一圈箭头＋页码。不用表格对象
# 用法：
#   python3 _scripts/an_弹窗汇报_给主管_PPT.py [输出.pptx]      生成主文件（带讲稿和若问），再生成「发给主管版/弹窗功能设计汇报.pptx」（备注清空）
#   python3 _scripts/an_弹窗汇报_给主管_PPT.py --check [pptx]   查页面只放内容：没有跳转，页面没有跳转指引字样和「EP」；标题＋组句 ≤120 字；两份页面相同、发给主管版无备注
#   python3 _scripts/an_弹窗汇报_给主管_PPT.py --stats [pptx]   页数、表格对象数、整页正文字数、标题＋组句字数、讲稿字数、禁用词、10 字以上重复、一行放得下、底边
# 渲染只用：zsh _scripts/pl_pptx渲染.sh <pptx> _versions/渲染/弹窗汇报_给主管/
# 配色、字号、行距、留白照推播成品脚本 _scripts/an_推播汇报_给主管_PPT.py（运营做的蓝、系统管的青），版式照思考页同一节第 3 节；那个脚本不改。
# 以后填内容只改下面 DATA 这块数据，不动版式代码。
import os
import re
import sys
from datetime import datetime, timezone
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

# ═════════ 内容（只改这里） ═════════
# 字句出处：思考页_退回重搭.md『按构图 A 填句子（审定 34 后）』第 1 节逐字定稿；五道关画法照同文件『构图 A：五道关收窄画明显（全貌不过后）』第 2、6 节（关 2、关 3 缝里的同色箭头照其后审定 36）。
# title＝总结论；groups[0]＝上带（系统做的）：每句 claim 管几道关，gates＝[(关名, 关里的支撑)]；groups[1]＝下带（运营做的）：每句 claim＋sups；
# 字符串里的 \n 是手动断行（只断在「，、；：」后面），不算字；notes＝讲稿；asks＝若问，每条 (问, 答)，放备注末尾。
DATA = {
    'title': '弹窗功能：系统替每位玩家挑出该弹的几个，运营负责配好、核对结果',
    'groups': [
        {'head': '每次进场景该弹哪几个，系统按玩家所在人群和上限算定',
         'items': [
             {'claim': '规则按人群发；符合几条时，默认只用优先级最高的那条',
              'gates': [('按人群', 'Braze 等五家\n营销平台，\n建弹窗都有这一步'),
                        ('只用一条', '符合几条很常见：8/16–9/16 登录玩家约 44%，\n既在会员卡等级群，又在新玩家群或回流群，\n按运营同事的规则草稿推算')]},
             {'claim': '最多弹几个由三道默认上限管住，后两道能按人群另设',
              'gates': [('这条规则一次连着弹', '进大厅最多 3 个，\n其他场景 1 个'),
                        ('进大厅每人每天', '最多 8 个'),
                        ('两次弹出', '至少隔 30 分钟')]},
         ]},
        {'head': '运营每项活动、礼包只配一份，配完上架前后都能核对',
         'items': [
             {'claim': '活动或礼包自带跳转、时机、次数，\n加进规则时自动带上，也可按规则另设',
              'sups': ['草稿 13 条规则里 14 项活动、礼包出现 43 次；\n回流规则里 3 项礼包每天 1 次、其他规则 2 次，就另设']},
             {'claim': '上架前能发测试，\n按玩家预览下次弹哪几个',
              'sups': ['符合几条、又有上限和间隔时，\n单看规则推不出弹哪几个']},
             {'claim': '上架后能按规则看各步人数、\n没弹原因，也能按玩家查',
              'sups': ['各步是触发场景、用到这条规则、\n弹出、点击']},
         ]},
    ],
    'notes': '这次照您推荐的《金字塔原理》来组织。结论是：弹窗由系统替每位玩家挑出该弹的几个，运营负责配好、核对结果。'
             '一是系统做的：每次进场景弹哪几个，按人群和上限算定。'
             '规则按人群发，符合几条默认只用优先级最高的那条，8 月中到 9 月中登录玩家推算约 44% 同在会员卡等级群和新玩家或回流群；'
             '这条规则进大厅一次最多弹 3 个，每人每天最多 8 个，两次至少隔 30 分钟，都是默认值。'
             '二是运营做的：活动、礼包只配一份，加进规则时自动带上；上架前能测试、按玩家预览，上架后能看各步人数和没弹原因。'
             '您对哪点有疑问？',
    'asks': [
        ('按人群发、只用一条，和现在有什么不同？',
         '现在也能选标签，但 10 月 10 日后台截图里上架中的 3 条规则（进大厅活动类、进大厅储值类、破产储值类）都发全部玩家；'
         '9 月 24 日整理的线上配置记着，多条规则都符合时「叠加触发」，实际弹几个还看每条规则的弹出个数和各项次数。'
         '新的默认只用优先级最高的一条，优先级就是同一场景里拖动排的先后。'
         '只用一条，是因为同时符合很常见：8 月 16 日到 9 月 16 日登录的 62,292 人（已去掉机器人和测试账号）里，新增 10,749 人、回流 16,564 人，共 27,313 人，约 44%；'
         '按运营同事规则草稿第二张表的分群，他们既在会员卡等级群，又在新玩家群或回流群。这是推算，数据里没有轻回流这一类，没算进去。'
         'Braze、MoEngage 同时符合也只弹一个；Braze、MoEngage、CleverTap、Airship、OneSignal 建弹窗都有选人群这一步。'),
        ('每天 8 个、间隔 30 分钟凭什么？',
         '两样都是起始值，可改，留空就不限，也能按人群另设。8 个取自早先草图里的示例值，没有数据依据；'
         '30 分钟取自运营同事规则草稿里的总规则「弹出间隔 1800 秒，破产礼包/发财金除外」，起始值就用它。'
         '草稿策略总表里新玩家那几项写的「每日 2 次，間隔 15 分鐘」，管的是同一项两次之间，不是这道弹出间隔。'
         'MoEngage 能在工作区按天设应用内消息上限，另有全局最小间隔。'
         '现在按 10 月 10 日后台截图，每条规则每次弹 1–3 个，进大厅活动类规则里 14 项活动各每天 1 次、冷却 0 秒；跨活动的每天上限和场景间隔，截图里没见到。'),
        ('按活动配一份，比每条规则各配一遍省多少？',
         '照运营同事规则草稿的第二张表，13 条规则里活动和礼包共出现 43 次，每次要填弹出时机、弹出形式、每天次数、冷却四项（冷却就是次数里的「两次至少隔多久」）；按活动配只要 14 份。'
         '另设的是回流、轻回流两条储值规则里的 5 次：独享礼包、平台限量/专属礼包各 2 次，惊喜三选一 1 次，都是每天 1 次，其他规则里是 2 次。'
         '现在的后台也是在每条规则的排序列表里，每一项各带这几项。'
         '出现在两条以上规则的 11 项活动和礼包，弹出形式和时机在各规则里都一样，只有次数随人群不同；这一点只在草稿第二张表里成立，所以跳转、时机、次数都允许在规则里另设。'
         '改活动设置时，规则里另设过的项不跟着变，没另设的跟着变。'),
        ('按玩家预览，别家有吗？',
         '没有按玩家看下一次会弹什么的：MoEngage 只按活动汇总没弹原因，Braze 只能在分群里查某人符不符合；'
         '测试发送 Braze、Firebase、OneSignal、MoEngage、CleverTap、Airship 都有。'
         '要做，是因为一位玩家符合几条规则、规则有先后、又有每天上限和间隔，单看一条规则推不出他会弹哪几个；'
         '运营 10 月 26 日两次反馈「频率每周和每天同时存在时怎么触发」「感觉没按之前优化做」，都是配完看不清结果。'
         '预览输入会员编号，按编辑中这一版算出他下次进场景用哪条规则、会弹哪几个、没弹的原因。10 月 10 日后台截图里没见到测试入口。'),
        ('现在不是已经能查玩家弹窗顺序吗？',
         '现在的玩家弹窗顺序查询列的是排序全部项，不是实际会弹的几个，列里也没有原因。'
         '新的玩家查询输入会员编号、昵称或手机号，看各场景下次会弹哪几个、用哪条规则、轮换池轮到哪个、没弹原因和近 30 天弹过的。'
         '没弹原因分时机和次数、场景的上限和间隔、规则的个数和轮换、活动或礼包弹不了四类，共 12 种，规则数据和玩家查询用同一套；MoEngage 的没弹原因分选择、投放、显示三段。'),
    ],
}
# 只留一出现就一定不对的两类（跳转指引字样、「EP」），页面和备注里都应为 0；其余按意思由评审判（对齐卡「检查」①）
BANNED = ['回到', '→ 第', '见第', '见附录', '细节见', 'EP']
NAV = ['回到', '→ 第', '见第', '见附录', '细节见', 'EP']   # 只查页面
BODY_MAX, HEAD_MAX, SPEECH_MAX, ASK_N = 400, 120, 240, 5   # 正文（不含标题）≤400、标题＋两句组句 ≤120、讲稿 ≤240 字（约 1 分钟）、追问 5

# ═════════ 版式（填内容不用动） ═════════
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, '评审版_定稿改_1027', '推送系统后台集成需求', '弹窗汇报_给主管.pptx')
MANAGER_NAME = '弹窗功能设计汇报.pptx'   # 发给主管版的文件名（讲稿版仍是 弹窗汇报_给主管.pptx）
FILE_TITLE = '弹窗功能设计汇报'
FONT = 'Microsoft YaHei'

# 版面（英寸，思考页『按构图 A 填句子（审定 34 后）』第 3 节）：照推播成品脚本，另加关卡行和一圈箭头。字号四级 22/18/16/12，行距固定磅数 30/25/23/18
WHITE = 'FFFFFF'; NAVY = '1F2A44'; MUTE = '9A9FA8'; LINE = 'E2DED5'; SUB = '5B6272'
BLUE = '2A63A6'; BLUE_T = 'EEF3FA'; BLUE_B = 'C9D7EA'      # 运营做的
TEAL = '2C7A6B'; TEAL_T = 'EAF4F1'; TEAL_B = 'C3DDD6'      # 系统管的
SLIDE_W, SLIDE_H = 13.333, 7.5
X0, X1 = 0.5, 12.833                                         # 左右边距 0.5（同推播）；一圈箭头的竖线就在这两条线上
TITLE_Y, TITLE_H, TITLE_SIZE, TITLE_PT = 0.30, 0.44, 22, 30
RULE_Y = 0.88
LANE_TOP, LANE_BOTTOM, LANE_GAP = 1.02, 6.88, 0.26
LANE_X0, LANE_X1 = 0.75, 12.583                              # 带比推播各收 0.25，让出一圈箭头
LANE_BAR = 0.08
CX0, CX1 = 1.00, 12.383                                      # 带内文字和关、卡的左右
HEAD_SIZE, HEAD_PT = 18, 25
HEAD_PAD, HEAD_GAP, LANE_PAD_B = 0.14, 0.14, 0.18
CLAIM_SIZE, CLAIM_PT = 16, 23
SUP_SIZE, SUP_PT = 12, 18
GAP_CS = 0.12
# 上带：两句一排，句下一条括线（横线两端带短竖），括线下五道关连成一整块从左往右收窄的楔形（横躺漏斗），每道关是楔形上的一段梯形
BRACKET_DY, BRACKET_TICK, GATES_DY = 0.07, 0.07, 0.10        # 句底到括线、括线短竖长、括线到关顶
FUNNEL_H0, FUNNEL_H1 = 1.829, 0.62                           # 楔形左口、右口高（左口＝原关 1 高，版面其余不动）
GATE_W = [1.75, 3.86, 2.05, 1.73, 1.613]                      # 宽按字分（关 2 最宽），高只跟着楔形走
GATE_GAPS = [0.06, 0.20, 0.06, 0.06]                          # 段与段之间的细缝；关 2、关 3 之间放宽，对上两段括线的分组
GATE_PAD_X, GATE_PAD_Y = 0.08, 0.06
FUNNEL_FILL = 'C2DFD5'; FUNNEL_LEAD = '1F5F53'; FUNNEL_BODY = '4A5161'   # 楔形底色、关名、楔形上的支撑字
GAP_ARROW_M, GAP_ARROW_D = 0.03, 0.08                         # 关 2、关 3 缝里的同色 V 形箭头：离两边关各 0.03、尖深 0.08；上下沿落在楔形斜边上（审定 36）
# 下带：三张卡，卡间放箭头
CARD_W = [4.533, 2.87, 3.30]
CARD_GAP = 0.34
CARD_PAD_X, CARD_PAD_MIN = 0.16, 0.20
CARROW_W, CARROW_H = 0.24, 0.24
LOOP_PT = 2.5
PAGENO = (12.59, 7.0, 0.23, 0.25, 10, 14)
BOTTOM_MAX = 6.88                             # 页码以外所有形状底边上限（下带底）
CHROME = {'标题', '页脚_页码'}                 # 不算正文的形状
N_SHAPES, N_TEXT = 45, 17                     # 版式核对：形状共几个（第 6 节 44 个，加关 2、关 3 缝里的箭头 1 个）、带字的几个


def rgb(h):
    return RGBColor.from_string(h)


def inch(pt):
    return pt / 72


def nlines(t):
    return t.count('\n') + 1


def font(run, size, color, bold=False):
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = rgb(color)
    rpr = run._r.get_or_add_rPr()
    rpr.set('lang', 'zh-CN'); rpr.set('altLang', 'en-US')
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set('typeface', FONT)


def textbox(s, name, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    return tb


def add_para(tf, first, t, size, color, pitch, bold=False, align=PP_ALIGN.LEFT):
    """一段：行距固定 pitch 磅；t 里的 \\n 是手动断行。"""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align; p.line_spacing = Pt(pitch)
    for k, part in enumerate(t.split('\n')):
        if k:
            p.add_line_break()
        r = p.add_run(); r.text = part; font(r, size, color, bold)


def text(s, name, x, y, w, h, t, size, color, pitch, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = textbox(s, name, x, y, w, h, anchor)
    add_para(tb.text_frame, True, t, size, color, pitch, bold, align)
    return tb


def shape(s, name, kind, x, y, w, h, fill, line=None, lw=0.75):
    sp = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.name = name
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    if line:
        sp.line.color.rgb = rgb(line); sp.line.width = Pt(lw)
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sp.adjustments[0] = 0.06
    return sp


def seg(s, name, x1, y1, x2, y2, color, width_pt, head=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb = rgb(color); c.line.width = Pt(width_pt)
    if head:
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    c._element.spPr.append(c._element.spPr.makeelement(qn('a:effectLst'), {}))   # 去掉主题带的阴影，细线才是细线
    return c


def path(s, name, pts, color, width_pt):
    for i in range(len(pts) - 1):
        seg(s, '%s_%d' % (name, i + 1), pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, width_pt,
            head=(i == len(pts) - 2))


def poly(s, name, pts, fill):
    """闭合的自由形状：pts＝[(x, y)] 英寸；点用 EMU 整数给、scale=1.0（不然点会被取整成 1 英寸一格）。实底、不描边、无阴影。"""
    E = lambda v: int(round(v * 914400))
    fb = s.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
    fb.add_line_segments([(E(x), E(y)) for x, y in pts[1:]], close=True)
    sp = fb.convert_to_shape()
    sp.name = name
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def funnel_h(x):
    """楔形在 x 处的高：左口 FUNNEL_H0（x＝CX0）线性收到右口 FUNNEL_H1（x＝CX1）。"""
    return FUNNEL_H0 - (FUNNEL_H0 - FUNNEL_H1) * (x - CX0) / (CX1 - CX0)


def set_notes(s, d):
    """备注：先放讲稿，空一行，再放「若问：…」（只在他问到时说）。"""
    parts = [d['notes']]
    for q, a in d.get('asks', []):
        parts += ['', '若问：%s\n答：%s' % (q, a)]
    s.notes_slide.notes_text_frame.text = '\n'.join(parts)


def set_props(pr):
    """文件属性：作者、上次修改者「产品部」，标题「弹窗功能设计汇报」，创建修改时间为当前（UTC），描述、关键词清空。"""
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    cp = pr.core_properties
    cp.author = '产品部'; cp.last_modified_by = '产品部'; cp.title = FILE_TITLE
    cp.created = now; cp.modified = now
    cp.comments = ''; cp.keywords = ''; cp.subject = ''; cp.category = ''


def print_props(path):
    cp = Presentation(path).core_properties
    print('  文件属性 %s：作者=%s｜上次修改者=%s｜标题=%s｜创建=%s｜修改=%s｜描述=%r｜关键词=%r' % (
        os.path.relpath(path, ROOT), cp.author, cp.last_modified_by, cp.title, cp.created, cp.modified,
        cp.comments, cp.keywords))


def est_w(t, size):
    """估算一行文字宽（英寸）：全角 1 字宽，数字字母约 0.55，空格约 0.3。"""
    em = 0.0
    for ch in t:
        em += 0.3 if ch == ' ' else (0.55 if ord(ch) < 0x2E80 else 1.0)
    return em * size / 72


def gate_text_h(lead, body):
    return inch(SUP_PT) * (1 + nlines(body))


def card_text_h(pt):
    return nlines(pt['claim']) * inch(CLAIM_PT) + GAP_CS + sum(nlines(t) * inch(SUP_PT) for t in pt['sups'])


# ───────── 页面：标题、标题线 → 上带（系统做的，青）→ 下带（运营做的，蓝）→ 一圈箭头 → 页码 ─────────
def page(s, D):
    claims = D['groups'][0]['items']   # 上带：每句管几道关
    points = D['groups'][1]['items']   # 下带：三张卡
    text(s, '标题', X0, TITLE_Y, X1 - X0, TITLE_H, D['title'], TITLE_SIZE, NAVY, TITLE_PT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    seg(s, '标题线', X0, RULE_Y, X1, RULE_Y, LINE, 0.75)

    # ── 先算高：上带＝顶空＋组句＋空＋句一行＋括线＋关区（楔形左口高，固定）＋底空；下带＝顶空＋组句＋空＋卡＋底空 ──
    claim_h = inch(CLAIM_PT)
    card_need = max(card_text_h(pt) for pt in points) + 2 * CARD_PAD_MIN
    fixed_top = HEAD_PAD + inch(HEAD_PT) + HEAD_GAP + claim_h + BRACKET_DY + GATES_DY + LANE_PAD_B
    fixed_bot = HEAD_PAD + inch(HEAD_PT) + HEAD_GAP + LANE_PAD_B
    card_h = (LANE_BOTTOM - LANE_TOP - LANE_GAP) - fixed_top - fixed_bot - FUNNEL_H0
    assert card_h >= card_need - 1e-6, '下带卡放不下：差 %.3f 英寸' % (card_need - card_h)

    # ── 上带：系统做的（青） ──
    y0 = LANE_TOP
    top_h = fixed_top + FUNNEL_H0
    shape(s, '带_1', MSO_SHAPE.RECTANGLE, LANE_X0, y0, LANE_X1 - LANE_X0, top_h, TEAL_T)
    shape(s, '色条_1', MSO_SHAPE.RECTANGLE, LANE_X0, y0, LANE_BAR, top_h, TEAL)
    hy = y0 + HEAD_PAD
    text(s, '组句_1', CX0, hy, CX1 - CX0, inch(HEAD_PT), D['groups'][0]['head'], HEAD_SIZE, NAVY, HEAD_PT, bold=True)
    cy = hy + inch(HEAD_PT) + HEAD_GAP
    gx = [CX0]
    for w, g in zip(GATE_W[:-1], GATE_GAPS):
        gx.append(gx[-1] + w + g)
    assert abs(gx[-1] + GATE_W[-1] - CX1) < 0.01, '五段加缝要正好铺满带内宽：%.3f' % (gx[-1] + GATE_W[-1])
    by = cy + claim_h + BRACKET_DY
    gy_top = by + GATES_DY
    mid = gy_top + FUNNEL_H0 / 2
    top = lambda x: mid - funnel_h(x) / 2   # 楔形上斜边
    bot = lambda x: mid + funnel_h(x) / 2   # 楔形下斜边
    k = 0
    for ci, c in enumerate(claims, start=1):
        n = len(c['gates'])
        x_a = gx[k]; x_b = gx[k + n - 1] + GATE_W[k + n - 1]
        nxt = gx[k + n] - 0.12 if k + n < len(gx) else CX1
        text(s, '句_1_%d' % ci, x_a, cy, nxt - x_a, claim_h, c['claim'], CLAIM_SIZE, NAVY, CLAIM_PT, bold=True)
        seg(s, '括线_1_%d_横' % ci, x_a, by, x_b, by, TEAL, 1.0)
        seg(s, '括线_1_%d_左' % ci, x_a, by, x_a, by + BRACKET_TICK, TEAL, 1.0)
        seg(s, '括线_1_%d_右' % ci, x_b, by, x_b, by + BRACKET_TICK, TEAL, 1.0)
        for gi, (lead, body) in enumerate(c['gates'], start=1):
            # 每道关是楔形上的一段梯形：左上 → 右上 → 右下 → 左下，上下边都是斜的；关间不放小箭头
            xa, xb = gx[k], gx[k] + GATE_W[k]
            poly(s, '关_%d' % (k + 1), [(xa, top(xa)), (xb, top(xb)), (xb, bot(xb)), (xa, bot(xa))], FUNNEL_FILL)
            th = gate_text_h(lead, body)
            tb = textbox(s, '撑_1_%d_%d' % (ci, gi), xa + GATE_PAD_X, mid - th / 2, GATE_W[k] - 2 * GATE_PAD_X, th)
            add_para(tb.text_frame, True, lead, SUP_SIZE, FUNNEL_LEAD, SUP_PT, bold=True)
            add_para(tb.text_frame, False, body, SUP_SIZE, FUNNEL_BODY, SUP_PT)
            k += 1
    # 关 2、关 3 之间的缝里补一个同色 V 形箭头（审定 36）：上下沿落在楔形斜边上，整块读成一个连续漏斗；缝宽不变，括线照旧分两组
    ga, gb, m, d = gx[1] + GATE_W[1], gx[2], GAP_ARROW_M, GAP_ARROW_D
    poly(s, '漏斗箭头', [(ga + m, top(ga + m)), (gb - m - d, top(gb - m - d)), (gb - m, mid),
                      (gb - m - d, bot(gb - m - d)), (ga + m, bot(ga + m)), (ga + m + d, mid)], FUNNEL_FILL)
    top_bottom = y0 + top_h

    # ── 下带：运营做的（蓝） ──
    y1 = top_bottom + LANE_GAP
    bot_h = fixed_bot + card_h
    shape(s, '带_2', MSO_SHAPE.RECTANGLE, LANE_X0, y1, LANE_X1 - LANE_X0, bot_h, BLUE_T)
    shape(s, '色条_2', MSO_SHAPE.RECTANGLE, LANE_X0, y1, LANE_BAR, bot_h, BLUE)
    hy2 = y1 + HEAD_PAD
    text(s, '组句_2', CX0, hy2, CX1 - CX0, inch(HEAD_PT), D['groups'][1]['head'], HEAD_SIZE, NAVY, HEAD_PT, bold=True)
    ky = hy2 + inch(HEAD_PT) + HEAD_GAP
    kx = [CX0]
    for w in CARD_W[:-1]:
        kx.append(kx[-1] + w + CARD_GAP)
    assert abs(kx[-1] + CARD_W[-1] - CX1) < 0.02, '三张卡加间距要正好铺满带内宽：%.3f' % (kx[-1] + CARD_W[-1])
    pad = (card_h - max(card_text_h(pt) for pt in points)) / 2
    for pi, (x, w, pt) in enumerate(zip(kx, CARD_W, points), start=1):
        shape(s, '卡_2_%d' % pi, MSO_SHAPE.ROUNDED_RECTANGLE, x, ky, w, card_h, WHITE, line=BLUE_B)
        tx, tw = x + CARD_PAD_X, w - 2 * CARD_PAD_X
        y = ky + pad
        h = nlines(pt['claim']) * inch(CLAIM_PT)
        text(s, '句_2_%d' % pi, tx, y, tw, h, pt['claim'], CLAIM_SIZE, NAVY, CLAIM_PT, bold=True)
        y += h + GAP_CS
        for si, sup in enumerate(pt['sups'], start=1):
            h = nlines(sup) * inch(SUP_PT)
            text(s, '撑_2_%d_%d' % (pi, si), tx, y, tw, h, sup, SUP_SIZE, SUB, SUP_PT)
            y += h
        if pi < len(CARD_W):
            ax = x + w + (CARD_GAP - CARROW_W) / 2
            shape(s, '卡箭头_%d' % pi, MSO_SHAPE.RIGHT_ARROW, ax, ky + card_h / 2 - CARROW_H / 2, CARROW_W, CARROW_H, BLUE)

    # ── 一圈箭头：左边蓝（运营配好的 → 进系统第 1 关），右边青（系统最后一关弹出的结果 → 运营上架后看） ──
    cmid = ky + card_h / 2
    path(s, '回环_左', [(kx[0] - 0.02, cmid), (X0, cmid), (X0, mid), (gx[0] - 0.02, mid)], BLUE, LOOP_PT)
    g5r = gx[4] + GATE_W[4]
    path(s, '回环_右', [(g5r + 0.02, mid), (X1, mid), (X1, cmid), (kx[2] + CARD_W[2] + 0.02, cmid)], TEAL, LOOP_PT)

    x, y, w, h, sz, pt = PAGENO
    text(s, '页脚_页码', x, y, w, h, '1', sz, MUTE, pt, align=PP_ALIGN.RIGHT)


def build(out):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W); prs.slide_height = Inches(SLIDE_H)
    set_props(prs)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(WHITE)
    page(s, DATA)
    set_notes(s, DATA)
    prs.save(out)
    print('已生成', out, '共', len(prs.slides), '张')


# ═════════ 发给主管版：逐页相同，只去掉备注 ═════════
def manager_path(src):
    return os.path.join(os.path.dirname(src), '发给主管版', MANAGER_NAME)


def make_manager_copy(src):
    dst = manager_path(src)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    pr2 = Presentation(src)
    for sl in pr2.slides:
        if sl.has_notes_slide:
            sl.notes_slide.notes_text_frame.text = ''
            for rel in list(sl.part.rels.values()):
                if rel.reltype.endswith('/notesSlide'):
                    sl.part.drop_rel(rel.rId)
    set_props(pr2)
    pr2.save(dst)
    pr3 = Presentation(dst)
    n_notes = sum(1 for sl in pr3.slides if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip())
    print('发给主管版', dst, '共', len(pr3.slides), '张，带备注的页数', n_notes)
    return dst


# ═════════ 页面文字读回 ═════════
def page_pieces(slide):
    """返回 [(名称, 文字)]：每个带字的形状算一块。"""
    return [(sh.name, sh.text_frame.text) for sh in slide.shapes if sh.has_text_frame]


def n_head(slide):
    """标题＋两句组句的字数（去空白，英文字母各算 1 字）。"""
    return sum(len(re.sub(r'\s', '', t)) for n, t in page_pieces(slide) if n == '标题' or n.startswith('组句'))


def n_tables(slide):
    return sum(1 for sh in slide.shapes if getattr(sh, 'has_table', False) and sh.has_table)


def page_sig(path):
    """页面签名：每个形状的 名称、位置、大小、文字，用来比两份是否页面相同。"""
    return [[(sh.name, sh.left, sh.top, sh.width, sh.height, sh.text_frame.text if sh.has_text_frame else '')
             for sh in sl.shapes] for sl in Presentation(path).slides]


# ═════════ 页面只放内容：没有任何跳转，页面上没有跳转指引字样和「EP」 ═════════
def check_links(path):
    sl = list(Presentation(path).slides)
    jumps = []; hits = []
    for i, x in enumerate(sl):
        for sh in x.shapes:
            try:
                tgt = sh.click_action.target_slide
                addr = sh.click_action.hyperlink.address
            except Exception:
                tgt = addr = None
            if tgt is not None or addr:
                jumps.append('第 %d 页 %s' % (i + 1, sh.name))
            if sh.has_text_frame:
                for r in (r for p_ in sh.text_frame.paragraphs for r in p_.runs):
                    if r.hyperlink.address:
                        jumps.append('第 %d 页 %s（文字链接）' % (i + 1, sh.name))
        for name, t in page_pieces(x):
            hits += ['第 %d 页 %s「%s」' % (i + 1, name, w) for w in NAV if w in t]
    print('跳转或链接：%d 个%s' % (len(jumps), ('：' + '、'.join(jumps)) if jumps else ''))
    print('页面文字里的导航词 %s：%d 处%s' % ('、'.join('「%s」' % w for w in NAV), len(hits),
                                          ('：' + '、'.join(hits)) if hits else ''))
    heads = [n_head(x) for x in sl]
    print('标题＋组句 %s 字（上限 %d%s）' % ('、'.join(str(h) for h in heads), HEAD_MAX,
                                          '，超' if any(h > HEAD_MAX for h in heads) else ''))
    ok = not jumps and not hits and all(h <= HEAD_MAX for h in heads)
    # 两份页面相同、发给主管版无备注（只在传入的是讲稿版、且发给主管版已生成时比）
    dst = manager_path(path)
    if os.path.abspath(path) != os.path.abspath(dst) and os.path.exists(dst):
        same = page_sig(path) == page_sig(dst)
        pr = Presentation(dst)
        n_notes = sum(len(re.sub(r'\s', '', sl_.notes_slide.notes_text_frame.text))
                      for sl_ in pr.slides if sl_.has_notes_slide)
        print('两份页面相同：%s；发给主管版备注字数 %d（应为 0）' % ('是' if same else '否', n_notes))
        ok &= same and n_notes == 0
    return ok


# ═════════ 程序检查：页数、表格对象、字数、讲稿、禁用词、重复 ═════════
def stats(path):
    sl = list(Presentation(path).slides)
    nows = lambda t: re.sub(r'\s', '', t)
    ok = len(sl) == 1
    s = sl[0]
    pieces = page_pieces(s)
    ntab = n_tables(s)
    title = next(t for n, t in pieces if n == '标题')
    body = [(n, t) for n, t in pieces if n not in CHROME and t.strip()]
    nb = sum(len(nows(t)) for _, t in body)
    note = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ''
    speech = len(nows(note.split('若问')[0]))
    nasks = note.count('若问：')
    nh = n_head(s)
    ok &= ntab == 0 and nb <= BODY_MAX and nh <= HEAD_MAX and speech <= SPEECH_MAX and nasks == ASK_N
    print('页数 %d（应为 1）；页面表格对象 %d（应为 0）' % (len(sl), ntab))
    print('标题 %d 字；整页正文（不算标题、页码）%d 字（上限 %d%s）；讲稿 %d 字（上限 %d%s）≈%d 秒；若问 %d 条（应为 %d）' % (
        len(nows(title)), nb, BODY_MAX, '，超' if nb > BODY_MAX else '', speech, SPEECH_MAX,
        '，超' if speech > SPEECH_MAX else '', round(speech / 4), nasks, ASK_N))
    print('标题＋组句 %d 字（上限 %d%s）' % (nh, HEAD_MAX, '，超' if nh > HEAD_MAX else ''))
    for n, t in body:
        print('  %s：%d 字' % (n, len(nows(t))))
    # 每行放得下：每个 组句／句／撑 框按手动断行拆行，每行估宽×1.03 ≤ 框宽；行数×行距（读段落的固定磅数）≤ 框高
    fit = []   # (最宽一行估宽÷框宽, 框名, 过不过)
    for sh in s.shapes:
        if not (sh.has_text_frame and sh.name.split('_')[0] in ('组句', '句', '撑')):
            continue
        cw, ch = sh.width / 914400, sh.height / 914400
        rows, need = [], 0.0
        for p_ in sh.text_frame.paragraphs:
            parts = re.split(r'[\v\n]', p_.text)
            rows += [est_w(r, p_.runs[0].font.size.pt) for r in parts]
            need += len(parts) * p_.line_spacing.pt / 72
        fit.append((max(rows) / cw, sh.name, all(w * 1.03 <= cw + 1e-6 for w in rows) and need <= ch + 0.005))
    fit_ok = bool(fit) and all(f for _, _, f in fit)
    bad_fit = [n for _, n, f in fit if not f]
    print('每行放得下（每行估宽×1.03 ≤ 框宽，行数×行距 ≤ 框高）：%s，共 %d 个框；最满四个：%s%s' % (
        '是' if fit_ok else '否', len(fit), '；'.join('%s %.0f%%' % (n, r * 100) for r, n, _ in sorted(fit, reverse=True)[:4]),
        ('；放不下：' + '、'.join(bad_fit)) if bad_fit else ''))
    # 楔形：读每个 关_k 自由形状的点（custGeom 路径点按路径宽高缩放到形状大小，再加形状左上角），得每段左口、右口的上下沿
    def verts(sh):
        out = []
        for p_ in sh._element.iter(qn('a:path')):
            pw, ph = int(p_.get('w')), int(p_.get('h'))
            for q in p_.iter(qn('a:pt')):
                out.append(((sh.left + (int(q.get('x')) * sh.width / pw if pw else 0)) / 914400,
                            (sh.top + (int(q.get('y')) * sh.height / ph if ph else 0)) / 914400))
        return out
    shp = {sh.name: sh for sh in s.shapes}
    seg_ = []   # 每段 (左 x, 右 x, 左上 y, 左下 y, 右上 y, 右下 y)
    for k in range(1, 6):
        v = verts(shp['关_%d' % k])
        xl, xr = min(x for x, _ in v), max(x for x, _ in v)
        yl = [y for x, y in v if abs(x - xl) < 1e-4]; yr = [y for x, y in v if abs(x - xr) < 1e-4]
        seg_.append((xl, xr, min(yl), max(yl), min(yr), max(yr)))
    lh = [g[3] - g[2] for g in seg_]; rh = [g[5] - g[4] for g in seg_]
    wedge = (all(rh[i] < lh[i] for i in range(5)) and all(lh[i + 1] <= rh[i] + 1e-6 for i in range(4))
             and rh[4] / lh[0] <= 0.40)

    def h_at(x):
        """x 处楔形的上下沿：落在哪段就用哪段左右口的上下沿线性插值。"""
        g = next(g for g in seg_ if g[0] - 1e-6 <= x <= g[1] + 1e-6)
        t = (x - g[0]) / (g[1] - g[0])
        return g[2] + (g[4] - g[2]) * t, g[3] + (g[5] - g[3]) * t
    # 关里文字：框高＋0.12 ≤ 框里最宽一行右端处的楔形高
    gate_fit = []
    for sh in s.shapes:
        if not (sh.has_text_frame and sh.name.startswith('撑_1_')):
            continue
        wmax = max(est_w(r, p_.runs[0].font.size.pt) for p_ in sh.text_frame.paragraphs for r in re.split(r'[\v\n]', p_.text))
        t_, b_ = h_at(sh.left / 914400 + wmax)
        need = sh.height / 914400 + 2 * GATE_PAD_Y
        gate_fit.append((sh.name, need, b_ - t_, need <= b_ - t_ + 1e-6))
    gate_fit_ok = len(gate_fit) == 5 and all(f for *_, f in gate_fit)
    print('关里文字高够（框高＋%.2f ≤ 最宽一行右端处楔形高）：%s；%s' % (
        2 * GATE_PAD_Y, '是' if gate_fit_ok else '否', '　'.join('%s %.2f／%.2f' % (n, a, b) for n, a, b, _ in gate_fit)))
    # 关 2、关 3 之间的缝和缝里的同色箭头：缝宽、箭头在缝里、上下沿落在两侧楔形斜边的连线上
    gap23 = seg_[2][0] - seg_[1][1]
    av = verts(shp['漏斗箭头']) if '漏斗箭头' in shp else []
    amid = (seg_[1][2] + seg_[1][3]) / 2   # 楔形中线

    def edge(x, upper):   # 关 2 右口和关 3 左口的上（下）沿连线在 x 处的 y
        y2, y3 = (seg_[1][4], seg_[2][2]) if upper else (seg_[1][5], seg_[2][3])
        return y2 + (y3 - y2) * (x - seg_[1][1]) / gap23
    off = [abs(y - edge(x, y < amid)) for x, y in av if abs(y - amid) > 1e-3]
    in_gap = bool(av) and all(seg_[1][1] - 1e-6 <= x <= seg_[2][0] + 1e-6 for x, _ in av)
    arrow_ok = in_gap and bool(off) and max(off) <= 0.005 and len(off) == 4
    print('关 2、关 3 之间的缝 %.2f；缝里箭头 %d 个点、在缝里：%s，上下沿 %d 个角偏离楔形斜边最大 %.4f 英寸（≤0.005）：%s' % (
        gap23, len(av), '是' if in_gap else '否', len(off), max(off) if off else -1, '过' if arrow_ok else '不过'))
    # 底边：页码以外所有形状底边 ≤ BOTTOM_MAX
    bots = [((sh.top + sh.height) / 914400, sh.name) for sh in s.shapes if sh.name != '页脚_页码']
    bot_ok = all(b_ <= BOTTOM_MAX for b_, _ in bots)
    bmax = max(b_ for b_, _ in bots)
    print('页码以外形状底边最大 %.2f 英寸（上限 %.2f，%s）：%s' % (
        bmax, BOTTOM_MAX, '过' if bot_ok else '超', '／'.join(n for b_, n in bots if abs(b_ - bmax) < 1e-6)))
    # 版式核对：形状数、带字数；楔形逐段收窄；关、卡、组句都在自己的带里；两带不重叠
    box = {sh.name: (sh.left / 914400, sh.top / 914400, (sh.left + sh.width) / 914400, (sh.top + sh.height) / 914400)
           for sh in s.shapes}
    n_shapes = len(s.shapes)
    n_text = sum(1 for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip())
    gw = [g[1] - g[0] for g in seg_]
    inside = lambda n, ln: (box[ln][0] - 1e-3 <= box[n][0] and box[n][2] <= box[ln][2] + 1e-3
                            and box[ln][1] - 1e-3 <= box[n][1] and box[n][3] <= box[ln][3] + 1e-3)
    lanes = {'带_1': ['组句_1'] + ['关_%d' % k for k in range(1, 6)] + ['漏斗箭头'],
             '带_2': ['组句_2'] + ['卡_2_%d' % k for k in range(1, 4)]}
    out_lane = [n for ln, ns in lanes.items() for n in ns if n not in box or not inside(n, ln)]
    apart = box['带_1'][3] <= box['带_2'][1]
    lay_ok = (n_shapes == N_SHAPES and n_text == N_TEXT and wedge and gate_fit_ok and arrow_ok
              and not out_lane and apart)
    print('版式：形状 %d 个（应为 %d）、带字 %d 个（应为 %d）；五段宽 %s；左口／右口 %s；'
          '楔形逐段收窄（每段右口＜左口、下一段左口≤本段右口、关 5 右口÷关 1 左口 %.0f%% ≤40%%）：%s；'
          '关、卡、组句都在自己的带里：%s；两带不重叠：%s（上带底 %.2f，下带顶 %.2f）' % (
              n_shapes, N_SHAPES, n_text, N_TEXT, '／'.join('%.2f' % w for w in gw),
              '、'.join('%.2f／%.2f' % (a, b) for a, b in zip(lh, rh)), rh[4] / lh[0] * 100,
              '是' if wedge else '否', '是' if not out_lane else '否：' + '、'.join(out_lane),
              '是' if apart else '否', box['带_1'][3], box['带_2'][1]))
    ok = ok and fit_ok and bot_ok and lay_ok
    # 10 字以上重复：标题和每一块两两之间的公共片段，加同一块里重复出现的片段。
    # 两种算法都打：按字符（英文字母各算 1 字）、按词（一个英文单词或数字算 1 字，判过不过用这个）。
    blocks = [(n, nows(t)) for n, t in pieces if n != '页脚_页码' and t.strip()]

    def dups(tok):
        hits = set()
        tb = [(n, tok(t)) for n, t in blocks]
        for a in range(len(tb)):
            A = tb[a][1]
            grams = {tuple(A[k:k + 10]) for k in range(len(A) - 9)}
            for g in grams:
                if sum(1 for k in range(len(A) - 9) if tuple(A[k:k + 10]) == g) > 1:
                    hits.add((tb[a][0], tb[a][0], ''.join(g)))
                for b in range(a + 1, len(tb)):
                    B = tb[b][1]
                    if any(tuple(B[k:k + 10]) == g for k in range(len(B) - 9)):
                        hits.add((tb[a][0], tb[b][0], ''.join(g)))
        return hits
    by_char = dups(list)
    hits = dups(lambda t: re.findall(r'[A-Za-z0-9][A-Za-z0-9,.%]*|\S', t))
    show = lambda h: '；'.join('%s/%s「%s」' % x for x in sorted(h)[:4])
    print('10 字以上重复（按词，英文单词算 1 字）：%d 处%s' % (len(hits), ('：' + show(hits)) if hits else ''))
    print('  参考：按字符算 %d 处%s' % (len(by_char), ('：' + show(by_char)) if by_char else ''))
    page_t = ''.join(nows(t) for _, t in pieces)
    cnt = {w: (page_t.count(w.replace(' ', '')), note.count(w)) for w in BANNED}
    bad = {w: c for w, c in cnt.items() if sum(c)}
    print('禁用词计数（页面, 备注）：' + '、'.join('%s %d,%d' % (w, *c) for w, c in cnt.items()))
    print('禁用词合计：%s；「金字塔原理」%d 次（备注）；「上架」%d 次' % (
        bad or '全 0', note.count('金字塔原理'), (page_t + note).count('上架')))
    return ok and not hits and not bad


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['--check']:
        sys.exit(0 if check_links(args[1] if len(args) > 1 else OUT_DEFAULT) else 1)
    if args[:1] == ['--stats']:
        sys.exit(0 if stats(args[1] if len(args) > 1 else OUT_DEFAULT) else 1)
    out = args[0] if args else OUT_DEFAULT
    build(out)
    dst = make_manager_copy(out)
    print_props(out); print_props(dst)
