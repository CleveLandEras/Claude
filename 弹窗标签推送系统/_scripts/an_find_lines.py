import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
"""定位任务清单、进展日志的节标题与总行数（只读）。不带参数运行。"""
for name in ('任务清单.md', '进展日志.md'):
    p = _ROOT + '/' + name
    lines = open(p, encoding='utf-8').read().split('\n')
    print(name, '总行数', len(lines))
    for i, l in enumerate(lines, 1):
        if l.startswith('## '):
            print(' ', i, l[:60])
