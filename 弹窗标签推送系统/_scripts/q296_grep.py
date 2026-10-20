import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob, os
base = _ROOT + '/'
files = [base + f for f in ['阶段5_方案选型.html', '阶段6_方案设计.html', '阶段7_方案验证.html', '阶段8_结论汇总.html', '弹窗标签推送方案_V1.html']]
for f in files:
    if not os.path.exists(f):
        print('缺', f); continue
    t = open(f, encoding='utf-8').read()
    text = re.sub(r'<[^>]+>', '', t)
    hits = [m.start() for m in re.finditer('消除', text)]
    print(os.path.basename(f), len(hits))
    for h in hits:
        print('   …' + text[max(0, h - 30):h + 30].replace('\n', ' ') + '…')
