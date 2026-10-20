# 推送统一后台 · 设计概要（给团队自己人看的设计层概要，需求评审用；不含字段、接口、错误码等实现层细节）
# 用法：
#   python3 an_推送后台_设计概要.py [输出.pptx] [措辞测试句子.tsv]   生成 pptx（默认 推送系统后台集成需求/5_设计概要.pptx）
#   python3 an_推送后台_设计概要.py --crop <整页截图目录>              由原型整页截图重新裁出 分析/推送后台_设计概要/ 下的配图
#   需要 python-pptx、pillow（另建 venv 安装）。
# 结构：封面 → 一 总览（一页总图；背景、范围与关键决定）→ 二 运营怎么用（7 件事）→ 三 各模块（9 页，每页原型截图＋编号标注）
#       → 四 取舍、依赖与验收 → 附录（完整材料、术语表；PowerPoint 单独一节，可折叠）。
# 截图做法：3_原型.html 另存到临时目录，每页一份（只显示该页 section；html{width:1280px;transform:scale(2)} 得 2 倍清晰度；
#   隐藏原型自带的紫色编号 .co、紫框 .hl、「新增／改」标记 .mk、蓝色虚线框；取消淡化），
#   用 _scripts/pl_网页截图.swift 以 2560 宽截整页，存为 <截图目录>/p1.jpg … p16.jpg；
#   再用 _scripts/pl_图片裁剪.swift 按下方 CROPS 坐标裁出关键区域（坐标为 2 倍截图的像素）。
# 版面沿用 an_呈交版V4_设计版.py 的配色、字号与组件（helper 复制自该文件，未改原文件）。
# 依据：2_方案设计.html（11 条决定与附录规则）、1_需求清单.html、3_原型.html、4_需求文档.md（第 2、3、9 章）、
#   an_推送后台_需求评审稿.py 里按模块整理的规则与理由（挑选，不照搬）。
# 颜色语义（全稿固定）：蓝＝游戏外推送，绿＝游戏内推送，红＝拦下与失败，深蓝圆点＝截图上的编号标注。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, math, unicodedata, uuid, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
IMG = os.environ.get('DECK_IMG', BASE + '分析/推送后台_设计概要/')   # 配图目录；试排版时可指向草稿目录
FONT = 'Microsoft YaHei'
FOOT = '推送统一后台 · 设计概要'

# ───────── 原型截图：按元素裁图（10/15 改：不再手量像素坐标） ─────────
# 每张配图＝原型某页里几个元素的外接框（再留边）；编号圆点按「锚点元素」自动放在其旁边的留白处。
# 元素用 (CSS 选择器, 文字片段) 找：该页 section 内第一个匹配选择器、且文字含该片段的元素（片段为 None 则取第一个）。
# 生成：python3 an_推送后台_设计概要.py --crop <截图目录>
#   逐页把 3_原型.html 另存一份（只显示该页，去掉紫色编号、紫框、「新增／改」标记、蓝色虚线框，取消淡化），
#   用 _scripts/pl_网页截图测量.swift 按 1280 宽、浅色、2 倍像素截整页并量出元素位置，再裁出配图，
#   编号位置写入 分析/推送后台_设计概要/marks.json。
from crops_spec import CROPS  # noqa: E402  （裁图定义单独放，见 _scripts/crops_spec.py）

SHOT_CSS = """
.page > *:not(section#%(p)s) { display:none !important }
section#%(p)s > .crumb, section#%(p)s > h2 { display:none !important }
.co, .mk, .mkc { display:none !important }
.hl { outline:none !important }
td.nc, th.nc { border-left-color:transparent !important; border-right-color:transparent !important }
div.nc, span.nc { outline:none !important }
.focus * { opacity:1 !important }
"""

MEASURE_JS = r"""
(function(spec){
  var sec=document.querySelector('section#%(p)s'); var out={};
  function find(sel,txt){var es=sec.querySelectorAll(sel);for(var i=0;i<es.length;i++){var t=(es[i].innerText||es[i].textContent||'');if(!txt||t.indexOf(txt)>=0){var r=es[i].getBoundingClientRect();if(r.width>0&&r.height>0)return r;}}return null;}
  for(var k in spec){var b=null,miss=[];spec[k].box.forEach(function(it){var r=find(it[0],it[1]);if(!r){miss.push(it);return;}
      var x0=r.left,y0=r.top+scrollY,x1=r.right,y1=r.bottom+scrollY; if(!b)b=[x0,y0,x1,y1]; else b=[Math.min(b[0],x0),Math.min(b[1],y0),Math.max(b[2],x1),Math.max(b[3],y1)];});
    var ms=[];(spec[k].marks||[]).forEach(function(m){var r=find(m[1],m[2]); if(!r){miss.push(m);return;} ms.push([m[0],r.left,r.top+scrollY,r.right,r.bottom+scrollY,m[3]||'r']);});
    out[k]={box:b,marks:ms,miss:miss};}
  var w=sec.querySelector('.win'); if(w){var r=w.getBoundingClientRect(); out['__win_%(p)s']={box:[r.left,r.top+scrollY,r.right,r.bottom+scrollY],marks:[],miss:[]};}
  return JSON.stringify(out);
})(%(spec)s)
"""


def do_crop(shots):
    import json
    os.makedirs(IMG, exist_ok=True); os.makedirs(shots, exist_ok=True)
    tool = BASE + '_scripts/pl_网页截图测量.swift'
    html = open(BASE + '推送系统后台集成需求/3_原型.html', encoding='utf-8').read()
    # 10/19 起原型样式另存为同目录 原型样式.css；页面另存到别处截图时，把样式内联回页面，否则另存的页面没有样式
    if '<link rel="stylesheet" href="原型样式.css">' in html:
        html = html.replace('<link rel="stylesheet" href="原型样式.css">', '<style>' + open(BASE + '推送系统后台集成需求/原型样式.css', encoding='utf-8').read() + '</style>', 1)
    pages = {}
    for k, c in CROPS.items():
        pages.setdefault(c['pg'], {})[k] = {'box': c['box'], 'marks': c.get('marks', [])}
        if 'until' in c:                 # 下沿截到某元素的底边（框住的元素下面还伸出别的东西时用）
            pages[c['pg']][k + '#until'] = {'box': [list(c['until'])], 'marks': []}
    procs = []
    for pg, spec in pages.items():
        hp = os.path.join(shots, pg + '.html'); jp = os.path.join(shots, pg + '.js')
        extra = ''.join(c.get('css', '') for c in CROPS.values() if c['pg'] == pg)
        open(hp, 'w', encoding='utf-8').write(html.replace('<details', '<details open').replace('</head>', '<meta name="color-scheme" content="light"><style>%s%s</style></head>' % (SHOT_CSS % {'p': pg}, extra), 1))
        open(jp, 'w', encoding='utf-8').write(MEASURE_JS % {'p': pg, 'spec': json.dumps(spec, ensure_ascii=False)})
        procs.append((pg, subprocess.Popen(['swift', tool, hp, os.path.join(shots, pg + '.jpg'), '1280', jp], stdout=subprocess.PIPE, text=True)))
    meas = {}
    for pg, pr in procs:
        out = pr.communicate()[0].strip().splitlines()
        meas.update(json.loads(out[0]) if out and out[0] != 'null' else {})
        tiles = []                       # 分段截图拼成整页
        i = 0
        while os.path.exists(os.path.join(shots, '%s_%d.jpg' % (pg, i))):
            tiles.append(Image.open(os.path.join(shots, '%s_%d.jpg' % (pg, i))).convert('RGB')); i += 1
        full = Image.new('RGB', (tiles[0].width, sum(t.height for t in tiles)), (255, 255, 255))
        y_ = 0
        for t in tiles:
            full.paste(t, (0, y_)); y_ += t.height
        full.save(os.path.join(shots, pg + '.jpg'), quality=92)
        for j in range(i):
            os.remove(os.path.join(shots, '%s_%d.jpg' % (pg, j)))
    # 原型章首缩略图（原型里 128×88 显示，存 2 倍）：取每页原型窗口的左上部，与设计概要配图同一批截图
    for pg in pages:
        wb = meas.get('__win_' + pg, {}).get('box')
        if not wb:
            continue
        im = Image.open(os.path.join(shots, pg + '.jpg')).convert('RGB'); sc = im.width / 1280.0
        x0, y0, x1, _ = wb; w_ = min(x1 - x0, 760); h_ = w_ * 88 / 128
        th = im.crop(tuple(int(round(v * sc)) for v in (x0, y0, x0 + w_, y0 + h_))).resize((256, 176), Image.LANCZOS)
        th.save(BASE + '分析/推送后台_原型/章节_页%s.jpg' % pg[1:], quality=90)
    marks = {}
    for k, c in CROPS.items():
        m = meas.get(k)
        if not m or not m['box']:
            print('MISSING crop', k, m and m['miss']); continue
        if m['miss']:
            print('partial', k, m['miss'])
        pt, pr_, pb, pl = c.get('pads', (6, 6, 6, 6))   # 上右下左留边（CSS 像素）；留边一律涂白，编号放在留边里不压内容
        bx0, by0, bx1, by1 = m['box']
        if 'clipx' in c:            # 只取左侧一部分（CSS 像素宽）
            bx1 = min(bx1, bx0 + c['clipx'])
        if 'until' in c and meas.get(k + '#until', {}).get('box'):
            by1 = meas[k + '#until']['box'][3]
        x0, y0, x1, y1 = bx0 - pl, by0 - pt, bx1 + pr_, by1 + pb
        im = Image.open(os.path.join(shots, c['pg'] + '.jpg')).convert('RGB')
        sc = im.width / 1280.0
        S = lambda v: int(round(v * sc))
        out = Image.new('RGB', (S(x1 - x0), S(y1 - y0)), (255, 255, 255))
        out.paste(im.crop((S(bx0), S(by0), S(bx1), S(by1))), (S(bx0 - x0), S(by0 - y0)))
        out.save(IMG + k + '.png')
        marks[k] = []
        for n, a0, b0, a1, b1, side in m['marks']:   # 记锚点元素在配图里的位置（像素），放编号时按英寸算偏移
            marks[k].append((n, (a0 - x0) * sc, (b0 - y0) * sc, (a1 - x0) * sc, (b1 - y0) * sc, side))
    json.dump(marks, open(IMG + 'marks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('cropped', len(marks))


if len(sys.argv) > 2 and sys.argv[1] == '--crop':
    do_crop(sys.argv[2])
    sys.exit(0)

OUT = sys.argv[1] if len(sys.argv) > 1 else BASE + '推送系统后台集成需求/5_设计概要.pptx'
TSV = sys.argv[2] if len(sys.argv) > 2 else None

# ───────── 颜色（同 V4 设计版） ─────────
BG = 'F7F6F2'; CARD = 'FFFEFC'; LINE = 'E2DED5'; HEAD = 'EFEDE7'; STONE = 'F0EEE9'
NAVY = '1F2A44'; INK = '3A4254'; GRAY = '6A707C'; MUTE = '9A9FA8'; ARW = 'CFC9BD'
RED = 'B03A2E'; RED_W = 'F8E7E3'; RED_L = 'E6B9AF'
BLUE = '2A63A6'; BLUE_W = 'E7EEF8'; BLUE_L = 'BFD3EC'
GREEN = '2F6B52'; GREEN_W = 'E3EFE8'; GREEN_L = 'B7D4C4'
AMBER = '9A6212'; AMBER_W = 'F6ECD9'
GRAY_W = 'ECEBE7'; GRAY_L = 'C9CCD2'
UI_LINE = 'CDD2DA'
OUTL, INL = BLUE, GREEN          # 游戏外推送、游戏内推送
OUTW, INW = BLUE_W, GREEN_W

L, C, RT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM
X0 = 0.9; CW = 11.53; XR = X0 + CW
TS = 28          # 标题字号
YC, YB = 1.85, 6.85   # 内容区上下沿

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
TITLES = []; WARN = []; LINES = []; SHOTINFO = []


def rgb(h):
    return RGBColor.from_string(h)


# ───────── 文字（同 V4） ─────────
def cw(ch):
    if unicodedata.east_asian_width(ch) in ('W', 'F', 'A') or ch in '→⇄≤÷×—–①②③④⑤⑥⑦':
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


PUNCT = '，；：。）」？！'   # 顿号不作断行点（并列的词留在同一行）


def _chunks(seg, w, size):
    """把一段过长的文字按字切开（拉丁字母按词不拆），末行不留一两个字的孤行"""
    toks = []; buf = ''
    for ch in seg:
        if ch.isascii() and ch not in ' ':
            buf += ch
        else:
            if buf:
                toks.append(buf); buf = ''
            toks.append(ch)
    if buf:
        toks.append(buf)
    lines = ['']
    for t in toks:
        if tw(lines[-1] + t, size) > w and lines[-1]:
            lines.append(t.lstrip())
        else:
            lines[-1] += t
    if len(lines) > 1 and len(lines[-1].strip()) <= 2 and len(lines[-2]) > 4:
        lines[-1] = lines[-2][-2:] + lines[-1]; lines[-2] = lines[-2][:-2]
    return lines


def brk(text, w, size):
    """在自然停顿处（标点之后、箭头之前）折行；一个分句放不下时才按字折。返回行列表"""
    w = w * 0.985
    out = []
    for para in text.split('\n'):
        segs = []; cur = ''
        k = 0
        while k < len(para):
            if para[k:k + 3] == ' → ' and cur:
                segs.append(cur); cur = ''
            cur += para[k]
            if para[k] in PUNCT:
                segs.append(cur); cur = ''
            k += 1
        if cur:
            segs.append(cur)
        line = ''
        for sg in segs:
            if tw(line + sg, size) <= w:
                line += sg
                continue
            if line:
                out.append(line); line = ''
            sg = sg.lstrip()
            if tw(sg, size) <= w:
                line = sg
            else:
                parts = _chunks(sg, w, size)
                out.extend(parts[:-1]); line = parts[-1]
        out.append(line)
    return out


def nlines(text, w, size, bold=False):
    return len(brk(text, w, size))


def _rf(r, size, color, bold):
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = rgb(color)
    rPr = r._r.get_or_add_rPr(); rPr.set('lang', 'zh-CN')
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)


def T(s, x, y, w, h, paras, size=15, color=INK, bold=False, align=L, anchor=TOP, ls=1.32, sa=0, spc=None, check=True, link=None):
    """paras: str | [para]；para: str | [(text, {size,color,bold,link})]"""
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


def CHEV(s, x, y, w=0.3, h=0.42, color=ARW):
    return _arrow(s, MSO_SHAPE.CHEVRON, x, y, w, h, color)


def DARR(s, x, y, w=0.28, h=0.3, color=ARW):
    return _arrow(s, MSO_SHAPE.DOWN_ARROW, x, y, w, h, color)


def DOT(s, x, y, n, d=0.3, fill=NAVY, size=12, ring=None):
    R(s, x, y, d, d, fill=fill, line=ring, lw=1.75, shape=MSO_SHAPE.OVAL)
    T(s, x - 0.06, y, d + 0.12, d, str(n), size, 'FFFFFF', True, align=C, anchor=MID, ls=1.0, check=False)


def chip(s, x, y, text, size=15, fill=STONE, color=NAVY, h=0.44, pad=0.22, bold=True, line=None):
    w = tw(text, size) * (1.04 if bold else 1) + 2 * pad
    R(s, x, y, w, h, fill=fill, line=line, r=h / 2)
    T(s, x, y, w, h, text, size, color, bold, align=C, anchor=MID, ls=1.0, check=False)
    return w


def bullet(s, x, y, color=NAVY, d=0.075):
    R(s, x, y, d, d, fill=color, line=None, shape=MSO_SHAPE.OVAL)


# ───────── 章节、页眉 ─────────
CH = [('一', '总览', NAVY), ('二', '运营怎么用', NAVY), ('三', '各模块的关键设计', NAVY), ('四', '验收', NAVY), ('附录', '附录', GRAY)]
NCH = len(CH)
CH_PAGE = {}


def progress(s, ci):
    gap = 0.08; w = (CW - gap * (NCH - 1)) / NCH
    for i, (num, name, col) in enumerate(CH):
        x = X0 + i * (w + gap)
        on = i == ci
        lc = col if on else MUTE; bc = col if on else 'E2DED5'
        T(s, x, 0.17, w, 0.24, (num + ' ' + name) if num != '附录' else '附录', 11, lc, on, ls=1.0, check=False)
        R(s, x, 0.44, w, 0.055 if on else 0.035, fill=bc, line=None, r=0)


def badge(s, x, y, d, num, col, size, txt='FFFFFF'):
    R(s, x, y, d, d, fill=col, line=None, r=d * 0.16)
    T(s, x - 0.1, y, d + 0.2, d, num, size, txt, True, align=C, anchor=MID, ls=1.0, check=False)


def new_slide(bg=BG):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(bg)
    return s


def page(ci, kicker, title, step=None):
    """ci：章节序号；kicker：页眉小字；step：右侧的路径编号标签（对应总图上的步骤）"""
    s = new_slide()
    n = len(prs.slides)
    CH_PAGE.setdefault(ci, n)
    progress(s, ci)
    col = CH[ci][2]
    if ci < NCH - 1:
        badge(s, X0, 0.64, 0.3, CH[ci][0], col, 13)
        T(s, X0 + 0.42, 0.62, 9, 0.32, kicker, 13, col, True, anchor=MID, ls=1.0, spc=60, check=False)
        if step:
            chip(s, X0 + 0.42 + tw(kicker, 13) * 1.12 + 0.22, 0.645, step, 11, fill=STONE, color=NAVY, h=0.29, pad=0.13)
    else:
        T(s, X0, 0.62, 9, 0.32, kicker, 13, GRAY, True, anchor=MID, ls=1.0, spc=60, check=False)
    T(s, X0, 0.98, CW + 0.3, 0.62, title, TS, NAVY, True, ls=1.1, check=False)
    if tw(title, TS) * 1.04 > CW + 0.3:
        WARN.append('title p%d too wide %.2f  %s' % (n, tw(title, TS) * 1.04, title))
    T(s, X0, 6.98, 6, 0.25, FOOT + '　·　第 ' + str(n) + ' 页', 11, MUTE, check=False)
    TITLES.append((n, ci, kicker, title))
    LINES.append((n, '标题', title))
    return s


def card(s, x, y, w, h, fill=CARD, line=LINE, lw=0.75):
    return R(s, x, y, w, h, fill=fill, line=line, lw=lw, r=0.1)


# ───────── 截图与编号标注 ─────────
SIZES = {}
for k in list(CROPS):
    p_ = IMG + k + '.png'
    if os.path.exists(p_):
        SIZES[k] = Image.open(p_).size
    else:
        WARN.append('missing image ' + k)


def place(s, key, x, y, w, frame=True):
    W, H = SIZES[key]
    h = w * H / W
    pic = s.shapes.add_picture(IMG + key + '.png', Inches(x), Inches(y), Inches(w), Inches(h))
    if frame:
        pic.line.color.rgb = rgb(UI_LINE); pic.line.width = Pt(0.75)
    return dict(x=x, y=y, w=w, h=h, k=w / W)


def stack(s, rows, x, y, maxw, maxh, gap=0.14, align=L, caps=None):
    """rows：每行一个或几个截图键；全部截图用同一比例，宽不超过 maxw、高不超过 maxh。
    caps：{截图键: 图上方的小标题}，有小标题的行上方多留 0.28。返回 (各图位置, 用到的宽, 底边)"""
    caps = caps or {}
    rw = [sum(SIZES[k][0] for k in r) for r in rows]
    rh = [max(SIZES[k][1] for k in r) for r in rows]
    chs = [0.28 if any(k in caps for k in r) else 0 for r in rows]
    gx = max(len(r) for r in rows) - 1
    ppi = max(max(rw) / (maxw - gap * gx), sum(rh) / (maxh - sum(chs) - gap * (len(rows) - 1)), 26 / (13.5 / 72))
    P = {}; yy = y; used = 0
    for r, h_, ch in zip(rows, rh, chs):
        xx = x
        for k in r:
            if k in caps:
                T(s, xx, yy, 6, 0.24, caps[k], 11.5, GRAY, True, ls=1.0, check=False)
            P[k] = place(s, k, xx, yy + ch, SIZES[k][0] / ppi)
            xx += SIZES[k][0] / ppi + gap
        used = max(used, xx - gap - x)
        yy += ch + h_ / ppi + gap
    SHOTINFO.append('p%d: %.0f px/in → 原型 13px 字约 %.1f pt' % (len(prs.slides), ppi, 26 / ppi * 72))
    return P, used, yy - gap


def rowwise(s, rows, x, y, imgw, h_avail, gap=0.3, rs=13, ws=12):
    """一行一张图，图右侧放它对应的规则。rows：[(截图键, 图上小标题, 规则列表)]；全部截图同一比例"""
    capH = 0.28
    hs = [SIZES[k][1] for k, _, _ in rows]; ws_ = [SIZES[k][0] for k, _, _ in rows]
    ppi = max(max(ws_) / imgw, sum(hs) / (h_avail - capH * len(rows) - gap * (len(rows) - 1)), 26 / (13.5 / 72))
    SHOTINFO.append('p%d: %.0f px/in → 原型 13px 字约 %.1f pt' % (len(prs.slides), ppi, 26 / ppi * 72))
    yy = y; P = {}
    for k, cap, items in rows:
        T(s, x, yy, 6, 0.24, cap, 11.5, GRAY, True, ls=1.0, check=False)
        P[k] = place(s, k, x, yy + capH, SIZES[k][0] / ppi)
        marks(s, P[k], k)
        cx = x + imgw + 0.45
        end = callouts(s, cx, yy + capH, XR - cx, items, maxh=max(P[k]['h'], 0.9) + 0.1, rs=rs, ws=ws, gmax=0.2)
        yy = max(yy + capH + P[k]['h'], end) + gap
    return P


MARKS = json.load(open(IMG + 'marks.json', encoding='utf-8')) if os.path.exists(IMG + 'marks.json') else {}


def marks(s, P, key, only=None, d=0.32):
    """按 marks.json 放这张配图的全部编号：r 锚点右侧、l 左侧、t 上方、b 下方、tr 右上角、in 锚点内右端；与锚点隔 0.03 英寸"""
    for n, a0, b0, a1, b1, side in MARKS.get(key, []):
        if only is not None and n not in only:
            continue
        k = P['k']; g = 0.03 + d / 2
        X0_, Y0_, X1_, Y1_ = P['x'] + a0 * k, P['y'] + b0 * k, P['x'] + a1 * k, P['y'] + b1 * k
        cx = {'r': X1_ + g, 'l': X0_ - g, 't': (X0_ + X1_) / 2, 'b': (X0_ + X1_) / 2, 'tr': X1_ - 0.02, 'in': X1_ - g}[side]
        cy = {'r': (Y0_ + Y1_) / 2, 'l': (Y0_ + Y1_) / 2, 't': Y0_ - g, 'b': Y1_ + g, 'tr': Y0_ - 0.02, 'in': (Y0_ + Y1_) / 2}[side]
        DOT(s, cx - d / 2, cy - d / 2, n, d=d, ring='FFFFFF', size=12.5)
    if not MARKS.get(key):
        WARN.append('no marks for ' + key)


def mark(s, P, n, px, py, d=0.32):
    """在截图像素坐标 (px, py) 处放编号圆点（圆心）"""
    cx = P['x'] + px * P['k']; cy = P['y'] + py * P['k']
    DOT(s, cx - d / 2, cy - d / 2, n, d=d, ring='FFFFFF', size=12.5)


def frame(s, P, x0, y0, x1, y1):
    k = P['k']
    R(s, P['x'] + x0 * k - 0.03, P['y'] + y0 * k - 0.03, (x1 - x0) * k + 0.06, (y1 - y0) * k + 0.06, fill=None, line=NAVY, lw=1.5, r=0.05)


def TL(s, x, y, w, text, size, color=INK, bold=False, ls=1.32, first=None):
    """按自然停顿折好行再放进文本框；first：第一行前面加的小标签 (文字, 颜色)。返回高度"""
    lines = brk(((first[0]) if first else '') + text, w, size)
    paras = []
    for i, ln in enumerate(lines):
        if i == 0 and first:
            paras.append([(first[0], {'bold': True, 'color': first[1]}), (ln[len(first[0]):], {})])
        else:
            paras.append(ln)
    h = len(lines) * size * ls / 72
    T(s, x, y, w + 0.3, h + 0.05, paras, size, color, bold, ls=ls, check=False)
    return h


def callouts(s, x, y, w, items, maxh=None, rs=13, ws=12, gmin=0.14, gmax=0.4):
    """items：(编号, 规则, 为什么) 或 ('§', 分组名, 颜色)。规则在前，为什么另起一行，前加「为什么」。"""
    tx = x + 0.42; tw_ = w - 0.42
    blocks = []
    for it in items:
        if it[0] == '§':
            blocks.append(('h', it, 0.42)); continue
        n, rule, why = it
        h1 = len(brk(rule, tw_, rs)) * rs * 1.32 / 72
        h2 = len(brk('为什么　' + why, tw_, ws)) * ws * 1.32 / 72 if why else 0
        blocks.append(('c', it, h1 + (0.04 + h2 if why else 0), h1, h2))
    total = sum(b[2] for b in blocks)
    nc = len(blocks) - 1
    avail = (maxh if maxh else YB - y)
    g = gmin if nc <= 0 else max(gmin, min(gmax, (avail - total) / nc))
    if total + g * max(nc, 0) > avail + 0.02:
        WARN.append('callouts overflow p%d: %.2f > %.2f' % (len(prs.slides), total + g * nc, avail))
    yy = y
    for b in blocks:
        if b[0] == 'h':
            T(s, x, yy + 0.02, w, 0.3, b[1][1], 13, b[1][2], True, ls=1.0, check=False)
            LN(s, x, yy + 0.34, x + w, yy + 0.34, b[1][2], 0.75)
            yy += b[2] - 0.1 + g * 0.5
            continue
        _, (n, rule, why), h, h1, h2 = b
        if n == '':
            R(s, x + 0.09, yy + 0.1, 0.1, 0.1, fill=NAVY, line=None, shape=MSO_SHAPE.OVAL)
        else:
            DOT(s, x, yy + 0.01, n, d=0.28, size=11.5)
        TL(s, tx, yy, tw_, rule, rs, NAVY, True)
        if why:
            TL(s, tx, yy + h1 + 0.04, tw_, why, ws, GRAY, first=('为什么　', MUTE))
        yy += h + g
    return yy - g


# ══════════════════════ 1 封面 ══════════════════════
s = new_slide()
CH_PAGE.setdefault(-1, 1)
R(s, X0, 2.35, 0.85, 0.08, fill=BLUE, line=None, r=0.04)
T(s, X0, 2.62, 10, 0.4, '需求评审材料', 18, BLUE, True, spc=150, check=False)
T(s, X0, 3.12, 11.5, 1.0, '推送统一后台 · 设计概要', 46, NAVY, True, ls=1.1, check=False)
y_ = 4.6
for lab, col, wash, members in [('游戏外推送', OUTL, OUTW, ['推播', '短信', 'Facebook', 'LINE']), ('游戏内推送', INL, INW, ['弹窗', '快显'])]:
    T(s, X0, y_, 1.6, 0.42, lab, 15, col, True, anchor=MID, ls=1.0, check=False)
    xx = X0 + 1.6
    for nm in members:
        xx += chip(s, xx, y_, nm, 14, fill=wash, color=col, h=0.42, pad=0.2) + 0.12
    y_ += 0.6
T(s, X0, 6.4, 6, 0.3, '2026-10-16', 13, MUTE, check=False)
TITLES.append((1, -1, '封面', '推送统一后台 · 设计概要'))

# ══════════════════════ 目录：先给出全文边界（几部分、各讲什么、各占几页） ══════════════════════
s = new_slide()
T(s, X0, 0.98, CW + 0.3, 0.62, '目录', TS, NAVY, True, ls=1.1, check=False)
T(s, X0, 6.98, 6, 0.25, FOOT + '　·　第 2 页', 11, MUTE, check=False)
TOC_ROWS = []
TOC_ITEMS = [(0, '一页总图；现在的问题与改后的做法；范围与配合改动'), (1, '运营要做的 7 件事，各经过后台哪几页'),
             (2, '12 页，每页一张原型截图配关键规则：新建推送、按行为推送、短信 Facebook LINE 与快显、\n弹窗规则与对象、弹窗保存与下架、频率上限、勿扰时段、失败与重试、\n数据看板、玩家查询、操作纪录与权限、迁移与切换'),
             (3, '一处配置和发送、按人群发、每人每天有上限、数据查得全，各怎么判断做成'), (4, '完整材料；术语表')]
y = YC - 0.05
for i, (ci, desc) in enumerate(TOC_ITEMS):
    dl = desc.split('\n')
    rh_ = 0.62 + 0.27 * len(dl)
    num, name, col = CH[ci]
    if ci < NCH - 1:
        badge(s, X0, y + 0.14, 0.5, num, NAVY, 19)
    else:
        R(s, X0, y + 0.14, 0.5, 0.5, fill=GRAY_W, line=None, r=0.08)
    T(s, X0 + 0.8, y + 0.04, 5.5, 0.4, name, 21, NAVY if ci < NCH - 1 else GRAY, True, ls=1.0, check=False)
    T(s, X0 + 0.8, y + 0.48, 8.6, 0.27 * len(dl), dl, 13.5, GRAY, ls=1.32, check=False)
    TOC_ROWS.append((ci, T(s, XR - 2.6, y + 0.04, 2.6, 0.4, '第 ? 页', 17, NAVY, True, align=RT, ls=1.0, check=False), None))
    if i < len(TOC_ITEMS) - 1:
        LN(s, X0, y + rh_ - 0.06, XR, y + rh_ - 0.06, GRAY_L if i == len(TOC_ITEMS) - 2 else LINE, 1.0 if i == len(TOC_ITEMS) - 2 else 0.75)
    y += rh_
if y > YB + 0.1:
    WARN.append('toc overflow %.2f' % y)
TITLES.append((2, -1, '目录', '目录'))


# ══════════════════════ 2 一页总图 ══════════════════════
# 左：侧栏（后台有哪些页面）；右：一条推送的路径，上段运营配置，下段系统执行（两层分开）
s = page(0, '总览 · 后台页面与一条推送的路径', '一个后台管全部推送，游戏外、游戏内推送的上限和数据分开算')
sx, sy, sw, sh = X0, YC, 2.1, YB - YC
T(s, sx, YC - 0.3, sw, 0.26, '后台侧栏：21 项', 12.5, GRAY, True, ls=1.0, check=False)
R(s, sx, sy, sw, sh, fill='FFFFFF', line=UI_LINE, lw=0.9, r=0.1)
T(s, sx + 0.2, sy + 0.17, sw - 0.3, 0.3, '推送统一后台', 14, NAVY, True, ls=1.0, check=False)
LN(s, sx + 0.14, sy + 0.55, sx + sw - 0.14, sy + 0.55, LINE)
RH = 0.2
yy = sy + 0.62


def sb_item(y, name, indent=0.2, color=INK, bold=False):
    T(s, sx + indent, y, sw - indent - 0.2, RH, name, 11.5, color, bold, anchor=MID, ls=1.0, check=False)


sb_item(yy, '总览'); yy += RH + 0.08
for gname, col, wash, members in [('游戏外推送', OUTL, OUTW, ['推播', '短信', 'Facebook', 'LINE']), ('游戏内推送', INL, INW, ['弹窗', '快显'])]:
    gh = RH * (len(members) + 1) + 0.1
    R(s, sx + 0.1, yy, sw - 0.2, gh, fill=wash, line=None, r=0.06)
    sb_item(yy + 0.05, gname, indent=0.2, color=col, bold=True)
    for k, m in enumerate(members):
        sb_item(yy + 0.05 + RH * (k + 1), m, indent=0.42)
    yy += gh + 0.1
LN(s, sx + 0.14, yy + 0.02, sx + sw - 0.14, yy + 0.02, LINE)
yy += 0.12
for nm in ['模板', '活动日历', '长期运行项', '频率上限', '数据看板（6 个子页）', '玩家查询', '操作纪录', '活动与事件目录', '迁入管理']:
    sb_item(yy, nm); yy += RH
if yy > YB - 0.05:
    WARN.append('sidebar overflow %.2f' % yy)

mx = sx + sw + 0.4; mw = XR - mx
# 上段：运营配置
T(s, mx, YC - 0.3, mw, 0.26, '运营配置：游戏外四种与快显的新建步骤相同，弹窗沿用规则表单', 12.5, GRAY, True, ls=1.0, check=False)
g1 = 0.26; BW = [1.25, 2.2, 1.3, 1.6]; BW.append(mw - sum(BW) - 4 * g1)
BX = [mx]
for w_ in BW[:-1]:
    BX.append(BX[-1] + w_ + g1)
by, bh = YC, 1.36
row1 = [('①', '内容', ['内容栏按', '推送方式不同']),
        ('②', '对象', ['立即、定时：全部玩家、', '标签群组或名单', '按行为：触发的玩家', '都可再排除群组']),
        ('③', '时间', ['立即、定时、', '按行为']),
        ('④', '频率上限', ['默认按每人每天', '上限，单条可设', '不受上限']),
        ('⑤', '确认', ['看到预计发出', '人数，可先发', '测试账号'])]
for i, (num, nm, ann) in enumerate(row1):
    x = BX[i]; bw = BW[i]
    card(s, x, by, bw, bh, fill='FFFFFF', line=NAVY, lw=1.0)
    T(s, x + 0.16, by + 0.11, bw - 0.25, 0.32, num + ' ' + nm, 15.5, NAVY, True, ls=1.0, check=False)
    T(s, x + 0.16, by + 0.46, bw - 0.2, bh - 0.48, ann, 12.5, INK, ls=1.27, check=False)
    if i < 4:
        CHEV(s, x + bw + 0.05, by + bh / 2 - 0.15, 0.16, 0.3, color=ARW)
# 下段：系统执行与统计
y2 = by + bh + 0.2
DARR(s, mx + 0.2, y2 - 0.2, 0.26, 0.2, color=ARW)
T(s, mx + 0.55, y2 - 0.05, mw - 0.6, 0.26, '确认后由系统执行与统计：游戏外、游戏内两层各算各的', 12.5, GRAY, True, ls=1.0, check=False)
CWS = [2.75, 1.95, 1.7]; CWS.append(1.85)
CG = (mw - sum(CWS)) / 3
CX = [mx]
for w_ in CWS[:-1]:
    CX.append(CX[-1] + w_ + CG)
hy = y2 + 0.3
cols = [('⑥', '发送前拦下'), ('⑦', '发出与计数'), ('⑧', '回传'), ('⑨', '数据')]
for i, (num, nm) in enumerate(cols):
    T(s, CX[i], hy, CWS[i] + 0.2, 0.3, num + ' ' + nm, 15.5, NAVY, True, ls=1.0, check=False)
T(s, CX[0], hy + 0.33, CWS[0] + CWS[1], 0.26, '到上限后当天不再发，次日不补发', 12.5, RED, True, ls=1.0, check=False)
ly1 = hy + 0.64
lh1, lh2, lg = 0.96, 0.9, 0.08
ly2 = ly1 + lh1 + lg
lanes = [('游戏外推送：推播、短信、Facebook、LINE', OUTL, OUTW, ly1, lh1,
          [['勿扰时段不发', '每种推送方式每人每天有上限'],
           ['服务商受理算 1 条', '临时错误自动重试'],
           ['到达 → 点击', '能回传时加曝光']]),
         ('游戏内推送：弹窗、快显', INL, INW, ly2, lh2,
          [['每种推送方式每人每天有上限'],
           ['弹出或显示算 1 次'],
           ['曝光（弹出或显示）', '→ 点击']])]
lw3 = CX[2] + CWS[2] - mx
for lname, col, wash, ly, lh, cells in lanes:
    R(s, mx, ly, lw3, lh, fill=wash, line=None, r=0.1)
    T(s, mx + 0.16, ly + 0.08, lw3 - 0.3, 0.28, lname, 12.5, col, True, ls=1.0, check=False)
    for i, cl in enumerate(cells):
        T(s, CX[i] + 0.16, ly + 0.4, CWS[i] - 0.12, lh - 0.42, cl, 12.5, INK, ls=1.27, check=False)
        if i < 2:
            CHEV(s, CX[i] + CWS[i] + CG / 2 - 0.08, ly + 0.4 + 0.1, 0.16, 0.28, color=col)
    CHEV(s, CX[2] + CWS[2] + CG / 2 - 0.08, ly + lh / 2 - 0.13, 0.16, 0.28, color=col)
card(s, CX[3], ly1, CWS[3], lh1 + lg + lh2, fill='FFFFFF', line=NAVY, lw=1.0)
T(s, CX[3] + 0.16, ly1 + 0.14, CWS[3] - 0.24, 1.8, ['两层各一张表', '', '按推送方式、人群、', '单条推送、日期查看', '', '拿不到的数写原因，', '不估算'], 12.5, INK, ls=1.2, check=False)
gy = ly2 + lh2 + 0.1
T(s, mx, gy, mw, 0.5, [[('标签群组', {'bold': True, 'color': NAVY}), ('＝用会员标签组合出的玩家群　', {}), ('按行为', {'bold': True, 'color': NAVY}), ('＝玩家做了指定行为（如礼包快到期）时发给这位玩家', {})],
                      [('快显', {'bold': True, 'color': NAVY}), ('＝大厅顶部的即时横幅，只给在线玩家　', {}), ('曝光', {'bold': True, 'color': NAVY}), ('＝玩家看到一次计 1　', {}), ('服务商', {'bold': True, 'color': NAVY}), ('＝接收发送请求的一方', {})]], 11.5, GRAY, ls=1.35, check=False)
if gy + 0.45 > YB + 0.1:
    WARN.append('overview overflow %.2f' % (gy + 0.45))
for t_ in ['① 内容：内容栏按推送方式不同', '② 对象：立即、定时：全部玩家、标签群组或名单；按行为：触发的玩家；都可再排除群组', '③ 时间：立即、定时、按行为',
           '④ 确认：看到预计发出人数；可先发测试账号', '⑤ 发送前拦下：到上限后当天不再发，次日不补发',
           '游戏外推送 ⑤：勿扰时段不发；每种推送每人每天有上限',
           '游戏外推送 ⑥：服务商受理算 1 条；临时错误自动重试', '游戏外推送 ⑦：到达 → 点击；能回传时加曝光',
           '游戏内推送 ⑤：每种推送每人每天有上限', '游戏内推送 ⑥：弹出或显示算 1 次', '游戏内推送 ⑦：曝光（弹出或显示）→ 点击',
           '⑧ 数据：两层各一张表；按推送方式、人群、单条推送、日期查看；拿不到的数写原因，不估算']:
    LINES.append((3, '总图', t_))


# ══════════════════════ 3 现在的问题与改后的做法（每个问题紧跟它的做法） ══════════════════════
s = page(0, '总览 · 现在的问题与改后的做法', '4 处分散配置，选人、限量、查数据都有缺口；改后一个后台补齐')
cx = [X0, X0 + 4.65, X0 + 7.45]; cwd_ = [4.15, 2.6, CW - 7.45]
hy = YC
for i, h_ in enumerate(['现在的问题', '改后的能力', '后台怎么做到']):
    T(s, cx[i], hy, cwd_[i], 0.3, h_, 13, [GRAY, NAVY, GRAY][i], True, ls=1.0, check=False)
LN(s, X0, hy + 0.36, XR, hy + 0.36, NAVY, 1.0)
rows3 = [
    ([[('礼包后台、营销侧、弹窗后台、客户端各管一部分', {})]], '一处配置和发送',
     ['6 种推送在侧栏各一页，弹窗沿用规则表单', '逐种切换到本后台，切换后原处不再新建']),
    ([[('游戏外：', {'bold': True, 'color': OUTL}), ('短信只能按名单发；Facebook、LINE 由营销侧发，都不能按标签群组选人', {})], [('游戏内：', {'bold': True, 'color': INL}), ('快显发给全部在线玩家', {})]], '按人群发',
     ['对象选全部玩家、标签群组或名单，', '再排除群组；确认前看到预计发出人数']),
    ([[('游戏外：', {'bold': True, 'color': OUTL}), ('4 种都没有每人每天上限', {})], [('游戏内：', {'bold': True, 'color': INL}), ('弹窗只限每个弹窗的次数，没有每天总数；快显不限', {})]], '每人每天有上限',
     ['「频率上限」页逐种设上限，两层分开计', '到上限当天不再发；游戏外另有勿扰时段']),
    ([[('游戏外：', {'bold': True, 'color': OUTL}), ('Facebook、LINE 没有后台报表；推播报表没有到达', {})], [('游戏内：', {'bold': True, 'color': INL}), ('快显没有后台页面可查', {})]], '数据查得全',
     ['「数据看板」两层各一张表', '拿不到的数写原因，不估算']),
]
ry = hy + 0.52; rh3 = 1.12
for i, (now, aft, how) in enumerate(rows3):
    y = ry + i * rh3
    T(s, cx[0], y, cwd_[0] + 0.1, rh3 - 0.1, now, 13.5, INK, ls=1.4, check=False)
    CHEV(s, cx[1] - 0.33, y + 0.04, 0.17, 0.3, color=ARW)
    T(s, cx[1], y, cwd_[1], rh3 - 0.1, aft, 15.5, NAVY, True, ls=1.3, check=False)
    T(s, cx[2], y, cwd_[2], rh3 - 0.1, how, 14, NAVY, ls=1.4, check=False)
    if i < len(rows3) - 1:
        LN(s, X0, y + rh3 - 0.14, XR, y + rh3 - 0.14, LINE, 0.75)
    LINES.append((4, '现在', ''.join(t for p in now for t, _ in p)))
    LINES.append((4, '改后', aft)); LINES.append((4, '做法', '；'.join(how)))
if ry + 4 * rh3 > YB + 0.1:
    WARN.append('p4 overflow %.2f' % (ry + 4 * rh3))

# ══════════════════════ 3b 范围与配合改动 ══════════════════════
s = page(0, '总览 · 范围与配合改动', '本期做推送的统一配置、发送、数据与标签配套，自动化不在本期')
lw_ = 6.75; x2 = X0 + lw_ + 0.5; rw_ = XR - x2


def sect(x, y, w, label, col):
    T(s, x, y, w, 0.3, label, 14, col, True, ls=1.0, check=False)
    LN(s, x, y + 0.36, x + w, y + 0.36, col if col != GRAY else GRAY_L, 1.0)
    return y + 0.5


DO = ['新建推送统一后台（侧栏 21 项）：6 种推送各一页，另有总览、数据看板、迁入管理等',
      '弹窗规则整页移入；推播（礼包快到期提醒）、短信、Facebook、LINE、快显逐种切换到本后台',
      '弹窗方案（同期的运营方案，共 17 项改动）中有 6 项由本需求开发：\n推送统一后台本身，以及推送跳转与触发自助、每种推送方式每日上限、\n新手弹窗接入后台、每人每日弹窗上限、快显与 Facebook、LINE 数据记录']
NOT = ['标签系统 4.3 以外的改动（4.3 由标签系统实现，属本需求）', '按人群拆分弹窗规则的配置', '多步自动化流程', 'A/B 测试', '审批', '埋点事件命名（按公司惯例另提）']
yy = sect(X0, YC, lw_, '本期做', NAVY)
for it in DO:
    bullet(s, X0 + 0.04, yy + 0.1, NAVY)
    yy += TL(s, X0 + 0.22, yy, lw_ - 0.3, it, 13, INK, ls=1.3) + 0.1
y_ = sect(x2, YC, rw_, '本期不做', GRAY)
for it in NOT:
    bullet(s, x2 + 0.04, y_ + 0.1, GRAY)
    y_ += TL(s, x2 + 0.22, y_, rw_ - 0.3, it, 13, INK, ls=1.3) + 0.02
dy = max(yy, y_) + 0.08
dy = sect(X0, dy, CW, '要配合改动的', NAVY)
DEP = [('营销侧', ['提供短信、Facebook、LINE 的服务商账号与接口', '导出退订名单、Facebook 绑定与 LINE 好友状态', '一次性排程在原处发完，周期排程迁入']),
       ('客户端', ['快显改由服务端下发，上报曝光、点击', '弹窗按每人每天上限截断；新手弹窗改由弹窗规则下发', '推播回传到达、点击与通知权限（到达只有 Android）']),
       ('数据平台', ['两层指标按人群、日期、小时汇总', '每 15 分钟内更新'])]
dw4 = (CW - 2 * 0.2) / 3
T(s, X0, YB - 0.02, CW, 0.26, [[('前置　', {'bold': True, 'color': NAVY}), ('标签系统按 4.3 实现群组交集、潜在付费与潜在流失新标签、人数预览与引用保护（属本需求）', {'color': GRAY})]], 12, ls=1.0, check=False)
ch_ = YB - dy
ch_ = ch_ - 0.3
for i, (who, items) in enumerate(DEP):
    x = X0 + i * (dw4 + 0.2)
    card(s, x, dy, dw4, ch_, fill='FFFFFF')
    T(s, x + 0.16, dy + 0.1, dw4 - 0.25, 0.3, who, 13.5, NAVY, True, ls=1.0, check=False)
    y2_ = dy + 0.44
    for it in items:
        bullet(s, x + 0.18, y2_ + 0.09, NAVY)
        y2_ += TL(s, x + 0.32, y2_, dw4 - 0.5, it, 12, INK, ls=1.25) + 0.05
    if y2_ > dy + ch_ + 0.02:
        WARN.append('dep card overflow %s %.2f > %.2f' % (who, y2_, dy + ch_))
    LINES.append((5, who, '；'.join(items)))
for it in DO:
    LINES.append((5, '本期做', it))
LINES.append((5, '本期不做', '；'.join(NOT)))


# ══════════════════════ 4 运营要做的事 ══════════════════════
s = page(1, '运营怎么用', '运营要做的 7 件事，每件在 1–3 个后台页面内做完')
TASKS = [
    ('给潜在流失发一条定时推播', ['选潜在流失（两档）7,880 人，排除后 7,850 人，可收推播 4,310 人', '→ 确认前看到被拦下的人数，先发测试账号 → 确认排程'], ['推播列表', '新建推播']),
    ('把礼包快到期提醒迁到本后台', ['新建按行为推播：礼包剩 2 小时、只发给未购买的', '→ 保存 → 在礼包后台「推荐礼包设定」页切到本后台'], ['新建推播', '礼包后台']),
    ('把「回流任务」弹窗排到第 1', ['弹窗列表找到回流玩家的规则 → 编辑时拖到第 1', '→ 保存前确认改动 → 操作纪录记下改前改后'], ['弹窗列表', '弹窗规则', '操作纪录']),
    ('调整每人每天上限与勿扰时段', ['推播上限改为 3 条，勿扰改为 23:00–08:00', '→ 保存前看到按行为推送每天会多放弃多少人次'], ['频率上限']),
    ('看近 7 天各推送的数据并导出', ['选近 7 天，两层各一张表 → 导出 Excel', '→ 点推送名称，看从符合条件的人数到点击的每一步'], ['数据看板', '单条推送数据']),
    ('查一个玩家为什么没收到短信', ['按会员编号查 → 短信一行：有手机号，今日已收 0、上限 1 条', '→ 近 30 天记录写明未送达原因：服务商接口超时'], ['玩家查询']),
    ('处理一条发送失败的推送', ['总览「待处理」列出这条 → 点重试失败部分', '→ 确认框写明可重试条数与截止时间 → 看重试结果'], ['总览', '单条推送数据']),
]
c1, c2, c3 = X0 + 0.42, X0 + 3.4, XR - 2.35
T(s, c1, YC - 0.02, 3.2, 0.3, '要做的事', 12.5, GRAY, True, ls=1.0, check=False)
T(s, c2, YC - 0.02, 5.2, 0.3, '每一步（人数为示例）', 12.5, GRAY, True, ls=1.0, check=False)
T(s, c3, YC - 0.02, 2.35, 0.3, '经过的后台页面', 12.5, GRAY, True, ls=1.0, check=False)
LN(s, X0, YC + 0.3, XR, YC + 0.3, NAVY, 1.0)
ty0 = YC + 0.42; trh = (YB - ty0) / len(TASKS)
for i, (nm, flow, pages) in enumerate(TASKS):
    y = ty0 + i * trh
    DOT(s, X0, y + 0.03, i + 1, d=0.28, size=11.5)
    T(s, c1, y + 0.02, 3.5, 0.3, nm, 13.5, NAVY, True, ls=1.0, check=False)
    T(s, c2, y + 0.02, c3 - c2 - 0.2, trh - 0.1, flow, 12.5, INK, ls=1.32, check=False)
    T(s, c3, y + 0.02, 2.35, 0.6, ' → '.join(pages), 12.5, NAVY, ls=1.3, check=False)
    if i < len(TASKS) - 1:
        LN(s, X0, y + trh - 0.04, XR, y + trh - 0.04, LINE, 0.75)
    LINES.append((6, '任务', nm))


# ══════════════════════ 三 各模块 ══════════════════════
# 顺序（10/15）：先各推送页怎么配（新建、按行为、其他推送方式、弹窗），再共用规则（上限与勿扰、失败与重试），
# 再查看（数据、玩家查询与纪录），最后上线迁移。每页：原型截图＋编号，右侧规则，每条一句为什么。
def cx_of(uw):
    return X0 + uw + 0.42


MODS = ['新建推送', '按行为推送', '短信、Facebook、LINE 与快显', '弹窗：规则与对象', '弹窗：保存与下架', '频率上限', '勿扰时段',
        '失败与重试', '数据看板', '玩家查询', '操作纪录与权限', '迁移与切换']
MODP = []


def mpage(kicker, title):
    k = len(MODP) + 1
    sp = page(2, '模块 %d / %d · %s' % (k, len(MODS), kicker), title)
    MODP.append((len(prs.slides), title))
    return sp


def foot(s, y, w, term, text):
    T(s, X0, y, w + 0.3, 0.26, [[(term + '　', {'bold': True, 'color': NAVY}), (text, {'color': GRAY})]], 12, ls=1.0, check=False)


# M1 新建推送
s = mpage('新建推送 · 推播页', '运营在一页建好推送，确认前看到预计发出人数')
P, uw, bot = stack(s, [['m1_steps'], ['m1_obj'], ['m1_conf'], ['m1_test']], X0, YC, 7.0, YB - YC - 0.36)
foot(s, bot + 0.1, uw, '可触达', '发得到的玩家，如推播须装 App 且开启通知；人数为示例')
for k in ['m1_steps', 'm1_obj', 'm1_conf', 'm1_test']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '五块固定顺序：内容 → 对象 → 时间 → 频率上限 → 确认与测试；时间选「按行为」时，对象变为触发的玩家', '游戏外四种与快显共用一套，学一次通用'),
    (2, '对象：全部玩家、标签群组或名单（上传会员编号），再排除群组', '短信现在按名单发，中奖、补偿这类一次性名单也要能发'),
    (3, '黑名单、机器人与测试账号固定排除；VIP 名单默认排除，可删', 'VIP 沿用现有做法单列、不作运营推送对象，全员通知可删掉；黑名单误删会发到封禁账号'),
    (4, '定时推送按开始发送那一刻的名单发；可设每天、每周重复，每次按当时名单发', '群组每 25 分钟刷新，按发送时的名单更准；营销侧现有的周期排程要能重建'),
    (5, '确认前逐层看到人数，直到预计发出；内容、对象、时间都校验通过才能确认', '不设审批，防错靠确认页'),
    (6, '确认前可发给测试账号，不计上限与数据', '先看到玩家实际收到的样子'),
], rs=12.5, ws=12, gmax=0.3)

# M2 按行为推送（新建与运行中修改是两个画面，分开标）
s = mpage('按行为推送 · 推播页', '按行为推送只发给触发的玩家，每次触发都先判断能否发送')
P, uw, bot = stack(s, [['m2_form'], ['m2_ver']], X0, YC, 6.8, YB - YC, gap=0.2, caps={'m2_form': '新建按行为推播', 'm2_ver': '修改运行中的按行为推播'})
for k in ['m2_form', 'm2_ver']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '对象是触发的玩家；群组只作可选限定，每次触发时判断', '触发条件本身已决定谁该收'),
    (2, '首批触发行为（暂定）：礼包快到期、玩家升级、完成任务、通行证升级；新增行为要服务端接入事件', '礼包快到期是现有提醒；后三种发生在游戏里，多用快显即时提示，不占推播额度'),
    (3, '生效期间开始必填、结束可不填；提醒次数与间隔可设，默认每次触发 1 次、同一玩家两次至少隔 24 小时', '礼包提醒这类常驻推送可长期运行；玩家一天多次触发也不会被反复打扰'),
    (4, '预计人数按近 7 天平均每天触发的人数估算', '按行为推送没有固定名单'),
    (5, '运行中修改存为新版本，只对之后的触发生效', '已发出的数据要能对应当时的设置'),
])

# M3 短信、Facebook、LINE 与快显
s = mpage('短信、Facebook、LINE 与快显 · 各推送页', '其他推送方式沿用推播的新建步骤，内容格式与可发对象各不同')
P, uw, bot = stack(s, [['m8_sms'], ['m8_fb', 'm8_fbto'], ['m8_qx']], X0, YC, 7.0, YB - YC, gap=0.2,
                   caps={'m8_sms': '短信页', 'm8_fb': 'Facebook、LINE 页', 'm8_qx': '快显页'})
for k in ['m8_sms', 'm8_fb', 'm8_fbto', 'm8_qx']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    ('§', '游戏外推送', OUTL),
    (1, '短信单则 70 字，超过按串接每则约 67 字（暂定）', '服务商按则计费；填写时显示字数与则数'),
    (2, '短信里的网址自动换成短链，点击计入数据', '能统计点击，也省字数'),
    (3, '点击跳转：短信、Facebook、LINE 跳外部链接，推播、快显跳游戏内页面', '推播、快显点开就在游戏里，其余在游戏外打开'),
    (4, '可发对象：Facebook 发给已绑定且平台允许发送的，LINE 发给已加好友且未封锁的', 'Facebook 限发送时间窗口与消息类型；LINE 被封锁后发不到'),
    ('§', '游戏内推送', INL),
    (5, '快显可立即、定时、按行为；只发给当时在线的玩家，按显示次数计上限', '快显是大厅横幅，玩家不在游戏里看不到'),
], rs=12.5, ws=12, gmax=0.3)

# M4 弹窗：规则与对象
s = mpage('弹窗 · 弹窗页（原「大厅弹窗顺序设定」）', '弹窗规则原样移入，改的是选对象：能直接排除，能先看到重叠')
P, uw, bot = stack(s, [['m7_tab'], ['m7_edit'], ['m7_ovl']], X0, YC, 7.3, YB - YC)
for k in ['m7_tab', 'm7_edit', 'm7_ovl']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '整页移入，规则、ID、历史数据不变；新手挑战、新手通行证改为排序项，计入弹出数量', '一条规则按排序依次弹出几个项目；新手弹窗现在写死在客户端，算不进上限'),
    (2, '列表加今日曝光与点击率（点击÷曝光）', '运营按效果调排序，要在列表上直接看到'),
    (3, '对象：全部玩家或一个标签群组，可直接排除群组或另一条规则的对象；被引用的规则不生效时，这项排除也不生效', '现在排除要另建带排除条件的群组；引用规则过期后不该还挡着人'),
    (4, '同一位置、同一弹窗类型的上架规则对象有交集即为重叠；逐条列出重叠的规则、人数与各弹哪一条', '一人命中多条只弹优先级最高的一条，只这条计入上限'),
], rs=12.5, ws=12)

# M5 弹窗：保存与下架（一张图配一条规则）
s = mpage('弹窗 · 弹窗页', '弹窗保存后玩家下次进大厅就生效，所以保存前确认、下架前提示')
rowwise(s, [('m7_save', '保存规则时', [(1, '保存前确认：改了什么、预计人数、与其他上架规则重叠几条', '保存后玩家下次进入大厅就按新设置弹出；不设审批，靠这一步防错')]),
            ('m7_bar', '规则编辑页底部', [(2, '可先测试预览：测试账号下次进入大厅按新设置弹一次，不计上限与数据', '弹窗是量最大的推送，先看到玩家实际看到的样子')]),
            ('m7_off', '下架规则时', [(3, '停用、下架、删除规则，或规则设了结束日期时，列出其他规则里受影响的：仍按群组名排除本规则群组的、引用本规则对象的，以及届时不再命中任何同类规则的人数', '例：下架回流规则后，16,564 名回流玩家一条大厅活动类弹窗都不命中')])],
        X0, YC, 5.4, YB - YC - 0.25, gap=0.2)

# M6 频率上限
s = mpage('频率上限 · 频率上限页', '每种推送方式每人每天各有上限，游戏外、游戏内互不占用')
P, uw, bot = stack(s, [['m3_tab'], ['m3_exc']], X0, YC, 6.6, YB - YC, gap=0.2, caps={'m3_exc': '单条推送的新建表单'})
for k in ['m3_tab', 'm3_exc']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '默认上限见左表（暂定）；弹窗 8 个是大厅与破产合计；游戏外另可开合计上限，默认关', '两层打扰的场合不同，分开计才不会互相挤占；弹窗沿用弹窗方案的合计口径'),
    (2, '游戏外按服务商受理计 1 条，游戏内按弹出或显示计 1 次', '到达回执会延迟或没有（如 iOS 推播），按到达计上限会失效'),
    (3, '到上限当天不再发，次日 00:00 重新计数；额度不够时，游戏外按发送先后、弹窗按排序、快显按触发先后', '补发会在次日集中打扰，有时效的内容也已过期'),
    (4, '单条推送可设「不受频率上限」：选计入方式，可同时不受勿扰，须填原因', '凌晨停机维护的通知不能被挡；原因记入操作纪录'),
], rs=12.5, ws=12, gmax=0.3)

# M7 勿扰时段
s = mpage('勿扰时段 · 频率上限页', '勿扰时段只管游戏外推送：立即、定时整条顺延，按行为默认放弃')
P, uw, bot = stack(s, [['m3_dnd'], ['m3_night'], ['m3_save']], X0, YC, 6.8, YB - YC, gap=0.2, caps={'m3_save': '改勿扰时段时的确认框'})
for k in ['m3_dnd', 'm3_night', 'm3_save']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '勿扰时段只管游戏外四种推送，默认 00:00–08:00（暂定）', '游戏内推送玩家在游戏里才看得到，不算打扰'),
    (2, '立即、定时按开始发送时刻判断，整条顺延到勿扰结束，自动重试也不拆批；按行为默认放弃；单条都可改选顺延或放弃', '一条推送不会拆成两批到；礼包快到期这类提醒顺延到早上已过期'),
    (3, '改勿扰时段前，确认框列出影响：按行为推送每天多放弃多少人次、已排程的推送有几条会被顺延', '改了勿扰，礼包提醒会少发、已排程的会晚发，改之前先看到'),
], rs=13, ws=12, gmax=0.4)

# M7 失败与重试
s = mpage('失败与重试 · 总览、单条推送数据', '临时错误自动重试；要人处理的失败集中到总览待处理')
P, uw, bot = stack(s, [['m4_todo'], ['m4_fail', 'm4_stop']], X0, YC, 6.9, YB - YC, gap=0.2)
for k in ['m4_todo', 'm4_fail', 'm4_stop']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '超时只对能去重的 LINE、短信自动重试；推播、Facebook 超时记「结果不明」、不重试', '能去重才重试，不会重复发'),
    (2, '当场拒绝的不重试，记原因：如推播令牌失效（多为 App 已卸载）、号码无效', '对无效的发送对象重试也发不到'),
    (3, '自动重试结束起 24 小时内可手动重试失败部分；按行为推送只重发条件仍成立的', '礼包可能已过期，过期的提醒不该再发'),
    (4, '总览「待处理」列出立即、定时推送的发送失败、可重试的部分失败、无可发送对象，以及按行为推送的异常：24 小时没有触发或 1 小时全部未受理（暂定）', '失败不用逐页找；按行为推送事件中断或证书过期也会被发现'),
    (5, '已排程、发送中的推送可停止，已发出的不撤回；按行为推送可暂停或结束', '不设审批，发错时靠停止止损'),
], rs=12.5, ws=12, gmax=0.3)

# M8 数据看板
s = mpage('数据看板 · 数据看板页', '两层各一张表、各用自己的分母，拿不到的数写原因不估算')
P, uw, bot = stack(s, [['m5_board']], X0, YC, 7.0, YB - YC, gap=0.2)
for k in ['m5_board']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '游戏外：到达率＝到达÷发送，点击率＝点击÷发送', 'iOS 推播没有到达，点击÷到达算不出'),
    (2, '游戏内：点击率＝点击÷曝光；发送、到达写「不适用」', '游戏内推送不经服务商，没有受理与回执'),
    (3, '拿不到的写原因，不估算：该渠道不回传、无回执、低于统计门槛、不适用', '代填会让 iOS 推播的到达率变成 100%'),
    (4, '到达、点击统计至发送后 5 天，LINE 14 天（暂定）；短信另看发送后登录人数，时长由运营设定', '回执和点击陆续回来；玩家多直接打开游戏、不点短信链接'),
    (5, '可按人群看：玩家计入发送时所在的群组；一人属于多个人群时，各人群的数不能相加', '数字不随名单刷新而变'),
], rs=12.5, ws=12, gmin=0.1, gmax=0.28)

# M9 玩家查询
s = mpage('玩家查询 · 玩家查询页', '一个玩家收到了什么、为什么没收到，在玩家查询一页查清')
P, uw, bot = stack(s, [['m6_can'], ['m6_rec']], X0, YC, 7.0, YB - YC, gap=0.2)
for k in ['m6_can', 'm6_rec']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '查一个玩家（会员编号、昵称或手机号）：每种推送能否收到，收不到写原因，如未绑定 Facebook', '玩家反馈没收到时，一页查出是收不到、被拦下还是没送达'),
    (2, '今日已收与上限并列，达上限标红', '没收到时，先看是否已达上限'),
    (3, '近 30 天收到记录：收到、勿扰放弃、上限拦下、未送达的逐条写原因', '直接看到原因，不用再查日志'),
], gmax=0.4)

# M10 操作纪录与权限
s = mpage('操作纪录与权限 · 操作纪录页', '不设审批，靠操作纪录追责、靠只读角色防误改')
P, uw, bot = stack(s, [['m6_log'], ['m6_ro']], X0, YC, 7.0, YB - YC, gap=0.2, caps={'m6_ro': '只读角色看到的推播列表'})
for k in ['m6_log', 'm6_ro']:
    marks(s, P[k], k)
callouts(s, cx_of(uw), YC, XR - cx_of(uw), [
    (1, '每个写操作记一条，编辑写改前改后；纪录只增不改不删', '出了问题能追到人和改动'),
    (2, '三种角色：运营可做全部操作；客服只查玩家、看纪录、做客服处置；只读只看列表与数据；另有值班附加权限', '各角色只做自己的事，核对数据的人不会误改'),
], gmax=0.4)

# M11 迁移与切换
s = mpage('迁移与切换', '迁移时同一条推送只在一处生效，玩家不会收到两次')
P, uw, bot = stack(s, [['m9_sw']], X0, YC, 6.6, 1.35, caps={'m9_sw': '推播（礼包快到期提醒）· 礼包后台推荐礼包设定页'})
marks(s, P['m9_sw'], 'm9_sw')
xc = X0 + uw + 0.42
callouts(s, xc, YC, XR - xc, [
    (1, '推播（礼包快到期提醒）：选定一条推播后切到本后台，礼包后台同一步改为只读、推播开始运行；可切回', '运营自己切换，不会两处都发'),
], maxh=1.4)
ty = max(bot, YC + 1.3) + 0.25
mcols = [X0, X0 + 2.2, X0 + 7.7]; mw_ = [2.1, 5.4, CW - 7.7]
for i, h_ in enumerate(['推送', '切换方式', '为什么']):
    T(s, mcols[i], ty, mw_[i], 0.3, h_, 13, NAVY, True, ls=1.0, check=False)
LN(s, X0, ty + 0.36, XR, ty + 0.36, NAVY, 1.0)
mig = [('游戏外推送', OUTL, '短信、Facebook、LINE', '逐种整体切换；一次性排程在营销侧发完，周期排程停掉、导入本后台为定时草稿；切换后营销侧只读', '出问题只影响一种；周期排程不会两处都发'),
       ('游戏内推送', INL, '快显', '每条写死快显一个开关，在迁入管理页逐条切换、切回；播报类标为未建、不切换；旧版客户端照旧显示写死内容', '同一玩家不会看到两次；出问题只退回一条'),
       ('游戏内推送', INL, '弹窗', '本后台建成前，每人每天弹窗上限先在弹窗后台设；建成后移到频率上限页', '弹窗方案的每日上限先上线，不等本后台')]
yy = ty + 0.48
for layer, col, nm, how, why in mig:
    T(s, mcols[0], yy - 0.02, mw_[0] - 0.1, 0.3, layer, 11.5, col, True, ls=1.0, check=False)
    hn = 0.24 + TL(s, mcols[0], yy + 0.24, mw_[0] - 0.2, nm, 13.5, NAVY, True, ls=1.25)
    h1 = TL(s, mcols[1], yy, mw_[1] - 0.25, how, 13, INK)
    h2 = TL(s, mcols[2], yy, mw_[2], why, 13, GRAY)
    rh_ = max(h1, h2, hn, 0.5) + 0.1
    LN(s, X0, yy + rh_ - 0.06, XR, yy + rh_ - 0.06, LINE, 0.75)
    yy += rh_ + 0.06
R(s, X0, yy + 0.02, CW, 0.62, fill=GRAY_W, line=None, r=0.06)
T(s, X0 + 0.18, yy + 0.1, CW - 0.3, 0.5, [[('迁移期例外，不计本后台上限与数据：', {'bold': True, 'color': NAVY}), ('切换前营销侧已排程的一次性推送、旧版客户端写死的快显；', {})],
                                         [('切换前的发送数据留在原处，不导入数据看板。这两类不经本后台发出，本后台管不到', {})]], 12.5, INK, ls=1.3, check=False)
if yy + 0.64 > YB + 0.05:
    WARN.append('migration overflow %.2f' % (yy + 0.64))


# ══════════════════════ 四 验收：怎么判断做成；暂定的时效与性能 ══════════════════════
s = page(3, '验收', '4 项能力都有可核对的标准，切换完成后逐项核对')
vc = [X0, X0 + 2.45, X0 + 8.85]; vcw = [2.3, 6.2, CW - 8.85]
for i, h_ in enumerate(['能力', '做成的标准', '什么时候看']):
    T(s, vc[i], YC, vcw[i], 0.3, h_, 13, [NAVY, NAVY, GRAY][i], True, ls=1.0, check=False)
LN(s, X0, YC + 0.38, XR, YC + 0.38, NAVY, 1.0)
ACC = [('一处配置和发送', '6 种推送都在本后台配置和发送，同一条推送只在一处发\n营销侧已排程的一次性推送在营销侧发完', '该推送方式切换完成、\n营销侧已排程的发完后'),
       ('按人群发', '按标签群组或名单发，可排除群组\n按行为推送只发给触发的玩家，群组只作可选限定', '上线后'),
       ('每人每天有上限', '按上限判断后发出的推送，没有人超过当天上限\n勿扰时段内游戏外推送发出 0 条\n除外：勾选不受频率上限的单条、调低上限前已收的、迁移期例外、\n上报晚于额度释放时间的弹窗与快显', '该推送方式切换完成后'),
       ('数据查得全', '两层各按自己的指标统计，按推送方式、人群、单条推送、日期查看并导出\n拿不到的数写原因，不估算', '上线后；到达、点击按发送后\n5 天统计（LINE 14 天）')]
yy = YC + 0.52
for a_, b_, c_ in ACC:
    lb = [l for part in b_.split('\n') for l in brk(part, vcw[1] - 0.05, 13.5)]; lc = [l for part in c_.split('\n') for l in brk(part, vcw[2], 13)]
    h_ = max(len(lb) * 13.5 * 1.33 / 72, len(lc) * 13 * 1.33 / 72, 0.45) + 0.06
    T(s, vc[0], yy, vcw[0], h_, a_, 15.5, NAVY, True, ls=1.2, check=False)
    T(s, vc[1], yy, vcw[1] + 0.3, h_, lb, 13.5, INK, ls=1.33, check=False)
    T(s, vc[2], yy, vcw[2] + 0.3, h_, lc, 13, GRAY, ls=1.33, check=False)
    LN(s, X0, yy + h_ + 0.06, XR, yy + h_ + 0.06, LINE, 0.75)
    yy += h_ + 0.18
    LINES.append((17, a_, b_.replace('\n', '；') + '｜' + c_.replace('\n', '')))
T(s, X0, yy + 0.06, CW, 0.3, '迁移期例外不计入以上标准：营销侧切换前已排程的一次性推送、旧版客户端写死的快显；验收用例 T01–T377 见原型附录', 12.5, GRAY, ls=1.0)
y_ = yy + 0.4
if y_ > YB + 0.05:
    WARN.append('acc overflow %.2f' % y_)


# ══════════════════════ 附录 ══════════════════════
s = page(4, '附录', '完整材料与术语表')
DOCS = [('1_需求清单.html', '需求清单', '现状问题、要做到什么与分级'),
        ('2_方案设计.html', '方案设计', '11 条设计决定与规则明细'),
        ('3_原型.html', '原型', '全景、27 页页面图、7 件事的走查、验收用例 T01–T377'),
        ('4_需求文档.md', '需求文档', '字段、状态、异常、验收标准与任务拆分'),
        ('6_研发评审要点.html', '研发评审要点', '研发评审时各方要定的值与要估的任务'),
        ('6_逐条需求表.pptx', '逐条需求表', '148 条逐条规则与理由，研发评审时核对')]
T(s, X0, YC, 8, 0.3, '完整材料（按阅读顺序）', 13, GRAY, True, ls=1.0, check=False)
yy = YC + 0.45
for f, nm, d in DOCS:
    T(s, X0, yy, 2.6, 0.4, [[(nm, {'link': f, 'color': BLUE, 'bold': True})]], 15, ls=1.0, anchor=MID, check=False)
    T(s, X0 + 2.7, yy, 3.0, 0.4, f, 12.5, MUTE, anchor=MID, ls=1.0, check=False)
    T(s, X0 + 5.8, yy, CW - 5.8, 0.4, d, 13.5, INK, anchor=MID, ls=1.0, check=False)
    LN(s, X0, yy + 0.47, XR, yy + 0.47, LINE, 0.75)
    yy += 0.55
GL_TB = T(s, X0, yy + 0.35, CW, 0.4, [[('术语表　', {'bold': True, 'color': NAVY}), ('第 ? 页起', {'color': INK})]], 15, ls=1.0, check=False)

GLOSSARY = [
    ('术语：推送方式、发送对象、可触达', [
        ('游戏外推送', '不在游戏里也收得到的推送：推播、短信、Facebook、LINE'),
        ('游戏内推送', '在游戏里才看得到的推送：弹窗、快显'),
        ('推送方式', '六种：推播、短信、Facebook、LINE、弹窗、快显'),
        ('推播', '手机 App 的通知'),
        ('快显', '大厅顶部的即时横幅，只给在线玩家'),
        ('弹窗', '玩家进大厅（大厅弹窗）或破产时（破产弹窗）按规则弹出的窗口'),
        ('推送统一后台', '本需求新建的后台，侧栏列出全部推送页与共用页面'),
        ('按行为推送', '玩家发生指定行为（如礼包快到期）时，发给这位玩家的推送'),
        ('标签群组', '在「会员标签设定」里用几个会员标签组合出的玩家群，如新增、回流、潜在付费、潜在流失；每 25 分钟刷新一次名单'),
        ('排除群组', '从发送对象中去掉的标签群组'),
        ('名单', '运营上传的会员编号，只用于这一条推送，不写入会员标签'),
        ('受众', '符合发送对象条件、排除后的玩家；按行为推送按触发人次计'),
        ('可触达', '受众中本推送发得到的玩家，如推播要装 App 且开启通知'),
        ('测试账号', '「运营测试组」里的账号或手动输入的会员编号，最多 10 个'),
    ]),
    ('术语：发送、到达与拦下；拿不到的数怎么写', [
        ('服务商', '接收发送请求的一方：推播为推送服务；短信为短信服务商；Facebook、LINE 为各自平台'),
        ('预计发出', '确认时估算的、将提交给服务商的人数'),
        ('发送', '游戏外推送被服务商受理的条数，含受理后退回的'),
        ('到达', '服务商回执为送达的条数；只有游戏外推送有'),
        ('曝光', '玩家看到的次数；游戏内推送弹出或显示 1 次计 1；游戏外推送只在服务商能回传时有，如 LINE'),
        ('发送前拦下', '受众中因规则没有发出的人次：无联系方式、通知关闭、勿扰时段放弃、频率上限拦下等'),
        ('频率上限', '每种推送每人每天最多收到几条（次、个）'),
        ('勿扰时段', '游戏外推送不发的时段，默认 00:00–08:00（台湾时间）'),
        ('该渠道不回传', '服务商本身不提供这一步，如 iOS 推播的到达'),
        ('无回执', '已受理，但统计窗口内没收到这一条的回执；不算失败，也不算到达'),
        ('低于统计门槛', '服务商只在人数达到门槛时才返回，如 LINE 曝光不足 20 人'),
        ('不适用', '这一层没有这一项，如游戏内推送的发送、到达'),
    ]),
]
GL_PAGE = None
for gname, rows in GLOSSARY:
    s = page(4, '附录 · 术语表', gname)
    GL_PAGE = GL_PAGE or len(prs.slides)
    yy = YC
    for a, b in rows:
        hh = nlines(b, CW - 2.7, 13.5) * 13.5 * 1.3 / 72
        T(s, X0, yy, 2.5, hh, a, 14, NAVY, True, ls=1.3, check=False)
        T(s, X0 + 2.7, yy, CW - 2.7, hh, b, 13.5, INK, ls=1.3, check=False)
        yy += hh + 0.12
        LN(s, X0, yy - 0.06, XR, yy - 0.06, LINE, 0.5)
for para in GL_TB.text_frame.paragraphs:
    for r in para.runs:
        r.text = r.text.replace('?', str(GL_PAGE))

# ══════════════════════ 回填：目录与模块索引的页码 ══════════════════════
NP = len(prs.slides)
def _set(tb, txt):
    rs = tb.text_frame.paragraphs[0].runs
    rs[0].text = txt
    for r in rs[1:]:
        r.text = ''
for ci, tb1, tb2 in TOC_ROWS:
    a = CH_PAGE[ci]; b = (CH_PAGE[ci + 1] - 1) if ci + 1 < NCH else NP
    _set(tb1, ('第 %d 页' % a) if a == b else ('第 %d–%d 页' % (a, b)))

# ══════════════════════ PowerPoint 节：正文各章一节，附录单独一节（可折叠） ══════════════════════
starts = [(1, '封面')] + [(CH_PAGE[i], (CH[i][0] + ' ' + CH[i][1]) if i < NCH - 1 else '附录') for i in range(NCH)]
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
for n, ci, k, t in TITLES:
    print('%2d  %-26s %s' % (n, k, t))
for x in SHOTINFO:
    print(x)
if TSV:
    with open(TSV, 'w', encoding='utf-8') as f:
        for n, pos, t in LINES:
            f.write('%d\t%s\t%s\n' % (n, pos, t))
if WARN:
    print('--- warnings')
    for w in WARN:
        print(w)
