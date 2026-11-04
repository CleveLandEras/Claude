"""Q50：列出 00 中含「25」「总充值」的行（定位第三节 25 回填行）。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(B, '支撑文件/00_推进记录.md')
for i, l in enumerate(open(p, encoding='utf-8'), 1):
    if l.startswith('#'):
        print(i, 'H', l.strip()[:60])
    elif ('问题 25' in l or '总充值' in l) and i < 185:
        print(i, l.strip()[:260])
