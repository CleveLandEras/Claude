"""Q80：列出迭代记录的 ## / ### 标题与 v 版本行号（只读）。"""
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
L = open(p, encoding='utf-8').read().split('\n')
print(len(L), '行')
for i, l in enumerate(L, 1):
    if l.startswith('## ') or (re.match(r'^(### )?v\d+', l) and ('决策' in l or '环节2' in l or 'Q7' in l or 'Q8' in l)):
        print(f'L{i}: {l[:110]}')
