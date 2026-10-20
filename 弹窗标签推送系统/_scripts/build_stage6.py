"""把 _versions/stage6_body.html 接在阶段5 的样式头后面，生成 阶段6_方案设计.html（不带参数运行）。"""
import os, re
from _textify import BASE

src = open(os.path.join(BASE, '阶段5_方案选型.html'), encoding='utf-8').read()
marker = '</style></head><body><div class="wrap">'
head = src[:src.index(marker) + len(marker)]
head = re.sub(r'<title>.*?</title>', '<title>方案设计</title>', head, count=1)
body = open(os.path.join(BASE, '_versions', 'stage6_body.html'), encoding='utf-8').read()
out = head + '\n' + body.strip() + '\n</div></body></html>\n'
path = os.path.join(BASE, '阶段6_方案设计.html')
open(path, 'w', encoding='utf-8').write(out)
print('已生成', path, len(out), '字符')
