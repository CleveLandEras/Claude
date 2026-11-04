import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['环节1_现状盘点.html', '决策汇报.html', '支撑文件/00_推进记录.md']
terms = ['怎么保级', '升级部分已确认', '才分得开', '更正记录', '<summary']
for f in files:
    t = open(base + f, encoding='utf-8').read()
    lines = t.split('\n')
    print('=' * 20, f, len(lines))
    for i, l in enumerate(lines):
        for term in terms[:3]:
            if term in l:
                print(i + 1, term, '::', l[:2500])
                print()
