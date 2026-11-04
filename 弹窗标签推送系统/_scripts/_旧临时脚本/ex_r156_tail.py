"""只读：打印任务清单与进展日志的总行数和最后 3 行。不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel in (os.path.join('过程记录', '任务清单.md'), '进展日志.md'):
    lines = open(os.path.join(BASE, rel), encoding='utf-8').read().split('\n')
    print('==', rel, '总行数', len(lines))
    for i in range(max(0, len(lines) - 3), len(lines)):
        print(i + 1, lines[i][:300])
