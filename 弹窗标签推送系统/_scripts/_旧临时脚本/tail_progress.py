"""打印 进展日志.md 的总行数与最后 6 行（带行号，完整内容）。不带参数运行。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '进展日志.md')
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i in range(max(0, len(lines) - 6), len(lines)):
    print(i + 1, repr(lines[i]))
