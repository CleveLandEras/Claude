import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob, os
base = _ROOT + '/'
files = sorted(glob.glob(base + '阶段*.html')) + [base + '弹窗标签推送方案_V1.html']
kws = ['活跃', '付费率', '业绩', '留存', '统一触达层', '统一层', '互斥', '保守', '乐观', '召回', '客单价', '首储转化', '待 Dk']
for f in files:
    t = open(f, encoding='utf-8').read()
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('=====', os.path.basename(f))
    for k in kws:
        hits = [m.start() for m in re.finditer(re.escape(k), t)]
        if not hits:
            continue
        print('--', k, len(hits))
        for h in hits[:6]:
            print('   …' + t[max(0, h - 50):h + 50] + '…')
