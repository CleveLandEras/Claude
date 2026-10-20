import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, html, os
base = _ROOT + '/'

def text_lines(fn):
    s = open(base + fn, encoding='utf-8').read()
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<(tr|p|li|h[1-6]|div|summary|td|th|br)[^>]*>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return [l.strip() for l in s.split('\n') if l.strip()]

def show(fn, start_kw, n):
    L = text_lines(fn)
    for i, l in enumerate(L):
        if start_kw in l:
            print('=====', fn, 'line', i, '=====')
            for x in L[i:i + n]:
                print('  ', x)
            return
    print('NOT FOUND', fn, start_kw)

show('阶段6_方案设计.html', '十关键假设', 140)
show('阶段8_结论汇总.html', '可顺手核实（7 项）', 60)
show('阶段8_结论汇总.html', '待决事项：13 项', 6)
L = text_lines('阶段7_方案验证.html')
for i, l in enumerate(L):
    if '回流' in l and ('推断' in l or '首次' in l):
        print('S7', i, l[:200])
L = text_lines('阶段8_结论汇总.html')
for i, l in enumerate(L):
    if ('回流' in l and '首次' in l) or '12 项' in l or '核实 6' in l or '6 项、数据' in l:
        print('S8', i, l[:200])
L = text_lines('阶段6_方案设计.html')
for i, l in enumerate(L):
    if ('回流' in l and ('首次' in l or '回流时间' in l or '回流事件' in l)) or '14 项推断' in l or '7 件事' in l:
        print('S6', i, l[:200])
