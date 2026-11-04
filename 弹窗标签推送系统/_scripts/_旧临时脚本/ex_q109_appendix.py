"""只读：打印决策汇报.html 附录一节（从「附 ·」到更正记录前）的行号与内容。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
lines = open(p, encoding='utf-8').read().split('\n')
on = False
for i, l in enumerate(lines, 1):
    if '附 · 需要你发出去的问题' in l:
        on = True
    if on and '更正记录' in l and '<summary>' in l:
        print(i, '|', l[:300]); break
    if on:
        print(i, '|', l)
