p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines, 1):
    if l.startswith('#') or 'v80' in l or 'v79' in l or '环节3' in l[:40]:
        print(i, l[:140])
