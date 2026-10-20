import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
base = _ROOT + '/'
files = {
 'p7': '阶段7_方案验证.html',
 'p8': '阶段8_结论汇总.html',
 'v1': '弹窗标签推送方案_V1.html',
 'brief': '简报/2026-10-09_呈交版结构与逻辑.html',
}
for k, f in files.items():
    s = open(base + f, encoding='utf-8').read()
    s = re.sub(r'(?is)<(style|script).*?</\1>', '', s)
    s = re.sub(r'(?i)</(tr|p|div|h\d|li|section|details|summary|table)>', '\n', s)
    s = re.sub(r'(?i)</t[dh]>', ' | ', s)
    s = re.sub(r'(?i)<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'&nbsp;', ' ', s)
    s = re.sub(r'&amp;', '&', s)
    s = re.sub(r'&lt;', '<', s)
    s = re.sub(r'&gt;', '>', s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    open(base + '_versions/a76_' + k + '.txt', 'w', encoding='utf-8').write(s)
    print(k, len(s))
