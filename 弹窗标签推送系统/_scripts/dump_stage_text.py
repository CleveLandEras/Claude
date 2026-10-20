import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
out = base + '_versions/'
for n in ['阶段3_现状盘点', '阶段6_方案设计']:
    t = open(base + n + '.html', encoding='utf-8').read()
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '|', t)
    t = re.sub(r'\|+', '|', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    open(out + 'txt_' + n + '.txt', 'w', encoding='utf-8').write(t)
