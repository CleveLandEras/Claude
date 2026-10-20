import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
t = open(base + '阶段产出规划.html', encoding='utf-8').read()
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
rows = re.findall(r'<tr.*?</tr>', t, flags=re.S)
for r in rows:
    if '结论汇总' in r:
        x = re.sub(r'<[^>]+>', ' | ', r)
        x = re.sub(r'(\s*\|\s*)+', ' | ', x)
        print(x)
        print('------')
