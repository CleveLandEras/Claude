import io, re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for fn in ['决策汇报.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html']:
    s = io.open(base + fn, encoding='utf-8').read()
    out = []
    for t in ['div', 'details', 'table', 'tr', 'td', 'ul', 'ol', 'li', 'p', 'section', 'pre', 'summary']:
        o = len(re.findall(r'<' + t + r'[\s>]', s))
        c = len(re.findall(r'</' + t + r'>', s))
        if o != c:
            out.append((t, o, c))
    print(fn, '不配对:', out or '无')
