"""Q97 辅助：列出 迭代记录.md 的 ## 与 ### 标题及行号（只看 环节3、03、决策汇报 相关节的最后几个版本）；另列 推进计划.md 队列里未完成项与 Q99。不带参数运行。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(BASE, '过程记录', '迭代记录.md'), encoding='utf-8').read().split('\n')
print('迭代记录 总行数', len(L))
cur = None
heads = []
for i, l in enumerate(L):
    if l.startswith('## '):
        cur = l; heads.append((i + 1, l, []))
    elif l.startswith('### ') and heads:
        heads[-1][2].append((i + 1, l))
for ln, h, subs in heads:
    print(f'L{ln}: {h}  （{len(subs)} 版）')
    if any(k in h for k in ('环节3', '03', '决策汇报')):
        for s in subs[-2:]:
            print(f'    L{s[0]}: {s[1][:100]}')
P = open(os.path.join(BASE, '过程记录', '推进计划.md'), encoding='utf-8').read().split('\n')
print('推进计划 第一行：', P[1][:120])
for i, l in enumerate(P):
    if l.startswith('- [ ]') or 'Q99' in l[:12]:
        print(f'  L{i+1}: {l[:160]}')
