# 只读：列出迭代记录的节标题与各节最后一个版本行的位置
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines):
    if l.startswith('## ') or (l.startswith('### ') and ('环节1' in l or '决策汇报' in l)):
        print(i + 1, l[:90])
