"""只读：打印 A27 的结论、表 3、表 4 与局限几段（按 ## 标题截取）。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/分析/A27_推送方案比较.md'
lines = open(p, encoding='utf-8').read().split('\n')
keep = False
for i, l in enumerate(lines, 1):
    if l.startswith('## '):
        keep = any(k in l for k in ['结论', '表 3', '表 4', '局限', '07 的角色'])
    if keep:
        print(i, '|', l[:700])
