import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
"""打印任务清单.md 与进展日志.md 的行数和最后 4 行（只读，不带参数）。"""
for name in ['任务清单.md', '进展日志.md']:
    p = _ROOT + '/' + name
    with open(p, encoding='utf-8') as f:
        lines = f.readlines()
    print('==', name, '总行数', len(lines))
    for i in range(max(0, len(lines) - 4), len(lines)):
        print(i + 1, lines[i].rstrip()[:300])
