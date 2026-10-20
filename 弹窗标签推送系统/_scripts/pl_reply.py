import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
base = _ROOT + '/'
lines = open(base + '过程记录/任务清单.md', encoding='utf-8').read().split('\n')
heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
for i, l in heads:
    print(i + 1, l)
s = [i for i, l in heads if l.startswith('## 四')]
if s:
    start = s[0]
    nxt = [i for i, l in heads if i > start]
    end = nxt[0] if nxt else len(lines)
    seg = lines[start:end]
    print('----- 第四节 lines', start + 1, '-', end, '; showing rows mentioning 10-09/10/9')
    for j, l in enumerate(seg):
        if '10-09' in l or '10/9' in l or '10-10' in l:
            print(start + j + 1, l[:600])
