"""打印任务清单第四节答复登记中最后 3 行（只读，不带参数）。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(B, '过程记录/任务清单.md'), encoding='utf-8').read().split('\n')
s = next(i for i, l in enumerate(L) if l.startswith('## 四'))
e = next(i for i, l in enumerate(L) if l.startswith('## 五'))
rows = [l for l in L[s:e] if l.startswith('| ')]
for r in rows[-3:]:
    print(r[:4000])
    print('-' * 10)
