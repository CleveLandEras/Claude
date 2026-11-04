import os
p = os.path.join(os.path.dirname(__file__), '..', '过程记录', '审查记录.md')
lines = open(p, encoding='utf-8').read().split('\n')
start = None
for i, l in enumerate(lines):
    if l.startswith('## 2026-09-29 01:20'):
        start = i
    if start is not None and i > start and l.startswith('## 2026-09-29 01:25'):
        end = i
        break
else:
    end = len(lines)
print('行号', start + 1, '到', end, '，全文行数', len(lines))
for l in lines[start:end]:
    print(l)
# 末尾几节标题
print('==== 最后 5 个节标题 ====')
hs = [(i + 1, l) for i, l in enumerate(lines) if l.startswith('## ')]
for h in hs[-5:]:
    print(h)
