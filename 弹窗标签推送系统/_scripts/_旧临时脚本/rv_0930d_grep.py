# 只读：汇报转纯文本，按关键词列出行号与所在上下文；另打印 04、07 的提案一节
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
print('总行数', len(lines))
keys = ['首期建议', '只剩 1 张', '首期改为', '推后', '首期基本不用', '不依赖外部答复', '只有 2 项', '可以原样转发', '可以转发', '一次生成', '不刷新', '复制', '审查核对通过', '存档', '原则 v2 之前']
for k in keys:
    hits = [i for i, l in enumerate(lines, 1) if k in l]
    print('==', k, hits)
# 打印第三节范围：找标题行
for i, l in enumerate(lines, 1):
    if l.startswith('三') or l.startswith('四') or l.startswith('五') or '第三节' in l[:6]:
        print('H', i, l[:80])
