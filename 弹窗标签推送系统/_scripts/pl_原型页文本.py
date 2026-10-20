#!/usr/bin/env python3
# 把 3_原型.html 按页拆成纯文本，给评审用（整份 HTML 太大，不能整份读）。可重复运行，输出每次覆盖。
# 用法：python3 _scripts/pl_原型页文本.py [输出目录] [原型HTML路径]
#   默认输出到 分析/标准判卷/推送后台_原型评审_1017/页文本/ ，默认读 推送系统后台集成需求/3_原型.html
# 只用标准库（html.parser）。做法：先把 HTML 解析成树，再按「读者看到的样子」输出文字：
#   - 单元：页首说明（head）、全景（overview）、页 id（p1…p19、p10a–c、p12a–d、p16a）、按任务走一遍（tasks）、
#     附录各节（appx_cases、appx_trace、appx_states、appx_terms）；每个单元一个 .txt，另写 目录.txt
#   - 标题层级：# 单元（页）标题；## 区块（页标题句、原型窗口、右侧说明栏、关键状态、折叠区标题）；### 其他界面状态的每张卡片、窗口内的小标题
#   - 表格：一行一行，单元格之间用「｜」；单元格内换行用「 ↵ 」；表格嵌在单元格里时用「⟦ ⟧」包起来
#   - 窗口里并排的控件（同一行）用空格隔开；并排的小块（卡片、网格）能判断成一行时用「｜」隔开
#   - 紫色编号标注写成〔注N〕，右侧说明栏每条写成〔注N〕标题：正文；蓝色「新增」「改」写成【新增】【改】
#   - 开关〔开〕〔关〕，单选 ◉ ○，复选 ☑ ☐，灰掉的按钮后加〔灰〕，「固定」标签前加「固定 」
#   - 折叠区（其他界面状态、全部字段与可选值、附录各节）一律展开写出
#   不输出：样式、脚本、悬停提示（title 属性）、图片本身、紫框／蓝色虚线框／淡化等纯视觉标记
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, re
from html.parser import HTMLParser

BASE = _ROOT + '/'
OUT = sys.argv[1] if len(sys.argv) > 1 else BASE + '分析/标准判卷/推送后台_原型评审_1017/页文本/'
SRC = sys.argv[2] if len(sys.argv) > 2 else BASE + '推送系统后台集成需求/3_原型.html'
if not OUT.endswith('/'):
    OUT += '/'

VOID = {'br', 'img', 'hr', 'input', 'meta', 'link', 'col', 'wbr', 'area', 'base', 'source', 'track'}
SKIP = {'style', 'script', 'head', 'title', 'meta', 'link', 'template', 'noscript'}
BLOCK = {'div', 'p', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'table', 'section', 'article', 'header', 'nav', 'footer',
         'aside', 'details', 'summary', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure', 'figcaption', 'blockquote',
         'pre', 'form', 'fieldset', 'tr', 'thead', 'tbody', 'tfoot', 'caption', 'hr'}


# ---------- 解析成树 ----------
class Node:
    __slots__ = ('tag', 'attrs', 'kids', 'parent', 'cls')

    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.kids = []
        self.parent = parent
        self.cls = set((self.attrs.get('class') or '').split())


class Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root')
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs), self.cur)
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        n = Node(tag, dict(attrs), self.cur)
        self.cur.kids.append(n)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.kids.append(data)


# ---------- 样式（只为判断并排布局）----------
class Css:
    def __init__(self, text):
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
        self.rules = []  # (tag, classes, decl dict)
        for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', text):
            sels, body = m.group(1).strip(), m.group(2)
            if sels.startswith('@') or sels.startswith(':root'):
                continue
            decl = {}
            for d in body.split(';'):
                if ':' in d:
                    k, v = d.split(':', 1)
                    decl[k.strip()] = v.strip()
            for s in sels.split(','):
                s = s.strip()
                if not s:
                    continue
                last = re.split(r'[\s>+~]+', s)[-1]
                if '::' in last or ':' in last and not last.endswith(')'):
                    last = last.split(':')[0]
                mm = re.match(r'^([a-zA-Z0-9]*)((?:\.[\w-]+)*)$', last)
                if not mm:
                    continue
                self.rules.append((mm.group(1), set(c for c in mm.group(2).split('.') if c), decl))

    def style(self, node):
        d = {}
        for tag, cls, decl in self.rules:
            if tag and tag != node.tag:
                continue
            if cls and not cls <= node.cls:
                continue
            if not cls:
                continue          # 只看带类名的规则；「.a>div」这类只认标签的规则不能套到所有 div 上
            d.update(decl)
        st = node.attrs.get('style') or ''
        for x in st.split(';'):
            if ':' in x:
                k, v = x.split(':', 1)
                d[k.strip()] = v.strip()
        return d


CSS = None


def hidden(n):
    st = (n.attrs.get('style') or '').replace(' ', '')
    return 'display:none' in st or 'hidden' in n.attrs and n.attrs.get('hidden') is not None


# ---------- 文字清理 ----------
def clean(s):
    s = s.replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'([（「《\(\[〔【⟦]) +', r'\1', s)
    s = re.sub(r' +([）」》，。；：、\)\]〕】⟧])', r'\1', s)
    return s.strip()


def text_of(n):
    if isinstance(n, str):
        return n
    return ''.join(text_of(k) for k in n.kids if isinstance(k, str) or k.tag not in SKIP)


def plain(n):
    return clean(text_of(n))


def has_block_desc(n):
    for k in n.kids:
        if isinstance(k, str):
            continue
        if k.tag in BLOCK or has_block_desc(k):
            return True
    return False


def has_tag(n, tag):
    for k in n.kids:
        if isinstance(k, str):
            continue
        if k.tag == tag or has_tag(k, tag):
            return True
    return False


def is_block(n):
    if n.tag in BLOCK:
        return True
    if n.tag == 'span' and n.cls and CSS is not None and CSS.style(n).get('display') == 'block':
        return True
    if n.tag in ('span', 'a', 'b', 'i', 'em', 'strong', 'label', 'small', 'u', 'button') and has_block_desc(n):
        return True
    return False


# ---------- 行内 ----------
def sp(n):
    if n.attrs.get('class') or n.attrs.get('style') or n.tag in ('b', 'strong', 'label', 'button', 'a', 'small'):
        return ' '
    if n.tag == 'span' and n.parent is not None:
        for k in n.parent.kids:
            if k is not n and not isinstance(k, str) and k.tag in ('span', 'a', 'b', 'i', 'em'):
                return ' '
    return ''


def inline_piece(n):
    """行内元素 -> 文字（含必要的空格与标记）"""
    if isinstance(n, str):
        return n
    t = n.tag
    if t in SKIP or hidden(n):
        return ''
    c = n.cls
    if t == 'br':
        return ' ↵ '
    if t == 'img':
        return ''
    if t == 'svg':
        return ' ' + svg_text(n) + ' '
    if 'co' in c and n.attrs.get('data-n'):
        return ' 〔注%s〕 ' % n.attrs['data-n']
    if t == 'span' and 'mk' in c:
        return ' 【%s】 ' % plain(n)
    if t == 'span' and (c & {'tsw', 'esw'}):
        return ' 〔关〕 ' if 'off' in c else ' 〔开〕 '
    if t == 'span' and (c & {'rad', 'erad'}):
        return (' ◉ ' if 'on' in c else ' ○ ') + clean(''.join(inline_piece(k) for k in n.kids)) + ' '
    if t == 'span' and 'cko' in c:
        return ' ☐ '
    if t == 'span' and 'eck' in c:
        return ' ☐ ' if 'off' in c else ' ☑ '
    if t == 'span' and 'ck' in c:
        return ' ☑ '
    if t == 'span' and 'seg' in c:
        parts = []
        for k in n.kids:
            if isinstance(k, str):
                continue
            s = plain(k)
            if s:
                parts.append('〈%s〉' % s if 'on' in k.cls else s)
        return ' ' + ' '.join(parts) + ' '
    pre = ''
    if 'fix' in c and 'tg' in c:
        pre = '固定 '
    if c & {'pd-ok'}:
        pre = '✓ '
    if c & {'pd-no'}:
        pre = '✕ '
    suf = ''
    if t == 'span' and 'off' in c and not (c & {'ci'}):
        suf = '〔灰〕'
    inner = ''.join(inline_piece(k) for k in n.kids)
    if t == 'a' and 'old' in c and n.parent and 'pgs' in n.parent.cls:
        pre = '〔虚线框〕'
    s = sp(n)
    return s + pre + inner + suf + s


# ---------- svg ----------
def svg_text(n):
    out = []

    def walk(x):
        for k in x.kids:
            if isinstance(k, str):
                continue
            if k.tag == 'text':
                s = plain(k)
                if s:
                    out.append(s)
            else:
                walk(k)

    walk(n)
    return '〔图示：' + ' '.join(out) + '〕' if out else ''


# ---------- 块 ----------
CELL_DEPTH = 0


def flatten(n, sep=' ↵ '):
    global CELL_DEPTH
    CELL_DEPTH += 1
    lines = []
    render_children(n, lines)
    CELL_DEPTH -= 1
    return sep.join(x for x in lines if x.strip())


def render_children(node, lines):
    buf = []

    def flush():
        s = clean(''.join(buf))
        buf.clear()
        if s:
            lines.append(s)

    for k in node.kids:
        if isinstance(k, str):
            buf.append(k)
            continue
        if k.tag in SKIP or hidden(k):
            continue
        if k.tag == 'br':
            flush()
            continue
        if is_block(k):
            flush()
            render_block(k, lines)
        else:
            buf.append(inline_piece(k))
    flush()


def grid_cols(st):
    v = st.get('grid-template-columns', '')
    m = re.match(r'repeat\((\d+)', v)
    if m:
        return int(m.group(1))
    toks = re.findall(r'minmax\([^)]*\)|[^\s]+', v)
    return max(1, len(toks))


def span_of(n):
    st = CSS.style(n)
    m = re.search(r'span\s+(\d+)', st.get('grid-column', ''))
    return int(m.group(1)) if m else 1


def try_row(node, lines):
    """并排的小块（网格或横排）能判断成一行时，一行一排，用｜隔开；否则返回 False"""
    st = CSS.style(node)
    disp = st.get('display', '')
    if disp not in ('flex', 'grid', 'inline-flex'):
        return False
    if disp != 'grid' and st.get('flex-direction', '').startswith('column'):
        return False
    kids = [k for k in node.kids if not isinstance(k, str) and k.tag not in SKIP and not hidden(k)]
    if len(kids) < 2:
        return False
    if not all(k.tag in BLOCK for k in kids):
        return False
    texts = []
    for k in kids:
        if k.tag == 'table' or has_tag(k, 'table'):
            return False
        t = flatten(k, ' ↵ ')
        if len(t) > 160 or t.count('↵') > 3:
            return False
        texts.append(t)
    if disp == 'grid':
        n = grid_cols(st)
        if n <= 1:
            return False
        row, used = [], 0
        for k, t in zip(kids, texts):
            sp_ = min(span_of(k), n)
            if used + sp_ > n:
                lines.append('｜'.join(row))
                row, used = [], 0
            row.append(t)
            used += sp_
            if used >= n:
                lines.append('｜'.join(row))
                row, used = [], 0
        if row:
            lines.append('｜'.join(row))
    else:
        lines.append('｜'.join(texts))
    return True


def render_table(n, lines):
    rows = []

    def walk(x):
        for k in x.kids:
            if isinstance(k, str):
                continue
            if k.tag == 'tr':
                cells = []
                for c in k.kids:
                    if isinstance(c, str) or c.tag not in ('td', 'th'):
                        continue
                    cells.append(flatten(c, ' ↵ ') or '')
                rows.append('｜'.join(cells))
            elif k.tag in ('thead', 'tbody', 'tfoot'):
                walk(k)
            elif k.tag == 'caption':
                rows.append(plain(k))

    walk(n)
    rows = [r for r in rows if r.strip('｜ ')]
    if CELL_DEPTH > 0:
        lines.append('⟦ ' + ' ；'.join(rows) + ' ⟧')
    else:
        lines.extend(rows)


def in_win(n):
    p = n.parent
    while p is not None:
        if 'win' in p.cls:
            return True
        p = p.parent
    return False


def render_note(n, lines):
    num = n.attrs.get('data-n') or ''
    b = None
    for k in n.kids:
        if not isinstance(k, str) and k.tag == 'div':
            b = k
    title, body = '', ''
    if b is not None:
        for k in b.kids:
            if isinstance(k, str):
                continue
            if k.tag == 'b':
                title = plain(k)
            elif k.tag == 'p':
                body = plain(k)
    if not num:
        nb = [k for k in n.kids if not isinstance(k, str) and 'nb' in k.cls]
        num = plain(nb[0]) if nb else ''
    lines.append('〔注%s〕%s：%s' % (num, title, body) if body else '〔注%s〕%s' % (num, title))


STATE = {'n': 0}


def render_block(n, lines):
    t, c = n.tag, n.cls
    if t in ('script', 'style'):
        return
    if t == 'table':
        render_table(n, lines)
        return
    if t == 'svg':
        s = svg_text(n)
        if s:
            lines.append(s)
        return
    if t in ('h1', 'h2', 'h3', 'h4'):
        s = plain(n)
        if s:
            lines.append({'h1': '## ', 'h2': '## ', 'h3': '### ', 'h4': '#### '}[t] + s)
        return
    if t == 'details':
        summ = [k for k in n.kids if not isinstance(k, str) and k.tag == 'summary']
        title = plain(summ[0]) if summ else ''
        lines.append('## 折叠区（已展开）：' + title)
        STATE['n'] = 0
        for k in n.kids:
            if isinstance(k, str) or k.tag == 'summary':
                continue
            if is_block(k):
                render_block(k, lines)
            else:
                tmp = Node('div')
                tmp.kids = [k]
                render_children(tmp, lines)
        return
    if t == 'summary':
        s = plain(n)
        if s:
            lines.append('### ' + s)
        return
    if t == 'li':
        sub = []
        render_children(n, sub)
        sub = [x for x in sub if x.strip()]
        if sub:
            idx = 1
            if n.parent:
                same = [k for k in n.parent.kids if not isinstance(k, str) and k.tag == 'li']
                idx = same.index(n) + 1
            mark = ('%d. ' % idx) if n.parent is not None and n.parent.tag == 'ol' else '- '
            if re.match(r'^\d+(\s|$)', sub[0]):
                mark = ''          # 条目自带序号（如任务的步骤），不再加一遍
            lines.append(mark + sub[0])
            lines.extend('   ' + x for x in sub[1:])
        return
    if 'note' in c and n.attrs.get('data-n') is not None:
        render_note(n, lines)
        return
    if t == 'dl':
        term = ''
        for k in n.kids:
            if isinstance(k, str):
                continue
            if k.tag == 'dt':
                term = plain(k)
            elif k.tag == 'dd':
                lines.append('%s：%s' % (term, plain(k)) if term else plain(k))
                term = ''
        return
    if t == 'div' and (c & {'side', 'menu'}) and not has_tag(n, 'table'):
        items = []
        for k in n.kids:
            if isinstance(k, str) or k.tag in SKIP:
                continue
            s = plain(k)
            if not s:
                continue
            items.append('〈%s〉' % s if (k.cls & {'on', 'cur'}) else s)
        if items:
            lines.append('侧栏：' + ' / '.join(items))
        return
    if 'notes' in c and t == 'div':
        lines.append('## 右侧说明栏（紫色编号说明）')
        render_children(n, lines)
        return
    if 'win' in c or ('fig' in c and t == 'div' and not in_win(n)):
        lines.append('## 原型窗口（界面）')
        render_children(n, lines)
        return
    if 'kst' in c:
        lines.append('## 关键状态（页面上直接可见的状态卡片）')
        STATE['n'] = 0
        render_children(n, lines)
        return
    if c & {'stc', 'pd-state'}:
        STATE['n'] += 1
        lines.append('### 状态卡片 %d' % STATE['n'])
        render_children(n, lines)
        return
    if c & {'cap', 'pd-cap'}:
        s = clean(''.join(inline_piece(k) if not isinstance(k, str) else k for k in n.kids))
        if s:
            lines.append('【说明】' + s)
        return
    if 'ttl' in c:
        s = clean(''.join(inline_piece(k) if not isinstance(k, str) else k for k in n.kids))
        if s:
            lines.append('### ' + s)
        return
    if 'crumb' in c:
        s = plain(n)
        s = re.sub(r'^回全景\s*', '', s)
        lines.append('路径：' + s)
        return
    if 'dlg' in c:
        lines.append('〔对话框〕')
        render_children(n, lines)
        return
    if 't' in c and n.parent is not None and 'dlg' in n.parent.cls:
        s = plain(n)
        if s:
            lines.append('#### ' + s)
        return
    if t == 'div' and try_row(n, lines):
        return
    render_children(n, lines)


# ---------- 单元切分 ----------
def head_text(n, keep_rg=False):
    """分部、分组标题：只取标题文字；分组可带页号范围（rg），副标题（sub）不要"""
    out = []
    for k in n.kids:
        if isinstance(k, str):
            out.append(k)
        elif keep_rg and 'rg' in k.cls:
            out.append('（%s）' % plain(k))
        elif 'sub' in k.cls or 'rg' in k.cls:
            continue
        else:
            out.append(text_of(k))
    return clean(''.join(out))


def find(n, tag=None, cls=None, idv=None):
    for k in n.kids:
        if isinstance(k, str):
            continue
        if (tag is None or k.tag == tag) and (cls is None or cls in k.cls) and (idv is None or k.attrs.get('id') == idv):
            return k
        r = find(k, tag, cls, idv)
        if r is not None:
            return r
    return None


def main():
    global CSS
    src = open(SRC, encoding='utf-8').read()
    m = re.search(r'<style>(.*?)</style>', src, flags=re.S)
    CSS = Css(m.group(1) if m else '')
    b = Builder()
    b.feed(src)
    page = find(b.root, 'div', 'page')
    units = []  # dict(id, title, group, lines)
    state = {'part': '', 'grp': ''}

    def new_unit(uid, title, node_list, group):
        lines = []
        STATE['n'] = 0
        tmp = Node('div')
        tmp.kids = list(node_list)
        render_children(tmp, lines)
        units.append({'id': uid, 'title': title, 'group': group, 'lines': lines})

    def group_text():
        g = state['part']
        if state['grp'] and state['part'].startswith('二'):
            g += ' › ' + state['grp']
        return g

    head_nodes = []
    pending = []          # 分部标题之后、页之前的导航条（如任务入口），归到下一页
    seen_part = False
    for k in page.kids:
        if isinstance(k, str):
            continue
        cl = k.cls
        if k.tag in ('nav', 'header'):
            (pending if seen_part else head_nodes).append(k)
            continue
        if k.tag == 'div' and 'part' in cl:
            seen_part = True
            if head_nodes:
                new_unit('head', '页首说明与导航', head_nodes, '页首')
                head_nodes = []
            state['part'] = head_text(k)
            state['grp'] = ''
            continue
        if k.tag == 'div' and 'grp' in cl:
            state['grp'] = head_text(k, keep_rg=True)
            continue
        if k.tag == 'section':
            sid = k.attrs.get('id', '')
            if sid == 'appx':
                names = {0: 'appx_cases', 1: 'appx_trace', 2: 'appx_states', 3: 'appx_terms'}
                i = 0
                for d in k.kids:
                    if isinstance(d, str):
                        continue
                    if d.tag == 'div' and 'part' in d.cls:
                        state['part'] = head_text(d)
                        state['grp'] = ''
                    elif d.tag == 'details':
                        summ = [x for x in d.kids if not isinstance(x, str) and x.tag == 'summary']
                        title = plain(summ[0]) if summ else ''
                        body = [x for x in d.kids if isinstance(x, str) or x.tag != 'summary']
                        uid = names.get(i, 'appx_%d' % (i + 1))
                        i += 1
                        new_unit(uid, title, body, group_text())
                continue
            crumb = find(k, 'div', 'crumb')
            h2 = find(k, 'h2')
            if crumb is not None:
                full = re.sub(r'^回全景\s*', '', plain(crumb))
                mm = re.match(r'^(.*?页 \S+ / \d+)', full)
                title = (mm.group(1) if mm else full) + ('：' + plain(h2) if h2 is not None else '')
            elif sid == 'overview':
                h = find(k, 'h2')
                title = '全景：' + (plain(h) if h else '')
            elif sid == 'tasks':
                title = '按任务走一遍'
            else:
                title = sid
            new_unit(sid, title, pending + [k], group_text())
            pending = []
    # 写文件
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.txt'):
            os.remove(os.path.join(OUT, f))
    cat = []
    for u in units:
        body = '\n'.join(u['lines'])
        body = re.sub(r'\n{3,}', '\n\n', body)
        head = '# [%s] %s\n所属部分：%s\n' % (u['id'], u['title'], u['group'])
        txt = head + body + '\n'
        open(OUT + u['id'] + '.txt', 'w', encoding='utf-8').write(txt)
        n = len(re.sub(r'\s', '', txt))
        cat.append((u['id'], u['title'], n, u['group']))
    note = [
        '原型 3_原型.html 的分页文本目录。字数＝去掉空格与换行后的字符数（含页内折叠区展开后的全部文字）。',
        '每个 .txt 的写法：表格一行一行，单元格用「｜」隔开，单元格内换行写「 ↵ 」，嵌在单元格里的表格用「⟦ ⟧」包住；',
        '窗口里同一行并排的控件用空格隔开；紫色编号标注写〔注N〕，右侧说明栏每条写〔注N〕标题：正文；',
        '蓝色「新增」「改」写【新增】【改】；开关〔开〕〔关〕，单选 ◉ ○，复选 ☑ ☐；折叠区一律展开。',
        '文本里没有：样式、紫色高亮框、蓝色虚线框、淡化等纯视觉标记（这些看页图）。',
        '要核对原文时，对 推送系统后台集成需求/3_原型.html 用 grep -n 定位，不要整份读。',
        '',
        'id｜页标题｜字数｜所属部分',
    ]
    for r in cat:
        note.append('%s｜%s｜%d｜%s' % r)
    note.append('')
    note.append('合计 %d 个文件，%d 字' % (len(cat), sum(r[2] for r in cat)))
    open(OUT + '目录.txt', 'w', encoding='utf-8').write('\n'.join(note) + '\n')
    print('单元', len(cat), '合计字数', sum(r[2] for r in cat), '最大', max(cat, key=lambda r: r[2])[:3])


main()
