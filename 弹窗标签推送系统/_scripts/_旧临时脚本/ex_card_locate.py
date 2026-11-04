"""只读：列出设计卡.md 中 Q102、Q104、Q106 卡的起止行号与状态行。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/设计卡.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
for k, (i, l) in enumerate(heads):
    if any(q in l for q in ['Q102', 'Q104', 'Q106']):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        print(i + 1, '-', end, '|', l[:150])
        for j in range(i, end):
            if '状态' in lines[j][:30]:
                print('   ', j + 1, lines[j][:200])
