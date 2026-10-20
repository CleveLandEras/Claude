# 推送系统的后台集成需求 · 需求评审稿（逐条评审每项细节需求）
# 用法：PYTHONPATH=<含 python-pptx 与 pillow 的目录> python3 an_推送后台_需求评审稿.py [输出.pptx] [措辞测试句子清单.tsv]
# 结构：封面 → 目录 → 17 个模块各一至两页（左：原型截图并圈出要看的地方；右：需求表 编号｜需求｜规则与取值｜为什么这样定｜结论）→ 附录术语。
# 版面沿用 an_呈交版V4_设计版.py 的配色、字号与页面组件（helper 复制自该文件，未改原文件）。
# 依据：推送系统后台集成需求/4_需求文档.md（4.1、4.2、非功能、合规）、2_方案设计.html（11 条设计决定与附录规则）、3_原型.html；成熟后台做法见 分析/A85_推送后台对标.md。
# 截图：分析/推送后台_需求评审稿/raw/m*.png 为原型（去掉页面淡化效果后）的 2 倍清晰度裁剪；运行时去掉原型自带的紫色编号与紫色框。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, unicodedata, uuid
import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn
from lxml import etree

BASE = _ROOT + '/'
OUT = sys.argv[1] if len(sys.argv) > 1 else BASE + '推送系统后台集成需求/6_逐条需求表.pptx'
IMG = BASE + '分析/推送后台_需求评审稿/'
FONT = 'Microsoft YaHei'
FOOT = '推送系统的后台集成需求'

# ───────── 颜色（同 V4 设计版） ─────────
BG = 'F7F6F2'; CARD = 'FFFEFC'; LINE = 'E2DED5'; HEAD = 'EFEDE7'; STONE = 'F0EEE9'
NAVY = '1F2A44'; INK = '3A4254'; GRAY = '6A707C'; MUTE = '9A9FA8'; ARW = 'CFC9BD'
RED = 'B03A2E'; RED_W = 'F8E7E3'; RED_L = 'E6B9AF'
BLUE = '2A63A6'; BLUE_W = 'E7EEF8'; BLUE_L = 'BFD3EC'
GREEN = '2F6B52'; GREEN_W = 'E3EFE8'; GREEN_L = 'B7D4C4'
AMBER = '9A6212'; AMBER_W = 'F6ECD9'; AMBER_L = 'E2C795'
GRAY_W = 'ECEBE7'; GRAY_L = 'C9CCD2'
UI_LINE = 'CDD2DA'; UI_BLUE = '409EFF'; UI_TXT = '303133'; UI_SUB = '606266'
HL = '2A63A6'      # 截图上的标注框：蓝＝改后

L, C, RT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM
X0 = 0.9; CW = 11.53; XR = X0 + CW
TS = 32

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
TITLES = []; WARN = []; LINES = []   # LINES：措辞测试要用的句子（页码, 位置, 文本）


def rgb(h):
    return RGBColor.from_string(h)


# ───────── 文字（同 V4） ─────────
def cw(ch):
    if unicodedata.east_asian_width(ch) in ('W', 'F'):
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


def T(s, x, y, w, h, paras, size=15, color=INK, bold=False, align=L, anchor=TOP, ls=1.32, sa=0, spc=None, check=True, link=None):
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
            if o.get('link') or link:
                r.hyperlink.address = o.get('link') or link
            width += tw(t, o.get('size', size)) * (1.04 if o.get('bold', bold) else 1.0)
        if check and width > w * 1.0:
            WARN.append('wrap p%d: %.2f>%.2f  %s' % (len(prs.slides), width, w, ''.join(t for t, _ in runs)[:30]))
    return tb


# ───────── 形状（同 V4） ─────────
def R(s, x, y, w, h, fill=CARD, line=LINE, lw=0.75, r=0.08, dash=False, shape=None):
    shp = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE)
    sp = s.shapes.add_shape(shp, Inches(x), Inches(y), Inches(w), Inches(h))
    if shp in (MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.ROUND_2_SAME_RECTANGLE):
        sp.adjustments[0] = min(0.5, r / min(w, h))
        if shp == MSO_SHAPE.ROUND_2_SAME_RECTANGLE:
            sp.adjustments[1] = 0
    if fill:
        sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
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


def _arrow(s, shape, x, y, w, h, color):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(color); sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def ARR(s, x, y, w=0.36, h=0.28, color=ARW):
    return _arrow(s, MSO_SHAPE.RIGHT_ARROW, x, y, w, h, color)


def CHEV(s, x, y, w=0.3, h=0.42, color=ARW):
    return _arrow(s, MSO_SHAPE.CHEVRON, x, y, w, h, color)


def DARR(s, x, y, w=0.28, h=0.3, color=ARW):
    return _arrow(s, MSO_SHAPE.DOWN_ARROW, x, y, w, h, color)


def DOT(s, x, y, n, d=0.3, fill=BLUE, size=12):
    R(s, x, y, d, d, fill=fill, line=None, shape=MSO_SHAPE.OVAL)
    T(s, x - 0.05, y, d + 0.1, d, str(n), size, 'FFFFFF', True, align=C, anchor=MID, ls=1.0, check=False)


def chip(s, x, y, text, size=15, fill=STONE, color=NAVY, h=0.44, pad=0.22, bold=True, line=None):
    w = tw(text, size) * (1.04 if bold else 1) + 2 * pad
    R(s, x, y, w, h, fill=fill, line=line, r=h / 2)
    T(s, x, y, w, h, text, size, color, bold, align=C, anchor=MID, ls=1.0, check=False)
    return w


def bullet(s, x, y, color=NAVY, d=0.08):
    R(s, x, y, d, d, fill=color, line=None, shape=MSO_SHAPE.OVAL)




def clean_shot(name, line_mode='erase', whiten=(), depink=(), src=None, crop=None, patch=()):
    """src：用另一张原始裁剪；crop：处理后再裁出 (x0, y0, x1, y1)，用于放大局部"""
    dst = IMG + name + '.png'; src = IMG + 'raw/' + (src or name) + '.png'
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255.0
    r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); d = mx - mn + 1e-6
    hue = np.where(mx == r_, ((g_ - b_) / d) % 6, np.where(mx == g_, (b_ - r_) / d + 2, (r_ - g_) / d + 4)) / 6
    sat = np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0)
    purple = (hue > 0.68) & (hue < 0.80) & (sat > 0.15) & (mx > 0.3)
    halo = (hue > 0.62) & (hue < 0.93) & (sat > 0.05)
    H, W = purple.shape
    # 编号圆点：紫色像素在 25×25 窗口内占比高
    k = 12
    ii = np.pad(purple.astype(np.int32), ((k + 1, k), (k + 1, k))).cumsum(0).cumsum(1)
    dens = (ii[2 * k + 1:, 2 * k + 1:] - ii[:-2 * k - 1, 2 * k + 1:] - ii[2 * k + 1:, :-2 * k - 1] + ii[:-2 * k - 1, :-2 * k - 1]) / float((2 * k + 1) ** 2)
    core = (dens > 0.42) & purple
    out = (a * 255).astype(np.uint8).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    done = np.zeros_like(core)
    badge_mask = np.zeros_like(core)
    for (cy, cx) in zip(*np.nonzero(core)):
        if done[cy, cx]:
            continue
        # 以这个核心点为种子，取周围 60×60 内的核心点求中心
        y0, y1, x0, x1 = max(0, cy - 30), min(H, cy + 30), max(0, cx - 30), min(W, cx + 30)
        sub = core[y0:y1, x0:x1]
        ys, xs = np.nonzero(sub)
        ccy, ccx = ys.mean() + y0, xs.mean() + x0
        done[y0:y1, x0:x1] |= sub
        rad = 26
        disk = (yy - ccy) ** 2 + (xx - ccx) ** 2 <= rad ** 2
        # 圆内每点取上下左右最近的圆外像素颜色，按钮、表头等底色能沿原样延续
        src_ = out.copy()
        for (py, px) in zip(*np.nonzero(disk)):
            best = None
            for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                k_ = 1
                while True:
                    qy, qx = py + dy * k_, px + dx * k_
                    if qy < 0 or qy >= H or qx < 0 or qx >= W:
                        k_ = None; break
                    if not disk[qy, qx] and not halo[qy, qx]:
                        break
                    k_ += 1
                if k_ is not None and (best is None or k_ < best[0]):
                    best = (k_, qy, qx)
            if best:
                out[py, px] = src_[best[1], best[2]]
        badge_mask |= disk
    line = (purple | (halo & np.pad(purple, 2)[2:-2, 2:-2])) & ~badge_mask
    # 线条：扩一圈，含抗锯齿
    lm = line.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            lm |= np.roll(np.roll(line, dy, 0), dx, 1) & halo
    if line_mode == 'gray':
        out[lm] = (205, 210, 218)
    else:
        src_ = out.copy()
        for (py, px) in zip(*np.nonzero(lm)):
            y0, y1, x0, x1 = max(0, py - 6), min(H, py + 7), max(0, px - 6), min(W, px + 7)
            m = ~lm[y0:y1, x0:x1]
            if m.any():
                out[py, px] = np.median(src_[y0:y1, x0:x1][m], axis=0)
    for (x0, y0, x1, y1) in whiten:
        out[y0:y1, x0:x1] = 255
    # 白底区域里残留的淡粉色（标注线的抗锯齿）改回白色；灰色标签不受影响
    for (x0, y0, x1, y1) in depink:
        reg = out[y0:y1, x0:x1].astype(int)
        pk = ((reg[..., 0] - reg[..., 1]) > 5) & ((reg[..., 2] - reg[..., 1]) > 3)
        reg[pk] = 255
        out[y0:y1, x0:x1] = reg.astype(np.uint8)
    for (x0, y0, x1, y1) in patch:   # 用右侧相邻底色盖掉残留细线
        out[y0:y1, x0:x1] = out[(y0 + y1) // 2, x1 + 6]
    if crop:
        out = out[crop[1]:crop[3], crop[0]:crop[2]].copy()
        H, W = out.shape[:2]
    Image.fromarray(out).save(dst)
    return dst, W, H




def shot(s, key, x, y, w=None, h=None, boxes=(), frame=True):
    """放截图；boxes 为截图像素坐标 (x0, y0, x1, y1) 的标注框，返回 (x, y, w, h)"""
    path, W, H = SHOTS[key]
    if w is None:
        w = h * W / H
    if h is None:
        h = w * H / W
    pic = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    if frame:
        pic.line.color.rgb = rgb(UI_LINE); pic.line.width = Pt(0.75)
    k = w / W
    for (bx0, by0, bx1, by1) in boxes:
        R(s, x + bx0 * k - 0.04, y + by0 * k - 0.04, (bx1 - bx0) * k + 0.08, (by1 - by0) * k + 0.08, fill=None, line=HL, lw=2.25, r=0.06)
    return x, y, w, h



# ══════════════════════ 内容：17 个模块，每页一张需求表 ══════════════════════
# 每页：标题＝模块名＋主要规则；shots＝[(截图键, [标注框])]（标注框为截图像素坐标）；wl＝截图列宽（0 表示无截图，表格占满）；
# rows＝[(需求, 规则与取值, 为什么这样定)]，单元格内用 \n 分行（两层推送分两行写，不混在一句）。
GROUPS = [('一', '入口与列表'), ('二', '新建推送'), ('三', '各推送方式'), ('四', '上限与数据'), ('五', '权限、迁移与性能')]

MODULES = [
 dict(n=1, name='总览', g=0, pages=[
  dict(title='总览：今日推送分游戏外、游戏内两组列，两组不合计', wl=4.4,
       shots=[('m01a', [(0, 88, 1230, 437), (0, 462, 1230, 650)])],
       rows=[
        ('侧栏列出全部页面，每种推送一页', '总览；游戏外推送：推播、短信、Facebook、LINE；游戏内推送：弹窗、快显；频率上限；数据看板；玩家查询；操作纪录', '现状推送分在四个地方配置，没有一处看全'),
        ('今日各推送分两组列，两组不合计', '游戏外推送四行、游戏内推送两行；列：已排程、发送中、运行中、有失败、发送、到达、曝光、点击\n弹窗写「按规则弹出 · 上架中 N 条规则」；快显没有定时，已排程写「—」', '两层数据算法不同，合计没有意义'),
        ('有失败的推送数标红', '游戏外推送：含部分失败（状态仍为已完成）\n游戏内推送：写「不适用」', '部分失败也要被看到'),
       ]),
  dict(title='总览：拿不到的格子写原因，并标明数据时点', wl=4.4,
       shots=[('m01a', [(745, 160, 1110, 340), (455, 515, 882, 612)])],
       rows=[
        ('拿不到的格子写原因，不写 0', '写「该渠道不回传」「无回执 N」「低于统计门槛」「不适用」之一；部分设备有数写「仅 Android」；今日没发写「今日未发送；已排程 HH:mm」；未切换的写「尚未切换」', '写 0 或代填会被当成真实数据'),
        ('标明数据时点与统计窗口', '每 15 分钟内更新，右上写「数据更新于 HH:mm」；表下常驻：游戏外推送的到达、点击统计至发送后 5 天（LINE 14 天），窗口内还会增长', '回执与点击陆续到达，避免把未统计完的数当最终值'),
        ('「新建 ▾」按两组列出六种推送', '每种写明发得到谁，如推播：装 App 且开启通知；快显：只发给在线玩家；选中进入该页新建表单，弹窗进入新增规则', '选之前就知道这种推送能触达谁'),
       ]),
  dict(title='待处理：发送失败、部分失败、无可发送对象集中列出', wl=4.4,
       shots=[('m01b', [(5, 154, 240, 535), (910, 154, 1200, 535)])],
       rows=[
        ('待处理列出三类一次性推送', '发送失败、部分失败·可重试、无可发送对象；每行写推送、发送时间、原因与可重试截止时间', '失败不用逐页去找'),
        ('按失败原因给下一步', '有可重试条数：重试失败部分\n系统延迟超时：复制\n全部被服务商当场拒绝：查看原因、标为已处理\n无可发送对象：复制并改受众', '不同原因的处理方式不同'),
        ('重试前先确认', '确认框写可重试条数与原因、截止时间、重发规则；短信写本次则数，如「本次 1,870 则」；重试结果更新到单条推送数据', '短信重发按则计费'),
        ('移出与不进待处理', '移出：重试后全部受理、窗口过后、标为已处理、复制并改受众后，或满 24 小时\n不进：按行为推送的失败；全部在发送前拦下的', '按行为推送逐次触发，失败在单条推送数据页处理'),
       ]),
 ]),
 dict(n=2, name='推播·列表与状态', g=0, pages=[
  dict(title='推播列表：一次性、按行为推送的状态分开计数', wl=4.4,
       shots=[('m02a', [(13, 152, 1206, 321)])],
       rows=[
        ('列表筛选与分页', '名称或 ID、受众、创建人、创建日期、发送方式、触发行为；每页 10 条，按 ID 倒序', '成熟后台（神策）同样按状态、创建人、渠道筛选'),
        ('状态计数分两套', '按行为：运行中、已暂停、已结束\n一次性：草稿、已排程、发送中、已完成、已停止、发送失败、无可发送对象\n点数字即筛选', '两种发送方式的生命周期不同'),
        ('另计「有失败可重试」', '有可重试的服务商未受理条数、且仍在重试窗口内的一次性推送；系统延迟超时的不算', '集中处理还能挽回的失败'),
        ('列表列', '名称（ID、创建人、日期）、发送方式、受众与人数、状态、发送、到达率／点击率、操作；推播到达率只算 Android，表下注明', 'iOS 不回传到达，不用发送数代填'),
        ('每行只给当前状态能做的操作', '草稿：编辑、复制、删除\n已排程：编辑、停止、复制\n发送中：停止、复制\n已完成、已停止、已结束：只读，可复制', '避免误操作；只有草稿能删，已发出的要留痕'),
       ]),
  dict(title='推播状态：部分失败也算已完成，停止不撤回已发出的', wl=4.4,
       shots=[('m02b', [(650, 109, 779, 230), (650, 343, 1247, 448)])],
       rows=[
        ('一次性推送的状态', '草稿 → 已排程（定时）／发送中（立即）→ 已完成、发送失败或已停止；到时名单或可触达为 0 人 → 无可发送对象', '每个状态对应确定的下一步'),
        ('已完成与发送失败的界线', '至少 1 条被受理即已完成（部分失败也算）；全部未受理为发送失败；全部在发送前拦下为已完成、发送 0', '失败条数与原因在单条推送数据页'),
        ('系统延迟发送', '定时推送因故障延后 2 小时内的恢复后发出；超过 2 小时不发，记发送失败「系统延迟超时」，不可重试，可复制', '过时的内容不再迟发'),
        ('按行为推送的状态', '草稿 → 运行中 ⇄ 已暂停 → 已结束；暂停可手动恢复或到时间自动恢复；生效期间结束自动结束；已结束不能恢复', '按行为推送持续运行，要能暂停与结束'),
        ('停止、暂停与复制', '已排程、发送中可停止：已发出的不撤回，自动重试取消\n暂停期间的触发不发，恢复后不补发\n全部状态可复制成新草稿，记来源 ID', '补发会集中打扰玩家'),
       ]),
 ]),
 dict(n=3, name='新建推送·内容', g=1, pages=[
  dict(title='推送内容：推播标题最多 30 字、内文最多 60 字', wl=4.4,
       shots=[('m03a', [(21, 124, 747, 272), (21, 372, 747, 420)])],
       rows=[
        ('新建表单一页五块', '推送内容 → 发送对象 → 发送时间 → 频率上限 → 确认与测试；顶部步骤条显示每块状态，点击跳到该块；弹窗保留现有规则表单', '游戏外推送四种与快显同一结构，学一次通用'),
        ('推播内容与字数', '推送名称；标题 ≤30 字；内文 ≤60 字；图片选填；计数实时显示，如「24/60」，超出变红、校验不通过；右侧同时预览 iOS 与 Android', '通知栏显示长度有限，两端样式不同'),
        ('推播点击跳转', '只能选游戏内页面：活动页面、礼包、大厅；外部链接只用于短信、Facebook、LINE', '推播点开即回到游戏'),
        ('存为草稿不校验', '任何时候可存；确认时才校验', '填到一半可先存'),
        ('文案变量（可选级）', '可插入玩家昵称、礼包名称、剩余时间、中奖金额；立即、定时只能用玩家昵称；每个变量须设取不到值时的替代文字', '取不到值时文案仍通顺'),
        ('复制到其他推送（可选级）', '保存时在所选推送方式页各生成一份草稿；推播的点击跳转不带入链接；弹窗不在可选项内', '同一内容不必重填'),
       ]),
 ]),
 dict(n=4, name='新建推送·发送对象', g=1, pages=[
  dict(title='发送对象：按标签群组选再排除，名单在开始发送时定', wl=5.0,
       shots=[('m04a', [(700, 50, 1110, 190), (690, 200, 1380, 540)])],
       rows=[
        ('立即、定时可按标签群组发', '全部玩家，或一个及以上标签群组（下拉列出当前人数，可搜索）；再选排除群组', '现状游戏外推送不能按人群发'),
        ('名单在开始发送那一刻定', '按各群组最近一次刷新的名单取并集、去重，再去掉排除群组；群组每 25 分钟刷新；确认页人数注明是预计值', '提前建好的推送按发送时的名单更准'),
        ('排除群组默认三项', 'VIP 名单（108 人）、黑名单（15 人）、机器人与测试账号（740 人）；可删可加', '这三类一般不该收到运营推送'),
        ('同一玩家只发 1 条', '多个群组重叠的只算一次；推播只发给最近一次登录的已装 App 设备', '避免重复打扰'),
        ('预计人数逐层显示', '群组人数 → 排除后人数 → 本推送可触达人数（占比）；改条件立即重算；大群组先标「估算值」，15 秒内换准确值', '成熟后台（Braze、CleverTap）选对象时同样显示可触达人数'),
       ]),
  dict(title='可触达：发送时逐人判断，可触达 0 人不能确认', wl=4.2,
       shots=[('m04b', [(10, 168, 760, 218)])],
       rows=[
        ('游戏外推送的可触达条件', '推播：装 App 且开启通知\n短信：有效手机号且未退订\nFacebook：已绑定且可发\nLINE：已加好友且未封锁\n不可触达的记原因：无联系方式、已退订、已封锁、平台限制、通知关闭', '只算本推送发得到的玩家，人少在哪一看便知'),
        ('游戏内推送的可触达条件', '弹窗：在线时进大厅、破产按规则弹出\n快显：发送时在线；不在线算受众，记「不在线」', '游戏内推送只有在线玩家看得到'),
        ('可触达在实际发送时判断', '每一人次发送时判断，不用确认时的结果；通知权限由客户端在 App 启动、回到前台时上报，服务端存最近一次的值', '名单与通知权限随时会变'),
        ('对象为 0 人不能确认', '群组 0 人：「当前群组没有玩家，不能发送」\n可触达 0 人：「当前群组没有可发送的玩家，不能确认」\n群组被停用：已排程的到时按无可发送对象处理', '发出去也没人收'),
       ]),
 ]),
 dict(n=5, name='新建推送·发送时间与按行为触发', g=1, pages=[
  dict(title='发送时间：定时限 30 天内，按行为发给触发的玩家', wl=4.1,
       shots=[('m05a', [(21, 425, 1198, 699)])],
       rows=[
        ('三种发送方式', '立即、定时、按行为；快显只有立即、按行为；弹窗按自己的规则弹出', '快显只发给在线玩家，定时到点时玩家多半不在线'),
        ('定时的时间范围', '须在 3 分钟后、30 天内，以点确认的时刻为准', '参照成熟后台：极光定时须 3 分钟后，OneSignal 30 天内'),
        ('按行为发给触发的玩家', '可加「只限这些群组」（默认不限，触发即发）与排除群组；每次触发时判断这位玩家在不在群组内', '触发条件本身已决定谁该收'),
        ('首批触发行为', '限时加码礼包快到期（剩 N 小时；默认只发给尚未购买的）、玩家升级、完成任务、通行证升级；快显另有中奖（金额不低于 N）', '覆盖现有礼包提醒与客户端写死的快显'),
        ('生效期间、提醒次数与间隔', '生效期间必填，结束日 24:00 自动结束，开始前的触发不发；每次触发最多发 N 条（默认 1），同一玩家两次提醒至少间隔 N 小时（默认 24）', '按行为推送不会无期限运行，也不会短时间重复提醒'),
        ('预计人数按近 7 天日均', '触发 → 排除后 → 可触达 → 勿扰放弃 → 频率上限拦下 → 预计发出', '按行为推送没有固定名单'),
       ]),
  dict(title='按行为推送：每次触发逐项判断，全部通过才发', wl=4.4,
       shots=[('m05b', [(779, 230, 1198, 439)])],
       rows=[
        ('每次触发的判断顺序', '生效期间与运行中 → 只限与排除群组 → 提醒次数与触发条件 → 可触达 → 勿扰（只查游戏外推送）→ 每人每天上限；全部通过才发', '前三步不通过不算受众；后三步不通过计入未送达原因'),
        ('顺延后重新判断', '勿扰顺延的到时段结束再判断触发条件与上限；条件不成立的不发，记「勿扰时段放弃」', '礼包已过期就不该再提醒'),
        ('重复触发提示', '同一推送方式已有运行中的同一触发行为时，提示「再建会重复发送」并附原推送链接；不阻止确认', '不同限定群组可以并存'),
        ('事件去重与补处理', '同一事件重复上报只触发一次；事件服务中断后补处理时重新判断条件，不成立的不发', '避免重复发与过期发'),
        ('礼包提醒在切换前不能运行', '「推荐礼包设定」为原处生效时，触发行为为「限时加码礼包快到期」的推播不能确认或恢复；确认按钮换成「保存，去切换」', '同一条提醒只在一处发'),
       ]),
 ]),
 dict(n=6, name='新建推送·频率上限、确认与测试发送', g=1, pages=[
  dict(title='确认：看人数逐步减少，全部校验通过才能确认', wl=4.4,
       shots=[('m06a', [(715, 239, 940, 352), (763, 62, 1021, 105)])],
       rows=[
        ('表单显示当前上限', '只读「推播每人每天 2 条（在「频率上限」页设置）」，可点去修改；「本条遵守频率上限」默认勾选', '上限在一处设，各推送共用'),
        ('不遵守上限须写明', '取消勾选时须选「仍计入当天条数」或「不计入」并填原因；确认页摘要写明，原因记入操作纪录', '维护公告这类通知不能被挡；留痕防滥用'),
        ('确认前校验', '内容完整、对象不为 0 人、定时时间有效、触发条件完整、生效期间有效、不遵守上限已写明；全部通过才可确认，未通过项逐项列出并标红', '一次看到全部要改的'),
        ('预计人数逐步减少', '群组 → 排除后 → 可触达 → 勿扰顺延（或放弃）→ 频率上限拦下 → 预计发出；拦下人数按近 7 天估算并注明', '成熟后台（Braze）发布前同样给确认摘要'),
        ('确认后直接生效，不设审批', '立即「确认发送」→ 发送中；定时「确认排程」→ 已排程；按行为「确认启用」→ 运行中；附摘要表', '防错靠确认页、测试发送与可停止'),
       ]),
  dict(title='测试发送：最多 10 个账号，不占上限也不计数据', wl=4.4,
       shots=[('m06b', []), ('m06c', [])],
       rows=[
        ('测试对象', '测试名单（默认「运营测试组」4 人）或输入会员编号；合计最多 10 个账号；编号不存在标红、不计入，重复的去重', '测试名单用现有标签群组，不另建'),
        ('发表单当前内容', '未保存的也发；按行为推送不等触发条件；新建与编辑页都能发；内容块必填项未填时不能发', '确认前看到玩家实际收到的样子'),
        ('测试不计入', '不占每人每天上限，不计入任何数据，不受勿扰限制，不记操作纪录；短信测试照常按则计费', '测试不影响玩家与统计'),
        ('测试结果逐行列出', '按账号与设备：已送达，或未送达及原因（如未开启通知、没有手机号）；快显为已显示或账号不在线；60 秒无回执写「无回执」', '成熟后台（Braze）测试对象不可达时同样直接报原因'),
       ]),
 ]),
 dict(n=7, name='编辑与版本', g=1, pages=[
  dict(title='编辑：运行中的改动存为新版本，只对之后的触发生效', wl=4.4,
       shots=[('m07a', [(18, 83, 1247, 157), (134, 286, 876, 402)])],
       rows=[
        ('各状态能否修改', '草稿随时改；发送中不可改，只能停止；已完成、已停止、已结束、发送失败、无可发送对象只读，可复制', '已发出的不随意改动'),
        ('已排程改后须重新确认', '按钮为「重新确认排程」，重新显示人数与拦下；确认前到时仍按原设置发', '改动经过同样的检查'),
        ('运行中、已暂停存为新版本', '只对保存之后的触发生效；状态不变；处理中的触发以触发时刻的有效版本为准', '已发出的数据要能对应当时的设置'),
        ('不可改的项', '发送方式、触发行为不可改，要换就复制成新推送', '换了会让前后版本的数据不可比'),
        ('标出改动并留快照', '改过的块标「已修改」并显示改前；确认时给改前改后对照；每次保存留快照，每一人次记所用版本', '改了什么一目了然，数据能对应版本'),
        ('版本记录可查', '单条推送数据页的版本条写起止与改动，可看当时设置，可按版本筛选数据；「本条操作纪录」跳到操作纪录页', '前后版本的数据分开看'),
       ]),
 ]),
 dict(n=8, name='短信、Facebook、LINE 的差异', g=2, pages=[
  dict(title='短信、Facebook、LINE：短信按 70 字计 1 则', wl=4.0,
       shots=[('m08a', [(618, 248, 779, 369)]), ('m08b', [(142, 324, 775, 388)])],
       rows=[
        ('与推播相同的部分', '列表、状态、表单五块、发送时间、频率上限、确认与测试、停止与重试都相同', '学一次通用'),
        ('短信按则计', '每 70 字计 1 则（含短链）：1–70 字 1 则，71–140 字 2 则；实时显示「77 字 · 2 则」；超过 5 则（350 字）校验不通过；确认块显示总则数', '服务商按则计费'),
        ('短信链接自动转短链', '内文网址换成短链，按短链计字数；点击计入数据；短链生成失败不能确认', '可统计点击，也省字数'),
        ('Facebook、LINE 的内容', '文字、图片（选填）、按钮文字、按钮链接；字数上限按平台规定；按钮链接未填标红；链接自动加追踪参数', '每位收件人独立追踪码，点击可按人统计'),
        ('预览样式', '短信：手机简讯；Facebook：Messenger 消息；LINE：官方账号消息', '按玩家实际看到的样子检查'),
        ('数据列的差异', '短信：曝光写「该渠道不回传」\nLINE：单条推送的到达写「该渠道不回传」，到达率写「—」', 'LINE 只给按日汇总的送达数'),
       ]),
 ]),
 dict(n=9, name='弹窗', g=2, pages=[
  dict(title='弹窗：现有规则表移入本后台，可排除群组、设生效期间', wl=5.0,
       shots=[('m09a', [(166, 186, 602, 238), (908, 36, 1350, 286)])],
       rows=[
        ('整页移入「弹窗」页', '「大厅弹窗顺序设定」移入侧栏；规则、ID、历史数据不变；现有标签对象按原 ID 转为标签群组', '只有一份规则，不会重复弹出'),
        ('对象与排除', '对象：全部玩家或一个标签群组；排除可多选标签群组，或选另一条规则的对象；显示群组、排除与预计人数', '现状对象不能排除，活动类规则会重叠'),
        ('生效期间', '选填，不填长期有效；期间外不弹出，列表写「未到生效期间」或「已过生效期间」', '现状规则没有生效期间'),
        ('排序与新手两项', '拖动调整先后，排在前面的先弹；新手挑战、新手通行证改为排序项，排最前，计入弹出数量；旧版客户端照旧写死', '现状只能逐项改顺序号，新手弹窗写死在客户端'),
        ('列表新增数据', '今日曝光；点击率＝点击÷曝光（曝光 0 写「—」）；上限提示条；数据更新时间', '现状列表看不到曝光、点击'),
       ]),
  dict(title='弹窗重叠：保存前列出重叠人数，可一键排除', wl=4.8,
       shots=[('m09b', [(1106, 223, 1453, 417)])],
       rows=[
        ('重叠检查', '同一位置、同一弹窗类型的上架规则对象有交集时，逐条列出规则与重叠人数', '重叠的人两条规则都会弹，占每人每天上限'),
        ('一键排除', '一般给「排除规则 N 的对象」；对方为全部玩家时给「在规则 5 中排除本规则的对象」，两条规则各记一条操作纪录', '本规则不会因排除全体玩家而变成 0 人'),
        ('「规则 N 的对象」实时计算', '跟随规则 N 当前对象；规则 N 下架或删除即失效、标红提示；不能互相排除；规则 5 已被他人修改时两条都不保存', '被引用的规则改了对象，排除自动跟着变'),
        ('下发时按上限截断', '找出命中规则 → 按排序取项目 → 按当天剩余额度截断 → 按间隔安排 → 下发；弹出 1 个计 1，大厅与破产合计', '每人每天弹窗上限在下发时生效'),
        ('额度占用', '同一玩家的大厅、破产请求串行处理；已返回未上报显示的占额度，5 分钟未上报释放', '并发下不超发'),
       ]),
 ]),
 dict(n=10, name='快显', g=2, pages=[
  dict(title='快显：只发给在线玩家，到有效期未显示就丢弃', wl=4.2,
       shots=[('m10a', [(215, 659, 666, 756), (21, 861, 650, 909)])],
       rows=[
        ('只发给在线玩家', '立即：确认发送时在线的；按行为：触发时在线的；不在线的算受众，记「不在线」，不下发；没有定时', '玩家不在线看不到快显'),
        ('快显内容', '横幅文字 ≤30 字（繁體）；显示位置（目前只有大厅顶部横幅）；停留秒数；点击跳转只选游戏内页面', '横幅只停留数秒，文字要短'),
        ('下发与有效期', '通过现有长连接下发；下发后 30 分钟仍未显示的由客户端丢弃，不计曝光；退出登录一并丢弃', '过时的横幅不再显示'),
        ('计数与截断', '下发前查当天已显示次数（含已下发未上报），到上限不下发，记「频率上限拦下」；显示 1 次计 1', '快显上限在下发前就生效'),
        ('不在大厅与多条', '在房间内的回到大厅后显示（有效期内、同一次登录）；多条按到达先后依次显示；点击按跳转打开并上报', '显示位置只有大厅顶部横幅'),
        ('列表与状态', '列：ID、名称、发送方式、状态、曝光、点击、点击率；发送、到达写「不适用」；立即：草稿 → 发送中 → 已完成或已停止；按行为同推播', '游戏内推送从曝光算起'),
       ]),
 ]),
 dict(n=11, name='频率上限与勿扰', g=3, pages=[
  dict(title='频率上限：每种推送每人每天各有上限，到上限不补发', wl=4.4,
       shots=[('m11a', [(303, 196, 424, 769)])],
       rows=[
        ('游戏外推送的默认上限', '推播 2 条；短信、Facebook、LINE 各 1 条；四种各自计数；服务商受理成功计 1 条', '受理当下就能确定；到达回执会延迟或没有'),
        ('游戏内推送的默认上限', '弹窗 8 个（大厅与破产合计），弹出 1 个计 1；快显 3 次，显示 1 次计 1', '玩家看到才算打扰'),
        ('两层分开计', '游戏内推送不占游戏外推送的条数，反之亦然', '两层打扰的场合不同，一层发得多不挤掉另一层'),
        ('到上限当天不再发', '不排队补发；次日 00:00（台湾时间）重新计数；记「频率上限拦下」；每行显示今日被拦下人数', '补发会集中打扰；成熟后台（Braze、OneSignal、神策）同样不补发'),
        ('截断顺序与预占', '游戏外推送：按发送先后\n快显：按触发先后；弹窗：按排序\n提交前预占 1 个名额，未受理时释放', '并发发送时不超发'),
        ('游戏外合计上限（可选级）', '默认关；开启后四种合计，与各自上限同时生效', '已定各推送分开计；合计上限只作可选'),
       ]),
  dict(title='勿扰：只管游戏外推送，定时的顺延，按行为推送的放弃', wl=4.1,
       shots=[('m11b', [(45, 191, 779, 240)])],
       rows=[
        ('勿扰时段', '默认开，00:00–08:00（台湾时间）；可跨午夜；只管推播、短信、Facebook、LINE，四种共用一个时段', '游戏内推送玩家在游戏里才看得到，不受勿扰时段限制'),
        ('命中时的处理', '立即、定时默认顺延到时段结束；按行为默认放弃；每条推送可改，不能单独设时段', '礼包剩 2 小时的提醒顺延到早上已过期'),
        ('顺延与放弃怎么记', '顺延的到时段结束再判断上限后发出；放弃的记「勿扰时段放弃」，计入未送达原因', '放弃的人次在数据看板与玩家查询可查'),
        ('修改设置', '保存前列出改前→改后与按近 7 天估算的影响；对之后的发送生效；两人同时改时后保存者须刷新', '改之前看到会多拦下或多放弃多少人'),
        ('中途调整上限', '调低：已达新上限的当天不再收到\n调高：立即放行，已拦下的不补发\n上限为正整数，最大 99', '已拦下的不回头补发'),
        ('弹窗间隔（可选级）', '默认关；开启后同一位置两个弹窗间隔不少于 N 秒；排序项勾选了「忽略间隔」的弹窗不受间隔限制', '成熟后台（MoEngage）有全局最小间隔，可单条豁免'),
       ]),
 ]),
 dict(n=12, name='数据看板与指标统计方法', g=3, pages=[
  dict(title='指标：游戏外从发送算起，游戏内从曝光算起', wl=4.0,
       shots=[('m12a', [(368, 246, 811, 311), (13, 883, 950, 960)])],
       rows=[
        ('游戏外推送的指标', '发送＝服务商受理条数（含受理后退回）；到达＝回执为送达；到达率＝到达÷发送；点击率＝点击÷发送', '点击÷到达算不出：iOS 推播没有到达'),
        ('游戏内推送的指标', '曝光＝弹出或显示 1 次计 1；点击率＝点击÷曝光；发送、到达写「不适用」', '游戏内推送没有发送、到达两步'),
        ('各推送的数据来源', '推播 Android：客户端回执；推播 iOS：不回传到达、曝光；短信：运营商回执；Facebook：送达、已读回调；LINE：只有按日汇总送达，曝光不足 20 人不返回', '各服务商能回传的步骤不同'),
        ('拿不到的数写原因', '该渠道不回传、无回执、低于统计门槛、不适用四种；部分设备有数写「仅 Android」；不估算，不用上一步代填', '代填会让 iOS 推播到达率显示成 100%；成熟后台（OneSignal、CleverTap）同样不代填'),
        ('统计窗口与归属', '游戏外推送的到达、点击统计至发送后 5 天（LINE 14 天），按发送日期归属；人群按发送时所在群组，都不属于的计入「其余」，各行不相加', '回执与点击陆续到达'),
       ]),
  dict(title='数据看板：按推送、人群、日期查看，未送达原因单列', wl=5.0,
       shots=[('m12b', [(13, 77, 1263, 125), (521, 246, 1350, 327)])],
       rows=[
        ('筛选', '日期：今日、近 7 天（默认）、近 30 天、自定义（不超过 1 年）；人群；推送方式（可多选）', '三个页签共用一套筛选'),
        ('各推送页签', '游戏外推送表：推播按 Android、iOS 分两行；表头写分母\n游戏内推送表：大厅弹窗、破产弹窗、快显', 'iOS 不回传到达与曝光，分开列才不失真'),
        ('按人群、按日期', '两层各一张表，可切换指标（默认点击率）；选到达率时游戏内各列写「不适用」', '目标要求发送量、到达率按人群可查'),
        ('未送达原因', '游戏外推送分三组：发送前拦下、服务商未受理、受理后退回；每行可导出名单（按玩家去重）', '现状查不到没送达的原因'),
        ('推送明细与导出', '列出所选日期内发送过的推送，两层分列，名称链接到单条推送数据；导出 Excel 四张表，量大时后台生成，文件保留 7 天', '需求清单要求按单条推送查看并可导出'),
       ]),
 ]),
 dict(n=13, name='单条推送数据与失败重试', g=3, pages=[
  dict(title='单条推送：从受众到点击，每步写明少了多少人、为什么', wl=5.0,
       shots=[('m13a', [(690, 321, 1350, 434)])],
       rows=[
        ('入口与顶部', '从数据看板、各推送列表、总览待处理、玩家查询进入，「返回」回到来源；顶部写名称、状态、设置摘要，失败时写失败条数、原因与可重试截止时间', '失败信息放在顶部，打开就能处理'),
        ('游戏外推送的漏斗', '受众 → 发送 → 到达 → 曝光 → 点击；每步写比上一步少多少、少在哪', '现状数据分散，看不出少在哪一步'),
        ('游戏内推送的漏斗', '受众 → 曝光 → 点击；受众与曝光之差写不在线、频率上限拦下', '游戏内推送没有发送、到达两步'),
        ('发送前拦下四项', '无联系方式（含已退订、已封锁、平台限制）、通知关闭、勿扰时段放弃、频率上限拦下；每人次只记第一个原因，四项相加等于总数；可导出名单', '只记一个原因，各项相加才等于总数'),
        ('统计范围与拆分', '今日、近 7 天（默认）、自生效起、自定义；可按版本筛选；推播按设备、人群、小时拆分，短信、Facebook、LINE 按人群、小时', 'iOS 不回传到达，按设备拆开才看得清'),
       ]),
  dict(title='失败重试：自动重试 3 次，之后 24 小时内可手动重试', wl=5.0,
       shots=[('m13b', [(771, 221, 997, 294)])],
       rows=[
        ('服务商未受理分两种', '可重试：超时、临时错误\n当场拒绝：令牌失效、号码无效、内容格式错误、平台拒绝；不重试，记原因', '不对无效号码反复发'),
        ('自动重试', '30 分钟内重试 3 次（第 5、15、30 分钟），每次前重新判断勿扰与上限', '运营不用处理大量瞬时失败'),
        ('手动重试', '自动重试结束起 24 小时内可「重试失败部分」，只重发可重试的；同一人只计 1 条上限；按行为推送只重发条件仍成立的人次', '按行为推送的条件可能已不成立，如礼包已过期'),
        ('不重复发送', '每一人次有唯一消息编号，重试沿用；服务商不支持去重时先查状态再重发', '超时的那次可能已被受理'),
        ('未受理与退回怎么计', '服务商未受理：不计发送、不占上限\n受理后退回：计入发送与上限，不计到达', '受理才算发出；退回发生在受理之后'),
       ]),
 ]),
 dict(n=14, name='玩家查询', g=3, pages=[
  dict(title='玩家查询：先看能否收到，再看近 30 天收到与拦下', wl=4.3,
       shots=[('m14a', [(513, 201, 1279, 628)]), ('m14b', [(940, 168, 1350, 523)])],
       rows=[
        ('查询方式', '会员编号、会员昵称或完整手机号码任填一项；昵称重名时列候选；手机号中间打码显示', '现状只能查弹窗顺序'),
        ('各推送能否收到', '分游戏外推送、游戏内推送两组；能收到写依据，不能写原因（如未装 App、已退订、未绑定 Facebook）；另列所属标签群组', '判断与可触达相同，查清「该收没收到」'),
        ('今日已收与上限', '如「推播 2／2 条」；达上限标红；测试发送与「不计入」的不计', '查没收到的原因时先看是否已达上限'),
        ('收到记录', '近 30 天倒序；收到与被拦下都列：已到达、已点击、勿扰顺延或放弃、频率上限拦下、未送达原因；一次进大厅记一行', '成熟后台（Braze、OneSignal）同样列出收到与拦下记录'),
        ('不逐条记的情况', '不可触达的写在「能否收到」；不在受众内的不记；快显不在线、过期未显示的不记', '玩家没有看到的不算收到'),
        ('筛选与导出', '按推送方式、结果、日期筛选，可导出；两张弹窗顺序表照旧', '原「玩家弹窗顺序查询」的内容不丢'),
       ]),
 ]),
 dict(n=15, name='操作纪录与权限', g=4, pages=[
  dict(title='操作纪录与权限：写操作全部留痕，只增不改不删', wl=5.0,
       shots=[('m15a', [(13, 442, 1350, 507), (13, 845, 1350, 1039)])],
       rows=[
        ('两种角色', '运营：全部操作\n只读：看全部页面与数据、可导出；不显示新建、操作列与保存', '不设审批，按角色分权'),
        ('服务端校验', '每个写操作在服务端校验角色；只隐藏按钮不算权限控制', '只隐藏按钮，仍可绕过页面直接操作'),
        ('记录范围', '新建、编辑（改前改后）、删除、复制、确认、停止、暂停、恢复、结束、重试、标为已处理、弹窗规则、上限与勿扰、切换开关；测试发送不记', '每次改动都能追到人'),
        ('系统自动的变化也记', '到时开始发送、发送结束、无可发送对象、发送失败、自动恢复、生效期间结束；操作人写「系统」', '每条推送可追到操作人与原因'),
        ('不可改与查询', '只增不改不删，长期保留；原弹窗页「操作纪录」页签移到侧栏，原有纪录保留；按时间、操作人、对象、推送方式、操作筛选', '纪录能改就失去留痕作用'),
       ]),
 ]),
 dict(n=16, name='迁移与切换', g=4, pages=[
  dict(title='礼包提醒迁移：在礼包后台选定一条推播即切换，可切回', wl=4.5,
       shots=[('m16a', [(28, 23, 1189, 249), (4, 765, 1214, 934)])],
       rows=[
        ('同一条推送只在一处发', '每项迁移一个切换开关：原处生效／本后台生效；一次切换同时改两处，不存在两处都发或都不发的时段', '切换期间玩家不会收到两次'),
        ('礼包提醒切到本后台', '运营在「推荐礼包设定」页切换，须选定一条触发行为为「限时加码礼包快到期」的草稿或已暂停推播；切换后推播时间与标题只读、礼包后台停发', '运营自己切换，不用等研发'),
        ('原设置对应到推播', '「还剩 2 小时」→ 触发条件剩 2 小时、只发给尚未购买的；标题照搬；内文在推播页填写', '迁移不丢设置'),
        ('切回原处与切换瞬间', '切回：同一触发行为的运行中推播全部暂停，礼包后台恢复编辑与发送\n切换瞬间：按事件发生时刻分，同一次只发 1 条', '切回后提醒不中断，也不重复'),
        ('关联推播被暂停或结束', '礼包后台不恢复发送，本页提示；已结束的可直接改选另一条推播', '自动恢复礼包后台会与推播重复发送'),
       ]),
  dict(title='短信、Facebook、LINE：从营销侧逐种切到本后台', wl=0, shots=[],
       rows=[
        ('短信、Facebook、LINE 逐种切换', '研发逐种打开开关；切换后该推送方式的新推送只能在本后台建；切换前检查：服务商发送联调通过、回执与退订或封锁状态回传可用、退订名单与绑定状态已导入、测试发送通过', '逐种切，出问题只影响一种'),
        ('切换前已排程的', '在营销侧发完，不在本后台重建；切换当天营销侧发出的不计入本后台的每人每天上限', '不用逐条重建'),
        ('切回营销侧', '本后台已排程、运行中的照常发完或运行，可停止、暂停；页顶与总览写明当前在哪发', '已排程的不中途改发送方'),
        ('快显改为服务端下发', '切换前把现有写死的快显逐条建好并启用；开关打开后客户端停用写死内容，关闭即恢复；不支持下发的旧版客户端照旧写死，服务端不向其下发', '同一玩家不会看到两次'),
        ('弹窗与玩家查询', '上线时整页移入；原菜单入口可恢复为原页面', '规则只有一份，不受影响'),
        ('切换前的数据', '留在原处（营销侧、数据平台、原推播报表），不导入数据看板', '两处口径不同，不混在一起'),
       ]),
 ]),
 dict(n=17, name='性能与合规', g=4, pages=[
  dict(title='性能：预计人数 15 秒内准确，推播 15 分钟内发完', wl=0, shots=[],
       rows=[
        ('预计人数', '改条件后估算值 2 秒内显示，准确值 15 秒内替换', '15 秒与原型一致；2 秒为暂定值'),
        ('发送吞吐', '推播：全部玩家（约 74,480 人）15 分钟内提交服务商；短信、Facebook、LINE：不低于每秒 50 条', '暂定值；短信等按服务商限速定'),
        ('发送时效', '定时到点后 1 分钟内开始；按行为事件发生到提交不超过 1 分钟；快显事件到下发不超过 5 秒', '暂定值；快显发给在线玩家，要及时'),
        ('数据与查询时效', '看板、总览每 15 分钟内更新；玩家查询结果 5 分钟内可查、3 秒内返回；列表与看板近 30 天 3 秒内返回', '15 分钟与原型一致；其余为暂定值'),
        ('保留期', '逐人明细 30 天；汇总、版本快照、操作纪录长期；每人每天计数 7 天；导出文件 7 天', '逐人明细 30 天与原型一致；其余为暂定值'),
        ('时区与审计', '全部按台湾时间计算与显示；每条推送可追到操作人、版本、逐人结果', '与原型一致'),
       ]),
  dict(title='合规：已退订、已封锁、平台限制的都在发送前拦下', wl=0, shots=[],
       rows=[
        ('短信退订', '服务商回传退订后标记，之后发送前拦下，记「已退订」；切换前导入现有退订名单；内文不含「退訂」时提示，不阻止确认', '短信须给玩家退订方式'),
        ('个人资料保护', '手机号中间打码，按手机号查询须完整号码；导出名单只含会员编号；追踪码不带个人明文；逐人明细 30 天后删除', '查询与导出不暴露个人资料'),
        ('Facebook 平台政策', '只发给已绑定且可发的；不在 Meta 发送范围的发送前拦下，记「平台限制」；平台拒绝记当场拒绝，不重试', '平台政策限制发送范围，违规会被拒发'),
        ('LINE 平台政策', '只发给已加好友且未封锁的；平台拒绝或超出消息额度记当场拒绝，不重试', '被封锁或超额度时重发也会被拒'),
        ('推播通知权限', '只发给开启通知的玩家；关闭的记「通知关闭」', '关闭通知的玩家收不到推播'),
       ]),
 ]),
]

GLOSSARY = [
 ('术语：推送、对象与可触达', [
  ('游戏外推送', '不在游戏里也收得到的推送：推播、短信、Facebook、LINE'),
  ('游戏内推送', '在游戏里才看得到的推送：弹窗、快显'),
  ('推送方式', '六种：推播、短信、Facebook、LINE、弹窗、快显'),
  ('推送', '某种推送方式下的一项发送任务，有推送 ID；弹窗以规则为单位，有规则 ID'),
  ('一次性推送', '发送方式为立即或定时的推送'),
  ('按行为推送', '玩家发生指定行为（如礼包快到期）时，发给这位玩家的推送'),
  ('标签群组', '在「会员标签设定」里用几个会员标签组合出的玩家群，如新增、回流、潜在付费、潜在流失；名单每 25 分钟刷新'),
  ('排除群组', '从发送对象中去掉的标签群组'),
  ('受众', '符合发送对象条件的玩家；按行为推送按触发人次计'),
  ('可触达', '受众中本推送发得到的玩家，如推播要装 App 且开启通知'),
 ]),
 ('术语：发送、到达与拦下', [
  ('服务商', '接收发送请求的一方：推播为推送服务；短信为短信服务商；Facebook、LINE 为各自平台'),
  ('发送', '游戏外推送被服务商受理的条数，含受理后退回的'),
  ('到达', '服务商回执为送达的条数；只有游戏外推送有'),
  ('曝光', '玩家看到的次数；游戏内推送弹出或显示 1 次计 1'),
  ('点击', '游戏外推送：点开推送或推送里链接的次数\n游戏内推送：点了弹窗或快显的次数'),
  ('发送前拦下', '受众中因规则没有发出的人次：无联系方式、已退订、已封锁、平台限制、通知关闭、勿扰时段放弃、频率上限拦下'),
  ('服务商未受理', '提交了但服务商没有接下的条数，分可重试与当场拒绝；不计入发送'),
  ('受理后退回', '服务商受理后又退回的条数；计入发送，不计入到达'),
  ('频率上限拦下', '当天该推送方式已达每人每天上限，没有发出'),
  ('勿扰时段', '游戏外推送不发的时段，默认 00:00–08:00（台湾时间）'),
 ]),
 ('术语：状态与拿不到的数怎么写', [
  ('发送失败', '一次性推送的状态：提交后全部未受理，或系统延迟超过 2 小时未开始'),
  ('部分失败', '已完成的推送中有服务商未受理的条数'),
  ('无可发送对象', '开始发送时名单或可触达为 0 人'),
  ('该渠道不回传', '服务商本身不提供这一步，如 iOS 推播的到达'),
  ('无回执', '已受理，但统计窗口内没收到这一条的回执；不算失败，也不算到达'),
  ('低于统计门槛', '服务商只在人数达到门槛时才返回，如 LINE 曝光不足 20 人'),
  ('不适用', '这一层或这种推送方式没有这一项，如游戏内推送的发送、到达'),
  ('统计窗口', '游戏外推送的到达、点击统计至发送后 5 天（LINE 14 天）'),
  ('原处生效／本后台生效', '切换开关的两种状态：推送在原来的地方发，或在推送统一后台发'),
 ]),
]


# ───────── 章节（进度条）：五组模块＋附录 ─────────
CH = [(g[0], g[1], NAVY) for g in GROUPS] + [('附录', '附录', GRAY)]
NCH = len(CH)
CH_PAGE = {}


def progress(s, ci):
    gap = 0.08; w = (CW - gap * (NCH - 1)) / NCH
    for i, (num, name, col) in enumerate(CH):
        x = X0 + i * (w + gap)
        on = i == ci
        lc = col if on else MUTE; bc = col if on else 'E2DED5'
        T(s, x, 0.17, w, 0.24, (num + ' ' + name) if num != '附录' else '附录', 10.5, lc, on, ls=1.0, check=False)
        R(s, x, 0.44, w, 0.055 if on else 0.035, fill=bc, line=None, r=0)


def badge(s, x, y, d, num, col, size, txt='FFFFFF'):
    R(s, x, y, d, d, fill=col, line=None, r=d * 0.16)
    T(s, x - 0.1, y, d + 0.2, d, num, size, txt, True, align=C, anchor=MID, ls=1.0, check=False)


def new_slide(bg=BG):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(bg)
    return s


def page(ci, kicker, title):
    """ci：章节序号（None 表示封面、目录）；kicker：页眉小字"""
    s = new_slide()
    n = len(prs.slides)
    if ci is not None:
        progress(s, ci)
        if ci < NCH - 1:
            badge(s, X0, 0.64, 0.3, CH[ci][0], NAVY, 13)
            T(s, X0 + 0.42, 0.62, 10, 0.32, kicker, 13, NAVY, True, anchor=MID, ls=1.0, spc=60, check=False)
        else:
            T(s, X0, 0.62, 10, 0.32, kicker, 13, GRAY, True, anchor=MID, ls=1.0, spc=60, check=False)
    T(s, X0, 0.98, CW + 0.4, 0.62, title, TS, NAVY, True, ls=1.1, check=False)
    if tw(title, TS) * 1.04 > CW + 0.4:
        WARN.append('title p%d too wide %.2f  %s' % (n, tw(title, TS) * 1.04, title))
    T(s, X0, 6.98, 6, 0.25, FOOT + '　·　第 ' + str(n) + ' 页', 11, MUTE, check=False)
    TITLES.append((n, ci, kicker, title))
    LINES.append((n, '标题', kicker + '｜' + title))
    return s


# ───────── 需求表：编号｜需求｜规则与取值｜为什么这样定｜结论（空，评审时填） ─────────
FS = 11; LS = 1.18; LH = FS * LS / 72; PADX = 0.08; PADY = 0.055
COLS = [('编号', 0.6), ('需求', 0.25), ('规则与取值', 0.48), ('为什么这样定', 0.27), ('结论', 0.6)]   # 编号、结论为固定宽（英寸），其余按剩余宽度分


def _cw_tbl(ch):
    # 表格估行用：→ ⇄ ≤ ÷ × 等按全角计
    if unicodedata.east_asian_width(ch) == 'A' or ch in '→⇄≤÷×—–':
        return 1.0
    return cw(ch)


def wrap_lines(text, w, size=FS):
    """估算一段文字在宽 w 英寸内的行数（逐字累加宽度；拉丁字母按词不拆）"""
    total = 0
    for para in text.split('\n'):
        lines = 1; cur = 0.0
        tokens = []
        buf = ''
        for ch in para:
            if ch.isascii() and ch not in ' ':
                buf += ch
            else:
                if buf:
                    tokens.append(buf); buf = ''
                tokens.append(ch)
        if buf:
            tokens.append(buf)
        for tk in tokens:
            tw_ = sum(_cw_tbl(c) for c in tk) * size / 72
            if cur + tw_ > w and cur > 0:
                lines += 1; cur = 0.0
                if tk == ' ':
                    continue
            cur += tw_
        total += lines
    return total


def row_height(cells, widths):
    n = max(wrap_lines(t, w - 2 * PADX - 0.1) for t, w in zip(cells, widths) if t)
    return n * LH + 2 * PADY, n


def table_height(w, rows):
    rest = w - COLS[0][1] - COLS[4][1]
    widths = [COLS[0][1]] + [rest * f for _, f in COLS[1:4]] + [COLS[4][1]]
    return 0.38 + sum(row_height(['0.00', a, b, c], widths[:4])[0] for a, b, c in rows)


def req_table(s, x, y, w, rows, mno, start, ymax):
    rest = w - COLS[0][1] - COLS[4][1]
    widths = [COLS[0][1]] + [rest * f for _, f in COLS[1:4]] + [COLS[4][1]]
    xs = [x]
    for ww in widths[:-1]:
        xs.append(xs[-1] + ww)
    hh = 0.36
    R(s, x, y, w, hh, fill=HEAD, line=None, r=0.05)
    for (nm, _), cx, ww in zip(COLS, xs, widths):
        T(s, cx + PADX, y, ww - 2 * PADX, hh, nm, 11.5, GRAY, True, anchor=MID, ls=1.0, check=False)
    yy = y + hh + 0.02
    for k, (req, rule, why) in enumerate(rows):
        no = '%d.%d' % (mno, start + k)
        cells = [no, req, rule, why]
        h, nl = row_height(cells, widths[:4])
        T(s, xs[0] + PADX, yy + PADY, widths[0] - PADX, h - PADY, no, FS, GRAY, True, ls=LS, check=False)
        T(s, xs[1] + PADX, yy + PADY, widths[1] - 2 * PADX, h - PADY, req.split('\n'), FS, NAVY, True, ls=LS, check=False)
        T(s, xs[2] + PADX, yy + PADY, widths[2] - 2 * PADX, h - PADY, rule.split('\n'), FS, INK, ls=LS, check=False)
        if why:
            T(s, xs[3] + PADX, yy + PADY, widths[3] - 2 * PADX, h - PADY, why.split('\n'), FS, GRAY, ls=LS, check=False)
        R(s, xs[4] + 0.06, yy + 0.06, widths[4] - 0.1, h - 0.12, fill='FFFFFF', line=LINE, lw=0.75, r=0.04)
        LN(s, x, yy + h, x + w, yy + h, LINE, 0.75)
        yy += h
        LINES.append((len(prs.slides), '需求行', no + ' ' + req))
    if yy > ymax + 0.01:
        WARN.append('table overflow p%d: %.2f > %.2f (module %d)' % (len(prs.slides), yy, ymax, mno))
    return yy


def shot_stack(s, x, y, wl, hmax, shots):
    """竖排放一张或几张截图，按列宽与可用高度等比缩放"""
    gap = 0.14
    sizes = [(SHOTS[k][1], SHOTS[k][2]) for k, _ in shots]
    maxw = max(W for W, H in sizes); sumh = sum(H for W, H in sizes)
    k_ = min(wl / maxw, (hmax - gap * (len(shots) - 1)) / sumh)   # 英寸/像素
    yy = y
    for (key, boxes), (W, H) in zip(shots, sizes):
        shot(s, key, x, yy, w=W * k_, boxes=boxes)
        yy += H * k_ + gap
    return k_


# ══════════════════════ 生成 ══════════════════════
SHOTS = {}
for m in MODULES:
    for pg in m['pages']:
        for key, _ in pg['shots']:
            if key not in SHOTS:
                SHOTS[key] = clean_shot(key)

# 封面
s = new_slide()
R(s, X0, 2.95, 0.85, 0.08, fill=BLUE, line=None, r=0.04)
T(s, X0, 3.25, 11, 1.0, '推送系统的后台集成需求', 46, NAVY, True, ls=1.1, check=False)
TITLES.append((1, None, '封面', '推送系统的后台集成需求'))

TOC = page(None, '', '目录')
MOD_PAGE = {}
for m in MODULES:
    no = m['n']; start = 1
    for pi, pg in enumerate(m['pages']):
        kick = '%s · 模块 %d%s' % (GROUPS[m['g']][1], no, '（续）' if pi else '')
        s = page(m['g'], kick, pg['title'])
        if pi == 0:
            MOD_PAGE[no] = len(prs.slides)
            CH_PAGE.setdefault(m['g'], len(prs.slides))
        ytop = 1.9; ybot = 6.9
        if pg['wl'] and pg['shots']:
            # 截图列尽量放宽（最宽 6.0 英寸），以表格放得下为限，截图里的字才看得清
            wl = pg['wl']
            for cand in [5.6, 5.4, 5.2, 5.0, 4.8, 4.6, 4.4]:
                if cand > wl and table_height(XR - (X0 + cand + 0.3), pg['rows']) <= ybot - ytop:
                    wl = cand
                    break
            shot_stack(s, X0, ytop, wl, ybot - ytop, pg['shots'])
            tx = X0 + wl + 0.3
        else:
            tx = X0
        req_table(s, tx, ytop, XR - tx, pg['rows'], no, start, ybot)
        start += len(pg['rows'])
    m['rows_total'] = start - 1

# 附录：术语
CH_PAGE[NCH - 1] = len(prs.slides) + 1
for pi, (gt, chunk) in enumerate(GLOSSARY):
    s = page(NCH - 1, '附录 · 术语' + ('（续）' if pi else ''), gt)
    y = 1.95; c1 = 2.6
    R(s, X0, y, CW, 0.36, fill=HEAD, line=None, r=0.05)
    T(s, X0 + 0.15, y, c1, 0.36, '术语', 11.5, GRAY, True, anchor=MID, ls=1.0, check=False)
    T(s, X0 + c1 + 0.15, y, CW - c1, 0.36, '含义', 11.5, GRAY, True, anchor=MID, ls=1.0, check=False)
    y += 0.38
    for term, d_ in chunk:
        nl = wrap_lines(d_, CW - c1 - 0.3, 12)
        h = nl * 12 * 1.25 / 72 + 0.14
        T(s, X0 + 0.15, y + 0.07, c1 - 0.2, h, term, 12, NAVY, True, ls=1.25, check=False)
        T(s, X0 + c1 + 0.15, y + 0.07, CW - c1 - 0.3, h, d_.split('\n'), 12, INK, ls=1.25, check=False)
        LN(s, X0, y + h, XR, y + h, LINE, 0.75)
        y += h
    if y > 6.85:
        WARN.append('glossary overflow p%d %.2f' % (len(prs.slides), y))

# 目录：按组列出模块与页码
s = TOC
colx = [X0, X0 + CW / 2 + 0.2]; colw = CW / 2 - 0.2
cols_ = [[0, 1, 2], [3, 4, 5]]
for ci_, gl in enumerate(cols_):
    y = 1.85
    for g in gl:
        if g < len(GROUPS):
            gnum, gname = GROUPS[g]
            badge(s, colx[ci_], y + 0.05, 0.3, gnum, NAVY, 13)
            T(s, colx[ci_] + 0.42, y, colw, 0.4, gname, 15, NAVY, True, anchor=MID, ls=1.0, check=False)
            y += 0.44
            for m in MODULES:
                if m['g'] != g:
                    continue
                T(s, colx[ci_] + 0.42, y, colw - 1.6, 0.3, '%d　%s' % (m['n'], m['name']), 13, INK, anchor=MID, ls=1.0, check=False)
                T(s, colx[ci_] + colw - 1.2, y, 1.2, 0.3, '第 %d 页' % MOD_PAGE[m['n']], 12, MUTE, align=RT, anchor=MID, ls=1.0, check=False)
                LN(s, colx[ci_] + 0.42, y + 0.31, colx[ci_] + colw, y + 0.31, LINE, 0.5)
                y += 0.33
            y += 0.12
        else:
            T(s, colx[ci_] + 0.42, y, colw, 0.4, '附录 · 术语', 15, GRAY, True, anchor=MID, ls=1.0, check=False)
            T(s, colx[ci_] + colw - 1.2, y, 1.2, 0.4, '第 %d 页' % CH_PAGE[NCH - 1], 12, MUTE, align=RT, anchor=MID, ls=1.0, check=False)

# ══════════════════════ PowerPoint 节：封面与目录、每组一节、附录一节 ══════════════════════
starts = [(1, '封面与目录')] + [(CH_PAGE[i], (CH[i][0] + ' ' + CH[i][1]) if i < NCH - 1 else '附录') for i in range(NCH)]
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
print('rows per module:', ', '.join('%d:%d' % (m['n'], m['rows_total']) for m in MODULES), '｜total', sum(m['rows_total'] for m in MODULES))
for n, ci, k, t in TITLES:
    print('%2d  %-24s %s' % (n, k, t))
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        for n, pos, t in LINES:
            f.write('%d\t%s\t%s\n' % (n, pos, t))
if WARN:
    print('--- warnings')
    for w in WARN:
        print(w)
