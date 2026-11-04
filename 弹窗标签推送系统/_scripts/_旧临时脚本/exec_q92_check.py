"""执行者用（Q92 完成标准）：统计汇报正文（存档框与更正记录之外）中旧句的出现次数；检查 details / div / section 开闭是否平衡。只读，不带参数。"""
import os
import re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(BASE, '决策汇报.html'), encoding='utf-8').read()
# 去掉存档 details 与更正记录 details
body = re.sub(r'<details[^>]*><summary>(存档|更正记录)[\s\S]*?</details>', '', s)
for t in ['其余按原设计推进', '本地接下来补的是弹窗线的诊断和证据', '可交研发', '你的 3 个关键决定', '发给运营的 3 句']:
    print(t, body.count(t))
for tag in ['details', 'div', 'section', 'table', 'pre']:
    print(tag, s.count(f'<{tag}'), s.count(f'</{tag}>'))
