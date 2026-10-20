#!/usr/bin/env python3
# 精简版原型拼装：把 推送系统后台集成需求/原型源_精简/ 下按页拆开的源文件，按 _顺序.txt 的顺序首尾相接，
# 并把 原型样式.css 内联进去，写出单个文件 推送系统后台集成需求/3_原型.html（直接打开即可，不依赖同目录的 css）。
#
# 用法：python3 _scripts/an_原型拼装_精简.py              拼装并写出 3_原型.html
#       python3 _scripts/an_原型拼装_精简.py 检查 [文件…]   检查标签是否配平（不给文件就检查全部源文件）
#       python3 _scripts/an_原型拼装_精简.py 找 <文字>      列出含该文字的源文件与行号
#
# 规则：改原型＝改 原型源_精简/ 里对应页的文件，再运行本脚本；不要直接改 3_原型.html。
#   新增一页：在 原型源_精简/ 新建文件，并在 _顺序.txt 相应位置加一行文件名。
#   拼装时顺带检查：标签配平、页内 id 不重复、「#锚点」都有对应 id。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, re
from html.parser import HTMLParser

BASE = _ROOT + '/推送系统后台集成需求/'
SRC = BASE + '原型源_精简/'
OUT = BASE + '3_原型.html'
CSS = BASE + '原型样式.css'
LINK = '<link rel="stylesheet" href="原型样式.css">'
VOID = {'meta', 'link', 'br', 'img', 'hr', 'input', 'col', 'wbr', 'area', 'base'}


class Bal(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errs, self.ids = [], [], []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == 'id':
                self.ids.append(v)
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        for k, v in attrs:
            if k == 'id':
                self.ids.append(v)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errs.append('多余的 </%s>（第 %d 行）' % (tag, self.getpos()[0]))
        elif self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.errs.append('第 %d 行 </%s> 与第 %d 行 <%s> 不配对' % (self.getpos()[0], tag, self.stack[-1][1], self.stack[-1][0]))
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break


def check_text(t):
    p = Bal()
    p.feed(t)
    errs = list(p.errs) + ['第 %d 行 <%s> 没有闭合' % (ln, tg) for tg, ln in p.stack]
    return errs, p.ids


def names():
    ns = [l.strip() for l in open(SRC + '_顺序.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
    miss = [n for n in ns if not os.path.exists(SRC + n)]
    if miss:
        sys.exit('源文件不存在：' + '、'.join(miss))
    return ns


cmd = sys.argv[1] if len(sys.argv) > 1 else '拼装'
if cmd == '找':
    for n in names():
        for i, l in enumerate(open(SRC + n, encoding='utf-8'), 1):
            if sys.argv[2] in l:
                p = l.find(sys.argv[2])
                print('%s:%d  …%s…' % (n, i, l[max(0, p - 30):p + len(sys.argv[2]) + 30].strip()))
    sys.exit(0)

if cmd == '检查':
    fs = sys.argv[2:] or [n for n in os.listdir(SRC) if n.endswith('.html')]
    bad = 0
    for f in sorted(fs):
        path = f if os.path.isabs(f) else SRC + os.path.basename(f)
        errs, _ = check_text(open(path, encoding='utf-8').read())
        if errs:
            bad += 1
            print('✘ %s：%s' % (os.path.basename(path), '；'.join(errs[:6])))
        else:
            print('✓ %s 标签配平' % os.path.basename(path))
    sys.exit(1 if bad else 0)

ns = names()
extra = sorted(f for f in os.listdir(SRC) if f.endswith('.html') and f not in ns)
if extra:
    print('提醒：这些源文件不在 _顺序.txt 里，没有拼进去：' + '、'.join(extra))
html = ''.join(open(SRC + n, encoding='utf-8').read() for n in ns)
if LINK not in html:
    sys.exit('页首里找不到：' + LINK)
html = html.replace(LINK, '<style>\n' + open(CSS, encoding='utf-8').read().strip() + '\n</style>', 1)
errs, ids = check_text(html)
dup = sorted({i for i in ids if ids.count(i) > 1})
anch = set(re.findall(r'href="#([^"]+)"', html))
noid = sorted(a for a in anch if a not in ids)
if errs:
    print('✘ 标签：' + '；'.join(errs[:8]))
if dup:
    print('✘ id 重复：' + '、'.join(dup))
if noid:
    print('✘ 锚点没有对应 id：' + '、'.join(noid))
open(OUT, 'w', encoding='utf-8').write(html)
print('已拼装 3_原型.html：%d 个源文件，%d 字符' % (len(ns), len(html)))
sys.exit(1 if (errs or dup or noid) else 0)
