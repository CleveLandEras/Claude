"""只读：进展日志最后 8 行；迭代记录最后 40 行。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lines = open(os.path.join(BASE, '进展日志.md'), encoding='utf-8').read().rstrip('\n').split('\n')
print('进展日志总行数', len(lines))
for i, l in enumerate(lines[-8:], len(lines) - 7):
    print(i, l[:1200])
print('=' * 60)
it = open(os.path.join(BASE, '过程记录', '迭代记录.md'), encoding='utf-8').read().rstrip('\n').split('\n')
for l in it[-40:]:
    print(l[:800])
