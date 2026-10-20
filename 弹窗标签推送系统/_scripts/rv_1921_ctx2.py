import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, html
base = _ROOT + '/'

def text_lines(fn):
    s = open(base + fn, encoding='utf-8').read()
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<(tr|p|li|h[1-6]|div|summary|td|th|br)[^>]*>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return [l.strip() for l in s.split('\n') if l.strip()]

L = text_lines('阶段6_方案设计.html')
print('--- S6 270-290')
for i in range(270, 291):
    print(i, L[i][:220])
print('--- S6 key assumptions')
for i, l in enumerate(L):
    if '关键假设' in l and i > 500:
        print(i, l[:200])
start = [i for i, l in enumerate(L) if '项推断的依据' in l][0]
for i in range(start, start + 110):
    print(i, L[i][:160])
