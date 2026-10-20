"""只读：打印审查记录.md 最后约 260 行及其中的最大 R 编号与各节标题。"""
import os, re
from _textify import BASE
p = os.path.join(BASE, '过程记录', '审查记录.md')
lines = open(p, encoding='utf-8').read().split('\n')
nums = [int(x) for x in re.findall(r'R(\d{3})', '\n'.join(lines))]
print('最大 R 编号：', max(nums) if nums else None, '｜总行数：', len(lines))
for i, l in enumerate(lines):
    if l.startswith('## '):
        print(i + 1, l)
print('-' * 40)
print('\n'.join(lines[-260:]))
