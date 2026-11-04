# Q181：只读，打印 进展日志.md 的行数和最后一行（用于追加定位）
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
ls = open(B + '进展日志.md', encoding='utf-8').read().rstrip('\n').split('\n')
print(len(ls))
print(ls[-1][-400:])
