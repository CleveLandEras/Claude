"""Q295 设计用：只读抽取阶段7 场景表与呈交版附录 B/C 的纯文本，便于设计方法。不得出结论。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, html, os
ROOT = _ROOT + '/'
def text(fn):
    s = open(ROOT + fn, encoding='utf-8').read()
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    s = re.sub(r'</(tr|p|h[1-6]|li|div|summary)>', '\n', s)
    s = re.sub(r'</t[dh]>', ' | ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s
out = []
t7 = text('阶段7_方案验证.html')
out.append('===== 阶段7 全文 =====\n' + t7)
tv = text('弹窗标签推送方案_V1.html')
i = tv.find('附录 B')
j = tv.find('附录 D')
out.append('===== 呈交版 附录B~C =====\n' + (tv[i:j] if i >= 0 else 'NOT FOUND'))
k = tv.find('建成标准')
out.append('===== 呈交版 建成标准附近 =====\n' + tv[k:k+3000])
k = tv.find('本期范围')
out.append('===== 呈交版 本期范围附近 =====\n' + tv[k:k+3000])
open(ROOT + '_versions/ds_q295_out.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(t7), len(tv))
