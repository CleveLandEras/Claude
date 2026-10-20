import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
p = _ROOT + '/迭代记录.md'
for i, line in enumerate(open(p, encoding='utf-8'), 1):
    s = line.strip()
    if s.startswith('#'):
        print(i, s[:120])
