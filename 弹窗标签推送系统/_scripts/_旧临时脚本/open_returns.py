"""列出审查记录中状态为「退回」且没有「已处理」「有异议」的条目；并打印最后一节审查的标题与行号。不带参数运行。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '过程记录', '审查记录.md')
lines = open(p, encoding='utf-8').read().split('\n')
sections = [i for i, l in enumerate(lines) if l.startswith('## ')]
print('总行数', len(lines), '；最后三节：')
for i in sections[-3:]:
    print(f'  L{i+1}: {lines[i]}')
cur = None; buf = []
items = []
for i, l in enumerate(lines):
    if l.startswith('### ') or l.startswith('## '):
        if cur: items.append((cur, buf))
        cur = (i + 1, l) if l.startswith('### ') else None; buf = []
    elif cur:
        buf.append(l)
if cur: items.append((cur, buf))
for (ln, h), b in items:
    if '退回' in h:
        body = '\n'.join(b)
        if '已处理' not in body and '有异议' not in body:
            print(f'未处理 L{ln}: {h}')
