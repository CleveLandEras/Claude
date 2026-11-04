"""只读：列出各过程记录文件的行数和 ## 标题所在行号（只列最后若干个）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel, n in [('过程记录/审查记录.md', 8), ('过程记录/设计卡.md', 6), ('过程记录/任务清单.md', 30),
               ('过程记录/迭代记录.md', 10), ('过程记录/监督记录.md', 4), ('进展日志.md', 0)]:
    p = os.path.join(BASE, rel)
    lines = open(p, encoding='utf-8').read().split('\n')
    heads = [(i + 1, l) for i, l in enumerate(lines) if l.startswith('## ')]
    print('=' * 50, rel, '行数', len(lines))
    for i, l in heads[-n:] if n else []:
        print(i, l[:100])
