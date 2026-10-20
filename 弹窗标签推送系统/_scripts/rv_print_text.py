"""只读：打印阶段 5 全文文本、阶段 6 第七节文本。"""
import os
from _textify import BASE, textify
s5 = textify(os.path.join(BASE, '阶段5_方案选型.html'))
print(s5[:9000])
print('#' * 60)
s6 = textify(os.path.join(BASE, '阶段6_方案设计.html'))
a = s6.find('七实施分层'); b = s6.find('八短期快速提升')
print(s6[a:b])
print('#' * 60)
print(s6[:2500])
