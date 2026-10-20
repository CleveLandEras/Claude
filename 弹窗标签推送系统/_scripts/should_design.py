"""设计者用：找出队列中标为「需设计」但还没有设计卡的项；有则上锁并列出本次要设计的（最多 3 项，按队列顺序）。不带参数运行。"""
import os, re
from _textify import BASE
from _lock import acquire
plan = open(os.path.join(BASE, '过程记录', '推进计划.md'), encoding='utf-8').read()
cp = os.path.join(BASE, '过程记录', '设计卡.md')
cards = set(re.findall(r'^## (Q\d+)', open(cp, encoding='utf-8').read(), re.M)) if os.path.exists(cp) else set()
need = [q for q, t in re.findall(r'^- \[ \] (Q\d+)｜([^｜\n]*)', plan, re.M) if t.strip().startswith('需设计') and q not in cards]
if not need:
    print('结论：跳过（没有待设计的队列项）')
else:
    ok, t = acquire('designer', 50)
    print('待设计：', '、'.join(need[:3]), f'（共 {len(need)} 项待设计）')
    print('结论：设计（已上锁）' if ok else f'结论：跳过（另一次设计 {t} 开始，仍在进行）')
