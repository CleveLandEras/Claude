"""R41 定位：在环节1、决策汇报中找「押注量」「约 12」「38 个百分点」「相当一部分」所在行（只读）。不带参数运行。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
keys = ['押注量', '约 12', '38 个百分点', '相当一部分', '11.5', '6,675']
for name in ('环节1_现状盘点.html', '决策汇报.html'):
    lines = open(B + name, encoding='utf-8').read().split('\n')
    print('=' * 20, name)
    for i, l in enumerate(lines, 1):
        if any(k in l for k in keys):
            print(f'{i}: {l.strip()}')
            print()
