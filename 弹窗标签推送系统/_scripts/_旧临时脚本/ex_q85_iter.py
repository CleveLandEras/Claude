"""Q85：定位迭代记录中决策汇报一节与最新版本号、任务清单第六节末尾、进展日志末尾（只读）。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
it = open(os.path.join(BASE, '过程记录', '迭代记录.md'), encoding='utf-8').read().split('\n')
for i, s in enumerate(it, 1):
    if s.startswith('#'):
        print(i, s[:120])
for i, s in enumerate(it, 1):
    if re.search(r'决策汇报.*v(79|8\d)', s) or re.match(r'^\*\*v(79|8\d)', s) or re.match(r'^### v(79|8\d)', s):
        print('V', i, s[:200])
print('迭代记录总行数', len(it))
tl = open(os.path.join(BASE, '过程记录', '任务清单.md'), encoding='utf-8').read().split('\n')
print('任务清单总行数', len(tl))
for i, s in enumerate(tl, 1):
    if s.startswith('## '):
        print('T', i, s[:80])
pl = open(os.path.join(BASE, '进展日志.md'), encoding='utf-8').read().split('\n')
print('进展日志总行数', len(pl))
