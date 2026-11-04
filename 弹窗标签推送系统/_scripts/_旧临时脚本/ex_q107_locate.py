"""只读：打印决策汇报.html 顶部 verdict、第四节（s4）起到第五节 h2 后导语，以及 cp() 函数定义。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
lines = open(p, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines, 1):
    if 'class="verdict plain"' in l:
        for j in range(i - 1, i + 6):
            print(j + 1, '|', lines[j][:600])
    if '<section id="s4">' in l:
        for j in range(i - 1, i + 30):
            print(j + 1, '|', lines[j][:400])
    if 'function cp' in l or '<script' in l:
        print(i, '|', l[:300])
