"""打印 任务清单.md 的节标题行号与最后 3 行、进展日志.md 的最后 3 行。不带参数运行。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel in [os.path.join('过程记录', '任务清单.md'), '进展日志.md']:
    L = open(os.path.join(BASE, rel), encoding='utf-8').read().split('\n')
    print('=' * 20, rel, '总行数', len(L))
    for i, l in enumerate(L):
        if l.startswith('## '): print(f'  L{i+1}: {l}')
    for i in range(max(0, len(L) - 4), len(L)):
        print(f'  L{i+1}: {L[i][:300]}')
