p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/设计卡.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines, 1):
    if l.startswith('## Q8') or l.startswith('## Q9') or l.startswith('- **状态**'):
        print(i, l[:100])
