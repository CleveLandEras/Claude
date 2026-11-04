import os
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().splitlines()
heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
for i, l in heads:
    if l.startswith('## 2026-09-29 0') and '无改动' not in l:
        print(i, l[:200])
# print sections 01:0x-01:3x and 04:49
for idx, (i, l) in enumerate(heads):
    if any(k in l for k in ['01:20', '01:1', '04:49']):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        print('=' * 40)
        for x in lines[i:end]:
            print(x[:3000])
