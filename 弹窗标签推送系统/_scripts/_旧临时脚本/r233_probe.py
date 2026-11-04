base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['过程记录/任务清单.md', '过程记录/迭代记录.md', '进展日志.md']:
    lines = open(base + f, encoding='utf-8').read().split('\n')
    print('=====', f, len(lines))
    for i, l in enumerate(lines):
        if f.endswith('迭代记录.md') and (l.startswith('## ') or l.startswith('### ')):
            print(i, l[:80])
        if f.endswith('任务清单.md') and (l.startswith('## ') or 'Q165' in l[:80]):
            print(i, l[:100])
    print('LAST', lines[-3][:160] if len(lines) > 3 else '')
    print('LAST2', lines[-2][:160])
