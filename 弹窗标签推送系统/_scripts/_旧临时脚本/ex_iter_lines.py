"""打印迭代记录.md 中各节标题与最近版本行的行号（只读）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '迭代记录.md')
for i, line in enumerate(open(p, encoding='utf-8'), 1):
    s = line.rstrip('\n')
    if s.startswith('## ') or s.startswith('v11（') or s.startswith('v12（') or s.startswith('v13（'):
        print(i, s[:80])
