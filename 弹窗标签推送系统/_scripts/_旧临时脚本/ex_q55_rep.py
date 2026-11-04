"""Q55：打印决策汇报中「超过 2,000 的只有」前后片段（只读，不带参数）。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(B, '决策汇报.html'), encoding='utf-8').read()
i = s.find('超过 2,000 的只有')
print(repr(s[i - 120:i + 160]))
