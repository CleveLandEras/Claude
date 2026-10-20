import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re

base = _ROOT + '/'
files = ['阶段1_需求分析.html', '阶段2_人群分析.html', '阶段3_现状盘点.html', '阶段4_问题诊断.html']
terms = ['近 4 个月', '近4个月', '储值衰减', '储值下滑', '衰减', '29,653', '少一半', '140,000', '13,449', '18,265', '25,972', '5,976', '月度储值', '未首储', '读法', '7,572', '98.30']
for f in files:
    t = open(base + f, encoding='utf-8').read()
    t = re.sub(r'<style>.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    for term in terms:
        for m in re.finditer(re.escape(term), t):
            s = t[max(0, m.start() - 50):m.end() + 50].replace('\n', ' ')
            print(f, '|', term, '|', s)
