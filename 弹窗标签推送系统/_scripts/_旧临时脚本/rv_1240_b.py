# 只读：打印环节3 指定行段，与 02 第二、四张卡「下一版怎么改」
import re, html
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def text_lines(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'</(p|div|li|tr|h\d|td|th|summary|section|table)>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return [l.strip() for l in s.split('\n') if l.strip()]
L = text_lines(BASE + '环节3_方案.html')
for a, b in [(106, 140), (494, 526)]:
    for i in range(a, min(b, len(L))):
        print(i, '|', L[i][:700])
    print('=' * 40)
P = text_lines(BASE + '支撑文件/02_弹窗分人群定制方案.html')
for i, l in enumerate(P):
    if '下一版怎么改' in l or '一半' in l:
        print(i, '|', l[:900])
        print('-')
