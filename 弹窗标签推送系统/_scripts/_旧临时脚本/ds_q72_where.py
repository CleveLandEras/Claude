p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/设计卡.md'
lines = open(p, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines, 1):
    if l.startswith('## ') or l.startswith('→ 执行结果') or l.startswith('- **状态**'):
        print(i, l[:60])
print('total', len(lines))
