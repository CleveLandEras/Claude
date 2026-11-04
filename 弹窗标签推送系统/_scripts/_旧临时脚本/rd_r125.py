p = '/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md'
t = open(p, encoding='utf-8').read()
print(len(t.splitlines()))
print('\n'.join(t.splitlines()[-4:]))
