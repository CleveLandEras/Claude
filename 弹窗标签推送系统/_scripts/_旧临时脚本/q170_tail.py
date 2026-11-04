BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['进展日志.md', '过程记录/任务清单.md']:
    lines = open(BASE + f, encoding='utf-8').read().rstrip('\n').split('\n')
    print('==', f, len(lines))
    for l in lines[-3:]:
        print('  ', l[:220])
