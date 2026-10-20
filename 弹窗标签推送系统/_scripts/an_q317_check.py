# Q317 复核：阶段 3、4、5、6 旧计数检索（只读）
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE
terms = ['5 个根因', '10 个缺口', '14 个场景', '12 个为推断', '推断可实现 12', '9 项推断', '15 项推断', '可实现 5']
for n in ['阶段3_现状盘点', '阶段4_问题诊断', '阶段5_方案选型', '阶段6_方案设计']:
    t = textify(os.path.join(BASE, n + '.html'))
    print(n, {k: t.count(k) for k in terms})
