# Q180：只读，把 决策汇报.html 去标签后按行打印（带行号），供读取附录里已有的问句
import re, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(B + '决策汇报.html', encoding='utf-8').read()
h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
h = re.sub(r'<(br|/p|/div|/tr|/li|/h\d|/table|/summary|/pre)[^>]*>', '\n', h)
h = re.sub(r'<[^>]+>', ' ', h)
h = html.unescape(h)
lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in h.split('\n')]
lines = [l for l in lines if l]
for i, l in enumerate(lines, 1):
    print(i, l[:700])
