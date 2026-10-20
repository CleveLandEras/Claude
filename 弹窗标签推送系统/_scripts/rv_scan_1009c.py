import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
B = _ROOT + '/'
files = ['分析/A68_推送与指标体系.md','分析/A65_推荐方案.md','分析/A69_实施分层与短期提升.md','分析/A73_根因验证与边界.md','分析/A74_假设汇总.md','分析/A75_待决事项.md']
terms = ['业务层','统一触达层','统一层','规则顺序','活跃','付费','留存']
for f in files:
    s = open(B+f, encoding='utf-8').read()
    print('==', f, '头部:', re.sub(r'\s+',' ', s[:300]))
    for t in terms:
        n = s.count(t)
        if n:
            m = s.find(t)
            print(f'  {t} x{n} :: ' + re.sub(r'\s+', ' ', s[max(0,m-60):m+80]))
# 任务清单 答复登记 中 Dk 10/9 11:5x
tl = open(B+'过程记录/任务清单.md', encoding='utf-8').read()
for m in re.finditer('按层推进|购买', tl):
    print('[任务清单] ' + re.sub(r'\s+',' ', tl[max(0,m.start()-200):m.end()+120]))
