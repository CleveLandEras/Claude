"""只读：列审查记录最后 6 个二级标题（行号）、总行数；进展日志、任务清单最后 3 行。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
L = open(B + '过程记录/审查记录.md', encoding='utf-8').read().rstrip('\n').split('\n')
print('审查记录', len(L))
heads = [(i + 1, s) for i, s in enumerate(L) if s.startswith('## ')]
for i, s in heads[-6:]:
    print(i, s[:120])
for f in ['进展日志.md', '过程记录/任务清单.md']:
    M = open(B + f, encoding='utf-8').read().rstrip('\n').split('\n')
    print(f, len(M))
    for i in range(max(0, len(M) - 3), len(M)):
        print(i + 1, M[i][:400])
