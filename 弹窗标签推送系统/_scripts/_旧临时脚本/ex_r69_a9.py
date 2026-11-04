"""R69：A9 中含「覆盖」的行（核对「意味着什么」第一条）。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for i, l in enumerate(open(os.path.join(B, '分析/A9_登录平台分布.md'), encoding='utf-8'), 1):
    j = l.find('覆盖')
    while j != -1:
        print(i, '…' + l[max(0, j - 80):j + 50].strip() + '…')
        j = l.find('覆盖', j + 1)
