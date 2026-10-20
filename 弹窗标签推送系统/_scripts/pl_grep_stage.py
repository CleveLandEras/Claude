import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os, re
root = _ROOT + ''
terms = [l.strip() for l in open(os.path.join(root, '_versions/search_terms.txt'), encoding='utf-8') if l.strip()]
files = sorted(f for f in os.listdir(root) if f.startswith('阶段') and f.endswith('.html') and f != '阶段产出规划.html')
def text(p):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s)
for f in files:
    t = text(os.path.join(root, f))
    print('==', f)
    for term in terms:
        hits = [m.start() for m in re.finditer(re.escape(term), t)]
        if not hits: continue
        print('  [%s] %d' % (term, len(hits)))
        for h in hits[:4]:
            print('     …' + t[max(0, h-60):h+80] + '…')
