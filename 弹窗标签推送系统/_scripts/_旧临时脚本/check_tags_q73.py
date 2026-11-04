"""环节2 与决策汇报的标签配对核对（div、section、details、table、tr、p、ol、li、h4），外加链接指向的本地文件是否存在。不带参数运行。"""
import os, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
for f in ['环节2_问题诊断.html', '决策汇报.html']:
    s = open(os.path.join(BASE, f), encoding='utf-8').read()
    out = []
    for t in ['div', 'section', 'details', 'table', 'tr', 'p', 'ol', 'li', 'h4', 'h3', 'h2', 'summary']:
        o = len(re.findall(r'<%s[\s>]' % t, s)); c = len(re.findall(r'</%s>' % t, s))
        out.append(f'{t} {o}/{c}' + ('' if o == c else ' ✗'))
    print(f, '｜'.join(out))
    bad = [h for h in set(re.findall(r'href="([^"#:]+)(?:#[^"]*)?"', s)) if not os.path.exists(os.path.join(BASE, h))]
    print('  坏的本地链接', bad)
