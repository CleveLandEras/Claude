import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
files = ['阶段1_需求分析.html','阶段5_方案选型.html','阶段6_方案设计.html','阶段7_方案验证.html','阶段8_结论汇总.html','弹窗标签推送方案_V1.html']
pats = [r'3[0-9] ?项', r'短期 ?1[0-9]', r'中期 ?1[0-9]', r'长期 ?1[0-9]', r'快速提升[^<]{0,12}[0-9]+ ?条', r'[0-9]+ ?条快速', r'现有后台配置 ?[0-9]+', r'后台小改动 ?[0-9]+', r'较大开发 ?[0-9]+',
        r'先看覆盖', r'先看能否验证', r'覆盖优先', r'验证优先', r'两种推进', r'两种建设顺序', r'先建后迁', r'推进顺序', r'按层推进', r'事后查得到[^<]{0,12}', r'事后可查[^<]{0,12}', r'效果可查覆盖[^<]{0,30}', r'待 ?Dk']
for f in files:
    t = open(base+f, encoding='utf-8').read()
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    print('=====', f)
    for p in pats:
        ms = list(re.finditer(p, t))
        for m in ms:
            s = max(0, m.start()-25); e = min(len(t), m.end()+25)
            print(f'[{p}] ', re.sub(r'<[^>]+>', '', re.sub(r'\s+', ' ', t[s:e])))
    ids = re.findall(r'(?<![A-Za-z0-9])[QRKA][0-9]{1,3}(?![0-9A-Za-z])', re.sub(r'<[^>]+>', ' ', t))
    print('内部编号疑似:', ids[:10])
