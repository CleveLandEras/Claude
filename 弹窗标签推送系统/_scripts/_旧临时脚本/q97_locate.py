"""Q97 辅助：打印决策汇报.html 中各 section 的起止行号与标题，便于对照。不带参数运行。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '决策汇报.html')
L = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(L))
for i, l in enumerate(L):
    if re.search(r'<section|<h2|class="no"|<details', l):
        t = re.sub(r'<[^>]+>', '', l).strip()
        print(f'L{i+1}: {t[:160]}')
