import os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '过程记录/设计卡.md', encoding='utf-8').read()
i = t.find('## Q77｜')
j = t.find('\n---\n', i)
print(t[i:j if j > 0 else None])
# also locate 机会 section in 环节2 and 汇报
import re
for fn in ['环节2_问题诊断.html', '决策汇报.html']:
    h = open(base + fn, encoding='utf-8').read()
    k = h.find('人还在')
    print('=====', fn, k)
    s = re.sub(r'<[^>]+>', ' ', h[max(0, k-3000):k+9000])
    s = re.sub(r'\s+', ' ', s)
    print(s)
