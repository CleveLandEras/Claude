"""列出迭代记录各「## 」节标题及每节最后一个版本行与节末行号。只读，不带参数。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(B, '过程记录/迭代记录.md'), encoding='utf-8').read().split('\n')
sec, last, start = None, None, 0
def out(end):
    if sec: print(f'{start}-{end}', sec[:40], '| 最后版本：', (last or '')[:70])
for i, l in enumerate(L, 1):
    if l.startswith('## '):
        out(i - 1); sec, last, start = l, None, i
    elif re.match(r'^(### )?v\d', l):
        last = f'{i}: {l}'
out(len(L))
