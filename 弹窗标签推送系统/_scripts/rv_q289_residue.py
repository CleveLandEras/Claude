import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os, html
base = _ROOT + '/'
files = ['阶段1_需求分析.html','阶段5_方案选型.html','阶段6_方案设计.html','阶段7_方案验证.html','阶段8_结论汇总.html','弹窗标签推送方案_V1.html','阶段产出规划.html']
terms = ['召回名单','召回接入','10 项对应','此项由主管定','Dk 判断 6']
def text(p):
    s = open(base+p, encoding='utf-8').read()
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s)
for f in files:
    t = text(f)
    print('=' * 20, f)
    for term in terms:
        hits = [m.start() for m in re.finditer(re.escape(term), t)]
        if not hits:
            continue
        print('--', term, len(hits))
        for h in hits:
            print('   …' + t[max(0, h-50):h+60] + '…')
