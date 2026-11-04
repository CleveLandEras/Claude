# 用法：python3 _逗号句清单.py 页面.html：列出网页里每个带中文逗号的文字块（标题、格子、条目、图内文字），逐句判断逗号两边是否有关系
import re, sys
s = open(sys.argv[1], encoding='utf-8').read()
s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
blocks = re.split(r'</(?:h1|h2|h4|li|td|th|p|text|summary|div|b|span)>', s)
seen = set()
for b in blocks:
    t = re.sub(r'<[^>]+>', '', b)
    t = re.sub(r'\s+', ' ', t).strip()
    if '，' in t and t not in seen:
        seen.add(t); print('·', t)
