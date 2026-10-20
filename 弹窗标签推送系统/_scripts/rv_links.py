import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
base = _ROOT + '/'
t = open(base + '过程记录/审查记录.md', encoding='utf-8').read()
i = t.rfind('\n## ')
print(len(t))
print(t[i:])
