"""Q85：定位决策汇报第三节标题与过时提示所在行号（只读）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '决策汇报.html')
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, s in enumerate(lines, 1):
    if ('<section' in s) or ('本节是问题诊断之前写的' in s) or ('<h2' in s) or ('环节3' in s):
        print(i, s[:220])
