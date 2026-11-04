import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['环节3_方案.html', '决策汇报.html']:
    t = open(base + f, encoding='utf-8').read()
    print(f)
    for tag in ['div', 'table', 'tr', 'td', 'th', 'details', 'summary', 'section', 'ol', 'ul', 'p', 'b', 'a', 'span']:
        o = len(re.findall(r'<%s[\s>]' % tag, t))
        c = len(re.findall(r'</%s>' % tag, t))
        print('  ', tag, o, c, '' if o == c else '<<< 不配对')
