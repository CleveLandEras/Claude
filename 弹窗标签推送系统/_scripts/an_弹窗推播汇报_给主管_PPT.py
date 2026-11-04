# -*- coding: utf-8 -*-
# 给主管的弹窗、推播一场汇报（11/03）：10 页，序言 → 目录 → 弹窗主界面 → 先场景还是先人群 → 弹窗新建 → 弹窗数据 → 过渡 → 推播主界面 → 推播新建 → 推播数据。
# 第 2 次改稿（思考页第 11 节、审定 4；标题照卡上第 1、2、15 条：词组、不带逗号、≤12 字，结论放各块带头句）。
# 用法：python3 _scripts/an_弹窗推播汇报_给主管_PPT.py            生成讲稿版和发给主管版两份
#       python3 _scripts/an_弹窗推播汇报_给主管_PPT.py --stats     读回两份已生成的文件，打印各页字数、讲稿、追问、每个文字框放不放得下（不改文件）
#       python3 _scripts/an_弹窗推播汇报_给主管_PPT.py --check     读回两份已生成的文件，逐项判过不过（全过退出码 0）
# 输出：评审版_定稿改_1027/推送系统后台集成需求/弹窗推播汇报_给主管.pptx（讲稿版，备注＝讲稿＋若问）
#       同目录 发给主管版/弹窗推播功能设计汇报.pptx（页面相同，没有备注）
# 渲染只用：zsh _scripts/pl_pptx渲染.sh <pptx> _versions/渲染/弹窗推播汇报_给主管/
# 依据：任务文件旁 2026-11-03_弹窗推播一场汇报_给主管/思考页.md 第 4.0–4.3 节（骨架、构图）、第 10 节（逐字）、审定 1–3。
# 构图从 scratchpad/一场汇报草图/草图.py 扩来（开篇·丙、主界面·丙、第 3 页·乙、第 4、5 页·甲、第 6–8 页）。
# 配色同旧弹窗、推播两份脚本：弹窗蓝 2A63A6/EEF3FA/C9D7EA，推播青 2C7A6B/EAF4F1/C3DDD6；「为什么」沙色；开篇三部分中性灰。
# 文字框边距 0、顶对齐、行距固定磅数：框高＝行数×行距，读回能核装不装得下。文字框命名「容器>名字」的，读回核它在容器里面（不压线）。
# 字串里的 \n 只是手动换行位置（只断在标点后），不算字。
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

# ═════════ 全部文字（照思考页第 10 节逐字，审定 3 改了追问 1、3、5；11/04 讲稿第二轮照第 17 节 17.2、17.4、17.5 和审定 9；按 Z、按注册后、默认合计的作废，见思考页第二级补记 10:28；11/04 审定 10 改 18 处）═════════
TITLES = [
    '序言',
    '目录',
    '弹窗 · 主界面',                      # 第 3–6、8–10 页：「模块 · 界面」导航式（思考页 13.3 开头那行、13.4 第 1 条）
    '弹窗 · 主界面 · 为什么先按人群',
    '弹窗 · 新建界面',
    '弹窗 · 数据界面',
    '过渡',                                # 第 7 页：不画标题（NO_TITLE），这里只留名字
    '推播 · 主界面',
    '推播 · 新建界面',
    '推播 · 数据界面',
]
SPEECH = [
    '推送统一后台把发给玩家的消息放在一个后台里管：游戏内是弹窗和快显，游戏外是推播和短信；数据和查询是四种推送共用的。今天讲其中两块：游戏内的弹窗、游戏外的推播；短信、快显这次不展开。',
    '弹窗是玩家进大厅、破产这些时刻在游戏里弹出来的；推播是发到玩家手机上的通知。两块都分三个界面：主界面列出在用的，总的上限在页顶设；新建界面建一条，定发给谁、什么时候、发什么；数据界面看每一步有多少人，漏掉的人是什么原因。先讲弹窗，再讲推播，中间有一处要请大家定。',
    '先分清两个词：场景是什么时候弹，人群是弹给谁。拿破产举例：「破产时」是场景，玩家破产那一刻当场弹；「近 7 天破产过」是会员标签，用标签圈出来的一群玩家就是人群，可以在别的场景里弹给他们，比如下次进大厅时。先看②，弹窗主界面先按人群排规则：每行一条规则，选一个或几个人群，发全部玩家的那条默认排在最后，拖动排优先级。每行有一列场景，一条规则可选一个或几个，其中首次、第二次登录按当天第一次、第二次登录算。展开一条，看每个场景弹哪些活动或礼包，分固定和轮换，各弹几个，这些在新建时设。最后看顶上①，有几样按场景设，默认所有人群一样。这排是设置入口，不是切换列表的页签：玩家同时符合几条规则时，默认只用排在最前的一条，也可设成每次进入换下一条；大厅每人每天最多弹 8 个，进大厅、首次登录、第二次登录三个场景共用这一个数，破产时不设；两次弹出至少隔 30 分钟；这两个数个别人群可另设。',
    '我们推荐先按人群，理由是更好理解：人群先后只有一份，回流排在全部玩家前面，到哪个场景都一样，不用每个场景再想一遍谁先。先按人群，人群只加一次，每个场景各配弹什么；代价是不同场景不能先弹不同的人群，我们判断这个需要没必要：运营草稿的规则全在进大厅，现在线上跨场景的也只有全部玩家一个人群。先按场景，每个场景各排一份人群先后，比如图上进大厅时回流先弹，破产时全部玩家先弹；代价是一个人群要在几个场景都弹，就得每个场景各建一条，四个场景最多 4 条。每个场景弹什么、上限和间隔，两种一样要设。想请主管和运营同事确认：不同场景让不同人群先弹，实际会有吗？',
    '新建一条弹窗规则分四步。走一个例子：给回流玩家在进大厅时弹回流礼包。第一步，点新建，发送对象选回流人群（后台字段叫群组），场景选进大厅。第二步，每个场景各挑活动或礼包，分固定和轮换两个池子，各设弹几个、各排先后。比如回流玩家进大厅，固定 A、B，默认是 3 个，这里运营改成 2 个，A 是回流礼包；轮换 C、D、E，每次弹 1 个，这是默认。同一个玩家第一次弹 A、B、C，第二次 A、B、D，第三次 A、B、E，第四次又从 C 开始。第三步，回流礼包第一次加进规则时，先配它的弹窗设置：点击跳到礼包页面，进大厅时哪种时机弹，每人每天 2 次；冷却时间是同一个礼包每人两次至少隔多久，默认不限。主界面的间隔管任意两次弹出，冷却只管同一个礼包。这份设置跟着礼包走，别的规则再加它就沿用，改了它，没另设过的规则都跟着变；回流玩家只想每天弹 1 次，就在这条规则里另设。第四步，上架前输入一个回流玩家的会员编号，预览他下次进大厅用哪条规则、弹哪几个。',
    '数据界面看每条规则的四步人数：触发场景、用到这条规则、弹出、点击。用到了却没弹出的人，分四类原因：活动或礼包自己设的时机、次数或冷却不符，场景的上限和间隔到了，固定的弹满了或轮换没轮到，活动或礼包本身弹不了，比如已结束或已关闭。同一个场景里各规则的点击率也能排着比。',
    '弹窗的三个界面讲完了：主界面先按人群、再选场景；新建界面定给谁弹、弹哪些，上架前预览；数据界面看各步人数和没弹原因。到这里大家有没有疑问？没有的话接着讲推播，同样是这三个界面，只是推播不排人群先后，靠每人每天上限和权重管。',
    '推播主界面顶上是两条限制，管这一页所有的营销推播：每位玩家每天最多收 2 条营销推播；营销推播晚上 22 点到早上 8 点不发，定时的推迟到 8 点；条件触发的这次不发，只有活动或礼包开始、结束前后 N 小时这种，由运营每条选推迟还是不发。下面是同一批推播的两种看法：日历看未来 7 天每天发几条、多少人到了上限，上限只按定时算；列表按定时、条件触发分开，定时的每行看预计发出人数，条件触发的看今天发了几条、近 7 天平均每天几条。',
    '新建推播也是四步。走一个例子：秋季排名赛最后一天晚上 7 点，提醒玩家回来冲排名。第一步，类别选营销，所属活动选秋季排名赛；发送对象选人群，营销推播默认排除 VIP 名单，选完马上看到预计人数。第二步，发送方式两种：定时是到点发，条件触发是条件到了才发。这条选定时，填晚上 7 点。第三步，写内容，写好繁中，越南文和英文一键生成。营销推播再设权重，定时、条件触发都有，默认 50：每人每天条数不够时，先留给当天后面权重比它高的定时推播。比如这条权重 50，当晚 8 点半还有一条权重 80 的定时，玩家今天只剩 1 条，就留给那条，这条不发给他。条件触发的也设权重：轮到它发时，同样给后面权重更高的定时让路；但别的推播不为它让路，所以不提前留条数，触发时用剩下的。第四步，发布前看到预计发出多少人，已经扣掉每人每天上限，也看到因为上限收不到的人数。条件触发的要触发了才知道几个人，看近 7 天平均每天发出多少。',
    '推播数据界面看每条推播的四步人数：发出、到达、曝光、点击。到达是推播到了玩家手机，曝光是玩家看见了；到了手机不等于看见，所以这两步分开看。发出这根柱，下面这段才是发出，顶上这截是该发却没发出的，列明原因：玩家正在游戏里、夜间这次不发（推迟到 8 点的算发出）、每人每天上限，其中多少是上限先留给了权重更高的定时推播，还有发送失败；没装 App 或关了通知的也算没发出。以上就是弹窗、推播两块，各三个界面。今天请大家定的就是弹窗主界面那一问：先按人群、再选场景，能不能认可。',
]
# 追问：(挂在第几页的备注, 问, 答)；出处见思考页 10.3、11.6、17.4（出处不进备注）
ASKS = [
    (3, '场景不就是人群标签吗？破产不也是一个标签吗？',
     '不是一回事，但破产确实两样都有。场景管什么时候弹：「破产时」是玩家破产那一刻当场弹；「首次登录」「第二次登录」也是玩家登录的那一刻，都是某个时刻发生的事，不是玩家身上的属性。人群管弹给谁：「近 7 天破产过」是会员标签，用它圈出最近破产过的玩家，在进大厅这类别的场景里弹给他们。Braze、OneSignal、Airship、Firebase 也都把「什么时候弹」和「弹给谁」分开设，Braze 建活动时投放（含触发）和受众是两步。'),
    (3, '弹窗和现在的后台有什么不同？',
     '现在按位置配：我们盘点线上后台记的 5 条规则，3 条发全部玩家（进大厅活动类、进大厅储值类、破产储值类），另 2 条发储值衰退 50% 的普卡、银卡玩家；多条符合时都会触发，实际弹几个看弹出数量、次数和冷却；活动和礼包在每条规则里逐项填弹出时机、形式、次数和冷却（同一项两次至少隔多久）。新的先按人群排规则，每条规则选一个或几个人群，规则里再选场景，同时符合只用排最前的一条；跳转、时机、次数跟着活动或礼包配一份。照运营同事的规则草稿，13 条规则里活动和礼包共出现 43 次，按活动配只要 14 份，另有 5 处按规则另设。'),
    (3, '同时符合几条，为什么只用一条、不叠加？',
     '同时符合很常见：8 月 16 日到 9 月 16 日登录的 62,292 人里，新增 10,749 人、回流 16,564 人，两者合计 27,313 人，占 62,292 人的约 44%；按运营同事草稿的分群，他们既在会员卡等级群，又在新玩家群或回流群（推算）。叠加的话，这些人每次进场景几条规则都会触发。Braze、MoEngage 同时符合也只出一个。场景设置里也能设成每次轮流用下一条。'),
    (3, '每天 8 个、间隔 30 分钟凭什么？',
     '两样都是起始值，可改，留空就不限，个别人群可另设。8 个取自早先草图里的示例值，没有数据依据；30 分钟取自运营同事规则草稿总规则「弹出间隔 1800 秒，破产礼包/发财金除外」。MoEngage 能按天设应用内消息上限，另有不分活动的最小间隔。'),
    (4, '行业怎么做？',
     'Braze 把受众和触发平铺在一条消息上，用一份拖动排序的优先级，同时符合只出最高一条。'),
    (6, '场景管什么时候弹，活动或礼包怎么还有弹出时机？',
     '场景定在哪一刻看规则。进大厅这个场景，玩家可能是重新登录进来，也可能是从游戏返回；活动或礼包的弹出时机只在进大厅有，是在这个场景里再挑它在哪种进大厅时弹，比如礼包默认只在从游戏返回时弹。其他场景没有这一项。'),
    (8, '推播和现在比差在哪？',
     '运营现在的推播后台能发全部玩家、上传名单或按标签圈的人群，但发给多少人要另找人查；游戏服务器按活动自动发 34 种推播，条件和文案写在服务器代码里，运营改不了；报表的列是「傳送」「曝光」「開啟」，没有到达，要拿推播编号去 Firebase 后台对照；运营规范每天不超过两条，后台限不了。夜里：规定晚上 10 点到早上 8 点不发推播，活动提醒落在这段就不提醒；但出过故障，玩家晚上 11 点还收到推播。'),
    (10, '到达率怎么算？iOS 为什么要上报？',
     '到达率＝到达 ÷ 能确认到达的发出，点击率＝点击 ÷ 发出。iOS 只告诉我们推送被受理，到没到手机要游戏 App 上报；没上报的版本显示「未接入」，不算进到达率的分母。Android 靠推送服务的回执，看得到，可能偏低。'),
    (10, '曝光怎么算？',
     '通知在玩家手机上显示出来算一次，Android 来自 Firebase 的 Impressions，玩家在游戏里收到的不算。短信没有这一步。'),
]

BANNED = ['回到第', '见第', '见附录', '细节见', '→ 第', '下一页', '上一页', '翻到', '点此', 'EP']
BODY_MAX, TITLE_MAX, LEAD_MAX, SPEECH_TOTAL_MAX, ASK_N, PAGES_N = 300, 12, 15, 2400, 9, 10   # 标题 ≤12 字（第 15 条③）；追问 9 条；10 页（卡上第 1 项：开场两页 → 弹窗三页 → 过渡一页 → 推播三页）
NO_TITLE = (1, 2, 7)   # 开场两页和过渡页不画标题（卡上完成标准第 1、2 项；TITLES 里照样留名字）
FILE_TITLE = '弹窗推播功能设计汇报'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, '评审版_定稿改_1027', '推送系统后台集成需求')
OUT_NOTES = os.path.join(OUT_DIR, '弹窗推播汇报_给主管.pptx')
OUT_SENT = os.path.join(OUT_DIR, '发给主管版', '弹窗推播功能设计汇报.pptx')
FONT = 'Microsoft YaHei'

WHITE = 'FFFFFF'; NAVY = '1F2A44'; SUB = '5B6272'; MUTE = '9A9FA8'; LINE = 'E2DED5'
BLUE, BLUE_T, BLUE_B = '2A63A6', 'EEF3FA', 'C9D7EA'       # 弹窗
TEAL, TEAL_T, TEAL_B = '2C7A6B', 'EAF4F1', 'C3DDD6'       # 推播
MOD_COL = {'弹窗': BLUE, '推播': TEAL}   # 内容页标题里的模块词用模块色（卡上第 1 项，第一级定）
SAND, SAND_T, SAND_B = '8A6D3B', 'F7F2E8', 'E3D7BF'       # 为什么（两种分法都不占模块色）
GRAY_T, GRAY_B, BAR = 'F4F5F7', 'D9DEE6', 'D9DEE6'        # 开篇三部分（两块共用）；示意行里的浅灰条
ROW_T = {BLUE: 'F8FAFD', TEAL: 'F7FBFA'}
SEQ = {BLUE: '8EA9CF', TEAL: '86B5A9'}                    # 漏斗旁表先后的竖箭头（比卡边深，比主色浅）
L, C, R = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE

SLIDE_W, SLIDE_H = 13.333, 7.5
X0, X1 = 0.5, 12.833
# 字号和固定行距（磅）
T22, T26, T20, T18, T16, T15, T14, T12, T11, T10 = (22, 30), (26, 34), (20, 28), (18, 25), (16, 23), (15, 21), (14, 20), (12, 18), (11, 16), (10, 14)
T28 = (28, 38)                                  # 标题（第五批，思考页第 15 节：标题升 28 磅粗）
T40 = (40, 52)                                  # 过渡页大字（第六批，全场只这一处：换块要一眼看出）
TITLE_Y, TITLE_H = 0.30, 38 / 72                # 标题框：顶 0.30，高一行 T28，底约 0.83
LEAD_Y = 0.92                                   # 带头句（T22 粗 NAVY）紧贴标题下的顶边；高一行 30/72，底约 1.34


# ═════════ 画图小工具 ═════════
def rgb(h):
    return RGBColor.from_string(h)


def font(run, size, color, bold=False):
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = rgb(color)
    rpr = run._r.get_or_add_rPr()
    rpr.set('lang', 'zh-CN'); rpr.set('altLang', 'en-US')
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {}); rpr.append(el)
        el.set('typeface', FONT)


def nl(t):
    return t.count('\n') + 1


def text(s, name, x, y, w, t, sp, color, bold=False, align=L, anchor=TOP, h=None):
    """一个文字框：一段，行距固定；框高默认＝行数×行距。sp＝(字号, 行距磅)。"""
    size, pitch = sp
    h = h if h is not None else nl(t) * pitch / 72
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align; p.line_spacing = Pt(pitch)
    for k, part in enumerate(t.split('\n')):
        if k:
            p.add_line_break()
        r = p.add_run(); r.text = part; font(r, size, color, bold)
    return tb


def no_effect(sp):
    sp._element.spPr.append(sp._element.spPr.makeelement(qn('a:effectLst'), {}))


def shape(s, name, kind, x, y, w, h, fill, line=None, lw=0.75, dash=False):
    sp = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.name = name
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    if line:
        sp.line.color.rgb = rgb(line); sp.line.width = Pt(lw)
        if dash:
            ln = sp.line._get_or_add_ln(); ln.append(ln.makeelement(qn('a:prstDash'), {'val': 'dash'}))
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sp.adjustments[0] = 0.05
    return sp                                  # shadow.inherit=False 已经写了空的 effectLst，不再另加（重复会让 PowerPoint 打不开）


def box(s, name, x, y, w, h, fill, line=None, lw=0.75, dash=False, rect=False):
    return shape(s, name, MSO_SHAPE.RECTANGLE if rect else MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, lw, dash)


def connector(s, name, x1, y1, x2, y2, color, width, head=False, dash=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb = rgb(color); c.line.width = Pt(width)
    if dash:
        ln = c.line._get_or_add_ln(); ln.append(ln.makeelement(qn('a:prstDash'), {'val': 'dash'}))
    if head:
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    no_effect(c)
    return c


def bars(s, name, x, y, ws, step=0.22, hh=0.08):
    for k, w in enumerate(ws):
        box(s, '%s条%d' % (name, k + 1), x, y + k * step, w, hh, BAR, rect=True)


def circle_no(s, name, x, y, n, col, d=0.38):
    shape(s, name, MSO_SHAPE.OVAL, x, y, d, d, col)
    text(s, name + '>号', x, y + (d - 16 / 72) / 2, d, str(n), (12, 16), WHITE, True, C)


def tag(s, name, x, y, w, t, col):
    """块右上角的标签：白底、主色边、主色粗字（完成标准第 14 条：场景／人群各管什么）。"""
    box(s, name, x, y, w, 0.32, WHITE, line=col, lw=1)
    text(s, name + '>名', x, y + (0.32 - 18 / 72) / 2, w, t, T12, col, True, C)


def arrow(s, name, kind, x, y, w, h, color, rot=0):
    sp = shape(s, name, kind, x, y, w, h, color)
    sp.rotation = rot
    return sp


def title_parts(t):
    """标题拆成几段：「弹窗」「推播」模块色，其余 NAVY，全粗（交给 runs_text，一个文字框多个 run）。"""
    return [(x, MOD_COL.get(x, NAVY), True) for x in re.split('(弹窗|推播)', t) if x]


def page(prs, no, sent):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(WHITE)
    if no not in NO_TITLE:
        runs_text(s, '标题', X0, TITLE_Y, X1 - X0, title_parts(TITLES[no - 1]), T28, align=L)   # 标题 T28 粗（第五批），框高＝一行 T28＝TITLE_H；标题带下不画线（参考版式「三」）
    text(s, '页码', 12.43, 7.02, 0.40, str(no), T10, MUTE, align=R)
    if not sent:
        parts = [SPEECH[no - 1]] + ['\n若问：%s\n答：%s' % (q, a) for p, q, a in ASKS if p == no]
        s.notes_slide.notes_text_frame.text = '\n'.join(parts).strip()
    return s


# ═════════ 第 1 页：只做一件事——今天讲弹窗、推播两块（完成标准第 1 项；17:21 起推送统一后台、游戏内外、快显、短信、数据、查询都不上页面，讲稿口头带过）═════════
# 不画标题，带头句占标题的位置（同第 2 页：T22 粗 NAVY，第 2 页不动）。第五批（18:44【第 1 页】）：两块缩成中等大小的两张卡，左右并排（左弹窗、右推播，接第 2 页 ①②），
# 卡＋卡下灰字一组在内容区（1.05–6.85）里上下居中。主＝两张卡（模块浅底＋模块色 2.25 磅粗边、T28 粗模块色，全页唯一一组框）；
# 辅＝卡下一行灰字（T14 SUB）说这块是什么，用词核功能框架：弹窗属「游戏内推送」、场景是进大厅、破产时等玩家在游戏里的时刻（框架 155–160 行）；
# 推播属「游戏外推送」（框架第 2 行），推播也能设「玩家正在游戏里时：发」（框架 62–64 行），所以不写「玩家不在游戏里时」，照第 2 页讲稿写「发到玩家手机上的通知」。
def p0(s):
    text(s, '序言带头句', X0, 0.30, X1 - X0, '今天讲弹窗、推播两块', T22, NAVY, True, anchor=MID, h=0.44)
    CW, CH, GAP, SG, NH, SH = 4.20, 2.10, 0.80, 0.16, 38 / 72, 20 / 72
    gx = (SLIDE_W - 2 * CW - GAP) / 2
    gy = (1.05 + 6.85) / 2 - (CH + SG + SH) / 2
    for k, (nm, sub, col, tint) in enumerate([('弹窗', '玩家在游戏里时弹出', BLUE, BLUE_T), ('推播', '发到玩家手机上的通知', TEAL, TEAL_T)]):
        x = gx + k * (CW + GAP); c = '块%d' % (k + 1)
        box(s, c, x, gy, CW, CH, tint, line=col, lw=2.25)
        text(s, c + '>名', x, gy + (CH - NH) / 2, CW, nm, T28, col, True, C)
        text(s, c + '说明', x, gy + CH + SG, CW, sub, T14, SUB, align=C)


# ═════════ 第 2 页 目录（参考版式「二」借 P4＋P5）：上行弹窗、推播两块左右对半；下行三个界面三等分大块（各 4 栏），SEQ 箭头串起先后（第 12 条）═════════
# 三层（第 18 条，scratchpad 批2_三层_第1_2页.md）：主＝三个界面一行（全页唯一一组带粗边的块：白底 NAVY 1.5 磅，名字 T18 粗 NAVY，SEQ 箭头串起）；
# 次＝① 弹窗、② 推播（T14 常规模块色，不加框，只靠左右对半的位置并排）和三个界面各自那句（T14 NAVY）；辅＝游戏内、游戏外（T12 SUB），界面块里不带字的简化示意（浅灰底、灰条，不画边）。
# 两行的关系由带头句「两块都分三个界面」说，放在三界面行正上方（亲近），不画连线。示意：主界面＝页签加列表，新建界面＝表单，数据界面＝四根等差变矮的柱（审定 5）。
def p1(s):
    P, GAP, LH, BH, AH = 0.20, 0.25, 25 / 72, 20 / 72, 18 / 72
    text(s, '三部分带头句', X0, 0.30, X1 - X0, '两块都分三个界面', T22, NAVY, True, anchor=MID, h=0.44)   # 不画标题，带头句占标题位置
    TY, TH = 1.05, P + BH + P                                  # 两块名画进同一个块（17:22）：浅灰底、不画边，横跨三张卡，紧贴在卡上方
    box(s, '两块', X0, TY, X1 - X0, TH, GRAY_T, rect=True)
    for k, (nm, sub, col) in enumerate([('① 弹窗', '游戏内', BLUE), ('② 推播', '游戏外', TEAL)]):
        x = X0 + P + k * 2.40
        text(s, '两块>名%d' % (k + 1), x, TY + P, 0.85, nm, T14, col, True)            # 次：T14 粗，模块色接上第 1 页两块
        text(s, '两块>内外%d' % (k + 1), x + 0.85, TY + P + (BH - AH), 0.80, sub, T12, SUB)
    cy = TY + TH + GAP; ch = 6.85 - cy; cw = 3.944             # 三等分 4×3（卡的画法、箭头、示意都不动）
    for k, (nm, mean) in enumerate([('主界面', '看正在用的，管每天上限'), ('新建界面', '配置发给谁、什么时候发、发什么'),
                                    ('数据界面', '看各环节人数，查没发出去的原因')]):   # 措辞借 Dk 给的版本二（措辞参考_Dk给的两版_1103.md）
        x = (0.500, 4.694, 8.889)[k]; c = '部分%d' % (k + 1)
        box(s, c, x, cy, cw, ch, WHITE, line=NAVY, lw=2.25)
        text(s, c + '>名', x + P, cy + P, cw - 2 * P, nm, T18, NAVY, True)
        text(s, c + '>意思', x + P, cy + P + LH + 0.10, cw - 2 * P, mean, T14, NAVY)
        mx, my = x + P, cy + P + LH + 0.10 + BH + 0.30; mw = cw - 2 * P; mh = cy + ch - P - my
        m = c + '示意'
        box(s, m, mx, my, mw, mh, GRAY_T, rect=True)            # 辅：浅灰底、不画边
        ix, iw = mx + 0.22, mw - 0.44                          # 示意里的内边
        top = my + 0.62; rh = 0.34; st = (my + mh - 0.22 - top - rh) / 3          # 四行（或四柱）占的那一截
        if k == 0:                                             # 主界面：页签一排，下面列表四行
            for t in range(4):
                box(s, '%s页签%d' % (m, t + 1), ix + t * 0.72, my + 0.22, 0.62, 0.20, BAR, rect=True)
            for j, w in enumerate([1.50, 1.10, 1.30, 0.90]):
                ry = top + j * st
                box(s, '%s行%d' % (m, j + 1), ix, ry, iw, rh, WHITE, rect=True)
                box(s, '%s行%d条' % (m, j + 1), ix + 0.15, ry + (rh - 0.08) / 2, w, 0.08, BAR, rect=True)
                box(s, '%s行%d尾' % (m, j + 1), ix + iw - 0.65, ry + (rh - 0.08) / 2, 0.50, 0.08, BAR, rect=True)
        elif k == 1:                                           # 新建界面：表头一条，下面四行字段
            box(s, m + '表头', ix, my + 0.26, 1.20, 0.12, BAR, rect=True)
            for j in range(4):
                ry = top + j * st
                box(s, '%s字段%d名' % (m, j + 1), ix, ry + (rh - 0.08) / 2, 0.70, 0.08, BAR, rect=True)
                box(s, '%s字段%d框' % (m, j + 1), ix + 0.90, ry, iw - 0.90, rh, WHITE, rect=True)
        else:                                                  # 数据界面：表头一条，下面四根柱等差变矮（示意，不是真数据）
            box(s, m + '表头', ix, my + 0.26, 1.20, 0.12, BAR, rect=True)
            yb = my + mh - 0.22; hh = yb - top; bw = 0.42; bg = (iw - 4 * bw) / 3
            for j in range(4):
                h = hh * (1 - 0.2 * j)
                box(s, '%s柱%d' % (m, j + 1), ix + j * (bw + bg), yb - h, bw, h, BAR, rect=True)
        if k < 2:                                              # 先后：主界面 → 新建界面 → 数据界面（两块共用，箭头用中性 SUB）
            arrow(s, '先后%d' % (k + 1), MSO_SHAPE.RIGHT_ARROW, x + cw + 0.02, cy + ch / 2 - 0.15, 0.21, 0.30, SUB)


# ═════════ 第 3、8 页 主界面：参考版式「二」第 3、7 页（借 W4 线稿示意＋W1 编号＋P3 反例），第 18 条分主次 ═════════
# 主＝左 7 栏一张简化界面示意（灰条代行，不放截图，判例 52）：全页唯一粗边（模块色 2.25 磅外框），面积最大；
#     示意里不再套框，分区靠浅底色块（无边）和浅分隔线，同粗细的框只剩标签那一组。
# 次＝右 5 栏编号标注的带头句（T14 NAVY 粗）；辅＝标注句（T12 SUB），都不加框。
# 编号圆白底、模块色描边、模块色数字：示意左侧一列和右栏一列同号同高（两边对位）。两页同版式，只换模块色。
MV_X, MV_W, NT_X = 0.500, 7.090, 7.840          # 左 7 栏起点、宽；右 5 栏起点（参考版式「三」7／5）
MV_A, MV_B = 1.15, 7.39                         # 示意里分区左右边（左边留一列编号圆）
MV_L, MV_R = 1.30, 7.24                         # 分区里内容左右边
MV_D = 0.32                                     # 编号圆直径


def mv_ring(s, name, x, cy, n, col):
    shape(s, name, MSO_SHAPE.OVAL, x, cy - MV_D / 2, MV_D, MV_D, WHITE, line=col, lw=1.25)
    text(s, name + '>号', x, cy - 18 / 72 / 2, MV_D, str(n), T12, col, True, C)


def mv_notes(s, col, items, hi=None):
    """右栏编号标注：items＝[(对位高度, 带头句, [标注句…])]；示意左侧同号圆和它同高。hi＝用模块色的编号（其余编号圈灰，同第 3 页）；不给＝全用模块色。"""
    tx = NT_X + MV_D + 0.18
    for k, (cy, lead, anns) in enumerate(items, start=1):
        rc = col if hi is None or k in hi else SUB
        mv_ring(s, '示意号%d' % k, MV_X + 0.19, cy, k, rc)
        mv_ring(s, '标注号%d' % k, NT_X, cy, k, rc)
        y = cy - 25 / 72 / 2
        text(s, '标注%d带头句' % k, tx, y, X1 - tx, lead, T18, NAVY)      # 次：右侧说明 T18 NAVY 常规（第五批全场统一）
        y += 25 / 72 + 0.06
        for j, a in enumerate(anns, start=1):
            text(s, '标注%d句%d' % (k, j), tx, y, X1 - tx, a, T14, SUB)   # 辅：灰字 T14 SUB（第五批全场统一）
            y += 20 / 72


# 第 3 页 弹窗主界面（第六批，第一级 11/04 09:49【第 3 页】，推荐改先按人群）：带头句 T22 粗 NAVY 紧贴标题下（LEAD_Y）；示意从 1.55 起到内容区底。
# 主＝示意里的人群规则表，只这里用模块色：浅蓝底带＋两个模块色实底标签（人群：弹给谁、场景：什么时候弹，T14 白粗）；每行一条规则（第一级 11/04 09:59：一条规则可选一个或几个人群，同第 5 页、框架），拖动排先后；每行「场景」一列，一条规则可选几个场景
#     （回流：进大厅、破产时，同第 4 页例子；新增玩家：进大厅；全部玩家：进大厅、破产时。第一级 11/04）。② 编号对第 1 行，③ 编号仍对第 3 行（不动）。
# 辅＝① 原页签位置改成场景设置入口，灰底（上限和间隔按场景设，不属于哪一群：2026-11-02_场景在外还是人群在外_给主管/思考页_退回重搭.md 第 25 行）；④ 展开一条，灰底：一个人群展开成它选的两个场景，每个场景两行（固定、轮换），内容只画灰块和灰条（第一级 11/04 10:06）。①④ 编号圈灰，②③ 模块色。
# 规则的「场景」列、一条规则选几个场景、场景设置入口，功能框架还没跟上（框架仍是按场景分页签），以 Dk 11/04 09:4x 为准，框架另说。
def p2(s):
    col = BLUE
    text(s, '主界面带头句', X0, LEAD_Y, X1 - X0, '先按人群排规则，规则里再选场景', T22, NAVY, True)
    FY, FB, TW, TH_ = 1.55, 6.85, 1.80, 0.34                             # 示意上下沿；两个实底标签宽、高
    box(s, '示意', MV_X, FY, MV_W, FB - FY, WHITE, line=GRAY_B, lw=1.0)
    ty, th = 1.71, 0.46                                                    # ① 场景设置入口：原页签位置，灰底
    box(s, '设置入口行', MV_A, ty, MV_B - MV_A, th, GRAY_T, rect=True)
    box(s, '设置入口', MV_L, ty + (th - TH_) / 2, TW, TH_, WHITE, line=GRAY_B, lw=0.75)
    text(s, '设置入口>名', MV_L, ty + (th - 20 / 72) / 2, TW, '场景设置 ›', T14, NAVY, True, C)
    SX = MV_L + TW + 0.15                                                  # 场景名、场景列的左沿
    x = SX
    for k, t in enumerate(['进大厅', '破产时', '首次登录', '第二次登录']):
        w = em(t) * 14 / 72 + 0.20
        text(s, '入口场景%d' % (k + 1), x, ty + (th - 20 / 72) / 2, w, t, T14, SUB, False, C)
        x += w + 0.06
    hy, hh, rh = 2.33, 0.46, 0.70                                          # ②③ 人群规则表：列头＋三行，整段浅蓝底带
    ry = hy + hh; rb = ry + 3 * rh
    cols = [(5.55, 0.55), (6.35, 0.80)]                                    # 其余列（人数、状态）只画灰条
    box(s, '规则行', MV_A, hy, MV_B - MV_A, rb - hy, BLUE_T, rect=True)
    for nm, lx, t in (('人群标签', MV_L, '人群：弹给谁'), ('场景标签', SX, '场景：什么时候弹')):
        box(s, nm, lx, hy + (hh - TH_) / 2, TW, TH_, col)
        text(s, nm + '>名', lx, hy + (hh - 20 / 72) / 2, TW, t, T14, WHITE, True, C)
    for j, (cx, cw) in enumerate(cols):
        bars(s, '列头%d' % (j + 1), cx, hy + (hh - 0.08) / 2, [cw * 0.6])
    connector(s, '列头线', MV_A, ry, MV_B, ry, BLUE_B, 0.75)
    for k, (t, scenes) in enumerate([('回流', ['进大厅', '破产时']), ('新增玩家', ['进大厅']), ('全部玩家', ['进大厅', '破产时'])]):
        y = ry + k * rh; c = '人群行%d' % (k + 1)
        text(s, c + '拖', 1.38, y + (rh - 20 / 72) / 2, 0.22, '⠿', T14, MUTE)
        text(s, c + '序', 1.62, y + (rh - 20 / 72) / 2, 0.22, str(k + 1), T14, SUB)
        text(s, c + '名', 1.92, y + (rh - 23 / 72) / 2, 1.20, t, T16, NAVY, True)
        cx = SX
        for j, sc in enumerate(scenes):
            w = em(sc) * 14 / 72 + 0.24; cn = '%s场景%d' % (c, j + 1)
            box(s, cn, cx, y + (rh - 0.36) / 2, w, 0.36, WHITE, line=BLUE_B, lw=0.75)
            text(s, cn + '>名', cx, y + (rh - 20 / 72) / 2, w, sc, T14, NAVY, False, C)
            cx += w + 0.08
        for j, (bx, bw) in enumerate(cols):
            bars(s, '%s格%d' % (c, j + 1), bx, y + (rh - 0.08) / 2, [bw])
        if k < 2:
            connector(s, c + '线', MV_A, y + rh, MV_B, y + rh, BLUE_B, 0.75)
    ey = 6.65                                                              # ④ 第 3 行展开：灰底，紧接规则行下
    box(s, '展开一条', MV_A, rb, MV_B - MV_A, ey - rb, GRAY_T, rect=True)
    PR, PG, CX, IX = 0.38, 0.12, 1.92, SX + 0.58                           # 池子行高；两个场景之间的空；场景块左沿（同人群名）；内容左沿（池子名左沿同场景列）
    et = rb + (ey - rb - (4 * PR + PG)) / 2
    for i, (sc, pools) in enumerate([('进大厅', ((0.62, 0.50), (0.50, 0.62, 0.44))), ('破产时', ((0.56,), (0.44, 0.60)))]):
        gy = et + i * (2 * PR + PG); c = '展开场景%d' % (i + 1)
        w = em(sc) * 14 / 72 + 0.24
        box(s, c, CX, gy + PR - 0.18, w, 0.36, WHITE, line=GRAY_B, lw=0.75)
        text(s, c + '>名', CX, gy + PR - 20 / 72 / 2, w, sc, T14, NAVY, False, C)
        for j, (pn, ws) in enumerate(zip(('固定', '轮换'), pools)):
            py = gy + j * PR; n = '%s池%d' % (c, j + 1)
            text(s, n + '名', SX, py + (PR - 20 / 72) / 2, 0.50, pn, T14, NAVY)
            bx = IX
            for k, bw in enumerate(ws):                                    # 不填具体内容：同原来的明细行，一个灰块加一根灰条
                box(s, '%s项%d图' % (n, k + 1), bx, py + (PR - 0.20) / 2, 0.20, 0.20, BAR, rect=True)
                bars(s, '%s项%d' % (n, k + 1), bx + 0.27, py + (PR - 0.08) / 2, [bw])
                bx += 0.27 + bw + 0.20
        if i == 0:
            connector(s, '展开场景线', MV_L, gy + 2 * PR + PG / 2, MV_R, gy + 2 * PR + PG / 2, GRAY_B, 0.75)
    tx = NT_X + MV_D + 0.12                                                # 右栏编号标注：同 mv_notes 的字号，只是 ①④ 编号圈用灰；圈和字的空比 mv_notes 少 0.06，① 18 字（估宽 4.50）才不折行
    for k, (cy, lead, anns) in enumerate([
            (ty + th / 2, '上限和间隔按场景设，人群默认一样', ['大厅每人每天最多弹 8 个', '两次弹出至少隔 30 分钟']),
            (ry + rh / 2, '每行一条规则，拖动排先后', []),
            (ry + 2.5 * rh, '一条规则可选几个场景', []),
            ((rb + ey) / 2, '展开看每个场景的固定和轮换', [])], start=1):
        rc = col if k in (2, 3) else SUB
        mv_ring(s, '示意号%d' % k, MV_X + 0.19, cy, k, rc)
        mv_ring(s, '标注号%d' % k, NT_X, cy, k, rc)
        y = cy - 25 / 72 / 2
        text(s, '标注%d带头句' % k, tx, y, X1 - tx, lead, T18, NAVY)
        y += 25 / 72 + 0.06
        for j, a in enumerate(anns, start=1):
            text(s, '标注%d句%d' % (k, j), tx, y, X1 - tx, a, T14, SUB)
            y += 20 / 72


# ═════════ 第 4 页 弹窗 · 主界面 · 为什么先按人群（第六批，第一级 11/04 09:49【第 4 页】、完成标准第 11、14 项）═════════
# 同一个例子在两种做法下各画一个小示意，左右并排；比较的字（两行代价）不改，只是推荐换了边。
# 主＝左「先按人群」＋小标「推荐」：浅蓝底＋弹窗蓝 2.25 磅粗边；人群在上（回流 → 新增玩家 → 全部玩家，一份顺序，弹窗蓝实底），场景挂在每个人群下面
#     （审定 10 第 12 条：回流：进大厅、破产时；新增玩家：进大厅；全部玩家：进大厅、破产时），挂线不带箭头头。次＝右「先按场景」：白底灰细边，两个页签各排各的（进大厅回流在前；破产时全部玩家在前、回流在后，两个场景先后不同，左图做不到），只用灰。
# 辅＝两边各一行代价（T14 SUB）。箭头只表先后。只用弹窗蓝和灰。「多条规则都符合时只用排在最前的一条」不上页面（卡上 D）。
def p3(s):
    col = BLUE
    text(s, '先后带头句', X0, LEAD_Y, X1 - X0, '先按人群，更好理解', T22, NAVY, True)
    CW, GAP, PAD, IP = 6.042, 0.25, 0.30, 0.28              # 两等分卡宽、卡距、卡内左右边距、卡内上下留白
    Y1, Y2 = 1.55, 6.85
    LH, SH = 25 / 72, 20 / 72                               # T18、T14 一行高
    PH, CH, AW = 1.55, 0.52, 0.40                           # 页签小示意高、人群块高、先后箭头长
    g = (Y2 - Y1 - 2 * IP - LH - 2 * PH - SH) / 3           # 名字、两个小示意、代价之间三段等距
    yh = Y1 + IP; ya = yh + LH + g; yb = ya + PH + g; yc = yb + PH + g
    PW = CW - 2 * PAD
    ORDER = ['回流', '新增玩家', '全部玩家']

    for k, (name, cost) in enumerate([('先按人群', '代价：不同场景不能先弹不同人群'),
                                      ('先按场景', '代价：几个场景都弹的人群要逐个场景建')]):
        x = X0 + k * (CW + GAP); c = '做法%d' % (k + 1); main = k == 0
        box(s, c, x, Y1, CW, Y2 - Y1, BLUE_T if main else WHITE, line=col if main else GRAY_B, lw=2.25 if main else 0.75)
        text(s, c + '>名', x + PAD, yh, PW, name, T18, col if main else NAVY, True)
        text(s, c + '>代价', x + PAD, yc, PW, cost, T14, SUB)
    rx0 = X0 + PAD + em('先按人群') * 18 / 72 + 0.14        # 小标「推荐」：紧跟左卡的名字
    box(s, '推荐', rx0, yh + (LH - 0.30) / 2, 0.62, 0.30, col)
    text(s, '推荐>名', rx0, yh + (LH - SH) / 2, 0.62, '推荐', T14, WHITE, True, C)

    px, ph = X0 + PAD, yb + PH - ya                         # 左：人群在上一份顺序，场景挂在每个人群下面
    box(s, '人群图', px, ya, PW, ph, WHITE, line=BLUE_B, lw=0.75)
    NH, CHIP, STEM, CG, CAPG, LAW = 0.56, 0.46, 0.40, 0.12, 0.10, 0.30   # 人群块高、场景块高、挂线长、场景块间距、小字到人群块、箭头长
    top = ya + (ph - (SH + CAPG + NH + STEM + 2 * CHIP + CG)) / 2
    ny = top + SH + CAPG; sy = ny + NH + STEM
    x = px + 0.64
    text(s, '人群图>顺序', x, top, 1.20, '一份顺序', T14, SUB)
    text(s, '人群图>人群', px + 0.15, ny + (NH - SH) / 2, 0.42, '人群', T14, SUB)
    text(s, '人群图>场景', px + 0.15, sy + (CHIP - SH) / 2, 0.42, '场景', T14, SUB)
    for j, (nm, scenes) in enumerate([('回流', ['进大厅', '破产时']), ('新增玩家', ['进大厅']), ('全部玩家', ['进大厅', '破产时'])]):
        w = em(nm) * 18 / 72 + 0.40; c = '人群块%d' % (j + 1); mid = x + w / 2
        box(s, c, x, ny, w, NH, col)
        text(s, c + '>名', x, ny + (NH - LH) / 2, w, nm, T18, WHITE, True, C)
        connector(s, c + '挂线', mid, ny + NH, mid, sy + (len(scenes) - 1) * (CHIP + CG), SEQ[col], 1.0)
        for i, sc in enumerate(scenes):
            cn = '%s场景%d' % (c, i + 1); cy = sy + i * (CHIP + CG)
            box(s, cn, mid - 0.45, cy, 0.90, CHIP, WHITE, line=BLUE_B, lw=0.75)
            text(s, cn + '>名', mid - 0.45, cy + (CHIP - 23 / 72) / 2, 0.90, sc, T16, NAVY, False, C)
        x += w
        if j < 2:
            connector(s, c + '箭头', x + 0.08, ny + NH / 2, x + 0.08 + LAW, ny + NH / 2, SEQ[col], 1.5, head=True)
            x += LAW + 0.16

    rx = X0 + CW + GAP + PAD                                # 右：两个页签，各排各的，只用灰
    for j, (scene, order) in enumerate([('进大厅', ORDER), ('破产时', ['全部玩家', '回流'])]):
        py = (ya, yb)[j]; p = '页签%d' % (j + 1)
        box(s, p, rx, py, PW, PH, WHITE, line=GRAY_B, lw=0.75)
        tw = em(scene) * 16 / 72 + 0.30
        text(s, p + '>名', rx + 0.20, py + 0.12, tw, scene, T16, SUB, True, C)
        box(s, p + '选中', rx + 0.20, py + 0.53, tw, 0.05, MUTE, rect=True)
        connector(s, p + '线', rx, py + 0.58, rx + PW, py + 0.58, GRAY_B, 0.75)
        cx, cy = rx + 0.25, py + 0.58 + (PH - 0.58) / 2
        for i, nm in enumerate(order):
            w = em(nm) * 18 / 72 + 0.40; b = '%s人群%d' % (p, i + 1)
            box(s, b, cx, cy - CH / 2, w, CH, WHITE, line=GRAY_B, lw=1.0)
            text(s, b + '>名', cx, cy - LH / 2, w, nm, T18, NAVY, False, C)
            cx += w
            if i < len(order) - 1:
                connector(s, '%s箭头%d' % (p, i + 1), cx + 0.08, cy, cx + 0.08 + AW, cy, MUTE, 1.5, head=True)
                cx += AW + 0.16


# ═════════ 第 5、9 页 新建界面：流程图（完成标准第 3、4 项）═════════
# 竖排四个节点（左 5 栏）＝运营建一条要走的每一步，节点只写这一步做什么；主线只有一条 SEQ 实线箭头，从上往下。
# 批 4（思考页审定 7 第 3 条）：选择不再画成两步之间的分叉，改成挂在那一步节点上的两个并列选项——节点下面接一块浅底托（模块浅色），
#   托里两个白底选项并排，选项名模块色粗；主线箭头从托底出来。右边两列并成一整栏，一句一行、不拆句，句间距放松（SG），
#   每步一块和节点上下居中。左右留白匀（第二级 17:5x）：句子栏宽＝这页最长一行的估宽，栏右沿收到右边距，节点加宽到句子栏左边一个栏距。
# 三层：主＝节点和箭头（模块色实底、T18 白粗，全页唯一一组实底框）；次＝页顶带头句、选项、右边句子（T14 NAVY）；
#   辅＝句子下面的灰字（T12 SUB，不加框；第 8 页权重那行，审定 7 第 4 条）。两页同一画法，只换模块色。
# 第五批（第一级 11/03 18:44【第 5、8 页】、完成标准第 14 项）：主＝页顶带头句（T22 粗 NAVY，紧贴标题下，说运营建一条最要紧的那一点）。
#   节点改成模块浅底＋模块色细边（不再实底），左边白底模块色细圈编号，宽收到 4 英寸，节点句 T18 粗 NAVY、动作开头；
#   挂在节点上的选项照留，并进节点卡下半，白底细边，一项一行（T18，名模块色粗）；右边说明放大到 T18 NAVY，灰字 T14 SUB；
#   箭头沿编号圈中线从上一卡底到下一卡顶。两页同一画法，只换模块色。
TINT = {BLUE: BLUE_T, TEAL: TEAL_T}; EDGE = {BLUE: BLUE_B, TEAL: TEAL_B}


def runs_text(s, name, x, y, w, parts, sp, align=C):
    """一个一行的文字框，几段不同颜色、粗细：parts＝[(字, 颜色, 粗)]；框高＝一行行距。"""
    size, pitch = sp
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(pitch / 72))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = TOP
    p = tf.paragraphs[0]; p.alignment = align; p.line_spacing = Pt(pitch)
    for t, colr, b in parts:
        r = p.add_run(); r.text = t; font(r, size, colr, b)
    return tb


def steps(s, top, items, col, opts, hi, NW=4.0, BG=0.30):
    """items＝[(节点句, [句…])]，一句一行；句写成 ('灰', 字) 的画成辅，紧贴上一句；opts＝(挂在第几步，从 0 数, 选项, 选项)，选项「名：说明」的名用模块色粗；
    hi＝带头句讲的那一步（从 0 数）：这一步的节点是全页唯一的模块色实底、白字，其余节点浅底细边（第一级 11/03 18:54）。
    NW＝节点卡宽；BG＝上下两块说明的最小间隔（第 5 页第 2 步节点句长、说明三行，单独给；第 9 页用默认）。"""
    text(s, '新建带头句', X0, LEAD_Y, X1 - X0, top, T22, NAVY, True)    # 主：T22 粗 NAVY，紧贴标题下
    H, GAP = 0.62, 0.60                                             # 节点行高；卡和右边说明之间的空
    SW = max(em(t[1]) * 14 / 72 if isinstance(t, tuple) else em(t) * 18 / 72 for _, anns in items for t in anns) + 0.25   # 说明栏宽：这页最长一句估宽，多留一个字（估宽偏窄，带西文和数字的长句差一点就折行）
    NX = X0 + (X1 - X0 - (NW + GAP + SW)) / 2                       # 第二级 18:5x：整组（节点卡＋说明栏）在内容区左右居中，看图左右匀
    D, RL = 0.40, 0.16                                              # 编号圈直径；圈离卡左沿
    TX = NX + RL + D + 0.14; TW = NX + NW - 0.14 - TX               # 节点句、选项的左沿和宽（编号圈右边）
    CH, CG, CB = 0.42, 0.08, 0.14                                   # 选项高（一行 T18）；选项上下间距；卡底留白
    OH = (len(opts) - 1) * CH + (len(opts) - 2) * CG + CB           # 选项占的高（并进那一步的卡下半）
    SX = NX + NW + GAP; SG = 0.10                                   # 右边说明栏左沿；句间距
    Y0 = 1.70; G = (6.85 - Y0 - 4 * H - OH) / 3                    # 流程图从带头句下起，用满到内容区底；三段箭头等长
    ax = NX + RL + D / 2                                            # 箭头走编号圈中线
    y = Y0; blocks = []                                             # 各步右边说明块
    for k, (lead, anns) in enumerate(items):
        c = '步%d' % (k + 1); yb = y + H + (OH if k == opts[0] else 0)
        if k == hi:                                                 # 主：带头句讲的那一步，节点行模块色实底；挂的选项留在下面浅底托上
            if yb > y + H:
                box(s, c + '选项托', NX, y + H / 2, NW, yb - y - H / 2, TINT[col], line=col, lw=1)   # 先画托，实底节点盖住它的上半
            box(s, c, NX, y, NW, H, col)
        else:
            box(s, c, NX, y, NW, yb - y, TINT[col], line=col, lw=1)   # 次：模块浅底＋模块色细边
        shape(s, c + '号', MSO_SHAPE.OVAL, NX + RL, y + (H - D) / 2, D, D, WHITE, line=col, lw=1.25)
        text(s, c + '号>字', NX + RL, y + (H - 20 / 72) / 2, D, str(k + 1), T14, col, True, C)
        text(s, c + '>带头句', TX, y, TW, lead, T18, WHITE if k == hi else NAVY, True, L, MID, h=H)
        if k == opts[0]:
            for j, o in enumerate(opts[1:]):
                oy, on = y + H + j * (CH + CG), '%s选项%d' % (c, j + 1)
                box(s, on, TX, oy, TW, CH, WHITE, line=SEQ[col], lw=0.75)
                nm, sep, rest = o.partition('：')
                runs_text(s, on + '>名', TX + 0.12, oy + (CH - 25 / 72) / 2, TW - 0.24,
                          [(nm + sep, col, True)] + ([(rest, NAVY, False)] if rest else []), T18, L)
        rows = [(a[1], T14, SUB, 0.04) if isinstance(a, tuple) else (a, T18, NAVY, SG) for a in anns]   # (字, 字号, 色, 和上一句的间距)
        tot = sum(nl(t) * sp[1] / 72 for t, sp, _, _ in rows) + sum(g for _, _, _, g in rows[1:])
        blocks.append([c, rows, y + H / 2 - tot / 2, tot])          # 整块先和节点行上下居中，画之前再让开下一块
        if k < 3:
            connector(s, '箭头%d' % (k + 1), ax, yb, ax, yb + G, SEQ[col], 2.0, head=True)
            y = yb + G
    for k in range(len(blocks) - 2, -1, -1):                        # 上下两块说明至少隔 BG，不够就把上一块往上挪（第 8 页第 3 步三行，不挪会和第 4 步连成一片）
        lack = blocks[k][2] + blocks[k][3] + BG - blocks[k + 1][2]
        if lack > 0:
            blocks[k][2] -= lack
    for c, rows, ty, _ in blocks:
        for j, (t, sp, colr, g) in enumerate(rows):
            ty += g if j else 0
            text(s, '%s句%d' % (c, j + 1), SX, ty, SW, t, sp, colr)
            ty += nl(t) * sp[1] / 72


P5 = 0.20


P4_LEAD = '跳转、次数和冷却默认跟着活动或礼包走，不用每条规则重设'   # 第一级 11/03 18:54：「配一份」听不懂，改直说；11/04 09:49 带上冷却；可超 15 字（--check 只对这一句放开）
P4_STEP2 = '每个场景挑活动或礼包，分固定和轮换'                      # 第一级 11/04 10:06 的原句，16 字；--check 只对这一句和上一句放开 15 字；节点卡因此加宽到 5.233 才不折行（整组正好铺满内容区，左沿对齐标题）


def p4(s):
    # 第五批带头句：运营建一条最要紧的是跳转、次数、冷却不用每条规则逐项填——默认跟着活动或礼包走、规则默认沿用（功能框架「活动或礼包的弹窗设置」372–407、规则里「沿用活动或礼包的设置」304–324）
    # 11/04 09:49：第 1 步先人群；第 3 步加冷却（框架 321–324、405–407：同一活动或礼包每人两次至少隔多久，默认留空即不限）
    # 11/04 10:27：灰字照第一级，每个池子各算默认（固定默认破产时 1 个、其余 3 个，轮换默认 1 个）
    # 11/04 10:06：第 2 步讲清固定和轮换两个池子（逐字照第一级 10:06；Dk 11/04 10:0x：两个池子都设在某个人群的某个场景里，各设弹几个、各有先后，轮换按单个玩家算）
    steps(s, P4_LEAD,
          [('选人群和场景', ['人群可多选，也可排除', '选完显示预计人数']),
           (P4_STEP2, ['固定：每次按同一顺序弹', '轮换：弹过的暂时沉底，这个玩家轮完一遍才回到原顺序', ('灰', '固定默认破产时 1 个、其余 3 个，轮换默认 1 个')]),
           ('设跳转、次数和冷却时间', ['默认每人每天：活动 1 次、礼包 2 次', '冷却：同一活动或礼包每人两次至少隔多久，默认不限']),
           ('输入会员编号预览，再上架', ['看他下次用哪条规则、弹哪几个', '也能发测试，每次最多 50 人'])],
          BLUE, (2, '沿用：和其他规则共用', '另设：只改这条规则'), 2, NW=5.233, BG=0.22)


def p7(s):
    # 第五批带头句：每人每天最多 2 条，运营建一条最要紧的是发布前就知道扣掉上限后实际发出多少人（功能框架新建推播「发布确认」81–87：预计发出人数（已扣每人每天上限））
    steps(s, '发布前看扣完上限能发多少人',
          [('选类别和人群，看预计人数', ['类别：营销或服务通知', '营销默认排除 VIP 名单']),
           ('选发送方式', ['条件触发：条件到了才发，如玩家升级、活动结束前 N 小时', '玩家在游戏里时可选不发']),   # 11/04 09:49 全稿查词：条件触发当页说清（框架 45–52）
           ('写内容，设权重', ['标题、内文、跳转页面写一种语言，另两种一键生成', '权重 0–100，默认 50，仅营销',
                              '每人每天条数不够时，先留给权重高的定时推播']),   # 审定 7 第 4 条，对过框架 74–75 的原句；第二级 18:5x 照冷读从灰字升成 T18 NAVY；11/04 09:49 补上「每人每天条数不够时」，权重干什么用当页说清
           # 11/04 09:49：框架新建推播（3–87）和每人每天上限与夜间勿扰（493–521）没有「两次至少隔多久」这类设置，不加冷却
           ('看预计发出人数，再发布', ['已扣每人每天上限', '也列出因上限收不到的人数'])],
          TEAL, (1, '定时', '条件触发'), 3)


# ═════════ 第 6、10 页 数据界面：构图 A（参考版式「二」；审定 5：柱高等差递减、只是示意，焦点＝用到却没弹出／发出前少掉的那一段）═════════
# 第五批（交接记录第一级 18:44【第 6、9 页】）：主次对调——
#   主＝没弹／没发出的原因：页顶带头句（T22 粗 NAVY，紧贴标题下）说这一句；焦点段模块色实底（T18 白粗），模块色引线进右半边的紧凑列表：
#     模块色竖线＋每项一个模块色圆点，项目 T18 NAVY 粗，不加框；框架里的下一级写成灰字 T14 SUB，紧贴上一项。列表在柱区里上下居中。
#   次＝左半边四步柱：灰条，柱上一行说明 T18 NAVY 常规，柱名 T18 NAVY；先后箭头放在两柱之间的底部（柱名 18 磅放不下箭头）。
#   两页同一画法，只换模块色。第 9 页原因照功能框架「没发出的原因」（框架 554–561）原样，没装 App 或关了通知照框架挂在没发出下。
#   第 10 页（审定 10 第 14 条，hero＝到达、曝光两根柱，从 0 数）：带头句讲这两步，重色给这两根柱；「没发出」块降成次（模块浅底、深字），引线和原因列表不动。第 6 页不传 hero，画法不变。
def funnel(s, col, lead, label, steps_, drop_after, reasons, drop_label, hero=()):
    LH, SH = 25 / 72, 20 / 72                           # T18、T14 一行高
    MID_X = (X0 + X1) / 2
    LX, LR = X0, MID_X - 0.25                           # 左半边：柱
    RL = MID_X + 0.90; TX = RL + 0.30                   # 右半边：列表竖线、列表字左沿（往右收，左右留白匀）
    text(s, '带头句', X0, LEAD_Y, X1 - X0, lead, T22, NAVY, True)                # 主的那句：T22 粗 NAVY 紧贴标题下
    text(s, '四步说明', LX, 1.62, LR - LX, label, T18, NAVY)                    # 次：T18 NAVY 常规
    YT = 2.15; YB = 6.85 - 0.10 - LH                    # 柱顶、柱底线（柱名一行的底落在内容区底）
    H = YB - YT; bw = 0.95; BX = LX + 0.15             # 柱从左边距内缩一点，第一个柱名不出左边距
    sp_ = (LR - BX - bw) / 3                            # 柱心间距：首柱左沿到末柱右沿铺满左半边
    f = drop_after + 1                                  # 焦点段压在第几根柱顶上；drop_after=-1 即第一根
    lv = 1 if f == 0 else 0                             # 焦点在第一根柱顶上时柱高整体降一档，让出同样高的焦点段
    hs = [H * (1 - 0.2 * (k + lv)) for k in range(4)]   # 等差递减：示意，不是真数据
    for k, t in enumerate(steps_):
        x = BX + k * sp_; cx = x + bw / 2; c = '柱%d' % (k + 1)
        box(s, c + '到达', x, YB - hs[k], bw, hs[k], col if k in hero else BAR, rect=True)
        if k == f:                                      # 只画焦点那段（17:23 冷读：没标注的虚线空框读不懂）
            top = hs[k - 1] if k else H
            y = YB - top; dh = top - hs[k]
            box(s, '焦点', x, y, bw, dh, TINT[col] if hero else col, line=EDGE[col] if hero else None, rect=True)
            text(s, '焦点>名', x, y + (dh - LH) / 2, bw, drop_label, T18, NAVY if hero else WHITE, True, C)
            fy, fx = y + dh / 2, x + bw
        nw = em(t) * 18 / 72 + 0.10
        text(s, c + '名', cx - nw / 2, YB + 0.10, nw, t, T18, NAVY, False, C)
        if k < 3:
            arrow(s, '先后箭头%d' % (k + 1), MSO_SHAPE.RIGHT_ARROW, cx + sp_ / 2 - 0.15, YB - 0.12 - 0.22, 0.30, 0.22, SEQ[col])
    connector(s, '底线', LX, YB, LR, YB, LINE, 1.0)
    G, SG = 0.30, 0.02                                  # 项间距；灰字紧贴上一项
    rows = [(r[1], T14, SUB, False, SG) if isinstance(r, tuple) else (r, T18, NAVY, True, G) for r in reasons]
    rows[0] = rows[0][:4] + (0,)
    tot = sum(nl(t) * sp[1] / 72 + g for t, sp, _, _, g in rows)
    ty = (YT + YB) / 2 - tot / 2                        # 列表在柱区里上下居中
    dots = []
    for j, (t, sp, colr, b, g) in enumerate(rows):
        ty += g
        text(s, '原因%d' % (j + 1), TX, ty, X1 - TX, t, sp, colr, b)
        if sp == T18:
            dots.append(ty + LH / 2)
        ty += nl(t) * sp[1] / 72
    connector(s, '引线', fx, fy, RL, fy, col, 1.5)
    connector(s, '原因竖线', RL, min(dots + [fy]), RL, max(dots + [fy]), col, 2.25)
    D = 0.14
    for i, m in enumerate(dots):
        shape(s, '原因点%d' % (i + 1), MSO_SHAPE.OVAL, RL - D / 2, m - D / 2, D, D, col)


def p5(s):
    funnel(s, BLUE, '没弹的分四类原因', '每条规则看四步人数', ['触发场景', '用到这条规则', '弹出', '点击'], 1,
           ['时机和次数', '场景上限和间隔', '弹满或没轮到', '活动或礼包弹不了'], '没弹')


def p8(s):
    # 第六批（第一级 11/04 09:49【推播数据页】，卡上第 15 项④）：四步改发出、到达、曝光、点击（曝光框架 553 行还没有，以 Dk 这次定的为准，不改框架）；
    # 发出是第一根柱，「没发出」实底压在它顶上，引线连到右边原因列表（原因照框架 554–561）
    funnel(s, TEAL, '到了手机不等于看见，四步分开看', '每条看四步人数', ['发出', '到达', '曝光', '点击'], -1,
           ['玩家正在游戏里时不发', '夜间勿扰', '每人每天上限', ('灰', '其中条数被权重更高的定时推播先占'), '发送失败', '没装 App 或关了通知'], '没发出', hero=(1, 2))


# ═════════ 第 8 页 推播主界面：同第 3 页版式（主＝左 7 栏示意，次＝右栏编号标注带头句，辅＝标注句），只换模块色 ═════════
# ①② 页顶两条限制（浅底色块里两行字段）；括线标字「管下面所有营销推播」罩住下面日历和列表；③ 日历 7 天；④ 列表两个页签＋行
# 思考页 13.3 第 7 页：示意里写界面上本来就有的字段名（数值仍用灰条），同第 3 页「回流」「进大厅」两档；括线标字去框、降成 NAVY 常规
# 第五批（18:44【第 7 页】、思考页第 15 节）：标题下加带头句（T22 粗 NAVY，≤15 字），原意「营销推播统一管，每人每天最多 2 条，夜里不发」，
# 核框架 493–521 行（每人每天上限 › 营销推播 默认 2 条；夜间勿扰 22:00–08:00 适用推播）。示意整体下移让出带头句，内容不动；
# 示意里的字段名、括线标字、页签升到 T18（全场正文 18 磅），右栏说明 T18、灰字 T14（mv_notes）。
# 同第 3 页画法（第二级 18:5x）：示意外框灰细边；只有带头句讲的 ①② 页顶两条限制用推播绿（浅绿底带＋绿色粗字段名＋绿括线），日历、列表和 ③④ 编号圈降成灰。
def p6(s):
    col = TEAL
    text(s, '推播主界面带头句', X0, LEAD_Y, X1 - X0, '营销推播每人每天限 2 条，夜里不发', T22, NAVY, True)
    box(s, '示意', MV_X, 1.55, MV_W, 6.85 - 1.55, WHITE, line=GRAY_B, lw=1.0)           # 外框灰细边（同第 3 页）
    py0, py1, a1, a2 = 1.72, 3.04, 1.99, 2.77                              # ①② 页顶两条限制（两行间距够右栏说明＋灰字）
    box(s, '页顶限制', MV_A, py0, MV_B - MV_A, py1 - py0, TEAL_T, rect=True)
    connector(s, '页顶限制线', MV_L, (a1 + a2) / 2, MV_R, (a1 + a2) / 2, TEAL_B, 0.75)
    for k, (a, t) in enumerate([(a1, '每人每天上限'), (a2, '夜间勿扰')]):
        text(s, '限制字段%d' % (k + 1), MV_L, a - 25 / 72 / 2, 2.60, t, T18, col, True)       # 字段名：推播绿粗字（主：带头句讲的两条）
        box(s, '限制取值%d' % (k + 1), 4.10, a - 0.16, 1.10, 0.32, WHITE, rect=True)
        bars(s, '限制取值%d' % (k + 1), 4.24, a - 0.04, [0.50])
    mx, ly = (MV_A + MV_B) / 2, 3.32                                       # 括线：页顶限制管下面全部
    connector(s, '罩线竖', mx, py1, mx, ly, col, 1.5)
    connector(s, '罩线横', MV_L, ly, MV_R, ly, col, 1.5)
    connector(s, '罩线左', MV_L, ly, MV_L, ly + 0.18, col, 1.5)
    connector(s, '罩线右', MV_R, ly, MV_R, ly + 0.18, col, 1.5)
    lab = '管下面所有营销推播'; lw_ = em(lab) * 18 / 72                     # 括线标字：白底无边断开括线，T18 NAVY 常规（次）
    box(s, '罩住', mx - lw_ / 2 - 0.10, ly - 0.19, lw_ + 0.20, 0.38, WHITE, rect=True)
    text(s, '罩住>名', mx - lw_ / 2 - 0.10, ly - 25 / 72 / 2, lw_ + 0.20, lab, T18, NAVY, align=C)
    text(s, '日历名', MV_L, 3.56, 2.0, '未来 7 天', T18, SUB, True)       # ③ 日历：左上写字段名；7 天，每天一块浅灰底（无边）
    cy0, cy1, dg = 3.96, 4.94, 0.08
    dw = (MV_R - MV_L - 6 * dg) / 7
    for d in range(7):
        x = MV_L + d * (dw + dg); c = '日%d' % (d + 1)
        box(s, c, x, cy0, dw, cy1 - cy0, GRAY_T, rect=True)
        bars(s, c, x + 0.10, cy0 + 0.14, [0.40, 0.56, 0.42, 0.50], step=0.20)
    connector(s, '日历线', MV_A, 5.04, MV_B, 5.04, LINE, 0.75)
    lt, ry, rh = 5.10, 5.50, 0.36                                          # ④ 列表：两个页签（定时、条件触发）＋三行，行间浅线
    x = MV_L
    for k, t in enumerate(['定时', '条件触发']):                            # 页签写真字，选中的加模块色下划线（同第 3 页「进大厅」）
        w = len(t) * 18 / 72 + 0.30; on = k == 0
        text(s, '列表页签%d' % (k + 1), x, lt + (ry - lt - 25 / 72) / 2, w, t, T18, SUB, on, C)   # 列表降成灰：选中页签灰粗字＋灰下划线
        if on:
            box(s, '列表页签选中', x, ry - 0.05, w, 0.05, MUTE, rect=True)
        x += w + 0.08
    connector(s, '列表页签线', MV_A, ry, MV_B, ry, GRAY_B, 0.75)
    for r in range(3):
        y = ry + r * rh; c = '列表行%d' % (r + 1)
        bars(s, c, MV_L + 0.10, y + (rh - 0.08) / 2, [1.6]); bars(s, c + 'b', 3.60, y + (rh - 0.08) / 2, [1.2])
        bars(s, c + 'c', 6.10, y + (rh - 0.08) / 2, [0.80])
        if r < 2:
            connector(s, c + '线', MV_A, y + rh, MV_B, y + rh, LINE, 0.75)
    mv_notes(s, col, [
        (a1, '每人每天最多收 2 条营销推播', ['可按人群另设；补偿、维护等服务通知不算']),
        (a2, '营销推播不在 22 点到 8 点发', []),
        ((cy0 + cy1) / 2, '日历看未来 7 天每天发几条', ['每天达到上限的人数']),
        (ry + rh / 2, '定时、条件触发各一张列表', ['条件触发：条件到了才发，如玩家升级、活动结束前', '定时：每行有预计发出人数', '条件触发：每行有今天发出条数']),   # 第六批，第 15 项③：本场第一次出现「条件触发」，当页说清，同新建页说法（框架 45–52 行）
    ], hi=(1, 2))


# ═════════ 第 7 页 过渡（第六批，第一级 11/04 09:49【过渡页】；Dk 11/04 09:4x「弹窗和推播之间没过度，我一下都没注意到这页开始讲推播了」）═════════
# 不画标题。主＝页面中间一行大字（T40，全场唯一，带头句位）；次＝第 2 页顶上那个块，同位置、同宽、同样的 ①② 排法：① 弹窗灰掉，② 推播实底标亮。
# 块里的字比第 2 页大一档（T18／T14，第 2 页是 T14／T12）：第 14 项要求正文 ≥18、灰字 ≥14，第 2 页版式不动，这页按第 14 项。
def pt(s):
    P, TY, NH, AH = 0.20, 1.05, 25 / 72, 20 / 72
    TH = P + NH + P
    box(s, '两块', X0, TY, X1 - X0, TH, GRAY_T, rect=True)             # 同第 2 页：浅灰底、不画边，横跨全宽
    x1, x2 = X0 + P, X0 + P + 2.40                                     # ①② 的横向位置同第 2 页
    box(s, '两块亮', x2 - 0.16, TY + 0.09, 1.95, TH - 0.18, TEAL)       # ② 标亮：全页唯一的实底
    for k, (x, nm, sub, c1, c2, b) in enumerate([(x1, '① 弹窗', '游戏内', MUTE, MUTE, False), (x2, '② 推播', '游戏外', WHITE, WHITE, True)]):
        text(s, '两块>名%d' % (k + 1), x, TY + P, 1.05, nm, T18, c1, b)
        text(s, '两块>内外%d' % (k + 1), x + 1.05, TY + P + NH - AH, 0.60, sub, T14, c2)
    cy = (TY + TH + 6.85) / 2 - T40[1] / 72 / 2                        # 大字在块下方到页底的区域里上下居中
    runs_text(s, '过渡带头句', X0, cy, X1 - X0, [('弹窗讲完，接下来讲', NAVY, True), ('推播', TEAL, True)], T40, align=C)


BUILDERS = [p0, p1, p2, p3, p4, p5, pt, p6, p7, p8]


def build(sent):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W); prs.slide_height = Inches(SLIDE_H)
    cp = prs.core_properties
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    cp.author = cp.last_modified_by = '产品部'
    cp.title = FILE_TITLE
    cp.created = cp.modified = now
    cp.comments = ''; cp.keywords = ''; cp.subject = ''; cp.category = ''
    for no, fn in enumerate(BUILDERS, start=1):
        fn(page(prs, no, sent))
    return prs


# ═════════ 读回：字数、装不装得下、压不压线 ═════════
EMU = 914400
PUNCT = re.compile(r'[\s，、。：；！？（）「」“”,.:;()·①②／]')


def n10(t):            # 完成标准第 10 条口径：标点、空格不算
    return len(PUNCT.sub('', t))


def n_chars(t):        # 正文口径（同旧脚本 --stats）：去空白，标点算字
    return len(re.sub(r'\s', '', t))


def em(t):
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
    prs = Presentation(path)
    cp = prs.core_properties
    d = {'pages': [], 'props': (cp.author, cp.last_modified_by, cp.title, cp.comments, cp.keywords)}
    for sl in prs.slides:
        pg = {'title': '', 'title_runs': [], 'leads': [], 'body': [], 'boxes': [], 'shapes': {}, 'notes': '', 'tables': 0, 'jumps': 0, 'text_all': ''}
        for sh in sl.shapes:
            g = {'x': sh.left / EMU, 'y': sh.top / EMU, 'w': sh.width / EMU, 'h': sh.height / EMU}
            g['r'] = g['x'] + g['w']; g['b'] = g['y'] + g['h']
            pg['shapes'][sh.name] = g
            try:
                pg['tables'] += bool(sh.has_table)
            except Exception:
                pass
            try:
                if sh.click_action.target_slide is not None or sh.click_action.hyperlink.address:
                    pg['jumps'] += 1
            except Exception:
                pass
            if sh.shape_type != MSO_SHAPE_TYPE.TEXT_BOX:
                continue
            t = sh.text_frame.text.replace('\x0b', '\n')
            p = sh.text_frame.paragraphs[0]
            size = max((r.font.size.pt for r in p.runs if r.font.size is not None), default=0)
            ls = p.line_spacing; pitch = ls.pt if hasattr(ls, 'pt') else None
            for r in p.runs:
                if r.hyperlink.address:
                    pg['jumps'] += 1
            pg['boxes'].append((sh.name, t, size, pitch, g))
            pg['text_all'] += t + '\n'
            if sh.name == '标题':
                pg['title'] = t
                pg['title_runs'] = [(r.text, str(r.font.color.rgb)) for r in p.runs]
            elif sh.name != '页码':
                pg['body'].append((sh.name, t))
                if sh.name.endswith('带头句') or re.search(r'带头句\d$', sh.name):
                    pg['leads'].append((sh.name, t))
        if sl.has_notes_slide:
            pg['notes'] = sl.notes_slide.notes_text_frame.text
        d['pages'].append(pg)
    return d


def fit(name, t, size, pitch, g):
    """每行估宽 ≤ 框宽；行数×行距 ≤ 框高；行距 ≥ 字号×1.25。返回（最满一行占框宽、问题）。"""
    worst, probs = 0.0, []
    for part in t.split('\n'):
        wd = em(part) * size / 72
        worst = max(worst, wd / g['w'] if g['w'] else 9)
        if wd > g['w'] + 1e-6:
            probs.append('%s「%s」估宽 %.2f > 框宽 %.2f' % (name, part, wd, g['w']))
    if pitch is None or pitch < size * 1.25 - 0.01:
        probs.append('%s 行距 %s 磅不够' % (name, pitch))
    need = nl(t) * (pitch or 0) / 72
    if need > g['h'] + 0.005:
        probs.append('%s %d 行要高 %.3f > 框高 %.3f' % (name, nl(t), need, g['h']))
    return worst, probs


def inside(a, b, tol=0.005):
    return a['x'] >= b['x'] - tol and a['y'] >= b['y'] - tol and a['r'] <= b['r'] + tol and a['b'] <= b['b'] + tol


def page_problems(pg):
    """装不装得下、出不出页面、压不压容器的线。"""
    probs, worst = [], []
    for name, t, size, pitch, g in pg['boxes']:
        w, pr = fit(name, t, size, pitch, g)
        worst.append((w, name)); probs += pr
        if '>' in name:
            cont = name.split('>')[0]
            if cont in pg['shapes'] and not inside(g, pg['shapes'][cont]):
                probs.append('%s 出了容器「%s」' % (name, cont))
    for name, g in pg['shapes'].items():
        if g['x'] < -0.01 or g['y'] < -0.01 or g['r'] > SLIDE_W + 0.01 or g['b'] > SLIDE_H + 0.01:
            probs.append('%s 出了页面' % name)
    return probs, max(worst) if worst else (0, '')


def need_files():
    miss = [p for p in (OUT_NOTES, OUT_SENT) if not os.path.exists(p)]
    if miss:
        print('文件还没生成，先不带参数跑一遍：', '、'.join(miss)); sys.exit(2)


def speech_of(note):
    cut = note.find('若问：')
    return note[:cut] if cut >= 0 else note


def stats():
    need_files()
    for label, path in (('讲稿版', OUT_NOTES), ('发给主管版', OUT_SENT)):
        d = read_deck(path)
        print('【%s】%s｜%d 页｜文件属性 作者=%s 上次修改者=%s 标题=%s' % ((label, path, len(d['pages'])) + d['props'][:3]))
        tot_sp = tot_ask = 0
        for i, pg in enumerate(d['pages'], start=1):
            body = sum(n_chars(t) for _, t in pg['body'])
            sp = n_chars(speech_of(pg['notes'])); ask = pg['notes'].count('若问：')
            tot_sp += sp; tot_ask += ask
            probs, (w, wn) = page_problems(pg)
            print('  第 %d 页｜标题 %d 字（≤%d）「%s」｜正文 %d 字（≤%d）｜讲稿 %d 字｜追问 %d｜文字框 %d 个，最满一行占框宽 %.0f%%（%s）｜%s' % (
                i, n10(pg['title']), TITLE_MAX, pg['title'], body, BODY_MAX, sp, ask, len(pg['boxes']), w * 100, wn,
                '全部放得下' if not probs else '问题：' + '；'.join(probs)))
            for n, t in pg['leads']:
                print('      带头句 %2d 字（≤%d）%s' % (n10(t), LEAD_MAX, t.replace('\n', '')))
        if tot_sp or tot_ask:
            print('  讲稿合计 %d 字（≤%d，按每分钟 240 字约 %.1f 分钟）｜追问合计 %d 条（应为 %d）' % (
                tot_sp, SPEECH_TOTAL_MAX, tot_sp / 240, tot_ask, ASK_N))
        else:
            print('  备注：无')


def check():
    need_files()
    ok_all = True

    def row(ok, msg):
        nonlocal ok_all
        ok_all &= bool(ok)
        print('  %s %s' % ('通过' if ok else '不通过', msg))
    texts = {}
    for label, path, sent in (('讲稿版', OUT_NOTES, False), ('发给主管版', OUT_SENT, True)):
        d = read_deck(path)
        print('【%s】' % label)
        row(len(d['pages']) == PAGES_N, '页数 %d（应为 %d）' % (len(d['pages']), PAGES_N))
        texts[label] = [pg['text_all'] for pg in d['pages']]
        all_txt = '\n'.join(pg['text_all'] + pg['notes'] for pg in d['pages'])
        bad = {w: all_txt.count(w) for w in BANNED if all_txt.count(w)}
        row(not bad, '跳转、指引字样和「EP」（页面＋备注）：%s' % (bad or '全 0'))
        quotes = sorted(set(re.findall(r'[“”‘’"\'『』]', all_txt)))
        row(not quotes, '非「」引号：%s' % (' '.join(quotes) or '无'))
        ng = all_txt.count('群组') - all_txt.count('测试群组')   # 「测试群组」是发测试的对象名（功能框架 328），不是人群的旧叫法，不算（批 3）
        row(ng <= 1 and '人群' in all_txt, '叫法统一成「人群」：「群组」出现 %d 次（≤1，只在讲稿说一次后台字段名；「测试群组」不算）' % ng)
        row(sum(pg['tables'] for pg in d['pages']) == 0, '表格形状 0')
        row(sum(pg['jumps'] for pg in d['pages']) == 0, '跳转或链接 0')
        for i, pg in enumerate(d['pages'], start=1):
            body = sum(n_chars(t) for _, t in pg['body'])
            long_leads = [t for _, t in pg['leads'] if n10(t) > LEAD_MAX
                          and not (i == 5 and t in (P4_LEAD, P4_STEP2))]   # 只对第 5 页这两句放开 15 字：第一级 11/03 18:54 定「这里让位给讲清楚」，11/04 10:06 给的节点原句
            probs, _ = page_problems(pg)
            if i in NO_TITLE:
                t_ok, t_msg = not pg['title'], '不画标题'
            else:
                t_ok = pg['title'] and n10(pg['title']) <= TITLE_MAX and '，' not in pg['title'] and ',' not in pg['title']
                t_msg = '标题 %d 字不带逗号' % n10(pg['title'])
            row(t_ok and body <= BODY_MAX and pg['leads'] and not long_leads and not probs,
                '第 %d 页：%s、正文 %d 字、带头句 %d 句都不超%s' % (
                    i, t_msg, body, len(pg['leads']),
                    '' if not (long_leads or probs) else '；' + '；'.join(long_leads + probs)))
        order = [pg['title'] for pg in d['pages']]
        want = ['' if i in NO_TITLE else t for i, t in enumerate(TITLES, start=1)]
        row(order == want, '各页标题和顺序照 TITLES（第 1、2、7 页不画标题）')
        off = [(i, x, c) for i, pg in enumerate(d['pages'], start=1) for x, c in pg['title_runs']
               if c != MOD_COL.get(x, NAVY) or any(m in x and x != m for m in MOD_COL)]
        row(not off, '内容页标题「弹窗」「推播」用模块色，其余 NAVY：%s' % (off or '全对'))
        row(d['pages'][6]['leads'] == [('过渡带头句', '弹窗讲完，接下来讲推播')] and '两块亮' in d['pages'][6]['shapes'],
            '第 7 页过渡：大字和 ② 推播标亮都在')
        row(d['props'][0] == '产品部' and d['props'][1] == '产品部' and d['props'][2] == FILE_TITLE
            and not d['props'][3] and not d['props'][4], '文件属性 作者、上次修改者「产品部」，标题「%s」，描述、关键词空' % FILE_TITLE)
        notes = [pg['notes'].strip() for pg in d['pages']]
        if sent:
            row(not any(notes), '发给主管版备注 %d 页有字（应为 0）' % sum(bool(n) for n in notes))
        else:
            sp = sum(n_chars(speech_of(n)) for n in notes)
            row(all(notes), '每页都有讲稿（%d/%d）' % (sum(bool(n) for n in notes), len(notes)))
            row(sp <= SPEECH_TOTAL_MAX, '讲稿合计 %d 字（≤%d，约 %.1f 分钟）' % (sp, SPEECH_TOTAL_MAX, sp / 240))
            row(sum(n.count('若问：') for n in notes) == ASK_N, '追问 %d 条（应为 %d）' % (sum(n.count('若问：') for n in notes), ASK_N))
            row('两块都分三个界面' in notes[1] and '讲完了' in notes[6] and '有没有疑问' in notes[6] and '有没有疑问' not in notes[5],
                '目录页讲稿说「两块、三部分」；第 7 页讲稿有复述和停顿，第 6 页不重复')
            row('推播和现在比差在哪' in notes[7] and '到达率怎么算' in notes[9],
                '推播的两条追问挂在第 8、10 页')
    print('【两份对照】')
    row(texts['讲稿版'] == texts['发给主管版'], '两份页面相同（逐页文字一字不差）')
    print('全部通过' if ok_all else '有项目不通过')
    return ok_all


if __name__ == '__main__':
    if '--stats' in sys.argv:
        stats(); sys.exit(0)
    if '--check' in sys.argv:
        sys.exit(0 if check() else 1)
    for sent, out in ((False, OUT_NOTES), (True, OUT_SENT)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        prs = build(sent)
        prs.save(out)
        print('已生成', out, '共', len(prs.slides), '张', '（发给主管版）' if sent else '（讲稿版）')
