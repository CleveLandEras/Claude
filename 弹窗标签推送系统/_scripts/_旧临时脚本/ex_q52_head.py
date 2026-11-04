"""Q52：打印决策汇报开头（第一个 section 之前的结论区）的纯文本（只读，不带参数）。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(B, '决策汇报.html'), encoding='utf-8').read()
body = s[s.find('<body'):]
i = body.find('<section')
head = re.sub(r'<[^>]+>', ' ', body[:i])
print(re.sub(r'\s+', ' ', head)[:3000])
