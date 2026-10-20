import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
files = ['阶段1_需求分析.html','阶段5_方案选型.html','阶段6_方案设计.html','阶段8_结论汇总.html','弹窗标签推送方案_V1.html']
pats = ['曝光、点击、购买[。）<]','曝光点击购买','待 ?Dk 确认','本方案建议','互斥','两项取舍','取舍一','取舍二','各自规则里','两侧各补各的','不设购买目标','推进按一条顺序']
for f in files:
    t = open(base+f, encoding='utf-8').read()
    print('=====', f)
    for p in pats:
        for m in re.finditer(p, t):
            s = max(0, m.start()-50); e = min(len(t), m.end()+50)
            print(f'[{p}] ', re.sub(r'\s+', ' ', t[s:e]))
