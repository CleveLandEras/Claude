import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
secs = t.split('\n## ')
print('sections', len(secs), 'last title:', secs[-1][:40])
s = secs[-1]
if not s.startswith('2026-09-30 10:29'):
    print('## ' + s[:6000])
for m in re.finditer(r'### (R\d+)[^\n]*状态：退回', t[-200000:]):
    seg = t[-200000:][m.start(): m.start() + 5000].split('\n### ')[0]
    if not ('已处理（' in seg or '有异议（' in seg):
        print('未处理', m.group(1))
