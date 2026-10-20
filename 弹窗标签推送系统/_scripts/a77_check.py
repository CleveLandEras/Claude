import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob, os
base = _ROOT + '/'
files = sorted(glob.glob(base + '阶段[1-8]_*.html')) + [base + '弹窗标签推送方案_V1.html']
terms = ['10,749', '62,292', '17.26', '27,313', '43.85', '40,117', '74,480', '53.86', '6／8', '6/8', '8,022', '16,564',
         '5,976', '25,972', '8,542', '51.57', '358', '36,028', '11,803', '34,979', '56.15', '5,960', '34,363', '12,188',
         '599', '141', '108', '15 人', '4 个', '26.59', '41.69', '29 天', '30 天', '10,000', '100,000', '34 项', '8 条',
         '25 个', '约 17', '14–18', '14 个', '10 个', '10 项', '6 项', '7 项', '3 倍', '5 条规则', '3 条']
def clean(h):
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', t)
out = []
texts = {}
for f in files:
    texts[os.path.basename(f)] = clean(open(f, encoding='utf-8').read())
for t in terms:
    out.append('## ' + t)
    for n, tx in texts.items():
        hits = [m.start() for m in re.finditer(re.escape(t), tx)]
        if hits:
            i = hits[0]
            out.append(f'- {n} ×{len(hits)}: …{tx[max(0,i-50):i+70]}…')
open(base + '_versions/a77_hits.txt', 'w', encoding='utf-8').write('\n'.join(out))
# arithmetic
print('10749/62292', 10749/62292*100)
print('27313/62292', 27313/62292*100, 10749+16564)
print('16564/62292', 16564/62292*100, 8022/62292*100)
print('34979', 62292-27313, 34979/62292*100)
print('40117/74480', 40117/74480*100, 40117+34363)
print('62292+12188', 62292+12188)
print('8542/16564', 8542/16564*100)
print('5960+8542', 5960+8542)
print('36028/11803', 36028/11803)
print('5976/62292', 5976/62292*100, 25972/62292*100)
print('34', 12+12+10)
