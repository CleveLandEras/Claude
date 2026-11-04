"""打印 A3 中含「敏感度」的行全文（只读，不带参数）。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for i, l in enumerate(open(os.path.join(B, '分析/A3_回流与潜在付费画像.md'), encoding='utf-8'), 1):
    if '**敏感度**' in l:
        print(i, l)
