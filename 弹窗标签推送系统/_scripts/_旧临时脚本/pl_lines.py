p = '/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('total', len(lines))
for i in range(max(0, len(lines) - 3), len(lines)):
    print(i + 1, lines[i][:120])
