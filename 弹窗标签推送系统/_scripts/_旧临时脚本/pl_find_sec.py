p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
lines = open(p, encoding='utf-8').read().splitlines()
for n, l in enumerate(lines, 1):
    if '<section' in l or '<h2' in l or 'class="dec"' in l or 'id="d' in l or '<details' in l and n > 340:
        print(n, l[:160])
