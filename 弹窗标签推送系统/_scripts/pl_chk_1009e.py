import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
files = ['阶段1_需求分析.html', '阶段5_方案选型.html', '阶段6_方案设计.html', '阶段7_方案验证.html', '阶段8_结论汇总.html', '弹窗标签推送方案_V1.html']
terms = ['先建统一后台', '先分侧补强', '建设顺序', '购买', '待 Dk 确认', '两项取舍', '互斥在哪', '各自规则里还是同一个后台', '两侧各补各的']
for f in files:
    t = open(base + f, encoding='utf-8').read()
    txt = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    txt = re.sub(r'<[^>]+>', '', txt)
    txt = re.sub(r'\s+', ' ', txt)
    print('=====', f)
    for k in terms:
        idx = [m.start() for m in re.finditer(re.escape(k), txt)]
        print('  [%s] %d' % (k, len(idx)))
        for i in idx[:8]:
            print('     …' + txt[max(0, i-50):i+50] + '…')
