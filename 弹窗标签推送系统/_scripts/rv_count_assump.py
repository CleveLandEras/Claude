import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob, os
base = _ROOT + '/'
for i in range(1, 7):
    f = glob.glob(base + f'阶段{i}_*.html')[0]
    t = open(f, encoding='utf-8').read()
    secs = re.split(r'(?=<section)', t)
    for s in secs:
        m = re.search(r'<h2[^>]*>(.*?)</h2>', s, re.S)
        if m and '关键假设' in re.sub('<.*?>', '', m.group(1)):
            h = re.sub('<.*?>', '', m.group(1)).strip()
            trs = len(re.findall(r'<tr', s))
            ths = len(re.findall(r'<th', s))
            tables = len(re.findall(r'<table', s))
            weak = len(re.findall('理由弱', s))
            print(i, h[:60], 'tr', trs, 'tables', tables, '理由弱 occurrences', weak)
