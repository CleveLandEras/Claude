B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
L = open(B + '过程记录/审查记录.md', encoding='utf-8').read().splitlines()
print('total', len(L))
start = None
for i, l in enumerate(L):
    if l.startswith('## ') and i > 900:
        print('SECTION', i + 1, l)
for i, l in enumerate(L[955:], 956):
    print(i, l[:2500])
