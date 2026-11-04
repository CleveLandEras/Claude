p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('total lines:', len(lines))
start = max(i for i, l in enumerate(lines) if l.startswith('## 2026-09-28 21:44'))
print('21:44 section starts at line', start + 1)
for l in lines[start:]:
    if l.startswith('###') or '已处理' in l or '有异议' in l or '复核' in l[:12]:
        print(l[:200])
p2 = '/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md'
l2 = open(p2, encoding='utf-8').read().split('\n')
print('--- 进展日志 tail')
for l in l2[-5:]:
    print(l[:300])
