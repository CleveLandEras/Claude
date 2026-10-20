import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
raw = open(base+'弹窗标签推送方案_V1.html', encoding='utf-8').read()
t = re.sub(r'<style.*?</style>', '', raw, flags=re.S)
t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
for m in re.finditer(r'<(h1|h2|h3)[^>]*>(.*?)</\1>', t, flags=re.S):
    print(m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()[:110])
txt = re.sub(r'<[^>]+>', ' ', t)
print('编号:', re.findall(r'(?<![A-Za-z0-9])(?:Q|R|K)[0-9]{1,3}(?![0-9A-Za-z])', txt)[:10])
print('A编号:', re.findall(r'(?<![A-Za-z0-9])A[0-9]{1,3}(?![0-9A-Za-z])', txt)[:10])
print('活跃/付费目标词:', [m.group(0) for m in re.finditer(r'.{12}(?:提升活跃|提升付费|付费率|活跃率|留存率).{12}', txt)][:8])
links = re.findall(r'href="([^"#][^"]*)"', raw)
import os
print('本地链接缺失:', [l for l in links if not l.startswith('http') and not os.path.exists(base+l.split('#')[0])][:10])
