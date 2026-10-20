import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
files = ['阶段5_方案选型.html', '阶段6_方案设计.html', '阶段7_方案验证.html', '阶段8_结论汇总.html', '弹窗标签推送方案_V1.html']
terms = ['互斥', '两种建设顺序', '改由统一后台承担', '取舍一', '取舍二', '全面领先', '简报', '35 项', '34 项', '建设项', '弹窗与推送接入同一个后台', '弹窗与推送都接入', '不推荐的是方案二']
for f in files:
    t = open(base + f, encoding='utf-8').read()
    txt = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    txt = re.sub(r'<[^>]+>', '', txt)
    txt = re.sub(r'\s+', ' ', txt)
    print('=====', f, len(txt))
    for k in terms:
        idx = [m.start() for m in re.finditer(re.escape(k), txt)]
        print('  [%s] %d' % (k, len(idx)))
        if k in ('35 项', '34 项', '建设项'):
            continue
        for i in idx[:4]:
            print('     …' + txt[max(0, i-60):i+60] + '…')
