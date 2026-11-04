# 只读：打印进展日志行数与最后 3 行的开头
p = '/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md'
lines = open(p, encoding='utf-8').read().split('\n')
print(len(lines))
for i in range(max(0, len(lines) - 4), len(lines)):
    print(i + 1, repr(lines[i][:120]))
