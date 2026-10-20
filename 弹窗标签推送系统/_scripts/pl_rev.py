import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
p = _ROOT + '/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read().split('\n')
heads = [i for i, l in enumerate(t) if l.startswith('## ')]
print('total', len(t), 'last heads:', [t[i][:80] for i in heads[-4:]])
for l in t[heads[-2]:]:
    print(l[:600])
