p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines, 1):
    if '<section' in l or '<h2' in l or '更正记录' in l[:200] or '本节是问题诊断之前写的' in l or '环节3_方案' in l:
        print(i, l.strip()[:160])
