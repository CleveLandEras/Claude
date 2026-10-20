"""审查者用：审查结束后运行，把当前各交付物存为「已审查版」。不带参数运行。"""
import os, datetime
from _textify import BASE, deliverables, textify
REV = os.path.join(BASE, '_versions', 'reviewed')
os.makedirs(REV, exist_ok=True)
names = []
for p in deliverables():
    n = os.path.basename(p)
    open(os.path.join(REV, n + '.txt'), 'w', encoding='utf-8').write(textify(p))
    names.append(n)
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
open(os.path.join(REV, '_reviewed_at.txt'), 'w').write(now)
print('已标记审查：', now)
print('\n'.join(names))
