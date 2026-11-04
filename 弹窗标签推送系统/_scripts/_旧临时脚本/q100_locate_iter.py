"""Q100：列出迭代记录的二级标题与各文件最新版本行号，以及任务清单第六节末尾行号（只读）。不带参数运行。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '过程记录', '迭代记录.md')
with open(p, encoding='utf-8') as fh:
    lines = fh.readlines()
print('迭代记录总行数', len(lines))
for i, l in enumerate(lines, 1):
    if l.startswith('## ') or re.match(r'^### .*(汇报 v9|环节3 v1|03 v|v9[0-9]|v1[0-9])', l):
        print(i, l.strip()[:120])
p2 = os.path.join(BASE, '过程记录', '任务清单.md')
with open(p2, encoding='utf-8') as fh:
    l2 = fh.readlines()
print('任务清单总行数', len(l2))
for i, l in enumerate(l2, 1):
    if l.startswith('## '):
        print(i, l.strip()[:80])
