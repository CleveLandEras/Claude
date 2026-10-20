import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
p = _ROOT + '/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
nums = [int(x) for x in re.findall(r'###\s*R(\d+)', t)]
print('max R:', max(nums) if nums else None, 'lines:', t.count('\n'))
heads = re.findall(r'^## .*$', t, flags=re.M)
print('last heads:', heads[-3:])
