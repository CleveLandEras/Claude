"""执行者用（Q91）：在 A21 中找「不符」「自述」「12 → 32」「02」相关行；打印 02 第 198–342 行的纯文本。只读，不带参数。"""
import os
import re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = open(os.path.join(BASE, '分析', 'A21_弹窗疲劳与规则叠加.md'), encoding='utf-8').read().split('\n')
for i, l in enumerate(A, 1):
    if any(k in l for k in ['不符', '自述', '32', '02 写', '02 的']):
        print(f'A21 {i}: {l[:400]}')
L = open(os.path.join(BASE, '支撑文件', '02_弹窗分人群定制方案.html'), encoding='utf-8').read().split('\n')
for i in range(115, 342):
    s = re.sub(r'<[^>]+>', ' ', L[i]).strip()
    s = re.sub(r'\s+', ' ', s)
    if s:
        print(f'02 {i + 1}: {s[:300]}')
