"""只读：打印审查记录中 R142 所在一节（从该节 ## 标题到下一个 ## 标题）及行号。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
idx = [i for i, l in enumerate(lines) if 'R142' in l]
print('命中行', [i + 1 for i in idx], '总行数', len(lines))
if idx:
    s = idx[0]
    while s > 0 and not lines[s].startswith('## '):
        s -= 1
    e = idx[0] + 1
    while e < len(lines) and not lines[e].startswith('## '):
        e += 1
    for i in range(s, e):
        print(i + 1, '|', lines[i])
