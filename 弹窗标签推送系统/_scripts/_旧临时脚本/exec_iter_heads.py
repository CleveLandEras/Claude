"""执行者用：打印迭代记录各级标题行号，以及含「05」「环节3」「决策汇报」的 ##/### 标题；再打印任务清单第六节末 3 行、进展日志末 3 行。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(BASE, '过程记录', '迭代记录.md'), encoding='utf-8').read().split('\n')
print('迭代记录总行数', len(L))
for i, l in enumerate(L, 1):
    if l.startswith('## '):
        print(i, l[:120])
for i, l in enumerate(L, 1):
    if l.startswith('### ') and ('05' in l or '环节3' in l or '决策汇报' in l):
        print('   ', i, l[:120])
T = open(os.path.join(BASE, '过程记录', '任务清单.md'), encoding='utf-8').read().split('\n')
print('任务清单总行数', len(T))
for l in T[-3:]:
    print('  T|', l[:300])
P = open(os.path.join(BASE, '进展日志.md'), encoding='utf-8').read().split('\n')
print('进展日志总行数', len(P))
for l in [x for x in P if x.strip()][-3:]:
    print('  P|', l[:300])
