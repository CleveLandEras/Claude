import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
files = ['阶段2_人群分析.html','阶段6_方案设计.html','阶段7_方案验证.html','阶段8_结论汇总.html','分析/A68_推送与指标体系.md']
pats = ['圈不出','直接圈','仅新增','只有新增','圈不准']
for f in files:
    n = 0
    with open(base+f, encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            txt = re.sub(r'<[^>]+>', ' ', line)
            for p in pats:
                if p in txt:
                    n += 1
                    k = txt.find(p)
                    print(f'{f}:{i}:[{p}] ...{txt[max(0,k-80):k+80].strip()}...')
                    break
    print(f, 'hits', n)
