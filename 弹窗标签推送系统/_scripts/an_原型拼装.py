#!/usr/bin/env python3
# 原型拼装：把 推送系统后台集成需求/原型源/ 下按页拆开的源文件，按 _顺序.txt 的顺序原样首尾相接，生成 3_原型.html。
# 样式不在源文件里：3_原型.html 用 <link> 引用同目录的 原型样式.css（验收用例.html 也引用它），改样式直接改该 css。
#
# 用法：python3 _scripts/an_原型拼装.py            拼装并写出 3_原型.html
#       python3 _scripts/an_原型拼装.py 比对       只拼装到内存，报告与现有 3_原型.html 是否一致，不写文件
#       python3 _scripts/an_原型拼装.py 找 <文字>   列出含该文字的源文件与行号（改稿前先用它定位要改的源文件）
#       python3 _scripts/an_原型拼装.py 强制       3_原型.html 被直接改过时也照样覆盖（直接改的内容会丢，慎用）
#
# 规则：改原型＝改 原型源/ 里对应页的文件，再运行本脚本；不要直接改 3_原型.html。
#   每次写出后把结果的指纹记在 原型源/_上次拼装.txt；下次拼装前若发现 3_原型.html 与上次写出的不同（有人直接改过），
#   先停下并提示，把那些改动搬进源文件后再拼装（或确认丢弃后用「强制」）。
#   新增一页：在 原型源/ 新建文件，并在 _顺序.txt 相应位置加一行文件名。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, hashlib

BASE = _ROOT + '/推送系统后台集成需求/'
SRC = BASE + '原型源/'
OUT = BASE + '3_原型.html'
MARK = SRC + '_上次拼装.txt'


def assemble():
    names = [l.strip() for l in open(SRC + '_顺序.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
    missing = [n for n in names if not os.path.exists(SRC + n)]
    if missing:
        sys.exit('源文件不存在：' + '、'.join(missing))
    extra = sorted(f for f in os.listdir(SRC) if f.endswith('.html') and f not in names)
    if extra:
        print('提醒：这些源文件不在 _顺序.txt 里，没有拼进去：' + '、'.join(extra))
    return ''.join(open(SRC + n, encoding='utf-8').read() for n in names), names


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


cmd = sys.argv[1] if len(sys.argv) > 1 else '拼装'
if cmd == '找':
    w = sys.argv[2]
    for n in assemble()[1]:
        for i, l in enumerate(open(SRC + n, encoding='utf-8'), 1):
            if w in l:
                p = l.find(w)
                print('%s:%d  …%s…' % (n, i, l[max(0, p - 30):p + len(w) + 30].strip()))
    sys.exit(0)

html, names = assemble()
cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None
if cmd == '比对':
    print('一致' if cur == html else '不一致：3_原型.html 与源文件拼装结果不同')
    sys.exit(0 if cur == html else 1)
if cur is not None and cur != html and os.path.exists(MARK) and cmd != '强制':
    if sha(cur) != open(MARK, encoding='utf-8').read().split()[0]:
        sys.exit('停：3_原型.html 在上次拼装后被直接改过。先把改动搬进 原型源/ 再拼装；确认丢弃这些改动时用「强制」。')
open(OUT, 'w', encoding='utf-8').write(html)
open(MARK, 'w', encoding='utf-8').write(sha(html) + '\n')
print('已拼装 3_原型.html：%d 个源文件，%d 字' % (len(names), len(html)))
