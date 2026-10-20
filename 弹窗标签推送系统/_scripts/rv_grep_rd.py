import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
files = ['阶段1_需求分析.html', '阶段6_方案设计.html', '阶段7_方案验证.html', '阶段8_结论汇总.html']
terms = ['研发', '自主', '配置操作', '提单', '编写人', '人群类数', '数据收集（', '9 项', '10 项', '操作人']
for f in files:
    raw = open(base + f, encoding='utf-8').read()
    body = raw.split('</style>')[-1]
    txt = re.sub(r'<[^>]+>', ' ', body)
    txt = re.sub(r'\s+', ' ', txt)
    print('=' * 20, f)
    for t in terms:
        for m in re.finditer(re.escape(t), txt):
            s = max(0, m.start() - 70)
            print(f'[{t}]', txt[s:m.end() + 70])
