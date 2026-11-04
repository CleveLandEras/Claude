import os, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
d = BASE + '来源资料/'
print(os.listdir(d))
for f in os.listdir(d):
    if 'Cowork' in f and f.endswith('.md'):
        t = open(d + f, encoding='utf-8').read()
        for m in re.finditer('展示配置页', t):
            print(repr(t[max(0, m.start() - 120):m.start() + 260]))
