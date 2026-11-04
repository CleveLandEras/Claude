"""Q83 辅助：打印任务清单、进展日志的总行数与最后 3 行（只读）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel in (('过程记录', '任务清单.md'), ('进展日志.md',)):
    p = os.path.join(BASE, *rel)
    lines = open(p, encoding='utf-8').read().split('\n')
    print('=' * 20, rel[-1], '共', len(lines), '行')
    for i in range(max(0, len(lines) - 4), len(lines)):
        print(i + 1, lines[i][:300])
