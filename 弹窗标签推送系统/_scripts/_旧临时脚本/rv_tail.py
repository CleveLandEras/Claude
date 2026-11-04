import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('total lines', len(lines))
heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
for i, l in heads[-6:]:
    print(i + 1, l)
start = heads[-1][0]
print('\n'.join(lines[start:start + 80]))
# 待复核：已处理/有异议 且后面未跟复核
pend = []
for i, l in enumerate(lines):
    if ('已处理' in l or '有异议' in l) and '复核' not in l:
        nxt = '\n'.join(lines[i + 1:i + 4])
        if '复核通过' not in nxt and '复核未通过' not in nxt:
            pend.append((i + 1, l[:160]))
print('\n--- possible pending (last 15) ---')
for x in pend[-15:]:
    print(x)
p2 = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/推进计划.md'
print('\n--- 推进计划 head ---')
print('\n'.join(open(p2, encoding='utf-8').read().split('\n')[:15]))
