"""审查者用：列出每个交付物自上次审查（mark_reviewed.py）以来的改动。不带参数运行。"""
import os, difflib, datetime
from _textify import BASE, deliverables, textify
REV = os.path.join(BASE, '_versions', 'reviewed')
stamp = os.path.join(REV, '_reviewed_at.txt')
print('上次审查时间：', open(stamp).read().strip() if os.path.exists(stamp) else '从未审查')
print('当前时间：', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
for p in deliverables():
    n = os.path.basename(p)
    cur = textify(p).splitlines()
    old_p = os.path.join(REV, n + '.txt')
    print('\n' + '=' * 60 + f'\n文件：{n}')
    if not os.path.exists(old_p):
        print('状态：新文件（上次审查后出现），全文如下')
        print('\n'.join(cur))
        continue
    old = open(old_p, encoding='utf-8').read().splitlines()
    d = list(difflib.unified_diff(old, cur, '上次审查版', '当前版', lineterm='', n=1))
    print('状态：无改动' if not d else '状态：有改动（- 为删去，+ 为新增）')
    for l in d:
        print(l)
