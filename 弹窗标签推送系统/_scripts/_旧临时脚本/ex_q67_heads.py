import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['环节1_现状盘点.html', '决策汇报.html']:
    lines = open(base + f, encoding='utf-8').read().split('\n')
    print('=' * 10, f, len(lines))
    for i, l in enumerate(lines):
        if re.search(r'<h[1-3]|<section|id="', l):
            s = re.sub(r'<[^>]+>', ' ', l).strip()
            ids = re.findall(r'id="([^"]+)"', l)
            print(i + 1, ids, s[:150])
