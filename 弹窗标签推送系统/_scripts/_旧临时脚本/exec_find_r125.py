"""执行者用：打印审查记录中 R125 条目全文（到下一个 ### 为止）。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(BASE, '过程记录', '审查记录.md'), encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if l.startswith('### R125'):
        j = i + 1
        while j < len(L) and not L[j].startswith('### ') and not L[j].startswith('## '):
            j += 1
        print('\n'.join(f'{k + 1}: {L[k]}' for k in range(i, j)))
