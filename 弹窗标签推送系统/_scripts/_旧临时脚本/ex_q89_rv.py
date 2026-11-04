p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines, 1):
    if l.startswith('## 2026') or ('状态：退回' in l and i > 2060):
        print(i, l[:120])
