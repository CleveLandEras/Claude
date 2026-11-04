
# 只读：列出迭代记录的节标题与每节最后一个版本号所在行
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
lines = open(BASE + '过程记录/迭代记录.md', encoding='utf-8').read().split('\n')
print('总行数', len(lines))
cur = None
last = {}
for i, l in enumerate(lines, 1):
    if l.startswith('## '):
        cur = l
        print(i, l[:80])
    m = re.match(r'^(v[\d.]+)（', l)
    if m and cur:
        last[cur] = (i, l[:100])
for k, v in last.items():
    print(k[:40], '→', v)
