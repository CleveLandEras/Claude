"""只读：在阶段 5–8 与呈交版的正文文本中检索 _versions/search_terms.txt 的词。"""
import os
from _textify import BASE, textify
terms = [t.strip() for t in open(os.path.join(BASE, '_versions', 'search_terms.txt'), encoding='utf-8') if t.strip()]
files = ['阶段5_方案选型.html', '阶段6_方案设计.html', '阶段7_方案验证.html', '阶段8_结论汇总.html', '弹窗标签推送方案_V1.html']
texts = {}
for f in files:
    p = os.path.join(BASE, f)
    texts[f] = textify(p).replace('\n', ' ⏎ ') if os.path.exists(p) else ''
for t in terms:
    print('=' * 50 + f'\n检索词：{t}')
    for f, s in texts.items():
        i = s.find(t); n = 0
        while i != -1 and n < 15:
            n += 1
            print(f'  [{f}] …{s[max(0, i-80):i+len(t)+80]}…')
            i = s.find(t, i + len(t))
