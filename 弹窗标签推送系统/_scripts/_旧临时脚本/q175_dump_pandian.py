# Q175：只读，把盘点 HTML 去掉标签后按行打印，供读取（带行号，便于引用）
import re, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(B + '来源资料/claude_弹窗标签推送_盘点.html', encoding='utf-8').read()
h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
h = re.sub(r'<(br|/p|/div|/tr|/li|/h\d|/table|/section)[^>]*>', '\n', h)
h = re.sub(r'<[^>]+>', ' ', h)
h = html.unescape(h)
lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in h.split('\n')]
lines = [l for l in lines if l]
for i, l in enumerate(lines, 1):
    print(i, l)
