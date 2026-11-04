import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['决策汇报.html', '环节2_问题诊断.html']:
    t = open(base + f, encoding='utf-8').read()
    for k in ['成本 NT$', '会多花', '留住大户', '导致流失', '问题空间扫描', '活动咬分比', 'A34', 'A35', 'A32']:
        pos = [m.start() for m in re.finditer(re.escape(k), t)]
        print(f, k, len(pos))
        if k in ('成本 NT$', '会多花', '留住大户', '导致流失'):
            for i in pos:
                print('   ', re.sub(r'<[^>]+>', '', t[max(0, i - 60): i + 60]).replace('\n', ' '))
