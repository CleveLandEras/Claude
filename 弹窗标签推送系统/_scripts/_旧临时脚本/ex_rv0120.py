p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
s = t.find('## 2026-09-29 01:20 审查')
e = t.find('## 2026-09-29 01:25')
print(t[s:e])
lines = t.splitlines()
print('总行数', len(lines))
for i, l in enumerate(lines):
    if '闸门审核：通过' in l and i > len(lines) - 400:
        print(i + 1, l[:200])
