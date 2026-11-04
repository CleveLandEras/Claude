"""打印审查记录中 R56 条目全文（只读，不带参数）。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(B, '过程记录/审查记录.md'), encoding='utf-8').read()
for p in re.split(r'\n(?=### )', s):
    if p.startswith('### R56'):
        print(p[:4000])
for m in re.finditer(r'R56[^\n]{0,200}', s):
    print('提及：', m.group(0))
