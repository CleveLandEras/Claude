"""Q50：列出环节1 中 .src 徽标的 CSS 类名定义及用法次数。只读，不带参数。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(B, '环节1_现状盘点.html'), encoding='utf-8').read()
print('定义：', sorted(set(re.findall(r'\.(s-[a-z]+)\b', s))))
for c in sorted(set(re.findall(r'class="src (s-[a-z]+)"', s))):
    print(c, s.count(f'class="src {c}"'), re.findall(rf'class="src {c}">([^<]*)<', s)[:3])
