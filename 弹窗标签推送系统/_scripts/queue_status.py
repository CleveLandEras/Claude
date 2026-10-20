"""列出推进计划队列里每个未完成项的状态：类型（需设计 / 直接做）、有没有设计卡、能不能执行。不带参数运行。"""
import os, re
from _textify import BASE
plan = open(os.path.join(BASE, '过程记录', '推进计划.md'), encoding='utf-8').read()
cp = os.path.join(BASE, '过程记录', '设计卡.md')
cards = set(re.findall(r'^## (Q\d+)', open(cp, encoding='utf-8').read(), re.M)) if os.path.exists(cp) else set()
items = re.findall(r'^- \[ \] (Q\d+)｜([^｜\n]*)', plan, re.M)
print('未完成队列项：', len(items))
for q, t in items:
    t = t.strip()
    kind = '需设计' if t.startswith('需设计') else ('直接做' if t.startswith('直接做') else '未标类型（按直接做）')
    ready = (kind != '需设计') or (q in cards)
    print(f'{q}｜{kind}｜设计卡：{"有" if q in cards else "无"}｜{"可执行" if ready else "等设计卡"}')
