import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
for f, terms in [('弹窗标签推送方案_V1.html', ['确认方式', '建成标准', '怎么确认', '按组拉出', '验收']),
                 ('阶段6_方案设计.html', ['按组拉出', '怎么确认', '建成标准', '验收', '关键假设']),
                 ('阶段1_需求分析.html', ['验收', '建成', '事后查得到'])]:
    t = open(base + f, encoding='utf-8').read()
    t = re.sub(r'<style>.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('=====', f)
    for term in terms:
        for m in re.finditer(re.escape(term), t):
            h = m.start()
            print('  [%s] …%s…' % (term, t[max(0, h-60):h+160]))
