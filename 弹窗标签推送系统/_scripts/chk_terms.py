import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
base = _ROOT + '/'
txt = open(base + '过程记录/迭代记录.md', encoding='utf-8').read()
lines = txt.split('\n')
print(len(lines), '行')
for i, l in enumerate(lines):
    if l.startswith('#'):
        print(i + 1, l[:100])
print('---- tail')
print('\n'.join(lines[-14:]))
