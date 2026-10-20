import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
p = _ROOT + '/过程记录/任务清单.md'
lines = open(p, encoding='utf-8').read().split('\n')
start = None
for i, l in enumerate(lines):
    if l.startswith('## 四'):
        start = i
    elif start is not None and l.startswith('## ') and i > start:
        end = i
        break
print('section 4 lines', start, end)
sec = lines[start:end]
for l in sec[-12:]:
    print(l[:700])
    print('---')
