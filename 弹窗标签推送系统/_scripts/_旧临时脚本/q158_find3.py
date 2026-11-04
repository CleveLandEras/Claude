import io
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
with io.open(base + '决策汇报.html', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        for t in ['原话', '附录', 'id="app']:
            if t in line:
                print(i, t, len(line), line.strip()[:140])
                break
