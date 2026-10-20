#!/usr/bin/env python3
# 需求文档拼装：把 推送系统后台集成需求/需求文档源/ 下按章拆开的源文件（第 4 章拆到 4.x.y 小节，第 5 章拆到 5.x 小节），
# 按 _顺序.txt 的顺序原样首尾相接，生成 4_需求文档.md。
# 第 1 章只留最近 3 条修改记录：源文件 1_修改记录.md 里的占位行，拼装时换成 需求文档_修改记录.md 表头与最后 3 行
#   （其中「](4_需求文档.md#」链接换回本文内的「](#」）。新版本只在 需求文档_修改记录.md 表末加一行，第 1 章不另改。
#
# 用法：python3 _scripts/an_需求文档拼装.py            拼装并写出 4_需求文档.md
#       python3 _scripts/an_需求文档拼装.py 比对       只拼装到内存，报告与现有 4_需求文档.md 是否一致，不写文件
#       python3 _scripts/an_需求文档拼装.py 找 <文字>   列出含该文字的源文件与行号（改稿前先用它定位要改的源文件）
#       python3 _scripts/an_需求文档拼装.py 强制       4_需求文档.md 被直接改过时也照样覆盖（直接改的内容会丢，慎用）
#
# 规则：改需求文档＝改 需求文档源/ 里对应小节的文件，再运行本脚本；不要直接改 4_需求文档.md。
#   每次写出后把结果的指纹记在 需求文档源/_上次拼装.txt；下次拼装前若发现 4_需求文档.md 与上次写出的不同（有人直接改过），
#   先停下并提示，把那些改动搬进源文件后再拼装（或确认丢弃后用「强制」）。
#   新增小节：在 需求文档源/ 新建文件，并在 _顺序.txt 相应位置加一行文件名。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, re, hashlib

BASE = _ROOT + '/推送系统后台集成需求/'
SRC = BASE + '需求文档源/'
OUT = BASE + '4_需求文档.md'
REC = BASE + '需求文档_修改记录.md'
MARK = SRC + '_上次拼装.txt'
SLOT = '<!-- 拼装时在此换成 需求文档_修改记录.md 的表头与最后 3 行，勿手改 -->'


def recent3():
    lines = open(REC, encoding='utf-8').read().split('\n')
    hd = [i for i, l in enumerate(lines) if l.startswith('| 版本号 |')][0]
    rows = []
    for l in lines[hd + 2:]:
        if not l.startswith('|'):
            break
        rows.append(l)
    return '\n'.join(lines[hd:hd + 2] + [re.sub(r'\]\(4_需求文档\.md#', '](#', r) for r in rows[-3:]])


def assemble():
    names = [l.strip() for l in open(SRC + '_顺序.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
    missing = [n for n in names if not os.path.exists(SRC + n)]
    if missing:
        sys.exit('源文件不存在：' + '、'.join(missing))
    extra = sorted(f for f in os.listdir(SRC) if f.endswith('.md') and f not in names)
    if extra:
        print('提醒：这些源文件不在 _顺序.txt 里，没有拼进去：' + '、'.join(extra))
    text = ''.join(open(SRC + n, encoding='utf-8').read() for n in names)
    if text.count(SLOT) != 1:
        sys.exit('1_修改记录.md 里的占位行应恰好 1 处')
    return text.replace(SLOT, recent3()), names


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

md, names = assemble()
cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None
if cmd == '比对':
    print('一致' if cur == md else '不一致：4_需求文档.md 与源文件拼装结果不同')
    sys.exit(0 if cur == md else 1)
if cur is not None and cur != md and os.path.exists(MARK) and cmd != '强制':
    if sha(cur) != open(MARK, encoding='utf-8').read().split()[0]:
        sys.exit('停：4_需求文档.md 在上次拼装后被直接改过。先把改动搬进 需求文档源/ 再拼装；确认丢弃这些改动时用「强制」。')
open(OUT, 'w', encoding='utf-8').write(md)
open(MARK, 'w', encoding='utf-8').write(sha(md) + '\n')
print('已拼装 4_需求文档.md：%d 个源文件，%d 字' % (len(names), len(md)))
