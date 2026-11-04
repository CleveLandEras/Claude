#!/usr/bin/env python3
"""功能框架大纲 → 一页思维导图网页（单文件、离线可开）。

用法：python3 _scripts/pl_功能框架导图.py
读：评审版_定稿改_1027/推送系统后台集成需求/功能框架_大纲.md
写：同目录 功能框架_思维导图.html
大纲改了重跑即可。脚本最后会把 HTML 里的节点文字与大纲逐条核对，不一致就报错退出。

大纲格式：
  "# " 一行是中心主题；
  缩进 2 格的 "- " 列表：第 1 层分支，第 2 层功能，第 3、4 层关键设置；
  行尾〔新增〕〔调整〕〔现有〕是标签，渲染成色块。
"""
import html
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '评审版_定稿改_1027' / '推送系统后台集成需求' / '功能框架_脑图.md'  # 10/29 起脑图 md 是唯一源文件，也是唯一交付物
OUT = SRC.parent / '功能框架_旧版_带解释_1655' / '功能框架_思维导图.html'  # 网页只作参考，不交

TITLE = '推送统一后台 · 功能框架'
TAGS = {'新增': 'new', '调整': 'adj', '现有': 'old'}
LEGEND = [('新增', '现在后台没有'), ('调整', '现在有，要改'), ('现有', '沿用'), ('', '无色块：分组或说明')]
TAG_RE = re.compile(r'〔([^〔〕]+)〕\s*$')
ITEM_RE = re.compile(r'^( *)- (.+)$')


class Node:
    def __init__(self, text, tags, level):
        self.text = text
        self.tags = tags
        self.level = level
        self.children = []


def split_tags(s):
    tags = []
    m = TAG_RE.search(s)
    while m:
        tags.insert(0, m.group(1))
        s = s[:m.start()].rstrip()
        m = TAG_RE.search(s)
    return s, tags


def parse(path):
    root = None
    stack = []
    for no, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.rstrip()
        if not line.strip():
            continue
        if '\t' in line[:len(line) - len(line.lstrip())]:
            sys.exit(f'第 {no} 行缩进用了 Tab，请改成空格：{raw}')
        if line.startswith('# '):
            if root is not None:
                sys.exit(f'第 {no} 行：中心主题只能有一个')
            text, tags = split_tags(line[2:].strip())
            root = Node(text, tags, 0)
            stack = [root]
            continue
        m = ITEM_RE.match(line)
        if not m:
            sys.exit(f'第 {no} 行格式不认识：{raw}')
        if root is None:
            sys.exit(f'第 {no} 行：列表前要先有 "# 中心主题"')
        indent = len(m.group(1))
        if indent % 2:
            sys.exit(f'第 {no} 行缩进不是 2 的倍数：{raw}')
        level = indent // 2 + 1
        if level > len(stack):
            sys.exit(f'第 {no} 行跳了层级：{raw}')
        text, tags = split_tags(m.group(2).strip())
        for t in tags:
            if t not in TAGS:
                print(f'提醒：第 {no} 行标签〔{t}〕不在 新增/调整/现有 之内，按灰色色块显示')
        node = Node(text, tags, level)
        del stack[level:]
        stack[-1].children.append(node)
        stack.append(node)
    if root is None:
        sys.exit('大纲里没有 "# 中心主题"')
    return root


def walk(node):
    for c in node.children:
        yield c
        yield from walk(c)


# ---------- 渲染 ----------

def esc(s):
    return html.escape(s, quote=False)


def seg_html(s, kind):
    if not s:
        return ''
    if kind == 'b':
        return f'<b>{esc(s)}</b>'
    if kind == 'rest':
        return f'<span class="rest">{esc(s)}</span>'
    return esc(s)


def tag_chips(tags):
    return ''.join(f'<span class="tag tag-{TAGS.get(t, "other")}">{esc(t)}</span>' for t in tags)


def node_div(text, tags, cls, part, lv, all_bold=False, break_after_colon=False):
    """「：」前加粗；all_bold 时没有冒号的整句加粗（中心主题、分支）。
    有标签时，最后一个字和色块绑在一起不拆行，免得色块单独掉到下一行。"""
    if '：' in text:
        head, rest = text.split('：', 1)
        segs = [[head, 'b'], ['：', ''], [rest, 'rest']]
    else:
        segs = [[text, 'b' if all_bold else '']]
    tail = ''
    if tags:
        last = next(s for s in reversed(segs) if s[0])
        tail = f'<span class="nw">{seg_html(last[0][-1], last[1])}{tag_chips(tags)}</span>'
        last[0] = last[0][:-1]
    br = '<br>' if break_after_colon and '：' in text else ''
    body = ''.join(seg_html(s, k) + (br if s == '：' else '') for s, k in segs)
    return (f'<div class="node {cls}" data-part="{part}" data-lv="{lv}">'
            f'<span class="tx">{body}{tail}</span></div>')


def short(text):
    return text.split('：', 1)[0] if '：' in text else text


def ncls(lv):
    return f'n{min(lv, 4)}'


def overview_wide(root, branches):
    half = (len(branches) + 1) // 2
    sides = []
    for side, group, offset in (('side-l', branches[:half], 0), ('side-r', branches[half:], half)):
        items = []
        for i, b in enumerate(group, offset + 1):
            kids = ''.join(f'<li>{node_div(short(c.text), c.tags, "n2", "ov", 2)}</li>' for c in b.children)
            ul = f'<ul>{kids}</ul>' if kids else ''
            items.append(f'<li style="--c:var(--b{color_no(i)})">'
                         f'{node_div(b.text, b.tags, "n1", "ov", 1, True, True)}{ul}</li>')
        sides.append(f'<ul class="side {side}">{"".join(items)}</ul>')
    return (f'<div class="ov-wide"><div class="ov-grid ht">{sides[0]}'
            f'{node_div(root.text, root.tags, "n0", "ov", 0, True, True)}{sides[1]}</div></div>')


def overview_narrow(root, branches):
    items = []
    for i, b in enumerate(branches, 1):
        kids = ''.join(f'<li class="l2">{node_div(short(c.text), c.tags, "n2", "ovn", 2)}</li>' for c in b.children)
        ul = f'<ul>{kids}</ul>' if kids else ''
        items.append(f'<li class="l1" style="--c:var(--b{color_no(i)})">'
                     f'{node_div(b.text, b.tags, "n1", "ovn", 1, True, True)}{ul}</li>')
    return (f'<div class="ov-narrow vt">{node_div(root.text, root.tags, "n0", "ovn", 0, True, True)}'
            f'<ul class="vroot">{"".join(items)}</ul></div>')


def subtree(nodes, lv, part='dt'):
    """part='dt' 宽屏横向树；part='dtn' 窄屏竖向缩进列表（li 带层级类，连线按它定位）。"""
    if not nodes:
        return ''
    li = f'<li class="d{min(lv, 4)}">' if part == 'dtn' else '<li>'
    lis = ''.join(f'{li}{node_div(n.text, n.tags, ncls(lv), part, lv)}{subtree(n.children, lv + 1, part)}</li>'
                  for n in nodes)
    return f'<ul class="u{min(lv, 4)}">{lis}</ul>'


def detail(b, i):
    """卡片不另写标题：树的根节点就是分支名。宽屏横向树、窄屏竖向列表各一份，按屏宽切换。"""
    return (f'<section class="detail" style="--c:var(--b{color_no(i)})" aria-label="{html.escape(b.text)}">'
            f'<div class="scroll dt-wide"><div class="ht dtree"><div class="droot">'
            f'{node_div(b.text, b.tags, "n1", "dt", 1, True, True)}{subtree(b.children, 2)}'
            f'</div></div></div>'
            f'<div class="dt-narrow vt">'
            f'{node_div(b.text, b.tags, "n1", "dtn", 1, True, True)}{subtree(b.children, 2, "dtn")}'
            f'</div></section>')


def color_no(i):
    return (i - 1) % 6 + 1


LIGHT = {
    'bg': '#F4F5F7', 'surface': '#FFFFFF', 'ink': '#1F2328', 'ink-2': '#4B5563',
    'border': '#D5DAE1', 'soft': '#EFF1F4',
    'root-bg': '#1F2937', 'root-ink': '#FFFFFF', 'line-root': '#8B95A3',
    'b1': '#4F86D9', 'b2': '#2E9E90', 'b3': '#8B6BD1', 'b4': '#62A03E', 'b5': '#B4609E', 'b6': '#A97B52',
    'tag-new': '#D93A3F', 'tag-new-ink': '#FFFFFF',
    'tag-adj': '#F2B200', 'tag-adj-ink': '#3A2A00',
    'tag-old': '#6B7280', 'tag-old-ink': '#FFFFFF',
}
DARK = {
    'bg': '#15171B', 'surface': '#1E2127', 'ink': '#E7E9EC', 'ink-2': '#A9B0BA',
    'border': '#3A404A', 'soft': '#272B32',
    'root-bg': '#E5E7EB', 'root-ink': '#111827', 'line-root': '#7A8491',
    'b1': '#7AA6EC', 'b2': '#55C0B1', 'b3': '#AB93E6', 'b4': '#8BC26A', 'b5': '#D58BC2', 'b6': '#C99E76',
    'tag-new': '#E5484D', 'tag-new-ink': '#FFFFFF',
    'tag-adj': '#E8AC00', 'tag-adj-ink': '#2A1E00',
    'tag-old': '#6B7280', 'tag-old-ink': '#FFFFFF',
}

# 节点尺寸：字号、行高、上下内边距、边框（窄屏竖排连线要按它算节点首行中线）
M = {
    'n0': (22, 30, 12, 0), 'n1': (16, 24, 7, 2), 'n2': (15, 23, 5, 1.5),
    'n3': (14, 22, 4, 1), 'n4': (14, 22, 4, 1), 'ov2': (14, 22, 4, 1.5),
}


def vars_css(d):
    return ';'.join(f'--{k}:{v}' for k, v in d.items())


def css():
    def metric(key):
        fs, lh, py, bw = M[key]
        return f'--fs:{fs}px;--lh:{lh}px;--py:{py}px;--bw:{bw}px'

    def half(key):  # 节点首行中线到节点上边的距离
        fs, lh, py, bw = M[key]
        return lh / 2 + py + bw

    half_l1, half_l2 = half('n1'), half('ov2')
    return f"""
:root{{{vars_css(LIGHT)};color-scheme:light dark}}
@media (prefers-color-scheme: dark){{:root{{{vars_css(DARK)}}}}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC","Source Han Sans SC",sans-serif;font-size:15px;line-height:1.5}}
.page{{max-width:1440px;margin:0 auto;padding:28px 32px 48px}}
.hd{{margin-bottom:18px}}
.hd h1{{margin:0 0 10px;font-size:26px;line-height:34px;font-weight:700;letter-spacing:.5px}}
.legend{{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px 26px;font-size:14px;line-height:22px;color:var(--ink-2)}}
.legend li{{--lh:22px;display:flex;align-items:center}}
.legend .tag{{margin:0 8px 0 0}}

.tag{{display:inline-block;vertical-align:top;margin-top:2px;margin-inline-start:6px;padding:0 6px;border-radius:5px;font-size:14px;line-height:calc(var(--lh) - 4px);font-weight:600;white-space:nowrap}}
.tag-new{{background:var(--tag-new);color:var(--tag-new-ink)}}
.tag-adj{{background:var(--tag-adj);color:var(--tag-adj-ink)}}
.tag-old{{background:var(--tag-old);color:var(--tag-old-ink)}}
.tag-other{{background:var(--ink-2);color:var(--surface)}}
.tag-none{{width:40px;height:calc(var(--lh) - 4px);border:1.5px dashed var(--ink-2);background:transparent}}

.node{{position:relative;flex:0 0 auto;max-width:360px;padding:var(--py) calc(var(--py) + 6px);border:var(--bw) solid transparent;border-radius:8px;background:var(--surface);color:var(--ink);font-size:var(--fs);line-height:var(--lh);font-weight:400;overflow-wrap:anywhere;text-wrap:pretty;direction:ltr;text-align:start}}
.node b{{font-weight:700}}
.node .rest{{font-weight:400}}
.nw{{white-space:nowrap}}
.n0{{{metric('n0')};padding-inline:22px;background:var(--root-bg);color:var(--root-ink);border-radius:14px;letter-spacing:.5px;text-align:center}}
.n0 .rest{{font-size:17px;letter-spacing:0}}
.n1{{{metric('n1')};padding-inline:14px;border-color:var(--c);background:color-mix(in srgb,var(--c) 16%,var(--surface));border-radius:10px}}
.n2{{{metric('n2')};border-color:var(--c);font-weight:500}}
.n3{{{metric('n3')};border-color:var(--border)}}
.n4{{{metric('n4')};background:var(--soft)}}
.ov .n2{{{metric('ov2')};max-width:300px}}

/* 横向树：嵌套列表＋伪元素连线；方向用逻辑属性，左半边设 rtl 即镜像 */
.ht{{--g1:22px;--g2:20px;--r:8px;--vg:4px}}
.ht ul{{list-style:none;margin:0;padding:0;margin-inline-start:var(--g1);display:flex;flex-direction:column;position:relative;flex:0 0 auto;--trunk:var(--c);--lw:1.5px}}
.ht ul::before{{content:"";position:absolute;inset-inline-start:calc(-1 * var(--g1));inline-size:var(--g1);top:calc(50% - var(--lw) / 2);border-top:var(--lw) solid var(--trunk)}}
.ht li{{position:relative;display:flex;align-items:center;padding-block:var(--vg);padding-inline-start:var(--g2)}}
.ht li::before,.ht li::after{{content:"";position:absolute;box-sizing:border-box;pointer-events:none}}
.ht li::before{{top:calc(50% - var(--lw) / 2);inset-inline-start:0;inline-size:var(--g2);border-top:var(--lw) solid var(--c)}}
.ht li::after{{top:0;bottom:0;inset-inline-start:0;border-inline-start:var(--lw) solid var(--trunk)}}
.ht li:first-child::after{{top:calc(50% - var(--lw) / 2);inline-size:var(--r);border-top:var(--lw) solid var(--trunk);border-start-start-radius:var(--r)}}
.ht li:last-child::after{{bottom:calc(50% - var(--lw) / 2);inline-size:var(--r);border-bottom:var(--lw) solid var(--trunk);border-end-start-radius:var(--r)}}
.ht li:first-child::before,.ht li:last-child::before{{inset-inline-start:var(--r);inline-size:calc(var(--g2) - var(--r))}}
.ht li:only-child::after{{display:none}}
.ht li:only-child::before{{inset-inline-start:0;inline-size:var(--g2)}}

/* 全景 */
.ov{{margin:0 0 28px}}
.ov-wide{{overflow-x:auto;overflow-y:hidden;padding:6px 0;margin-inline:-20px}}
.ov-grid{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;min-width:max-content}}
.ov-grid > .n0{{grid-column:2}}
.ov .side{{--trunk:var(--line-root);--lw:2.5px;--g1:22px;--g2:24px;--vg:7px}}
.ov .side > li > ul{{--lw:2px;--g1:18px;--g2:18px;--vg:3px}}
.ov .side-l{{justify-self:end;direction:rtl}}
.ov .side-r{{justify-self:start}}
.ov-narrow{{display:none}}

/* 竖排树（窄屏全景） */
.vt{{--vi:22px;--g2:18px;--r:8px;--vgap:8px}}
.vt .node{{display:block;width:fit-content;max-width:min(360px,100%)}}
.vt ul{{list-style:none;margin:0;padding:0;margin-inline-start:var(--vi);--trunk:var(--c);--lw:2px}}
.vt .vroot{{--trunk:var(--line-root);--lw:2.5px}}
.vt li{{position:relative;padding-top:var(--vgap);padding-inline-start:var(--g2)}}
.vt li.l1{{--vgap:12px;--half:{half_l1}px}}
.vt li.l2{{--vgap:6px;--half:{half_l2}px}}
.vt li::before,.vt li::after{{content:"";position:absolute;box-sizing:border-box;pointer-events:none}}
.vt li::after{{top:0;bottom:0;inset-inline-start:0;border-inline-start:var(--lw) solid var(--trunk)}}
.vt li::before{{top:calc(var(--vgap) + var(--half) - var(--lw) / 2);inset-inline-start:0;inline-size:var(--g2);border-top:var(--lw) solid var(--c)}}
.vt li:last-child::after{{bottom:auto;height:calc(var(--vgap) + var(--half) + var(--lw) / 2);inline-size:var(--r);border-bottom:var(--lw) solid var(--trunk);border-end-start-radius:var(--r)}}
.vt li:last-child::before{{inset-inline-start:var(--r);inline-size:calc(var(--g2) - var(--r))}}

/* 分支详图：宽屏横向树，窄屏竖向缩进列表（连线用分支色） */
.detail{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px 22px;margin-top:18px}}
.scroll{{overflow-x:auto;padding:2px}}
.dtree{{width:max-content;--g1:24px;--g2:18px}}
.droot{{display:flex;align-items:center}}
.dtree ul.u2{{--lw:2px;--vg:5px}}
.dt-narrow{{display:none;--vi:16px;--g2:14px;--r:6px}}
.dt-narrow ul.u2{{--lw:2px}}
.dt-narrow ul.u3,.dt-narrow ul.u4{{--lw:1.5px}}
.dt-narrow li.d2{{--vgap:10px;--half:{half('n2')}px}}
.dt-narrow li.d3{{--vgap:6px;--half:{half('n3')}px}}
.dt-narrow li.d4{{--vgap:4px;--half:{half('n4')}px}}

@media screen and (max-width: 899.98px){{
  .page{{padding:20px 16px 40px}}
  .hd h1{{font-size:22px;line-height:30px}}
  .ov-wide{{display:none}}
  .ov-narrow{{display:block}}
  .ov .n0{{--fs:20px;--lh:28px;--py:10px}}
  .detail{{padding:14px 14px 16px;border-radius:12px}}
  .dt-wide{{display:none}}
  .dt-narrow{{display:block}}
}}

@media print{{
  @page{{size:A4 portrait;margin:10mm}}
  @page overview{{size:A4 landscape;margin:10mm}}
  .hd,.ov{{page:overview}}
  :root{{{vars_css(LIGHT)};color-scheme:light}}
  html,body{{background:#FFFFFF}}
  body{{zoom:.7;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  .page{{max-width:none;padding:0}}
  .ov-wide,.scroll{{overflow:visible}}
  .ov{{break-after:page}}
  .detail{{break-before:page;page-break-before:always}}
  .detail li.d3,.detail li.d4{{break-inside:avoid;page-break-inside:avoid}}
  .detail li.d2>:first-child{{break-after:avoid;page-break-after:avoid}}
  .detail li.d2>ul>li:first-child{{break-before:avoid;page-break-before:avoid}}
  .dt-wide{{display:none}}
  .dt-narrow{{display:block}}
}}
"""


def render(root):
    branches = root.children
    used = {t for n in walk(root) for t in n.tags}
    legend = [(t, s) for t, s in LEGEND if not t or t in used] if used else []  # 图里没用到的标签不进图例；全图没有标签就不出图例
    body = (f'<div class="page">'
            f'<header class="hd"><h1>{esc(TITLE)}</h1><ul class="legend">'
            + ''.join(f'<li><span class="tag tag-{TAGS[t]}">{t}</span>{esc(s)}</li>' if t else
                      f'<li><span class="tag tag-none" aria-hidden="true"></span>{esc(s)}</li>' for t, s in legend)
            + '</ul></header>'
            f'<section class="ov">{overview_wide(root, branches)}{overview_narrow(root, branches)}</section>'
            + ''.join(detail(b, i) for i, b in enumerate(branches, 1))
            + '</div>')
    return ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(TITLE)}</title>\n<style>{css()}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n')


# ---------- 核对：HTML 里的节点文字与大纲逐条对上 ----------

NODE_RE = re.compile(r'<div class="node (n\d)" data-part="(\w+)" data-lv="(\d+)">(.*?)</div>', re.S)
CHIP_RE = re.compile(r'<span class="tag tag-\w+">(.*?)</span>')


def html_nodes(doc):
    out = []
    for cls, part, lv, inner in NODE_RE.findall(doc):
        tags = [html.unescape(t) for t in CHIP_RE.findall(inner)]
        text = html.unescape(re.sub(r'<[^>]+>', '', CHIP_RE.sub('', inner)))
        out.append((part, int(lv), text, tuple(tags)))
    return out


def check(root, doc):
    items = list(walk(root))
    got = html_nodes(doc)
    problems = []

    want_dt = Counter((n.level, n.text, tuple(n.tags)) for n in items)
    for part, name in (('dt', '详图(宽屏)'), ('dtn', '详图(窄屏)')):
        have_dt = Counter((lv, t, tags) for p, lv, t, tags in got if p == part)
        if want_dt != have_dt:
            problems.append(f'{name}缺：{list((want_dt - have_dt).elements())}；多：{list((have_dt - want_dt).elements())}')

    want_ov = Counter([(0, root.text, tuple(root.tags))]
                      + [(1, b.text, tuple(b.tags)) for b in root.children]
                      + [(2, short(c.text), tuple(c.tags)) for b in root.children for c in b.children])
    for part in ('ov', 'ovn'):
        have = Counter((lv, t, tags) for p, lv, t, tags in got if p == part)
        if want_ov != have:
            problems.append(f'全景({part})缺：{list((want_ov - have).elements())}；多：{list((have - want_ov).elements())}')

    visible = re.sub(r'<style>.*?</style>', '', doc, flags=re.S)
    if '〔' in visible or '〕' in visible:
        problems.append('HTML 里还有〔〕方括号文字')

    plain = html.unescape(re.sub(r'<[^>]+>', '', visible))
    for n in [root] + items:
        if n.text not in plain:
            problems.append(f'正文里找不到：{n.text}')

    by_lv = Counter(n.level for n in items)
    tag_n = Counter(t for n in items for t in n.tags)
    print(f'节点总数 {1 + len(items)}（中心 1，' + '，'.join(f'第{k}层 {by_lv[k]}' for k in sorted(by_lv)) + '）')
    print(f'详图节点 {sum(want_dt.values())}（宽屏、窄屏各一份），全景节点 {sum(want_ov.values())}，标签 '
          + '，'.join(f'{k} {v}' for k, v in tag_n.items()))
    if problems:
        print('核对不通过：')
        for p in problems:
            print('  -', p)
        sys.exit(1)
    print('核对通过：大纲每个节点的文字都在 HTML 里，数量一致；没有〔〕方括号文字')


def main():
    root = parse(SRC)
    if len(root.children) != 6:
        print(f'提醒：分支数是 {len(root.children)}，不是 6；全景按左 {(len(root.children) + 1) // 2} 右其余排')
    doc = render(root)
    OUT.write_text(doc, encoding='utf-8')
    print(f'已写出 {OUT}')
    check(root, OUT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
