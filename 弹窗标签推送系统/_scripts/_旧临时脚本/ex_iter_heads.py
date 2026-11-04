p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
print(len(lines))
for i, l in enumerate(lines):
    if l.startswith('#'):
        print(i + 1, l[:160])
