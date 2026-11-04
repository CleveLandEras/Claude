# 只读：把决策汇报、02 转成纯文本逐行打印，供审查阅读
import re, html
from pathlib import Path
root = Path('/Users/decheng.huang/claude/弹窗标签推送系统')
for f in [root/'决策汇报.html', root/'支撑文件'/'02_弹窗分人群定制方案.html']:
    t = f.read_text(encoding='utf-8')
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<(br|/p|/div|/li|/tr|/h\d|/summary|/details|/td|/th)[^>]*>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    print('#' * 20, f.name, len(lines))
    for i, l in enumerate(lines, 1):
        print(i, l)
