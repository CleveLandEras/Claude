import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob
root = _ROOT + '/'
pat = re.compile(r'(消除|能消除)[^。<]{0,6}全部\s*5\s*个根因')
for f in sorted(glob.glob(root + '*.html')):
    t = open(f, encoding='utf-8').read()
    for m in pat.finditer(t):
        s = max(0, m.start() - 80)
        print(f.split('/')[-1], '|', re.sub(r'<[^>]+>', '', t[s:m.end() + 40]).replace('\n', ' '))
