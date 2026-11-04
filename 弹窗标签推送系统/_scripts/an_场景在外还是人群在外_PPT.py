# 给主管的单独汇报（11/03 重搭第 1 版）：金字塔一页，两组上下叠放：标题＋标题线＋每组（竖色条＋组句＋各句＋支撑）＋页码；没有表格、没有栏
# 用法：python3 _scripts/an_场景在外还是人群在外_PPT.py            生成讲稿版和发给主管版两份
#       python3 _scripts/an_场景在外还是人群在外_PPT.py --stats     读回两份已生成的文件，打印各项数字（不改文件）
#       python3 _scripts/an_场景在外还是人群在外_PPT.py --check     读回两份已生成的文件，逐项判过不过（全过退出码 0）
# 输出：评审版_定稿改_1027/推送系统后台集成需求/场景在外还是人群在外_给主管.pptx（讲稿版，备注＝讲稿＋追问）
#       同目录 发给主管版/弹窗规则_先分场景还是先按人群.pptx（页面相同，没有备注）
# 填内容只改下面的 DATA；版式代码不用动。
# 版式（思考页「重搭第 1 版续：页面」第 4 节，写法照 an_推播汇报_给主管_PPT.py）：16:9，微软雅黑，左右边距 0.5 英寸，字号四级——标题 26 粗｜组句 22 粗｜各句 18 粗｜支撑 15 常规灰（页码 10 号不算一级）；
# 标题横跨最上，两组上下叠放；每组以组句带头，左边一条竖色条从组句顶拉到这组最后一行底；组内各句缩进一级（句前一个小方块），支撑再缩进一级，紧挂在它撑的那句下面；没有表头、没有标签、没有栏。
# 渲染只用：zsh _scripts/pl_pptx渲染.sh <pptx> _versions/渲染/场景在外还是人群在外_给主管/
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
# 依据：任务文件旁 2026-11-02_场景在外还是人群在外_给主管/思考页_退回重搭.md「重搭第 1 版：层级骨架」第 1 节和「重搭第 1 版续：页面」第 5、8 节（页面逐字、讲稿和追问）
# title：最上面一句总结论
# groups：两组，从上到下；每组 head＝组句（统领这一组），points＝组内各句；每句 claim＝一句判断，sups＝挂在它下面的支撑（条数按需要，每句不一样，可以为空）
# notes：讲稿版备注，speech＝1 分钟讲稿（每项一行），more＝追问；发给主管版不建备注
# 页面上全部单行，不用手动换行
DATA = {
    'title': '弹窗规则先分场景、场景内按人群配：先按人群要多管一处，只省几条规则',
    'groups': [
        {'head': '谁先弹、弹多少，先分场景在场景里一处定，先按人群要多一处定人群间谁优先',
         'points': [
             {'claim': '谁先弹，先分场景排一次，先按人群要在人群里、人群间各排一次',
              'sups': ['一人可同在几个人群，会同时符合几条规则']},
             {'claim': '每人每天上限、弹出间隔，先分场景按人群另设也在场景设置，先按人群要另定按谁算',
              'sups': ['另设每行有先后，一人在几个人群用最前那行']},
         ]},
        {'head': '按人群做的事，先分场景只在人群要在几个场景都弹时多建几条',
         'points': [
             {'claim': '看一个人群，先分场景用跨场景的按人群筛选，同样一页看全',
              'sups': []},
             {'claim': '加几个场景都弹的人群，先按人群加一次，先分场景每个场景各建一条',
              'sups': ['4 个场景：进大厅、破产时、买了指定礼包后、押注达到指定金额']},
         ]},
    ],
    'notes': {
        'speech': [
            '弹窗规则先分场景、场景内按人群配；先按人群要多管一处，只省几条规则。',
            '第一块，谁先弹、弹多少，先分场景在场景里一处定。一人可同在几个人群：先分场景每个场景排一次，先按人群人群里排完、人群间再排；每人每天上限和弹出间隔，按人群另设也在场景设置里，一人在几个人群用排最前的那行，先按人群各设各的，还得另定按谁算。',
            '第二块，按人群做的事，先分场景只在人群要在几个场景都弹时多建几条：看一个人群，按人群筛选跨场景，一样一页看全；加这样的人群，每个场景建一条，最多 4 条。',
            '您对哪一点有疑问？',
        ],
        'more': [
            '追问 3 条：',
            '1. 运营同事的规则草稿是按人群写的，为什么不照它？→ 草稿按人群写，也离不开人群之外那一处：另写了一份总规则，弹出间隔 1800 秒写在总规则里，哪个人群先弹看各人群的权重，权重大的先；一人同在两个人群时按谁的弹窗数量算，草稿没写。先分场景把这一处放进场景设置，和规则列表在同一个场景页签里。业界 Braze、MoEngage、CleverTap 也是同一触发里按优先级取一条，人群设在每条消息上。这份草稿还没启用，线上没有配置，只当参照。',
            '2. 以后要在几个场景都弹的人群多了呢？→ 每个这样的人群，先分场景最多建 4 条，场景只有进大厅、破产时、买了指定礼包后、押注达到指定金额 4 个；上架后场景不能改，复制一条存为草稿再改场景就行。看这群人仍用按人群筛选一页看全。各场景弹的内容本来不一定相同：按 10 月 10 日后台截图，破产时那条规则配 8 项，进大厅两条各配 7 项、14 项，所以先按人群也不一定只建 1 条。现有材料看不出这类人群会有多少。',
            '3. 先分场景自己没有麻烦吗？→ 有一处：一个场景里有两套先后，规则列表的先后定弹哪条，按人群另设那几行的先后定一人在几个人群时用谁的上限和间隔，两套可以不一样；但都在同一个场景里，不多出要管的地方。',
        ],
    },
}
# 页面上应有的文字框数（检查用，按 DATA 算）：标题 1＋组句＋各句＋支撑＋页码 1
N_HEAD = len(DATA['groups'])
N_CLAIM = sum(len(g['points']) for g in DATA['groups'])
N_SUP = sum(len(pt['sups']) for g in DATA['groups'] for pt in g['points'])
N_TEXT = 1 + N_HEAD + N_CLAIM + N_SUP + 1

# 页面和备注里一出现就一定不对的字（卡上「检查」①，11/03 09:55）：跳转和指引字样不讲内容（完成标准第 2 条）；
# EP 是落地负责人，页面不写落地（完成标准第 3 条）；其余要求由评审按意思判，不按字面拦
BANNED = ['回到', '→ 第', '见第', '见附录', '细节见', 'EP']
BODY_MAX, HEAD_MAX, SPEECH_MAX, ASK_MAX = 260, 110, 240, 3   # 正文（不含标题）≤260、标题＋组句 ≤110、讲稿 ≤240 字（约 1 分钟）、追问 ≤3

FILE_TITLE = '弹窗规则：先分场景还是先按人群'          # pptx 文件属性里的标题
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, '评审版_定稿改_1027', '推送系统后台集成需求')
OUT_NOTES = os.path.join(OUT_DIR, '场景在外还是人群在外_给主管.pptx')
OUT_SENT = os.path.join(OUT_DIR, '发给主管版', '弹窗规则_先分场景还是先按人群.pptx')
FONT = 'Microsoft YaHei'

WHITE = 'FFFFFF'; NAVY = '1F2A44'; INK = '3A4254'; MUTE = '9A9FA8'
LINE = 'E2DED5'
BLUE = '2A63A6'
SUB = '5B6272'                              # 支撑的灰
L, R = PP_ALIGN.LEFT, PP_ALIGN.RIGHT
TOP, MID = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE
X0 = 0.5; TITLE_W = 12.33                    # 左右边距 0.5 英寸

# 版面（英寸，思考页「重搭第 1 版续：页面」第 4 节）：两组上下叠放，字号四级——标题 26 粗｜组句 22 粗｜各句 18 粗｜支撑 15 常规灰（页码 10 号不算一级）
# 文字框边距 0、行距 1.15、顶对齐；每框一段、全部一行，框高＝每行高；纵向往下累加
TITLE_Y, TITLE_H, TITLE_SIZE = 0.5, 0.7, 26
RULE_Y = 1.35                                # 标题下细线 0.75 磅
BAR_X, BAR_W = 0.5, 0.07                     # 每组一条竖色条，从组句顶拉到这组最后一行底
HEAD_X, HEAD_W, HEAD_SIZE, HEAD_LH = 0.75, 12.08, 22, 0.38
DOT, DOT_X, DOT_DY = 0.09, 0.98, 0.11        # 各句前的小方块；y＝该句顶＋0.11
CLAIM_X, CLAIM_W, CLAIM_SIZE, CLAIM_LH = 1.2, 11.63, 18, 0.31
SUP_X, SUP_W, SUP_SIZE, SUP_LH = 1.6, 11.23, 15, 0.26
GROUP_TOP = 1.75                             # 第一组顶
GAP_HEAD, GAP_CLAIM, GAP_GROUP = 0.14, 0.20, 0.55   # 组句后空；第 2 句前空；组间空
PAGENO_X, PAGENO_Y, PAGENO_W, PAGENO_H, PAGENO_SIZE = 12.59, 7.0, 0.23, 0.25, 10


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


def fill_tf(tf, paras, size, color, bold=False, align=L, anchor=TOP, gap=6, ls=1.15, margin=0.0, wrap=True):
    """往一个文字框里写段落；margin＝四边内边距（英寸）。"""
    tf.word_wrap = wrap; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = anchor
    if isinstance(paras, str):
        paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align; para.line_spacing = ls
        if i < len(paras) - 1:
            para.space_after = Pt(gap)
        for j, part in enumerate(p.split('\v')):          # \v＝手动换行，只定换行位置，不改字
            if j:
                para.add_line_break()
                br = para._p.findall(qn('a:br'))[-1]
                rpr = br.makeelement(qn('a:rPr'), {'sz': str(int(size * 100)), 'lang': 'zh-CN'})
                br.append(rpr)
            r = para.add_run(); r.text = part
            font(r, size, color, bold)


def text(s, name, x, y, w, h, paras, **kw):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    fill_tf(tb.text_frame, paras, **kw)
    return tb


def rect(s, name, x, y, w, h, fill):
    sp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.name = name
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def hline(s, name, x1, y, x2, color, width):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y), Inches(x2), Inches(y))
    c.name = name
    c.line.color.rgb = rgb(color); c.line.width = Pt(width)
    c._element.spPr.append(c._element.spPr.makeelement(qn('a:effectLst'), {}))   # 去掉主题带的阴影，细线才是细线
    return c


def set_notes(s, txt):
    """有内容才建备注页。"""
    if txt:
        s.notes_slide.notes_text_frame.text = txt


# ═════════ 整页：标题 → 两组（竖色条＋组句＋各句＋支撑）→ 页码 ═════════
def build(data, sent):
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    # 文件属性：去掉 python-pptx 默认的作者和 2013 年时间
    cp = prs.core_properties
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    cp.author = cp.last_modified_by = '产品部'
    cp.title = FILE_TITLE
    cp.created = cp.modified = now
    cp.comments = ''; cp.keywords = ''
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(WHITE)
    text(s, '标题', X0, TITLE_Y, TITLE_W, TITLE_H, data['title'], size=TITLE_SIZE, color=NAVY, bold=True, anchor=MID, ls=1.05)
    hline(s, '标题线', X0, RULE_Y, X0 + TITLE_W, LINE, 0.75)
    y = GROUP_TOP
    for gi, g in enumerate(data['groups'], start=1):
        top = y                                                   # 这组的顶：竖色条从这里起
        text(s, '组句%d' % gi, HEAD_X, y, HEAD_W, HEAD_LH, g['head'], size=HEAD_SIZE, color=NAVY, bold=True, ls=1.15)
        y = round(y + HEAD_LH + GAP_HEAD, 2)
        for pi, pt in enumerate(g['points'], start=1):
            if pi > 1:
                y = round(y + GAP_CLAIM, 2)
            rect(s, '点%d-%d' % (gi, pi), DOT_X, round(y + DOT_DY, 2), DOT, DOT, BLUE)
            text(s, '分句%d-%d' % (gi, pi), CLAIM_X, y, CLAIM_W, CLAIM_LH, pt['claim'], size=CLAIM_SIZE, color=NAVY, bold=True, ls=1.15)
            y = round(y + CLAIM_LH, 2)
            for si, sup in enumerate(pt['sups'], start=1):
                text(s, '支撑%d-%d-%d' % (gi, pi, si), SUP_X, y, SUP_W, SUP_LH, sup, size=SUP_SIZE, color=SUB, ls=1.15)
                y = round(y + SUP_LH, 2)
        rect(s, '色条%d' % gi, BAR_X, top, BAR_W, round(y - top, 2), BLUE)   # 到这组最后一行底
        y = round(y + GAP_GROUP, 2)
    text(s, '页码', PAGENO_X, PAGENO_Y, PAGENO_W, PAGENO_H, '1', size=PAGENO_SIZE, color=MUTE, align=R, wrap=False)
    if not sent:
        n = data.get('notes') or {}
        set_notes(s, '\n'.join(n.get('speech', []) + [''] + n.get('more', [])).strip())
    return prs


# ═════════ 读回已生成的文件，算各项数字 ═════════
def n_chars(t):
    return len(re.sub(r'\s', '', t))


def read_deck(path):
    """返回一份文件的各项数字和原文。块＝页面上每个形状里的每一段（标题和页码单列）。"""
    prs = Presentation(path)
    slides = list(prs.slides)
    cp = prs.core_properties
    info = {'path': path, 'pages': len(slides), 'tables': 0, 'jumps': 0, 'blocks': [], 'breaks': 0, 'notes': '', 'has_notes': False,
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
                        info['breaks'] += p.text.count('\v')
                        info['blocks'].append(('%s-%d' % (sh.name, k + 1), p.text.replace('\v', '')))
        if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip():
            info['has_notes'] = True
            info['notes'] += sl.notes_slide.notes_text_frame.text
    page = info['blocks']
    info['title'] = ''.join(t for n, t in page if n.startswith('标题'))
    info['body_blocks'] = [(n, t) for n, t in page if not n.startswith('标题') and not n.startswith('页码')]
    info['n_title'] = n_chars(info['title'])
    info['n_body'] = sum(n_chars(t) for _, t in info['body_blocks'])
    info['n_all'] = info['n_title'] + info['n_body']
    info['n_head'] = info['n_title'] + sum(n_chars(t) for nm, t in info['body_blocks'] if nm.startswith('组句'))
    note = info['notes']
    cut = re.search(r'追问\s*\d+\s*条', note)
    speech = note[:cut.start()] if cut else note
    info['n_speech'] = n_chars(speech)
    info['n_asks'] = len(re.findall(r'(?m)^\s*\d+\.', note[cut.start():] if cut else ''))
    page_text = '\n'.join(t for _, t in page)
    info['page_text'] = page_text

    def count(w, t):
        return len(re.findall(r'\s*'.join(map(re.escape, w.split(' '))), t))
    info['banned'] = {w: count(w, page_text + '\n' + note) for w in BANNED}
    info['quotes'] = sorted(set(re.findall(r'[“”‘’"\'『』]', page_text + note)))
    # 10 字以上重复：标题和每一段（去空白）两两之间的公共 10 字片段，加同一段里重复的片段
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
    return info


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
        print('  页数 %d｜表格形状 %d｜跳转或链接 %d｜手动换行 %d 处' % (d['pages'], d['tables'], d['jumps'], d['breaks']))
        print('  正文（不含标题、页码，去空白、含标点）%d 字（上限 %d）｜连标题 %d 字｜标题 %d 字' % (
            d['n_body'], BODY_MAX, d['n_all'], d['n_title']))
        print('  标题＋组句 %d 字（上限 %d）' % (d['n_head'], HEAD_MAX))
        for n, t in d['body_blocks']:
            print('    %-8s %2d 字  %s' % (n, n_chars(t), t.replace('\n', ' / ')))
        if d['has_notes']:
            print('  讲稿 %d 字（上限 %d；按每分钟 240 字约 %d 秒）｜追问 %d 条（上限 %d）' % (
                d['n_speech'], SPEECH_MAX, round(d['n_speech'] / 4), d['n_asks'], ASK_MAX))
        else:
            print('  备注：无')
        bad = {w: c for w, c in d['banned'].items() if c}
        print('  跳转指引字样和 EP（页面＋备注）合计 %d：%s' % (sum(d['banned'].values()), bad or '全 0'))
        print('  页面 10 字以上重复 %d 处%s' % (len(d['dups']), ''.join('\n    %s／%s「%s」' % x for x in d['dups'])))
        print('  页面形状：文字框 %d 个，其余 %d 个：%s' % (d['text_shapes'], len(d['other_shapes']), '、'.join(d['other_shapes'])))
        print('  非「」引号：%s' % (' '.join(d['quotes']) or '无'))
        print('  文件属性：作者=%s｜上次修改者=%s｜标题=%s｜描述=%r｜关键词=%r' % d['props'])


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
        row(d['n_head'] <= HEAD_MAX, '标题＋组句 %d 字（≤%d）' % (d['n_head'], HEAD_MAX))
        row(len({nm.split('-')[0] for nm, _ in d['body_blocks'] if nm.startswith('组句')}) in (2, 3), '组句数 2–3')
        row(d['tables'] == 0, '表格形状 %d（应为 0）' % d['tables'])
        row(d['jumps'] == 0, '跳转或链接 %d（应为 0）' % d['jumps'])
        row(not sum(d['banned'].values()), '跳转指引字样和 EP（页面＋备注）%d' % sum(d['banned'].values()))
        row(not d['dups'], '页面 10 字以上重复 %d 处' % len(d['dups']))
        row(not d['quotes'], '非「」引号 %s' % (' '.join(d['quotes']) or '无'))
        row(d['text_shapes'] == N_TEXT, '页面文字框 %d 个（应为 %d：标题、组句 %d、各句 %d、支撑 %d、页码）；其余形状 %s' % (
            d['text_shapes'], N_TEXT, N_HEAD, N_CLAIM, N_SUP, '、'.join(d['other_shapes'])))
        row(d['props'][0] == '产品部' and d['props'][1] == '产品部' and d['props'][2] == FILE_TITLE
            and not d['props'][3] and not d['props'][4], '文件属性 作者、上次修改者「产品部」，标题「%s」，描述、关键词空' % FILE_TITLE)
        if sent:
            row(not d['has_notes'], '发给主管版备注为空（%s）' % ('有备注' if d['has_notes'] else '无备注'))
        else:
            row(d['has_notes'] and d['n_speech'] <= SPEECH_MAX, '讲稿 %d 字（≤%d），约 %d 秒' % (
                d['n_speech'], SPEECH_MAX, round(d['n_speech'] / 4)))
            row(1 <= d['n_asks'] <= ASK_MAX, '追问 %d 条（≤%d）' % (d['n_asks'], ASK_MAX))
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
