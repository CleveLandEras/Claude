"""Q58 定位：汇报附录「你自己查的 3 件」区块、含「叠加」「占用」的行；00 现行版自查表行号。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(B, '决策汇报.html'), encoding='utf-8').read().split('\n')
for i, l in enumerate(L, 1):
    if '自己查的' in l or '叠加' in l or '占用' in l:
        print('汇报', i, l.strip()[:220])
for i in range(len(L)):
    if '你自己查的' in L[i]:
        for j in range(i, min(i + 14, len(L))):
            print('   ', j + 1, L[j][:400])
        break
Z = open(os.path.join(B, '支撑文件/00_推进记录.md'), encoding='utf-8').read().split('\n')
for i, l in enumerate(Z, 1):
    if l.startswith('| ③ ') or l.startswith('| ② ') or l.startswith('| ① ') or 'Dk 自查 3 件' in l:
        print('00', i, l[:300])
