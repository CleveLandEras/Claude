import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
p = _ROOT + '/过程记录/任务清单.md'
lines = open(p, encoding='utf-8').read().split('\n')
s = None
e = len(lines)
for i, l in enumerate(lines):
    if l.startswith('## 四'):
        s = i
    elif s is not None and l.startswith('## ') and i > s:
        e = i
        break
print('section lines', s, e)
for l in lines[max(s, e - 30):e]:
    print(l[:700])
