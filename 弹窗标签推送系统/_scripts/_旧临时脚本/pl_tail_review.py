import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
idx = [m.start() for m in re.finditer(r'^## 2026', t, re.M)]
print('sections:', len(idx), 'total chars', len(t))
print(t[idx[-2]:])
