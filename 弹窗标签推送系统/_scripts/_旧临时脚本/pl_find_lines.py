base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
lines = open(base + '过程记录/任务清单.md', encoding='utf-8').read().split('\n')
print('total', len(lines))
for i, l in enumerate(lines, 1):
    if l.startswith('## ') or l.startswith('### '):
        print(i, l[:80])
