import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob
base = _ROOT + '/'
for f in sorted(glob.glob(base + '阶段*_*.html')):
    s = open(f, encoding='utf-8').read()
    txt = re.sub(r'<[^>]+>', ' ', s)
    txt = re.sub(r'\s+', ' ', txt)
    hits = []
    for kw in ['研发', '只有新增能直接圈出', '可直接圈出']:
        for m in re.finditer(kw, txt):
            hits.append((kw, txt[max(0, m.start()-40):m.end()+30]))
    print('=====', f.split('/')[-1], len(hits))
    for h in hits:
        print('  [' + h[0] + ']', h[1])
