"""只读：打印推进计划第三节队列，以及审查记录中 R143、R144 与 09:40 一节的行号与内容。"""
base = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/'
lines = open(base + '推进计划.md', encoding='utf-8').read().split('\n')
on = False
for i, l in enumerate(lines, 1):
    if l.startswith('## 三'):
        on = True
    elif l.startswith('## 四'):
        on = False
    if on:
        print(i, '|', l)
rv = open(base + '审查记录.md', encoding='utf-8').read().split('\n')
start = None
for i, l in enumerate(rv):
    if l.startswith('## 2026-09-29 09:4'):
        start = i
        break
if start is not None:
    for i in range(start, len(rv)):
        print(i + 1, '|', rv[i])
