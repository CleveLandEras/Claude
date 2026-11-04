"""只读：打印任务清单、进展日志末尾几行与行数，定位追加位置。"""
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['过程记录/任务清单.md', '进展日志.md']:
    lines = open(base + f, encoding='utf-8').read().split('\n')
    print('=' * 20, f, '总行数', len(lines))
    for i in range(max(0, len(lines) - 4), len(lines)):
        print(i + 1, '|', lines[i][:300])
