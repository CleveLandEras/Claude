import os, re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'

def lines(p):
    with open(B + p, encoding='utf-8') as f:
        return f.read().split('\n')

# 审查记录：从最后一个包含 14:35 的二级标题起，打印到末尾
L = lines('过程记录/审查记录.md')
heads = [i for i, s in enumerate(L) if s.startswith('## ')]
print('审查记录 总行数', len(L), '最后5个二级标题:')
for i in heads[-5:]:
    print(i, L[i][:120])
start = heads[-2] if len(heads) >= 2 else 0
print('=' * 60)
print('\n'.join(L[start:])[:40000])

print('=' * 60, '进展日志尾部')
L = lines('进展日志.md')
print('\n'.join(L[-12:]))

print('=' * 60, '设计卡 Q174/Q175')
L = lines('过程记录/设计卡.md')
s = next(i for i, x in enumerate(L) if x.startswith('## Q174'))
print('\n'.join(L[s:])[:30000])
