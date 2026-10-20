import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
p = _ROOT + '/过程记录/任务清单.md'
lines = open(p, encoding='utf-8').read().splitlines()
print('total', len(lines))
for i, l in enumerate(lines):
    if '2026-10-09' in l:
        print(i + 1, l[:400])
