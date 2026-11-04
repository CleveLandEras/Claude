import os
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def tail(p, n):
    with open(B + p, encoding='utf-8') as f:
        lines = f.readlines()
    print('=====', p, 'total', len(lines))
    start = max(0, len(lines) - n)
    for i, l in enumerate(lines[start:], start + 1):
        print(i, l.rstrip()[:1500])
tail('过程记录/审查记录.md', 120)
tail('进展日志.md', 15)
tail('过程记录/任务清单.md', 15)
