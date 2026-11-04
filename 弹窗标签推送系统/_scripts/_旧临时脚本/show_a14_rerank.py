"""打印 A14 中「重排（按业绩）」一节全文。不带参数运行。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
p = os.path.join(BASE, '分析', 'A14_问题清单与影响规模.md')
lines = open(p, encoding='utf-8').read().split('\n')
start = None
for i, l in enumerate(lines):
    if l.startswith('#') and '重排' in l and '按业绩' in l:
        start = i; break
if start is None:
    print('未找到'); raise SystemExit
lvl = len(lines[start]) - len(lines[start].lstrip('#'))
out = [lines[start]]
for l in lines[start + 1:]:
    if l.startswith('#') and (len(l) - len(l.lstrip('#'))) <= lvl:
        break
    out.append(l)
print('起始行', start + 1)
print('\n'.join(out))
