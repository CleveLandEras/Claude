t = open(_ROOT + '/过程记录/任务清单.md', encoding='utf-8').read()
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
heads = [(m.start(), m.group(0)) for m in re.finditer(r'^#{1,3} .*$', t, re.M)]
for pos, h in heads:
    print(pos, h)
i = t.find('答复登记')
j = None
for pos, h in heads:
    if '答复登记' in h:
        i = pos
for pos, h in heads:
    if pos > i and h.startswith('## '):
        j = pos
        break
seg = t[i:j]
print('=====', len(seg))
print(seg[-7000:])
