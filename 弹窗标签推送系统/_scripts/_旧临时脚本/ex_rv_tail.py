"""只读：列出审查记录所有 ## 节标题（后 8 个）和状态为退回、后面没有已处理 / 有异议的条目。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
heads = [(i + 1, l) for i, l in enumerate(lines) if l.startswith('## ')]
for h in heads[-8:]:
    print(h[0], '|', h[1][:120])
print('总行数', len(lines))
# 找退回条目
for i, l in enumerate(lines):
    if l.startswith('### R') and '状态：退回' in l:
        j = i + 1
        done = False
        while j < len(lines) and not lines[j].startswith('#'):
            if lines[j].startswith('- 已处理') or lines[j].startswith('- 有异议'):
                done = True
            j += 1
        if not done:
            print('未处理：', i + 1, l[:120])
