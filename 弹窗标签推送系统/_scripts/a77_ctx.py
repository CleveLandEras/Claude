import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
tx = open(base + '弹窗标签推送方案_V1.html', encoding='utf-8').read()
tx = re.sub(r'<style.*?</style>', '', tx, flags=re.S)
tx = re.sub(r'<script.*?</script>', '', tx, flags=re.S)
tx = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', tx))
out = []
for t, w in [('建成标准', 900), ('潜在流失', 260), ('衰减三档', 300), ('现有后台可做', 400), ('已能做', 200)]:
    out.append('## ' + t)
    for k, m in enumerate(re.finditer(re.escape(t), tx)):
        if k >= 4:
            break
        i = m.start()
        out.append(f'- …{tx[max(0,i-60):i+w]}…')
open(base + '_versions/a77_ctx3.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
