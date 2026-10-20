import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
B = _ROOT + '/'
def strip(t):
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t)
t = strip(open(B + '弹窗标签推送方案_V1.html', encoding='utf-8').read())
for k in ['理由弱', '内容选择', '排储值类第一', '储值集中只说明', '少弹']:
    for m in re.finditer(re.escape(k), t):
        print('[%s] …%s…' % (k, t[max(0, m.start()-120):m.start()+90]))
