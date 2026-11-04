"""Q24：核对 A3 中表 4、负值账号、新增与注册 30 天吻合的原文（只读）。不带参数运行。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for name in ('分析/A3_回流与潜在付费画像.md', '环节1_现状盘点.html'):
    lines = open(B + name, encoding='utf-8').read().split('\n')
    print('=' * 20, name)
    for i, l in enumerate(lines, 1):
        if any(k in l for k in ['表 4', '负值', '吻合', '往前 30']):
            print(f'{i}: {l.strip()[:260]}')
