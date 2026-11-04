"""只读：打印进展日志与任务清单的总行数和最后 2 行（行号）。"""
for f in ['进展日志.md', '过程记录/任务清单.md']:
    L = open('/Users/decheng.huang/claude/弹窗标签推送系统/' + f, encoding='utf-8').read().rstrip('\n').split('\n')
    print(f, len(L))
    for i in range(max(0, len(L) - 2), len(L)):
        print(i + 1, L[i][:300])
