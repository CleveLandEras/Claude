"""列出环节2_问题诊断.html 的 section / h2 / h4 / details 结构与行号。不带参数运行。"""
import os, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
p = os.path.join(BASE, '环节2_问题诊断.html')
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines), '字符', sum(len(l) for l in lines))
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('<section') or s.startswith('</section') or s.startswith('<!--') or '<h2' in s or s.startswith('<h3') or s.startswith('<details') or s.startswith('<div class="no"'):
        print(i + 1, s[:150])
