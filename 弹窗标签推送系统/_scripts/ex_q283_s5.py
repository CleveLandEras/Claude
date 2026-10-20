import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
t = open(base+'阶段5_方案选型.html', encoding='utf-8').read()
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', '|', t)
t = re.sub(r'\|+', '|', re.sub(r'\s+', ' ', t))
for m in re.finditer('统一后台', t):
    print(t[max(0, m.start()-45):m.end()+55])
    print('--')
