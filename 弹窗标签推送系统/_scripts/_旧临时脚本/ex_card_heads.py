"""列出设计卡.md 的各级标题与状态行（只读，不带参数）。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(B, '过程记录/设计卡.md')
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines, 1):
    if l.startswith('#') or '状态' in l[:20]:
        print(i, l[:150])
