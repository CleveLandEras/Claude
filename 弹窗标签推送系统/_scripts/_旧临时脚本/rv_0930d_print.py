# 只读：汇报纯文本，打印指定行段
import re, html
from pathlib import Path
root = Path('/Users/decheng.huang/claude/弹窗标签推送系统')
f = root/'决策汇报.html'
t = f.read_text(encoding='utf-8')
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
t = re.sub(r'<(br|/p|/div|/li|/tr|/h\d|/summary|/details|/td|/th)[^>]*>', '\n', t)
t = re.sub(r'<[^>]+>', '', t)
t = html.unescape(t)
lines = [l.strip() for l in t.split('\n') if l.strip()]
for a, b in [(1, 30), (286, 470), (489, 540), (556, 572), (630, 650), (660, 670), (770, 776), (830, 880), (975, 983)]:
    print('-' * 10, a, b)
    for i in range(a, b + 1):
        print(i, lines[i - 1])
