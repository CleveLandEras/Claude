
# 只读：打印进展日志、任务清单末尾几行，便于追加
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['进展日志.md', '过程记录/任务清单.md']:
    lines = open(BASE + f, encoding='utf-8').read().split('\n')
    print('=' * 10, f, len(lines))
    for i in range(max(0, len(lines) - 4), len(lines)):
        print(i + 1, lines[i][:400])
