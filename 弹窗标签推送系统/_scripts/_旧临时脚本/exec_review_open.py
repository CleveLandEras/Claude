"""执行者用：列出审查记录中状态为退回、且条目内没有「已处理」「有异议」的条目；并打印最后一节审查的行号。不带参数。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '过程记录', '审查记录.md')
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
secs = [i for i, l in enumerate(lines) if l.startswith('## ')]
print('最后三节:', [(i + 1, lines[i]) for i in secs[-3:]])
items = [i for i, l in enumerate(lines) if l.startswith('### ')]
items.append(len(lines))
for a, b in zip(items, items[1:]):
    head = lines[a]
    body = '\n'.join(lines[a:b])
    if '退回' in head and '已处理' not in body and '有异议' not in body:
        print('未处理：行', a + 1, head)
