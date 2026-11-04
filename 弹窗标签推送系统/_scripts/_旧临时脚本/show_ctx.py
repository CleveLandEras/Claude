"""显示决策汇报.html 第三节（s3）到第四节之前的原文。只读，不带参数。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
t = open(p, encoding='utf-8').read()
a = t.index('<section id="s3">')
b = t.index('<section id="s4">')
print(t[a:b])
