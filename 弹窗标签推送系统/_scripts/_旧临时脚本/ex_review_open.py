"""列出审查记录中状态为「退回」且其后没有「已处理」「有异议」的条目标题（只读，不带参数）。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(B, '过程记录/审查记录.md'), encoding='utf-8').read()
parts = re.split(r'\n(?=### )', s)
for p in parts:
    head = p.split('\n', 1)[0]
    if head.startswith('### ') and '状态：退回' in head:
        if '已处理' not in p and '有异议' not in p:
            print('未处理：', head[:120])
print('节标题：', [l for l in s.split('\n') if l.startswith('## ')][-3:])
