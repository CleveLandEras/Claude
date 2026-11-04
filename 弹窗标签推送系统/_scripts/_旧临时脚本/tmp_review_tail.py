p='/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines=open(p,encoding='utf-8').read().split('\n')
print(len(lines))
idx=[i for i,l in enumerate(lines) if l.startswith('## ')]
for i in idx[-3:]:
    print(i+1, lines[i][:100])
