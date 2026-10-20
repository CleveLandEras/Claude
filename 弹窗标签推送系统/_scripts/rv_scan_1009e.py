import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
files = ['阶段1_需求分析.html','阶段5_方案选型.html','阶段6_方案设计.html','阶段7_方案验证.html','阶段8_结论汇总.html','弹窗标签推送方案_V1.html']
terms = ['购买','活跃','付费率','业绩','统一触达层','规则顺序','二选一','两条路径','待 Dk 确认','互斥']
for f in files:
    p = base + f
    if not os.path.exists(p):
        print('MISSING', f); continue
    t = open(p, encoding='utf-8').read()
    t = re.sub(r'<style>.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('=====', f)
    for term in terms:
        hits = [m.start() for m in re.finditer(re.escape(term), t)]
        print('  [%s] %d' % (term, len(hits)))
        for h in hits:
            print('     …' + t[max(0,h-50):h+40] + '…')
