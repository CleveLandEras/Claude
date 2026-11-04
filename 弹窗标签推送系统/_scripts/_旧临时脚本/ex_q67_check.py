import os
import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t2 = open(base + '环节2_问题诊断.html', encoding='utf-8').read()
t1 = open(base + '环节1_现状盘点.html', encoding='utf-8').read()
ids1 = set(re.findall(r'id="([^"]+)"', t1))
ids2 = set(re.findall(r'id="([^"]+)"', t2))
bad = []
for href in re.findall(r'href="([^"]+)"', t2):
    if href.startswith('#'):
        if href[1:] not in ids2:
            bad.append(href)
    elif '#' in href:
        f, a = href.split('#')
        if f == '环节1_现状盘点.html' and a not in ids1:
            bad.append(href)
    elif not os.path.exists(base + href):
        bad.append(href)
print('坏链接', bad)
for tag in ['section', 'div', 'table', 'details', 'p', 'tr', 'h2', 'h4']:
    print(tag, len(re.findall('<' + tag + r'[\s>]', t2)), len(re.findall('</' + tag + '>', t2)))
print('节数', len(re.findall(r'<section id="(d\d\w?|e\d)"', t2)))
print('每节六个小标题', [len(re.findall('<h4>', s)) for s in re.split(r'<section id=', t2)[2:-1]])
