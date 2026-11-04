import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
f = open(B + '过程记录/审查记录.md', encoding='utf-8').read()
heads = [m.start() for m in re.finditer(r'^## 2026', f, re.M)]
print(f[heads[-1]:])
