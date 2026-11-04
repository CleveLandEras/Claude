"""执行者用（Q89）：抽环节1 第四节（标签）正文、环节3 第四节、决策汇报第三节标签相关文字。只读，不带参数。"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import BASE, textify

s = textify(os.path.join(BASE, '环节1_现状盘点.html'))
i = s.find('标签')
# 找第四节起点：以「四」开头的标题
m = [x.start() for x in re.finditer(r'\n\s*四[、．.]', s)]
print('环节1 第四节候选起点', m[:5])
if m:
    st = m[0]
    nx = [x.start() for x in re.finditer(r'\n\s*五[、．.]', s) if x.start() > st]
    print(s[st:(nx[0] if nx else st + 9000)][:9000])
print('\n' + '=' * 60 + '\n环节1 中含「未登入」「当前卡别」「卡别」标签的行：')
for ln in s.split('\n'):
    if ('未登' in ln or '当前卡别' in ln or 'ID6' in ln or 'ID10' in ln or 'ID11' in ln) and len(ln) < 600:
        print('  ', ln.strip()[:400])
