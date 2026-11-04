base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['决策汇报.html', '支撑文件/00_推进记录.md']:
    lines = open(base + f, encoding='utf-8').read().split('\n')
    for i, l in enumerate(lines):
        if '再导' in l or '<td>⑤</td>' in l or l.startswith('| ⑤ |') or '5 件' in l:
            print(f, i + 1, l[:600])
            print()
