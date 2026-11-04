"""只读：打印审查记录中 R128 条目（### R128 起到下一个 ### 或 ## 前）。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines):
    if l.startswith('### R128'):
        j = i
        while True:
            print(j + 1, '|', lines[j][:400])
            j += 1
            if j >= len(lines) or lines[j].startswith('#'):
                break
