"""列出迭代记录的各级标题与 00、汇报、A8、环节1 最新版本行（带行号）。只读。"""
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
L = open(BASE + '过程记录/迭代记录.md', encoding='utf-8').read().split('\n')
print('总行数', len(L))
for i, l in enumerate(L, 1):
    if l.startswith('#'):
        print(i, l[:100])
