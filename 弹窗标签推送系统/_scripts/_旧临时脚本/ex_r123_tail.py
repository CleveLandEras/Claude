"""打印任务清单、进展日志末尾几行（只读），用于追加日志。"""
for p in ['过程记录/任务清单.md', '进展日志.md']:
    ls = open('/Users/decheng.huang/claude/弹窗标签推送系统/' + p, encoding='utf-8').read().split('\n')
    print('=' * 40, p, len(ls), '行')
    for i in range(max(0, len(ls) - 4), len(ls)):
        print(i + 1, ls[i][:300])
