# 第 2 页「结论」设计稿：上层「现在 → 目标」两块面板对照；下层一张卡按差距类别分三栏，栏上写原因，栏下写做法（项数大字＋全部条目）
# 用法：python pl_结论页_设计.py 输出.pptx
import sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_呈交版V2_版式库 import *

OUT = sys.argv[1] if len(sys.argv) > 1 else 'V4_第2页_结论_设计.pptx'
GREEN = '2F6B52'; GREEN_W = 'E2EFE8'; BLUE_L = 'C6D9F1'
KIND = {'blue': (BLUE_W, BLUE), 'green': (GREEN_W, GREEN), 'amber': (AMBER_W, AMBER), 'gray': (GRAY_W, GRAY)}
MID = MSO_ANCHOR.MIDDLE
X0 = 0.9; W = 11.53; XR = X0 + W
TITLE = '弹窗与推送改按五类人群配置：弹窗分组现有后台就能做，另需开发 6 项能力'


def tw(t, size):
    return sum(1.0 if unicodedata.east_asian_width(c) in ('W', 'F') else 0.55 for c in t) * size / 72


def tag(s, x, y, label, kind='blue', size=12, h=0.25, pad=0.24):
    f, c = KIND[kind]
    w = tw(label, size) + pad
    box(s, x, y, w, h, fill=f, line=None, radius=0.2)
    text(s, x, y, w, h, label, size=size, color=c, bold=True, align=PP_ALIGN.CENTER, anchor=MID, line=1.0)
    return w


def kicker(s, x, y, w, t, c, h=0.28):
    text(s, x, y, w, h, t, size=13, bold=True, color=c, anchor=MID, spc=150)


def g(t):
    return (t, {'color': GRAY, 'size': 12})


def n(t, c=NAVY, size=12):
    return (t, {'color': c, 'size': size, 'bold': True})


prs = new_prs(); s = new_slide(prs)
text(s, X0, 0.78, 11.5, 0.3, '结论', size=12, color=BLUE, bold=True, spc=100, name='kicker')
text(s, X0, 1.07, 11.85, 0.55, TITLE, size=24, color=NAVY, bold=True, line=1.05, name='title')
text(s, X0, 6.88, 6, 0.3, FOOT + '　·　2', size=12, color=GRAY, name='footer')

# ═════ 上层：现在 → 目标 ═════
PAD = 0.3
Y1 = 1.8; H1 = 2.38
GA = 0.4
WL = (W - GA) / 2
XRt = X0 + WL + GA
IW = WL - 2 * PAD
K_Y, B_Y, C_Y, DV, L_Y = 0.2, 0.5, 0.98, 1.58, 1.7   # 段名、大字、说明、分隔线、推送与标签两行

# 现在
box(s, X0, Y1, WL, H1)
kicker(s, X0 + PAD, Y1 + K_Y, 2, '现在', RED)
text(s, X0 + PAD, Y1 + B_Y, IW, 0.44, '所有玩家看同一套弹窗', size=24, bold=True, color=NAVY, anchor=MID, line=1.0)
text(s, X0 + PAD, Y1 + C_Y, IW, 0.46, [[g('近一月登录 '), n('62,292 人'), g('都看这一套，')],
                                       [g('其中新增与回流 '), n('27,313 人'), g('，占 '), n('43.85%', RED, 13)]], line=1.15)
hline(s, X0 + PAD, Y1 + DV, IW)
text(s, X0 + PAD, Y1 + L_Y, IW, 0.6, [[n('五种推送分在三处配置', NAVY, 13), g('  8 天以上未登录的 '), n('40,117 人', RED, 13), g('只能靠推送')],
                                      [n('两类目标人群没有现成标签', NAVY, 13), g('  潜在付费、潜在流失')]], line=1.3)

arrow(s, X0 + WL + 0.1, Y1 + H1 / 2 - 0.12, GA - 0.2, 0.24)

# 目标
box(s, XRt, Y1, WL, H1, line=BLUE_L, lw=1.0)
kicker(s, XRt + PAD, Y1 + K_Y, 2, '目标', BLUE)
text(s, XRt + PAD, Y1 + B_Y, IW, 0.44, '五类人群各看一套弹窗', size=24, bold=True, color=BLUE, anchor=MID, line=1.0)
cx = XRt + PAD
for name in ['新增', '回流', '破产', '潜在付费', '潜在流失']:
    cx += tag(s, cx, Y1 + C_Y, name) + 0.08
text(s, XRt + PAD, Y1 + C_Y + 0.27, IW, 0.2, '每人每次、每日最多弹几个，事前读得出', size=12, color=GRAY, anchor=MID)
hline(s, XRt + PAD, Y1 + DV, IW)
text(s, XRt + PAD, Y1 + L_Y, IW, 0.6, [[n('五种推送一处配置、按人群发送', NAVY, 13)],
                                       [n('五类人群都能用标签圈出', NAVY, 13)]], line=1.3)

# ═════ 下层：原因 → 做法 ═════
Y2 = Y1 + H1 + 0.26; H2 = 6.6 - Y2
box(s, X0, Y2, W, H2)
LW = 0.62
GAPC = 0.26
BX = X0 + PAD + LW
cols = [  # (各列宽, 色, 原因类别, 原因说明（分行）, 项数, 做法类别, 条目（按列）)
    ([2.0, 1.72], 'green', '只缺配置', ['弹窗分人群，现有后台就能配'], '6', '现有功能可做',
     [['活动弹窗按人群分组', '五类人群首版内容', '新建两类标签'], ['推播、短信按标签发送', '效果按人群汇总', '组内随机对照']]),
    ([1.83, 1.72], 'amber', '缺功能', ['现有后台没有，要新建'], '6', '需开发',
     [['每人每日弹窗上限', '新手弹窗接入后台', '推送统一后台'], ['推送跳转与触发自助', '每种推送方式每日上限', '群组交集']]),
    (None, 'gray', '待核实', ['资料没写或未确认'], '5', '核实后定',
     [['标签工具 4 项：人数预览、', '口径说明、变更记录、引用清单', '快显、Facebook、LINE 效果记录']])]
RY = Y2 + 0.24          # 原因行
NY = Y2 + 0.7           # 项数行
IY = NY + 0.5           # 条目
kicker(s, X0 + PAD, RY, LW, '原因', NAVY)
kicker(s, X0 + PAD, NY, LW, '做法', NAVY, h=0.42)
x = BX
for i, (ws, kind, rk, rb, num, dk, lists) in enumerate(cols):
    wcol = sum(ws) if ws else XR - PAD - x
    f, c = KIND[kind]
    if i:
        rect(s, x - GAPC / 2, Y2 + 0.26, 0.012, H2 - 0.52, LINE)
    text(s, x, RY, wcol, 0.5, [[(rk + '　', {'bold': True, 'color': c, 'size': 13}), (rb[0], {'color': INK})]] +
         [[(t, {'color': INK})] for t in rb[1:]], size=12, line=1.15)
    text(s, x, NY, wcol, 0.42, [[(num, {'bold': True, 'color': c, 'size': 26}), (' 项　', {'bold': True, 'color': c, 'size': 13}),
                                 (dk, {'bold': True, 'color': c, 'size': 13})]], anchor=MID, line=1.0)
    xx = x
    for j, items in enumerate(lists):
        cw_ = ws[j] if ws else wcol
        text(s, xx, IY, cw_, 0.8, items, size=12, color=NAVY, line=1.25)
        xx += cw_
    x += wcol + GAPC

prs.save(OUT)
print('saved', OUT)
