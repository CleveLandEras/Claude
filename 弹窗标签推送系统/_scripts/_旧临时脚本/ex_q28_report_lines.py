"""Q28：定位决策汇报第一节「标签与推送」面板与缺口面板（只读）。不带参数运行。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
lines = open(B + '决策汇报.html', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines, 1):
    if any(k in l for k in ['标签与推送', '推送', '缺口', '<h2', '<h3', 'class="panel', 'pn-h']):
        print(f'{i}: {l.strip()[:220]}')
