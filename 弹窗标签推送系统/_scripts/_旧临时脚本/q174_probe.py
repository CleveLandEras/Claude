BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
L = open(BASE + '过程记录/设计卡.md', encoding='utf-8').read().split('\n')
print(len(L))
idx = [n for n, s in enumerate(L) if 'Q174' in s or 'Q175' in s]
print(idx[:20])
heads = [(n, s[:100]) for n, s in enumerate(L) if s.startswith('## ')]
print(heads[-6:])
