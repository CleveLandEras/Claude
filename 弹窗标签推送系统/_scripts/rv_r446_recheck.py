import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
terms3 = ['为推断', '可实现 5', '可实现 3', '可实现 1', '推断可实现 12', '推断可实现 14', '推断可实现 3', '推断可实现 1', '项推断', '可做', '可实现 17', '16 个']
terms4 = ['个根因', '个缺口', '项推断', '推送数据', '原「']
terms6 = ['项已有记录', '已有记录', '项推断', '7 项']
def scan(fn, terms):
    print('=' * 20, fn)
    with open(base + fn, encoding='utf-8') as f:
        lines = f.readlines()
    for i, l in enumerate(lines, 1):
        t = re.sub(r'<[^>]+>', ' ', l)
        t = re.sub(r'\s+', ' ', t).strip()
        for term in terms:
            if term in t:
                print(i, '[' + term + ']', t[:260])
                break
scan('阶段3_现状盘点.html', terms3)
scan('阶段4_问题诊断.html', terms4)
scan('阶段6_方案设计.html', terms6)
# count scenario verdicts in stage 3 section 7: look for lines that are exactly a verdict cell
with open(base + '阶段3_现状盘点.html', encoding='utf-8') as f:
    html = f.read()
for lab in ['推断可实现', '推断不可实现', '不可实现', '可实现']:
    pass
cells = re.findall(r'<span class="tag[^"]*">\s*([^<]{2,8})\s*</span>', html)
from collections import Counter
print(Counter(cells))
