"""Q32 回归检查：00 与汇报附录问题 25 原话是否逐字一致；环节1 新锚点是否存在。只读。"""
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
a = open(BASE + '支撑文件/00_推进记录.md', encoding='utf-8').read()
b = open(BASE + '决策汇报.html', encoding='utf-8').read()
h = open(BASE + '环节1_现状盘点.html', encoding='utf-8').read()
def q25(t):
    i = t.index('25. 有几件事想确认')
    j = t.index('\n', t.index('  d. ', i))
    return t[i:j]
x, y = q25(a), q25(b)
print('问题 25 逐字一致:', x == y, len(x), len(y))
import difflib
for l in difflib.unified_diff(x.split('\n'), y.split('\n'), lineterm=''):
    print(l[:300])
print('环节1 #u4d 锚点:', h.count('id="u4d"'), ' 指向 #u4d 的链接:', h.count('href="#u4d"'))
print('「有三件事想确认」残留 00/汇报:', a.count('有三件事想确认'), b.count('有三件事想确认'))
print('A11 链接 环节1/汇报:', h.count('分析/A11_会员等级.md'), b.count('分析/A11_会员等级.md'))
