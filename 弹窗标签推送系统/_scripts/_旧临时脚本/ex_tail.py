"""打印进展日志最后 8 行、设计卡最后 60 行、任务清单最后 10 行。不带参数运行。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel, n in [('进展日志.md', 8), ('过程记录/设计卡.md', 60), ('过程记录/任务清单.md', 6)]:
    p = os.path.join(BASE, rel)
    lines = open(p, encoding='utf-8').read().splitlines()
    print('=' * 20, rel, '总行数', len(lines))
    for i, l in enumerate(lines[-n:], len(lines) - n + 1):
        print(i, l[:900])
