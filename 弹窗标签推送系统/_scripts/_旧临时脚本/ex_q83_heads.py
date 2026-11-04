"""Q83 辅助：列出迭代记录的二级标题行号，以及含「核对表第 22 行」的行号（只读）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '过程记录', '迭代记录.md')
for i, line in enumerate(open(p, encoding='utf-8'), 1):
    if line.startswith('## ') or '核对表第 22 行' in line:
        print(i, line.rstrip()[:120])
