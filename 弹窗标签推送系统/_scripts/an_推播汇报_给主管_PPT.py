# 给主管的推播汇报（11/03 构图 A 填句子）：一页，标题＋上下两条泳道：上带＝运营做的（带顶组句一，三张卡横排、箭头连成先后），
# 下带＝系统管的（带顶组句二，两张卡并排）；没有表格。
# 用法：python3 _scripts/an_推播汇报_给主管_PPT.py            生成讲稿版和发给主管版两份
#       python3 _scripts/an_推播汇报_给主管_PPT.py --stats     读回两份已生成的文件，打印各项数字和各形状位置（不改文件）
#       python3 _scripts/an_推播汇报_给主管_PPT.py --check     读回两份已生成的文件，逐项判过不过（全过退出码 0）
# 输出：评审版_定稿改_1027/推送系统后台集成需求/推播汇报_给主管.pptx（讲稿版，备注＝讲稿＋若问）
#       同目录 发给主管版/推播功能设计汇报.pptx（页面相同，没有备注）
# 渲染只用：zsh _scripts/pl_pptx渲染.sh <pptx> _versions/渲染/推播汇报_给主管/
# 填内容只改下面的 DATA；版式代码不用动。DATA 里的 \n 只是手动换行位置（只断在自然停顿，构图草图第 47 节 A 那三处），不改字。
# 版式（思考页「构图草图」第 47 节草图 A、第 48 节、审定 29；来源 scratchpad/推播构图/草图A_泳道.py）：16:9，微软雅黑，左右边距 0.5 英寸；
# 标题横跨最上；两条横贯全宽的带子上下排列，每带左边一条色条，一色一义（运营做的蓝、系统管的青）；每张卡＝一句加挂在它下面的支撑；
# 字号四级：标题 22 粗｜组句 18 粗｜句 16 粗｜支撑 12 常规灰（页码 10 不算一级）。审定 29：压缩标题区和组句上下留白，卡加高。
import os
import sys
import re
from datetime import datetime, timezone
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR, MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

# ═════════ 全部文字（以后填内容只改这里）═════════
# 依据：任务文件旁 2026-11-02_推播汇报给主管/思考页.md『重搭第 2 版』4.3 节骨架、『重搭第 2 版续』第 18、21、22 节、『重搭第 3 版：计数第 1 次后改』第 33 节和『重搭第 4 版：计数第 2 次后改』第 42 节；构图照『构图草图』第 47 节草图 A、第 48 节和审定 29；『构图 A 第 2 次改稿（填句版评审后）』第 53–60 节；『构图 A 第 3 次改稿（第 2 次评审后）』第 67–71 节
# title：最上面一句总结论
# groups：两组，从上到下；每组 head＝组句（统领这一组，写在带顶），points＝组内各句（一句一张卡）；每句 claim＝一句判断，sups＝挂在它下面的支撑（条数按需要，每句不一样）
# notes：讲稿版备注，speech＝1 分钟讲稿，asks＝若问（问，答；出处不进备注）；发给主管版不建备注
DATA = {
    'title': '推播由运营自助完成，系统替玩家控制打扰',
    'groups': [
        {'head': '一条推播从建到看效果，运营都能自己做',
         'points': [
             {'claim': '发给哪些玩家，运营选群组来定',
              'sups': ['可多选群组或上传名单，也能排除群组',
                       '选完就显示预计人数']},
             {'claim': '能定时发，\n也能设条件让系统自动发',
              'sups': ['条件如玩家升级、活动或礼包前后 N 小时']},
             {'claim': '每条推播能看\n发出、到达、点击人数',
              'sups': ['没发出的人列明原因，\n如关了通知、已达每天上限',
                       'iOS 到达默认看不到，显示「未接入」']},
         ]},
        {'head': '不管运营建多少条，每位玩家受的打扰都由系统统一管',
         'points': [
             {'claim': '每位玩家每天默认最多收 2 条营销推播',
              'sups': ['补偿、维护等服务通知不算在内',
                       '条数可改，也能按群组另设']},
             {'claim': '营销推播默认不在 22 点到 8 点发',
              'sups': ['定时推播，推迟到 8 点再发',
                       '活动或礼包前后的提醒，运营每条选推迟或不发',
                       '玩家升级这类发送时间因人而异的，落在夜里就不发，也不补发']},
         ]},
    ],
    'notes': {
        'speech': '推播由运营自助完成，系统替玩家控制打扰。'
                  '第一块，一条推播从建到看效果，运营都能自己做：选群组定发给谁，选完就看到预计人数；'
                  '能定时发，也能设条件自动发；'
                  '每条能看发出、到达、点击人数，没发出的列明原因，iOS 到达默认看不到。'
                  '第二块，不管运营建多少条，每位玩家受的打扰都由系统统一管：每人每天默认最多 2 条营销推播；'
                  '22 点到 8 点营销推播都不发：定时的推迟到 8 点；'
                  '活动、礼包的提醒，运营只选推迟或不发；'
                  '玩家升级这类发送时间因人而异的，落在夜里就不发，也不补发。'
                  '您对哪点有疑问？',
        'asks': [
            ('和现在的推播比，差在哪？',
             '运营现在的推播后台能发全部玩家、上传名单或标签群组，但发给多少人要另找人查；'
             '此外游戏服务器按活动自动发 34 种推播，如倒计时、未领奖，条件和文案写在服务器代码里，运营改不了；'
             '推播报表的列是「傳送」「曝光」「開啟」，没有到达，成败要拿推播编号去 Firebase 后台对照查；'
             '运营规范每天不超过两条，后台限不了；'
             '规定晚上 10 点到早上 8 点的推播设不了、也不发，活动提醒落在这段就不提醒，但出过晚上 11 点还收到推播的情况。'),
            ('每天 2 条凭什么？',
             '沿用运营规范「每天推播不超过两条」，是起始值；在每人每天上限设置里可改，也可按群组另设，保存前看到改后今天收不到的人数增减。'
             '业界 Braze、MoEngage、CleverTap、Airship 都按渠道设每人上限；按群组另设是我们多做的。'),
            ('一人当天超过 2 条，留哪条？业界也这样吗？',
             '留权重高的。'
             '每条营销推播新建时填权重，0–100 的整数，越大越优先，默认 50。'
             '当天后面还有权重更高的定时推播，名额由它先占，前面权重低的就不发。'
             '数据里，这样没发出的人记在原因「每人每天上限」下面的一项「其中条数被权重更高的定时推播先占」，不另算一个原因。'
             '代价是运营多设一项权重。'
             '业界 Adobe Journey Optimizer 思路相同：给每条流程打 0–100 的优先级分，先给之后已排好、优先级更高的流程留位置。'
             '只是它限的是玩家进几条流程，不是每天收几条推播。'
             'MoEngage 文档写明先到先得，和我们不同；Braze、OneSignal、Airship 的文档没写谁先发。'),
            ('夜里三类为什么处理不同？服务通知怎么算？',
             '定时的和活动、礼包的提醒，都是所有人同一时刻到点，推迟后能在 8 点整批发；零点开的活动，开始后几小时的提醒要是一律不发，一条都发不出去。'
             '活动、礼包这类推迟还是不发，由运营新建时每条必选，不设默认。'
             '玩家升级这类发送时间因人而异的，要推迟就得到早上重新判断条件和上限，各人的礼包可能已经过期；所以落在夜里就不发，也不补发。'
             '推迟的那几条，发送对象按 8 点那一刻算；夜间勿扰时段在设置里可改。'
             '服务通知只用于补偿、维护、账号安全、绑定结果，不算进每天的条数；夜里账号安全照发，其余推迟到 8 点。'),
            ('到达率、点击率怎么算？',
             '到达率＝到达 ÷ 能确认到达的发出；iOS 到达默认看不到，显示「未接入」，不算进分母。'
             '点击率＝点击 ÷ 发出。'),
        ],
    },
}
# 页面上应有的文字框数（检查用，按 DATA 算）：标题 1＋组句＋各句＋支撑＋页码 1
N_HEAD = len(DATA['groups'])
N_CLAIM = sum(len(g['points']) for g in DATA['groups'])
N_SUP = sum(len(pt['sups']) for g in DATA['groups'] for pt in g['points'])
N_TEXT = 1 + N_HEAD + N_CLAIM + N_SUP + 1
# 页面上应有的其余形状（检查用，按 DATA 算）：标题线；每组一条带、一条色条、每句一张卡；第 1 组卡与卡之间各一个箭头
EXPECT_OTHER = (['标题线']
                + [n for gi, g in enumerate(DATA['groups'], start=1)
                   for n in ['带%d' % gi, '色条%d' % gi] + ['卡%d-%d' % (gi, pi) for pi in range(1, len(g['points']) + 1)]]
                + ['箭头%d' % k for k in range(1, len(DATA['groups'][0]['points']))])

# 页面和备注里一出现就一定不对的字（卡上「检查」①，11/03 09:55）：跳转和指引字样、「EP」；其余要求由评审按意思判，不按字面拦
BANNED = ['回到第', '见第', '见附录', '细节见', '→ 第', 'EP']
BODY_MAX, SPEECH_MAX, ASK_N = 300, 240, 5      # 正文（不含标题、页码）≤300（卡上定）、讲稿 ≤240 字（约 1 分钟）、追问 5 条

FILE_TITLE = '推播功能设计汇报'                  # pptx 文件属性里的标题（思考页 7.5）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, '评审版_定稿改_1027', '推送系统后台集成需求')
OUT_NOTES = os.path.join(OUT_DIR, '推播汇报_给主管.pptx')
OUT_SENT = os.path.join(OUT_DIR, '发给主管版', '推播功能设计汇报.pptx')
FONT = 'Microsoft YaHei'

WHITE = 'FFFFFF'; NAVY = '1F2A44'; MUTE = '9A9FA8'; LINE = 'E2DED5'
SUB = '5B6272'                                             # 支撑的灰
BLUE = '2A63A6'; BLUE_T = 'EEF3FA'; BLUE_B = 'C9D7EA'     # 运营做的：蓝（色条、箭头）、浅蓝带底、卡边
TEAL = '2C7A6B'; TEAL_T = 'EAF4F1'; TEAL_B = 'C3DDD6'     # 系统管的：青（色条）、浅青带底、卡边
LANE_STYLE = [(BLUE_T, BLUE, BLUE_B), (TEAL_T, TEAL, TEAL_B)]
L, R = PP_ALIGN.LEFT, PP_ALIGN.RIGHT
TOP, MID = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE

# 版面（英寸）。文字框边距 0、顶对齐、行距用固定磅数：框高＝行数×行距，读回能按行距核框装不装得下
SLIDE_W, SLIDE_H = 13.333, 7.5
X0, X1 = 0.5, 12.833                         # 左右边距 0.5
TITLE_Y, TITLE_H, TITLE_SIZE, TITLE_PT = 0.30, 0.44, 22, 30   # 标题（审定 29 压缩标题区：草图 0.42–0.92、线 1.08、带 1.30）
RULE_Y = 0.88                                # 标题下细线 0.75 磅
LANE_TOP, LANE_BOTTOM, LANE_GAP = 1.02, 6.88, 0.26             # 上带顶、下带底（同草图 6.88）、两带间
LANE_BAR = 0.08                              # 每带左边色条宽
IN_X0, IN_X1 = 0.80, 12.53                   # 带内左右（左边让出色条，同草图）
HEAD_SIZE, HEAD_PT = 18, 25                  # 组句（带顶一行）
HEAD_PAD, HEAD_GAP, LANE_PAD_B = 0.14, 0.14, 0.18              # 带顶到组句、组句到卡、卡到带底（草图是 0.18 和约 0.39）
CLAIM_SIZE, CLAIM_PT = 16, 23                # 句
SUP_SIZE, SUP_PT = 12, 18                    # 支撑
GAP_CS, GAP_SS = 0.12, 0.06                  # 卡里：句到第一条支撑、支撑和支撑之间
CARD_PAD_X, CARD_PAD_MIN = 0.16, 0.20        # 卡左右内边距；上下内边距至少 0.20，排完多出来的高平分进去（卡加高）
ARW, ARROW_W, ARROW_H = 0.50, 0.32, 0.28     # 上带两卡之间留给箭头的宽；箭头大小
CARD_GAP = 0.30                              # 下带两卡之间
PAGENO_X, PAGENO_Y, PAGENO_W, PAGENO_H, PAGENO_SIZE, PAGENO_PT = 12.59, 7.0, 0.23, 0.25, 10, 14


def rgb(h):
    return RGBColor.from_string(h)


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


def textbox(s, name, x, y, w, h, anchor=TOP, wrap=True):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = wrap; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    return tb


def add_runs(p, t, size, color, bold=False):
    """往一段里加字；t 里的 \n 变成手动换行（同一段内）。"""
    for k, part in enumerate(t.split('\n')):
        if k:
            p.add_line_break()
        r = p.add_run(); r.text = part
        font(r, size, color, bold)


def text(s, name, x, y, w, h, t, size, color, pitch, bold=False, align=L, anchor=TOP, wrap=True):
    """一个文字框，一段，一种字；行距固定 pitch 磅。"""
    tb = textbox(s, name, x, y, w, h, anchor, wrap)
    p = tb.text_frame.paragraphs[0]
    p.alignment = align; p.line_spacing = Pt(pitch)
    add_runs(p, t, size, color, bold)
    return tb


def no_effect(sp):
    sp._element.spPr.append(sp._element.spPr.makeelement(qn('a:effectLst'), {}))   # 去掉主题带的阴影


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


def connector(s, name, x1, y1, x2, y2, color, width, head=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb = rgb(color); c.line.width = Pt(width)
    if head:                                   # 终点加三角箭头
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    no_effect(c)
    return c


def notes_text(n):
    """备注＝讲稿，空一行，再逐条「若问：…／答：…」（条间空一行）。"""
    parts = [n['speech']]
    for q, a in n.get('asks', []):
        parts += ['', '若问：%s\n答：%s' % (q, a)]
    return '\n'.join(parts).strip()


# ═════════ 整页：标题 → 上带（组句一＋三张卡＋箭头）→ 下带（组句二＋两张卡）→ 页码 ═════════
def n_lines(t):
    return t.count('\n') + 1


def inch(pt):
    return pt / 72


def card_content_h(pt):
    """一张卡里字的总高：句的行数×句行距＋句到支撑的空＋各支撑行数×支撑行距＋支撑之间的空。"""
    h = n_lines(pt['claim']) * inch(CLAIM_PT) + GAP_CS
    h += sum(n_lines(t) * inch(SUP_PT) for t in pt['sups']) + GAP_SS * (len(pt['sups']) - 1)
    return h


def layout(data):
    """算两条带和卡的位置（英寸）。卡宽：上带三张等宽、中间留箭头；下带两张等宽。
    卡高按每带字最多的那张统一；从上带顶排到下带底（LANE_BOTTOM）多出来的高，平分给各带卡的上下内边距（卡加高）。"""
    lanes = []
    for gi, g in enumerate(data['groups'], start=1):
        n = len(g['points'])
        gap = ARW if gi == 1 else CARD_GAP
        w = (IN_X1 - IN_X0 - (n - 1) * gap) / n
        lanes.append({'w': w, 'xs': [IN_X0 + k * (w + gap) for k in range(n)],
                      'content': max(card_content_h(pt) for pt in g['points'])})
    fixed = sum(HEAD_PAD + inch(HEAD_PT) + HEAD_GAP + l['content'] + 2 * CARD_PAD_MIN + LANE_PAD_B for l in lanes)
    fixed += LANE_GAP * (len(lanes) - 1)
    pad = CARD_PAD_MIN + max(0.0, LANE_BOTTOM - LANE_TOP - fixed) / (2 * len(lanes))
    y = LANE_TOP
    for l in lanes:
        l['top'] = y
        l['head_y'] = y + HEAD_PAD
        l['card_y'] = l['head_y'] + inch(HEAD_PT) + HEAD_GAP
        l['card_h'] = l['content'] + 2 * pad
        l['bottom'] = l['card_y'] + l['card_h'] + LANE_PAD_B
        y = l['bottom'] + LANE_GAP
    return lanes, pad


def build(data, sent):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W); prs.slide_height = Inches(SLIDE_H)
    # 文件属性：作者、上次修改者「产品部」，标题「推播功能设计汇报」，创建修改时间为当前，描述、关键词清空
    cp = prs.core_properties
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    cp.author = cp.last_modified_by = '产品部'
    cp.title = FILE_TITLE
    cp.created = cp.modified = now
    cp.comments = ''; cp.keywords = ''; cp.subject = ''; cp.category = ''
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(WHITE)
    text(s, '标题', X0, TITLE_Y, X1 - X0, TITLE_H, data['title'], TITLE_SIZE, NAVY, TITLE_PT, bold=True, anchor=MID)
    connector(s, '标题线', X0, RULE_Y, X1, RULE_Y, LINE, 0.75)
    lanes, pad = layout(data)
    for gi, (g, l) in enumerate(zip(data['groups'], lanes), start=1):
        fill, accent, border = LANE_STYLE[gi - 1]
        lane_h = l['bottom'] - l['top']
        shape(s, '带%d' % gi, MSO_SHAPE.RECTANGLE, X0, l['top'], X1 - X0, lane_h, fill)
        shape(s, '色条%d' % gi, MSO_SHAPE.RECTANGLE, X0, l['top'], LANE_BAR, lane_h, accent)
        text(s, '组句%d' % gi, IN_X0, l['head_y'], IN_X1 - IN_X0, n_lines(g['head']) * inch(HEAD_PT),
             g['head'], HEAD_SIZE, NAVY, HEAD_PT, bold=True)
        for pi, (x, pt) in enumerate(zip(l['xs'], g['points']), start=1):
            shape(s, '卡%d-%d' % (gi, pi), MSO_SHAPE.ROUNDED_RECTANGLE, x, l['card_y'], l['w'], l['card_h'], WHITE, line=border)
            tx, tw = x + CARD_PAD_X, l['w'] - 2 * CARD_PAD_X
            y = l['card_y'] + pad
            h = n_lines(pt['claim']) * inch(CLAIM_PT)
            text(s, '分句%d-%d' % (gi, pi), tx, y, tw, h, pt['claim'], CLAIM_SIZE, NAVY, CLAIM_PT, bold=True)
            y += h + GAP_CS
            for si, sup in enumerate(pt['sups'], start=1):
                if si > 1:
                    y += GAP_SS
                h = n_lines(sup) * inch(SUP_PT)
                text(s, '支撑%d-%d-%d' % (gi, pi, si), tx, y, tw, h, sup, SUP_SIZE, SUB, SUP_PT)
                y += h
            if gi == 1 and pi < len(g['points']):                   # 上带卡与卡之间的箭头：建 → 发 → 看
                ax = x + l['w'] + (ARW - ARROW_W) / 2
                ay = l['card_y'] + l['card_h'] / 2 - ARROW_H / 2
                shape(s, '箭头%d' % pi, MSO_SHAPE.RIGHT_ARROW, ax, ay, ARROW_W, ARROW_H, BLUE)
    text(s, '页码', PAGENO_X, PAGENO_Y, PAGENO_W, PAGENO_H, '1', PAGENO_SIZE, MUTE, PAGENO_PT, align=R, wrap=False)
    if not sent:
        s.notes_slide.notes_text_frame.text = notes_text(data['notes'])
    return prs


# ═════════ 读回已生成的文件，算各项数字 ═════════
def n_chars(t):
    return len(re.sub(r'\s', '', t))


def em(t):
    """估宽（以字号为 1）：汉字和全角标点 1，英文字母数字和半角符号 0.55，空格 0.3（同草图 sketch_common.py）。"""
    n = 0.0
    for c in t:
        if c == ' ':
            n += 0.3
        elif ord(c) > 0x2E7F:
            n += 1.0
        else:
            n += 0.55
    return n


def read_deck(path):
    """返回一份文件的各项数字和原文。块＝页面上每个形状里的每一段（标题和页码单列）。"""
    prs = Presentation(path)
    slides = list(prs.slides)
    cp = prs.core_properties
    info = {'path': path, 'pages': len(slides), 'tables': 0, 'jumps': 0, 'blocks': [], 'notes': '', 'has_notes': False,
            'props': (cp.author, cp.last_modified_by, cp.title, cp.comments, cp.keywords),
            'text_shapes': 0, 'other_shapes': []}
    for sl in slides:
        for sh in sl.shapes:
            try:
                is_table = bool(sh.has_table) or sh.shape_type == MSO_SHAPE_TYPE.TABLE
            except Exception:
                is_table = bool(getattr(sh, 'has_table', False))
            info['tables'] += is_table
            try:
                if sh.click_action.target_slide is not None or sh.click_action.hyperlink.address:
                    info['jumps'] += 1
            except Exception:
                pass
            if sh.shape_type == MSO_SHAPE_TYPE.TEXT_BOX:
                info['text_shapes'] += 1
            else:
                info['other_shapes'].append(sh.name)
            if sh.has_text_frame:
                for k, p in enumerate(sh.text_frame.paragraphs):
                    for r in p.runs:
                        if r.hyperlink.address:
                            info['jumps'] += 1
                    if p.text.strip():
                        info['blocks'].append(('%s-%d' % (sh.name, k + 1), p.text))
        if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip():
            info['has_notes'] = True
            info['notes'] += sl.notes_slide.notes_text_frame.text
    page = info['blocks']
    info['title'] = ''.join(t for n, t in page if n.startswith('标题'))
    info['body_blocks'] = [(n, t) for n, t in page if not n.startswith('标题') and not n.startswith('页码')]
    info['n_title'] = n_chars(info['title'])
    info['n_body'] = sum(n_chars(t) for _, t in info['body_blocks'])
    info['n_all'] = info['n_title'] + info['n_body']
    note = info['notes']
    cut = note.find('若问')
    speech = note[:cut] if cut >= 0 else note
    info['n_speech'] = n_chars(speech)
    info['n_asks'] = note.count('若问：')
    page_text = '\n'.join(t for _, t in page)
    info['page_text'] = page_text

    def count(w, t):
        return len(re.findall(r'\s*'.join(map(re.escape, w.split(' '))), t))
    info['banned'] = {w: count(w, page_text + '\n' + note) for w in BANNED}
    info['quotes'] = sorted(set(re.findall(r'[“”‘’"\'『』]', page_text + note)))
    # 10 字以上重复：标题和每一段（去空白，英文字母各算 1 字）两两之间的公共 10 字片段，加同一段里重复的片段
    # 页面上没有「现在」「依据」标签，「现在」是句子里的字，比对时只去空白
    blocks = [(n, re.sub(r'\s', '', t)) for n, t in page if not n.startswith('页码')]
    dups = set()
    for a in range(len(blocks)):
        A = blocks[a][1]
        grams = [A[k:k + 10] for k in range(len(A) - 9)]
        for g in set(grams):
            if grams.count(g) > 1:
                dups.add((blocks[a][0], blocks[a][0], g))
            for b in range(a + 1, len(blocks)):
                if g in blocks[b][1]:
                    dups.add((blocks[a][0], blocks[b][0], g))
    info['dups'] = sorted(dups)
    info['geom'] = read_geom(slides[0]) if slides else {}
    return info


# ═════════ 读回各形状的位置（英寸）和字，核版式 ═════════
EMU = 914400


def read_geom(sl):
    """每个形状：x、y、w、h、右 r、底 b；连接线另给两端；文字框另给每行（字、字号、行距磅数）。"""
    out = {}
    for sh in sl.shapes:
        g = {'x': sh.left / EMU, 'y': sh.top / EMU, 'w': sh.width / EMU, 'h': sh.height / EMU, 'order': len(out)}
        g['r'] = g['x'] + g['w']; g['b'] = g['y'] + g['h']
        if hasattr(sh, 'begin_x'):
            g['ends'] = (sh.begin_x / EMU, sh.begin_y / EMU, sh.end_x / EMU, sh.end_y / EMU)
            g['lw'] = sh.line.width.pt
        if sh.shape_type == MSO_SHAPE_TYPE.TEXT_BOX:
            rows = []
            for p in sh.text_frame.paragraphs:
                size = max((r.font.size.pt for r in p.runs if r.font.size is not None), default=0)
                ls = p.line_spacing
                pitch = ls.pt if hasattr(ls, 'pt') else None           # 固定磅数；倍数行距记 None，判不了高
                for part in p.text.split('\v'):
                    rows.append((part, size, pitch))
            g['rows'] = rows
        out[sh.name] = g
    return out


def fit(g):
    """估一个文字框装不装得下：每行估宽 ≤ 框宽，行数×行距 ≤ 框高，行距 ≥ 字号×1.25。返回（最满一行占框宽、问题列表）。"""
    worst, probs = 0.0, []
    for part, size, pitch in g['rows']:
        wd = em(part) * size / 72
        worst = max(worst, wd / g['w'])
        if wd > g['w'] + 1e-6:
            probs.append('「%s」估宽 %.2f > 框宽 %.2f' % (part, wd, g['w']))
        if pitch is None or pitch < size * 1.25:
            probs.append('「%s」行距 %s 磅不够' % (part, pitch))
    need = sum((p or 0) for _, _, p in g['rows']) / 72
    if need > g['h'] + 0.005:
        probs.append('%d 行要高 %.3f > 框高 %.3f' % (len(g['rows']), need, g['h']))
    return worst, probs


def inside(a, b, tol=0.002):
    return a['x'] >= b['x'] - tol and a['r'] <= b['r'] + tol and a['y'] >= b['y'] - tol and a['b'] <= b['b'] + tol


def layout_rows(G):
    """版式逐项判，返回 [(过不过, 说明)]。应得值都是本版式（构图 A）的。"""
    rows = []
    over = []
    worst = ('', 0.0)
    for n, g in G.items():
        if 'rows' in g:
            w, probs = fit(g)
            over += ['%s：%s' % (n, p) for p in probs]
            if w > worst[1]:
                worst = (n, w)
    rows.append((not over, '文字溢出框 %d 处（估宽、行数×行距对框；最满的是「%s」占框宽 %.0f%%）%s' % (
        len(over), worst[0], worst[1] * 100, ''.join('\n      ' + o for o in over))))
    t = G.get('标题', {})
    rows.append((len(t.get('rows', [])) == 1 and fit(t)[1] == [], '标题一行（估宽占框宽 %.0f%%）' % (fit(t)[0] * 100 if t else 0)))
    rows.append((t and t['b'] <= G['标题线']['y'] <= G['带1']['y'],
                 '标题底 %.2f ≤ 标题线 %.2f ≤ 上带顶 %.2f' % (t['b'], G['标题线']['y'], G['带1']['y'])))
    bad = []
    for gi, g in enumerate(DATA['groups'], start=1):
        lane = G['带%d' % gi]
        if not inside(G['组句%d' % gi], lane):
            bad.append('组句%d 出带' % gi)
        cards = [G['卡%d-%d' % (gi, pi)] for pi in range(1, len(g['points']) + 1)]
        if len({round(c['h'], 3) for c in cards}) != 1 or len({round(c['y'], 3) for c in cards}) != 1:
            bad.append('带%d 的卡不等高或不齐顶' % gi)
        if cards[0]['y'] < G['组句%d' % gi]['b']:
            bad.append('带%d 的卡压到组句' % gi)
        for pi, pt in enumerate(g['points'], start=1):
            card = G['卡%d-%d' % (gi, pi)]
            if not inside(card, lane):
                bad.append('卡%d-%d 出带' % (gi, pi))
            seq = ['分句%d-%d' % (gi, pi)] + ['支撑%d-%d-%d' % (gi, pi, si) for si in range(1, len(pt['sups']) + 1)]
            prev = None
            for n in seq:
                if not inside(G[n], card):
                    bad.append('%s 出卡' % n)
                if prev is not None and G[n]['y'] < G[prev]['b'] - 0.002:
                    bad.append('%s 压到 %s' % (n, prev))
                prev = n
        if G['色条%d' % gi]['y'] != lane['y'] or abs(G['色条%d' % gi]['h'] - lane['h']) > 0.002:
            bad.append('色条%d 和带不一样高' % gi)
    rows.append((not bad, '字都在卡里、卡都在带里、卡里各框从上到下不重叠、同带卡等高齐顶%s' % (
        '' if not bad else '：' + '；'.join(bad))))
    l1, l2, pg = G['带1'], G['带2'], G['页码']
    rows.append((l1['b'] < l2['y'] and l2['b'] <= pg['y'] and SLIDE_H - l2['b'] >= 0.5,
                 '上带 %.2f–%.2f，下带 %.2f–%.2f；下带底到页码顶 %.2f、到页底 %.2f（≥0.5）' % (
                     l1['y'], l1['b'], l2['y'], l2['b'], pg['y'] - l2['b'], SLIDE_H - l2['b'])))
    ok_arr = True
    for k in range(1, len(DATA['groups'][0]['points'])):
        a, c1, c2 = G['箭头%d' % k], G['卡1-%d' % k], G['卡1-%d' % (k + 1)]
        ok_arr &= c1['r'] <= a['x'] and a['r'] <= c2['x'] and c1['y'] <= a['y'] and a['b'] <= c1['b']
    rows.append((ok_arr, '箭头 %d 个，各在上带两张卡之间' % (len(DATA['groups'][0]['points']) - 1)))
    return rows


def need_files():
    miss = [p for p in (OUT_NOTES, OUT_SENT) if not os.path.exists(p)]
    if miss:
        print('文件还没生成，先不带参数跑一遍：', '、'.join(miss))
        sys.exit(2)


def stats():
    need_files()
    for label, path in (('讲稿版', OUT_NOTES), ('发给主管版', OUT_SENT)):
        d = read_deck(path)
        print('【%s】%s' % (label, path))
        print('  页数 %d｜表格形状 %d｜跳转或链接 %d' % (d['pages'], d['tables'], d['jumps']))
        print('  正文（不含标题、页码，去空白、含标点）%d 字（上限 %d）｜连标题 %d 字｜标题 %d 字' % (
            d['n_body'], BODY_MAX, d['n_all'], d['n_title']))
        for n, t in d['body_blocks']:
            print('    %-8s %2d 字  %s' % (n, n_chars(t), t.replace('\n', ' / ').replace('\x0b', ' / ')))
        if d['has_notes']:
            print('  讲稿 %d 字（上限 %d；按每分钟 240 字约 %d 秒）｜追问 %d 条（应为 %d）' % (
                d['n_speech'], SPEECH_MAX, round(d['n_speech'] / 4), d['n_asks'], ASK_N))
        else:
            print('  备注：无')
        bad = {w: c for w, c in d['banned'].items() if c}
        print('  跳转指引字样和「EP」（页面＋备注，%d 个）合计 %d：%s' % (len(BANNED), sum(d['banned'].values()), bad or '全 0'))
        print('  页面 10 字以上重复 %d 处%s' % (len(d['dups']), ''.join('\n    %s／%s「%s」' % x for x in d['dups'])))
        print('  页面形状：文字框 %d 个，其余 %d 个：%s' % (d['text_shapes'], len(d['other_shapes']), '、'.join(d['other_shapes'])))
        print('  非「」引号：%s' % (' '.join(d['quotes']) or '无'))
        print('  文件属性：作者=%s｜上次修改者=%s｜标题=%s｜描述=%r｜关键词=%r' % d['props'])
        G = d['geom']
        print('  各形状位置（英寸，x / y / 宽 / 高 / 底）：')
        for n, g in sorted(G.items(), key=lambda kv: kv[1]['order']):
            extra = ''
            if 'rows' in g:
                w, probs = fit(g)
                extra = '｜%d 行，最满一行占框宽 %.0f%%%s' % (len(g['rows']), w * 100, '，溢出' if probs else '')
            if 'ends' in g:
                extra = '｜两端 (%.2f, %.2f)→(%.2f, %.2f)，%.2f 磅' % (g['ends'] + (g['lw'],))
            print('    %-10s %6.2f %5.2f %6.2f %5.2f %5.2f%s' % (n, g['x'], g['y'], g['w'], g['h'], g['b'], extra))
        print('  版式：')
        for ok, msg in layout_rows(G):
            print('    %s %s' % ('是' if ok else '否', msg))


def check():
    need_files()
    ok_all = True

    def row(ok, msg):
        nonlocal ok_all
        ok_all &= bool(ok)
        print('  %s %s' % ('通过' if ok else '不通过', msg))
    pages = {}
    for label, path, sent in (('讲稿版', OUT_NOTES, False), ('发给主管版', OUT_SENT, True)):
        d = read_deck(path)
        pages[label] = d['page_text']
        print('【%s】' % label)
        row(d['pages'] == 1, '页数 %d（应为 1）' % d['pages'])
        row(d['n_body'] <= BODY_MAX, '正文不含标题 %d 字（≤%d）；连标题 %d 字' % (d['n_body'], BODY_MAX, d['n_all']))
        row(d['tables'] == 0, '表格形状 %d（应为 0）' % d['tables'])
        row(d['jumps'] == 0, '跳转或链接 %d（应为 0）' % d['jumps'])
        row(not sum(d['banned'].values()), '跳转指引字样和「EP」（%d 个，页面＋备注）%d' % (len(BANNED), sum(d['banned'].values())))
        row(not d['dups'], '页面 10 字以上重复 %d 处' % len(d['dups']))
        row(not d['quotes'], '非「」引号 %s' % (' '.join(d['quotes']) or '无'))
        row(d['text_shapes'] == N_TEXT, '页面文字框 %d 个（应为 %d：标题、组句 %d、各句 %d、支撑 %d、页码）' % (
            d['text_shapes'], N_TEXT, N_HEAD, N_CLAIM, N_SUP))
        row(sorted(d['other_shapes']) == sorted(EXPECT_OTHER), '其余形状 %d 个（应为 %d：%s）' % (
            len(d['other_shapes']), len(EXPECT_OTHER), '、'.join(EXPECT_OTHER)))
        for ok, msg in layout_rows(d['geom']):
            row(ok, msg)
        row(d['props'][0] == '产品部' and d['props'][1] == '产品部' and d['props'][2] == FILE_TITLE
            and not d['props'][3] and not d['props'][4], '文件属性 作者、上次修改者「产品部」，标题「%s」，描述、关键词空' % FILE_TITLE)
        if sent:
            row(not d['has_notes'], '发给主管版备注为空（%s）' % ('有备注' if d['has_notes'] else '无备注'))
        else:
            row(d['has_notes'] and d['n_speech'] <= SPEECH_MAX, '讲稿 %d 字（≤%d），约 %d 秒' % (
                d['n_speech'], SPEECH_MAX, round(d['n_speech'] / 4)))
            row(d['n_asks'] == ASK_N, '追问 %d 条（应为 %d）' % (d['n_asks'], ASK_N))
    print('【两份对照】')
    row(pages['讲稿版'] == pages['发给主管版'], '两份页面相同（讲稿版和发给主管版的页面文字一字不差）')
    print('全部通过' if ok_all else '有项目不通过')
    return ok_all


if __name__ == '__main__':
    if '--stats' in sys.argv:
        stats()
        sys.exit(0)
    if '--check' in sys.argv:
        sys.exit(0 if check() else 1)
    for sent, out in ((False, OUT_NOTES), (True, OUT_SENT)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        prs = build(DATA, sent)
        prs.save(out)
        print('已生成', out, '共', len(prs.slides), '张', '（发给主管版）' if sent else '（讲稿版）')
