"""Q97 回归：检查 环节3_方案.html 与 决策汇报.html 的页内锚点、相对链接是否都存在；统计 HTML 标签配对。不带参数运行。"""
import os, re
from urllib.parse import unquote
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for name in ['环节3_方案.html', '决策汇报.html']:
    p = os.path.join(BASE, name)
    s = open(p, encoding='utf-8').read()
    ids = set(re.findall(r'id="([^"]+)"', s))
    bad = []
    for href in re.findall(r'href="([^"]+)"', s):
        if href.startswith('#'):
            if href[1:] not in ids: bad.append(href)
        elif not href.startswith(('http', 'mailto')):
            f, _, frag = href.partition('#')
            fp = os.path.join(BASE, unquote(f))
            if not os.path.exists(fp): bad.append(href)
            elif frag and fp.endswith('.html'):
                t = open(fp, encoding='utf-8').read()
                if f'id="{frag}"' not in t: bad.append(href)
    print(name, '链接数', len(re.findall(r'href="', s)), '失效：', bad or '无')
    for tag in ['section', 'table', 'details', 'div', 'tr', 'ol', 'p']:
        o = len(re.findall(rf'<{tag}[\s>]', s)); c = len(re.findall(rf'</{tag}>', s))
        if o != c: print(f'  标签不配对 {tag}: {o} / {c}')
