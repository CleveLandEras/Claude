for p in ['/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md', '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/任务清单.md', '/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md']:
    t = open(p, encoding='utf-8').read()
    print('=====', p, repr(t[-200:]))
