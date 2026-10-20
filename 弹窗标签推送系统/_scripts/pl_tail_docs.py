import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
base = _ROOT + '/过程记录/'
for name, n in [('审查记录.md', 9000), ('设计卡.md', 7000), ('迭代记录.md', 3500)]:
    t = open(base + name, encoding='utf-8').read()
    print('=' * 20, name, len(t))
    print(t[-n:])
