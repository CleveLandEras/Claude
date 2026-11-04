#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性.py  思考页第 8 节第 3、5 项的程序检查

用法：
  python3 一致性.py            跑第 3 项三小项（①控件回指 ②叫法 ③旧词）
  python3 一致性.py 控件        只跑①
  python3 一致性.py 叫法        只跑②
  python3 一致性.py 旧词        只跑③
  python3 一致性.py 已定        第 5 项：已定关键词在框架和原型里改后次数 ≥ 改前（基线见下）
  python3 一致性.py 已定 --存基线   把现状次数存成基线（比对.py 存底本时也会存）
  可加 --页 10_规则编辑,10n_场景设置  只查指定原型页（①用；默认查全部弹窗页）

「成品弹窗范围」（待查 5 已按标题／关键词定）：
  框架：功能框架_脑图.md 里「弹窗场景设置／弹窗规则列表／新建弹窗规则／活动或礼包的弹窗设置」四个二级节点所在行（现为第 194–414 行，程序按节点名找，不写死）。
  源.html：「<h2>按玩家分群配置弹窗</h2>」到「<h2>快显</h2>」之前（现为第 362–466 行）。13、14、19 页只在这三页的原型里，不在这一段（13、14、19 的图在源.html 别的节），所以源.html 里只查这一段。
  原型页：控件回指表里出现的 10*、11 页（10、10a、10a2、10a3、10b、10e、10f、10g、10h、10m、10n、11；旧的 10c、10c3、10d、10j、10k 已不在面包板里，不算）的全部可见文字；13_游戏内数据、14_单条规则数据、19_玩家查询只取含「弹窗」二字的行
        （13 共 4 行、14 共 2 行、19 共 5 行，现状），它们只管叫法。

待查 3（已查，10/31）：源.html 弹窗段「权重」「弹窗类型」各 1 处，都在第 389 行的迁移说明里（「原「权重」改为同一场景内的优先级……
  不再分弹窗类型」），是讲去掉它的说明句，算旧词例外，不算违规。③会逐条列出例外。

检查口径：
  ① 回指表每行的字段编号必须在来源链里存在（追链.py 的字段／规则／异常／栏／入口编号），原型页文件必须存在；
     原型页里「按钮、输入框／下拉、单选、复选、开关、链接」这些元素的可见文字，必须出现在回指表该页所有行的「控件」文字里（比对时去标点和空格）。
     原型是 span 样式（class 含 btnp btno inp radio ckl tgs lk），所以按类名取。纯数字、日期、单个字的文字不查。
  ② 叫法表（功能清单.md 第五节）「叫法」列每个词：在框架弹窗段、在（原型＋源.html 弹窗段）里，要么都出现要么都不出现；
     框架字段名（四个二级节点的直接子节点）在原型＋源.html 文字里找不到的，逐条列出（应为 0；选项类节点不是字段名，不在此列）。
  ③ 旧词＝叫法表「不再用」列的词（去〔旧〕前缀；两个字的和「不用于规则内」之类不取）＋ 显示方式、弹窗内容、冷却、弹窗位置、分桶、权重、弹窗类型。
     例外只认：词前紧跟〔旧〕的；整句含「去掉、不再、改为、改成、改叫、原「、迁移」之类说明的。非例外的数 0 才算过；例外逐条列出。
  ⑤ 已定关键词（见 YIDING）在框架弹窗段、原型＋源.html 里的出现次数，改后 ≥ 改前；少了的逐条列出。另检两处默认：
     框架「是否进轮换池」下有「默认：否」，「轮换池每次弹几个」下有「默认：1 个」。
基线：改前底本/已定基线.json（比对.py 存底本时写）；没有就用 改前底本/修改前/ 里的文件算；都没有就只打印现状次数。
"""
import re, sys, json, html as htmlmod
from pathlib import Path
import importlib.util
from html.parser import HTMLParser

HERE = Path(__file__).resolve().parent
BEN = HERE.parent
spec = importlib.util.spec_from_file_location('zl', HERE / '追链.py')
z = importlib.util.module_from_spec(spec); spec.loader.exec_module(z)

PROTO = z.FRAME.parent / '需求评审版_原型'
BASE_JSON = BEN / '改前底本/已定基线.json'
EXTRA_OLD = ['显示方式', '弹窗内容', '冷却', '弹窗位置', '分桶', '权重', '弹窗类型']
EXEMPT_RE = re.compile(r'去掉|不再|改为|改成|改叫|原「|迁移|迁过来|迁为|停用|旧入口|对应旧|〔旧〕')
YIDING = ['是否进轮换池', '轮换池每次弹几个', '在所有规则里暂停', '点击后是否跳转', '进大厅', '破产时', '买了指定礼包后',
          '押注达到指定金额', '两次至少隔多久', '活动或礼包的弹窗设置', '每人每天几次', '多条规则都符合时', '弹出间隔']
ACTION_RE = re.compile(r'＋|编辑|复制|删除|暂停|恢复|结束|查看|看数据|操作纪录|修改|保存|取消|确认|返回|预览|发送|移除|上传|恢复用|去改|展开|收起|本规则另设|上架')
BASEMAP = {'10e_': ['10_规则编辑'], '10f_': ['10_规则编辑'], '10g_': ['10_规则编辑', '10a_弹窗列表'], '10h_': ['10_规则编辑'], '10m_': ['10_规则编辑'],
           '11_': ['10_规则编辑'], '10a2_': ['10a_弹窗列表'], '10a3_': ['10a_弹窗列表'], '10b_': ['10a_弹窗列表'], '10n_': ['10a_弹窗列表']}
CTRL_CLASSES = {'btnp', 'btno', 'inp', 'radio', 'ckl', 'tgs', 'lk'}


# ------------------------------------------------------------ 文本抽取
class Txt(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.lines = []      # (行号, 文本)
        self.buf = []
        self.ctrls = []      # (类名, 文本)
        self.stack = []      # (tag, is_ctrl, buf_start)
        self.attr_txt = []
        self.heading = ''    # 当前分节标题（class 含 sh，如「3 发送对象」）
        self.rowlabel = ''   # 当前行的 <label>（如「多个群组的关系」）

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        for k in ('data-tabs', 'data-page', 'placeholder', 'title', 'alt'):
            if a.get(k):
                self.attr_txt.append((self.getpos()[0], a[k].replace('|', ' ').replace('*', '')))
        cls = set((a.get('class') or '').split())
        hit = cls & CTRL_CLASSES
        if 'row' in cls:
            self.rowlabel = ''
        kind = 'label' if tag == 'label' else ('sh' if 'sh' in cls else None)
        self.stack.append((tag, (hit, cls, kind), len(self.buf)))

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                t, hit, st = self.stack.pop(i)
                if hit and hit[2]:
                    txt = ''.join(self.buf[st:]).strip()
                    if hit[2] == 'label':
                        self.rowlabel = txt
                    else:
                        self.heading = re.sub(r'^[\d\s*]+', '', txt)
                if hit and hit[0]:
                    txt = ''.join(self.buf[st:]).strip()
                    self.ctrls.append((sorted(hit[0])[0], txt, hit[1], self.heading, self.rowlabel, self.getpos()[0]))
                break

    def handle_data(self, data):
        if self.skip:
            return
        self.buf.append(data)
        if data.strip():
            self.lines.append((self.getpos()[0], data.strip()))


def parse_html(path):
    p = Txt()
    p.feed(Path(path).read_text(encoding='utf-8'))
    return p


def proto_pages():
    """弹窗原型页＝回指表里出现的 10*、11 页（旧的 10c、10c3、10d、10j、10k 已不在面包板里，不算成品范围）"""
    names = set()
    for r in z.parse_ref(z.ORIG / '控件回指表.md'):
        for pg in z.page_names(r['page']):
            if pg.startswith(('10', '11_')):
                names.add(pg)
    return sorted(names)


def proto_files():
    return [PROTO / (n + '.html') for n in proto_pages() if (PROTO / (n + '.html')).exists()]


def proto_texts():
    """返回 [(来源标签, 行号, 文本)]：原型成品范围"""
    out = []
    for f in proto_files():
        p = parse_html(f)
        out += [(f.name, ln, t) for ln, t in p.lines]
        out += [(f.name, ln, t) for ln, t in p.attr_txt]
    for stem in ('13_游戏内数据', '14_单条规则数据', '19_玩家查询'):
        f = PROTO / (stem + '.html')
        if f.exists():
            p = parse_html(f)
            out += [(f.name, ln, t) for ln, t in p.lines if '弹窗' in t]
            out += [(f.name, ln, t) for ln, t in p.attr_txt if '弹窗' in t]
    return out


def src_html_range():
    L = z.rd(z.SRC_HTML)
    a = next(i for i, l in enumerate(L) if '<h2>按玩家分群配置弹窗</h2>' in l)
    b = next(i for i, l in enumerate(L) if i > a and '<h2>' in l)
    return L, a, b


def src_texts():
    L, a, b = src_html_range()
    out = []
    for i in range(a, b):
        t = htmlmod.unescape(re.sub(r'<[^>]+>', ' ', L[i]))
        t = re.sub(r'\s+', ' ', t).strip()
        # 图片 alt 也算
        for m in re.findall(r'alt="([^"]*)"', L[i]):
            t += ' ' + m
        if t:
            out.append(('需求评审版源.html', i + 1, t))
    return out


def frame_scope():
    L = z.rd(z.FRAME)
    nodes, ranges = z.frame_nodes()
    a = min(r[0] for r in ranges.values()) - 1
    b = max(r[1] for r in ranges.values())
    return L, ranges, [(i + 1, L[i]) for i in range(a, b)]


def frame_texts():
    _, _, rows = frame_scope()
    return [('功能框架_脑图.md', ln, l.strip()[2:] if l.strip().startswith('- ') else l.strip()) for ln, l in rows]


# ------------------------------------------------------------ 叫法表
def parse_jiaofa():
    L = z.rd(z.DIG / '功能清单.md')
    names, olds = [], []
    on = False
    for l in L:
        if l.startswith('## 五、叫法表'):
            on = True; continue
        if on and l.startswith('## '):
            break
        if on and l.startswith('|') and not l.startswith('|---') and not l.startswith('| 叫法'):
            c = z.cells(l)
            if len(c) >= 3:
                names.append(c[0])
                for w in re.split(r'[、，,]', c[2]):
                    w = re.sub(r'（[^）]*）', '', w).replace('〔旧〕', '').strip()
                    if len(w) >= 3 and not w.startswith(('不用于', '不叫', '不')) and '「' not in w and w not in ('无',):
                        olds.append(w)
    olds = sorted(set(olds + EXTRA_OLD))
    return names, olds


# ------------------------------------------------------------ ① 控件回指
OPT_SPLIT = re.compile(r'[／/、，,；;「」『』]')
QUOTE_RE = re.compile(r'[「『“"]([^」』”"]+)[」』”"]')


def _k(s):
    s = re.sub(r'[「」『』“”"\'⌵▾▴×✓＋+]', '', s)
    return z.norm(s)


def ctrl_tokens(ctrl):
    """回指表一格「控件」文字 → 可映射的词：整格（去括号）；①括号里的选项；冒号前的标签和冒号后的选项；「／」「、」分隔的各项。"""
    t = re.sub(r'〔[^〕]*〕', '', ctrl)
    toks = set()
    for q in QUOTE_RE.findall(t):           # 回指表里「」括起来的就是控件名
        toks.add(_k(q))
        for part in OPT_SPLIT.split(q):
            toks.add(_k(part))
        if re.search('[：:]', q):
            toks.add(_k(re.split('[：:]', q, 1)[0]))
    for m in re.finditer(r'[（(]([^）)]*)[）)]', t):
        for part in OPT_SPLIT.split(m.group(1)):
            toks.add(_k(part))
    head = re.sub(r'[（(][^）)]*[）)]', '', t)
    toks.add(_k(head))
    if re.search('[：:]', head):
        label, opts = re.split('[：:]', head, 1)
        toks.add(_k(label))
        for part in OPT_SPLIT.split(opts):
            toks.add(_k(part))
    for part in OPT_SPLIT.split(head):
        toks.add(_k(part))
    toks.discard('')
    return toks


def ctrl_key(t):
    """页面上控件的可见文字 → 要映射的词：②「标签：选中值⌵」只取标签，选中值不算控件。"""
    if re.search('[：:]', t):
        t = re.split('[：:]', t, 1)[0]
    return _k(t)


def field_for(ch, *labels):
    """按标签文字猜该回指的卡和字段（名字对得上才写，对不上返回空）"""
    for lab in labels:
        k = _k(re.split('[：:]', lab or '', 1)[0])
        if len(k) < 2:
            continue
        for f in ch.fields:
            if f['kind'] == 'F' and (_k(f['name'].split('·')[-1]) == k):
                return '卡%s·%s（%s）' % (f['card'], f['name'], f['code'])
        for f in ch.fields:
            if f['kind'] == 'F' and (k in _k(f['name']) and len(k) >= 3):
                return '卡%s·%s（%s）' % (f['card'], f['name'], f['code'])
    return ''


def check_ctrl(pages_filter=None, gaps_out=None):
    """页面上可点控件的可见文字 → 回指表里该页（含底图页）的控件词。口径：
       ①回指表一格写多个控件或选项的（／、，括号里、冒号后、「」里）先拆成词再匹配；
       ②按页面结构排除不可点的：标签芯片(tgs)、灰掉的只读控件(dis)、已填值的输入框（只留下拉和占位输入框）、链接里的数据名（只留带动作词的）、勾选项里的活动名；
       ③下拉和单选的「标签：选中值」只取标签；单选、勾选、下拉所在的行标签或分节标题在该页回指表里写了，算按组写、不拆到每个选项。"""
    ch = z.Chain()
    allcodes = set(ch.byfield) | {r['code'] for r in ch.rules} | {e['code'] for e in ch.excepts}
    bad = []
    pagetxt = {}      # 页文件名 → 回指表该页所有控件文字
    for r in ch.ref:
        for c in r['codes']:
            ok = c in allcodes or re.search(r'-S\d+$', c) or c.endswith('-X*') or c.endswith('-D')
            if not ok:
                bad.append('回指表 %s 的字段编号 %s 在来源链里不存在' % (r['id'], c))
        if not r['codes']:
            bad.append('回指表 %s 没有字段编号' % r['id'])
        pn = z.page_names(r['page'])
        for pg in pn:
            f = PROTO / (pg + '.html')
            if not f.exists():
                bad.append('回指表 %s 的页面文件不存在：%s' % (r['id'], pg + '.html'))
            pagetxt.setdefault(pg + '.html', []).append(r['ctrl'])
    nmiss = {}
    ntot = 0
    for fname, txts in sorted(pagetxt.items()):
        if pages_filter and not any(fname.startswith(x) for x in pages_filter):
            continue
        f = PROTO / fname
        if not f.exists() or not fname.startswith(('10', '11')):
            continue
        raw = list(txts)
        for pre, bases in BASEMAP.items():     # 底图页上的控件不在本页重复列
            if fname.startswith(pre):
                for basep in bases:
                    raw += pagetxt.get(basep + '.html', [])
        toks = set()
        for x in raw:
            toks |= ctrl_tokens(x)
        rawkeys = [_k(x) for x in raw]
        p = parse_html(f)
        seen = set()
        for cls, t, allc, heading, rowlabel, ln in p.ctrls:
            t = re.sub(r'\s+', '', t)
            if len(t) < 2 or re.fullmatch(r'[\d.,:：/\-—%]+', t) or t in seen:
                continue
            if cls == 'tgs' or 'dis' in allc:
                continue          # 标签芯片（选中值）、灰掉的只读控件：不可点
            if cls == 'lk' and not ACTION_RE.search(t):
                continue          # 链接里的数据（规则名、活动名）不是控件
            if cls == 'inp' and not (t.endswith('⌵') or 'ph' in allc or '×' in t):
                continue          # 只查下拉和占位输入框，已填的值不查
            if cls == 'ckl' and t.startswith('✓'):
                continue          # 勾选项「✓名字」里的名字是数据（活动名）
            seen.add(t)
            ntot += 1
            key = ctrl_key(t)
            ok = key in toks or (len(key) >= 3 and any(key in rk for rk in rawkeys))
            if not ok and cls in ('radio', 'ckl', 'inp', 'btno', 'btnp'):
                hd = heading if len(heading) <= 8 else heading[:4]
                for lab in (rowlabel, hd):
                    lk = _k(lab)
                    if len(lk) >= 2 and any(lk in rk for rk in rawkeys):
                        ok = True; break
            if not ok:
                nmiss.setdefault(fname, []).append('%s「%s」' % (cls, t[:24]))
                if gaps_out is not None:
                    gaps_out.append((fname, ln, cls, t, heading, rowlabel, field_for(ch, rowlabel, t, heading)))
    return bad, nmiss, ntot, len(ch.ref)


def write_gaps(gaps):
    """真缺回指 → 本夹/回指缺口.md"""
    out = ['# 回指缺口：原型页上的可点控件，回指表（含底图页）里找不到', '',
           '由 `程序/一致性.py 控件` 生成。口径见该函数说明：回指表一格写多个控件／选项的先拆词；不可点的（标签芯片、灰掉的只读控件、已填值输入框、数据名链接、勾选项里的活动名）按页面结构排除；单选／下拉的行标签或分节标题在回指表里写了的算按组写。',
           '共 **%d 条**真缺回指。「该回指的卡和字段」：名字对得上的写出，对不上写「判不了」；回指表别的页已有同名行的，写出行号和它记的页。' % len(gaps), '',
           '| 页 | 行 | 控件文字 | 所在分节／行标签 | 该回指的卡和字段 |', '|---|---|---|---|---|']
    refs = z.parse_ref(z.ORIG / '控件回指表.md')
    for fname, ln, cls, t, hd, rl, fld in gaps:
        key = ctrl_key(t)
        other = [r['id'] + '（页栏写 ' + '、'.join(z.page_names(r['page'])) + '）' for r in refs
                 if key in ctrl_tokens(r['ctrl']) or (len(key) >= 3 and key in _k(r['ctrl']))]
        if other:
            fld = (fld + '；' if fld else '') + '回指表已有 ' + '；'.join(other[:3]) + '，但原型页栏没写本页'
        out.append('| %s | %d | %s「%s」 | %s%s | %s |' % (fname.replace('.html', ''), ln, cls, t, (hd[:12] if hd else '—'), ('／' + rl if rl else ''), fld or '判不了'))
    (BEN / '回指缺口.md').write_text('\n'.join(out) + '\n', encoding='utf-8')


# ------------------------------------------------------------ ② 叫法
def check_jiaofa():
    names, olds = parse_jiaofa()
    F = ' '.join(t for _, _, t in frame_texts())
    P = ' '.join(t for _, _, t in proto_texts()) + ' ' + ' '.join(t for _, _, t in src_texts())
    diff = []
    for w in names:
        inF, inP = w in F, w in P
        if inF != inP:
            diff.append('「%s」框架%s、原型／源.html%s' % (w, '有' if inF else '无', '有' if inP else '无'))
    # 框架字段名
    nodes, ranges = z.frame_nodes()
    Pn = z.norm(P)
    miss = []
    for name, (a, b) in ranges.items():
        for ln, d, t in nodes:
            if a <= ln <= b and d == 3 or (a <= ln <= b and d == 2 and False):
                nm = z.norm(t.split('：')[0])
                if len(nm) >= 2 and nm not in Pn:
                    miss.append('框L%d「%s」' % (ln, t[:20]))
    return names, diff, miss


# ------------------------------------------------------------ ③ 旧词
def check_old():
    names, olds = parse_jiaofa()
    hits, ex = [], []
    for scope, texts in (('框架', frame_texts()), ('原型', proto_texts()), ('源.html', src_texts())):
        for item in texts:
            tag, ln, t = item
            for w in olds:
                for m in re.finditer(re.escape(w), t):
                    pre = t[max(0, m.start() - 3):m.start()]
                    s = '%s %s 第%d行「%s」…%s' % (scope, tag, ln, w, t[max(0, m.start() - 14):m.end() + 14].replace('\n', ' '))
                    if '〔旧〕' in pre or '〔旧〕' in t[max(0, m.start() - 8):m.start()] or EXEMPT_RE.search(t):
                        ex.append(s)
                    else:
                        hits.append(s)
    return olds, hits, ex


# ------------------------------------------------------------ ⑤ 已定
def count_yiding(frame_lines, proto_blob):
    cnt = {}
    for k in YIDING:
        cnt[k] = [sum(1 for l in frame_lines if k in l), proto_blob.count(k)]
    return cnt


def frame_default_check():
    nodes, ranges = z.frame_nodes()
    res = {}
    a = ranges['新建弹窗规则']
    for key, want in (('是否进轮换池', '默认：否'), ('轮换池每次弹几个', '默认：1 个')):
        ok = False
        L = [n for n in nodes if a[0] <= n[0] <= a[1]]
        for i, n in enumerate(L):
            if n[2].startswith(key):
                for m in L[i + 1:]:
                    if m[1] <= n[1]:
                        break
                    if m[2].replace(' ', '') == want.replace(' ', '') or want.replace(' ', '') in m[2].replace(' ', ''):
                        ok = True
                break
        res[key + ' ' + want] = ok
    return res


def now_counts():
    fl = [t for _, _, t in frame_texts()]
    blob = ' '.join(t for _, _, t in proto_texts()) + ' ' + ' '.join(t for _, _, t in src_texts())
    return count_yiding(fl, blob)


def base_counts():
    if BASE_JSON.exists():
        return json.loads(BASE_JSON.read_text(encoding='utf-8')), '已定基线.json'
    return None, None


def save_base():
    BASE_JSON.parent.mkdir(parents=True, exist_ok=True)
    BASE_JSON.write_text(json.dumps(now_counts(), ensure_ascii=False, indent=1), encoding='utf-8')
    return BASE_JSON


def run_yiding(args):
    if '--存基线' in args:
        p = save_base(); print('已存基线', p); return 0
    now = now_counts()
    base, src = base_counts()
    dflt = frame_default_check()
    bad = 0
    print('== 已定关键词次数（框架／原型＋源.html）：现状%s ==' % ('，基线 ' + src if base else '（无基线，只打印现状；比对.py 存底本时会存基线）'))
    for k, (f, p) in now.items():
        if base and k in base:
            bf, bp = base[k]
            flag = '' if (f >= bf and p >= bp) else '  ← 少了'
            if flag: bad += 1
            print('  %-14s 框架 %3d（改前 %3d） 原型+源 %3d（改前 %3d）%s' % (k, f, bf, p, bp, flag))
        else:
            print('  %-14s 框架 %3d  原型+源 %3d' % (k, f, p))
    for k, v in dflt.items():
        print('  默认值 %s：%s' % (k, '在' if v else '没找到  ←'))
        if not v: bad += 1
    print('已定检查：%s' % ('过' if bad == 0 else '不过 %d 项' % bad))
    return bad


def main(argv):
    args = argv[1:]
    pf = None
    if '--页' in args:
        i = args.index('--页'); pf = args[i + 1].split(','); del args[i:i + 2]
    cmd = args[0] if args and not args[0].startswith('--') else '全部'
    rc = 0
    if cmd == '已定':
        return run_yiding(args)
    if cmd in ('全部', '控件'):
        gaps = []
        bad, nmiss, ntot, nref = check_ctrl(pf, gaps)
        if not pf:
            write_gaps(gaps)
        print('== ① 控件回指 ==')
        print('回指表 %d 行；回指表自身问题 %d 条' % (nref, len(bad)))
        for b in bad: print('   ', b)
        tot_miss = sum(len(v) for v in nmiss.values())
        print('原型页上可见控件文字（去重后）%d 个，不在回指表该页控件文字里的 %d 个' % (ntot, tot_miss))
        for f, v in nmiss.items():
            print('   %s：%d 个，如 %s' % (f, len(v), '、'.join(v[:6])))
        rc += len(bad) + tot_miss
    if cmd in ('全部', '叫法'):
        names, diff, miss = check_jiaofa()
        print('== ② 叫法 ==')
        print('叫法表 %d 个词；框架与原型／源.html 出现情况不一致的 %d 个' % (len(names), len(diff)))
        for d in diff: print('   ', d)
        print('框架字段名在原型＋源.html 文字里找不到的 %d 个' % len(miss))
        for d in miss: print('   ', d)
        rc += len(diff) + len(miss)
    if cmd in ('全部', '旧词'):
        olds, hits, ex = check_old()
        print('== ③ 旧词 ==')
        print('旧词表 %d 个：%s' % (len(olds), '、'.join(olds)))
        print('非例外出现 %d 处；例外 %d 处（逐条列出）' % (len(hits), len(ex)))
        for h in hits: print('  违规', h)
        for e in ex: print('  例外', e)
        rc += len(hits)
    if cmd == '全部':
        print('== ⑤ 已定（见 一致性.py 已定）==')
        rc += run_yiding([])
    print('合计待处理项：%d' % rc)
    return rc


if __name__ == '__main__':
    main(sys.argv)
