import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
targets = [
    ('阶段5_方案选型.html', ['先建后迁', '先看覆盖', '待 Dk', '不需抉择']),
    ('阶段6_方案设计.html', ['待 Dk 或上级确认', '两条路径', '先看覆盖']),
    ('阶段7_方案验证.html', ['先看覆盖', '两条路径', '待 Dk', '规则顺序']),
    ('阶段8_结论汇总.html', ['meta']),
    ('阶段4_问题诊断.html', ['机会', '第三节', '四']),
]
for f, kws in targets:
    t = open(base + f, encoding='utf-8').read()
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('=====', f)
    for k in kws:
        for m in list(re.finditer(re.escape(k), t))[:3]:
            h = m.start()
            print('--', k, ':', t[max(0, h - 160):h + 260])
