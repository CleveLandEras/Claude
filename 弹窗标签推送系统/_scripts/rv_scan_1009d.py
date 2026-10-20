import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
B = _ROOT + '/'
for f in ['阶段5_方案选型.html','阶段8_结论汇总.html','阶段6_方案设计.html','阶段7_方案验证.html']:
    s = open(B+f, encoding='utf-8').read()
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    for m in re.finditer(r'\d+ 项推断', s):
        print(f'[{f}] ' + re.sub(r'\s+',' ', s[max(0,m.start()-50):m.end()+50]))
