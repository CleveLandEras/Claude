import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['决策汇报.html', '环节2_问题诊断.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html']:
    t = open(base + f, encoding='utf-8').read()
    c = {}
    for tag in ['section', 'details', 'div', 'table', 'tr', 'td', 'th', 'p', 'ul', 'ol', 'li', 'summary', 'pre', 'h2', 'h3']:
        o = len(re.findall('<' + tag + r'[\s>]', t)); cl = len(re.findall('</' + tag + '>', t))
        c[tag] = (o, cl)
    bad = {k: v for k, v in c.items() if v[0] != v[1]}
    print(f, len(t), '不配对:', bad if bad else '无')
    ids = re.findall(r'id="([^"]+)"', t)
    dup = {i for i in ids if ids.count(i) > 1}
    print('  重复 id:', dup if dup else '无')
    hrefs = set(re.findall(r'href="#([^"]+)"', t))
    print('  缺失锚点:', sorted(h for h in hrefs if h not in ids) or '无')
