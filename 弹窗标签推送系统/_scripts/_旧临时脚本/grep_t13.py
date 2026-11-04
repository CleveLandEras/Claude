d = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for i, l in enumerate(open(d + '迭代记录.md', encoding='utf-8'), 1):
    if l.startswith('#') or '00 v1' in l or '00_推进记录' in l:
        print(i, l.rstrip()[:160])
