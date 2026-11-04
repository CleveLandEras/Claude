p = '/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md'
lines = open(p, encoding='utf-8').read().splitlines()
print('总行数', len(lines))
for l in lines[-4:]:
    print(l[:600])
