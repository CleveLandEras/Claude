import os
p = os.path.join(os.path.dirname(__file__), '..', '进展日志.md')
lines = open(p, encoding='utf-8').read().split('\n')
print('全文行数', len(lines))
for i, l in enumerate(lines[-8:], start=len(lines) - 7):
    print(i, l[:600])
