import re
root = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['环节3_方案.html', '分析/A31_盯住高卡的配置与提案.md']:
    import os
    p = root + f
    if not os.path.exists(p):
        print('MISSING', f); continue
    for i, line in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
        for m in re.finditer('5,146', line):
            s = max(0, m.start() - 70)
            print(f'{f}:{i}: ...{line[s:m.end()+50]}')
