import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
base = _ROOT + '/过程记录/'
lines = open(base + '任务清单.md', encoding='utf-8').read().split('\n')
start = None
end = len(lines)
for i, l in enumerate(lines):
    if l.startswith('## 四'):
        start = i
    elif start is not None and l.startswith('## ') and i > start:
        end = i
        break
print('section 四 lines', start, end, 'total', len(lines))
sec = lines[start:end]
# print header area and rows mentioning 10/9 or 10-09
for i, l in enumerate(sec[:15]):
    print(start + i, l[:400])
print('----- rows mentioning 10/9 / 10-09 -----')
for i, l in enumerate(sec):
    if ('10/9' in l or '10-09' in l or '10/09' in l):
        print(start + i, l[:700])
print('----- last 8 lines -----')
for i, l in enumerate(sec[-8:]):
    print(end - 8 + i, l[:700])

print('===== 审查记录 last headers =====')
rl = open(base + '审查记录.md', encoding='utf-8').read().split('\n')
heads = [(i, l) for i, l in enumerate(rl) if l.startswith('## ')]
print('total', len(rl))
for i, l in heads[-6:]:
    print(i, l)
