# 只读：列出审查记录各节标题，以及状态为「退回」的条目是否已追加「已处理」/「有异议」
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines):
    if l.startswith('## '):
        print(i + 1, l[:80])
# 条目块
blocks = []
cur = None
for i, l in enumerate(lines):
    if l.startswith('### R'):
        if cur: blocks.append(cur)
        cur = [i + 1, l, []]
    elif l.startswith('## ') or l.startswith('### '):
        if cur: blocks.append(cur); cur = None
    elif cur:
        cur[2].append(l)
if cur: blocks.append(cur)
print('---- 退回且未处理 ----')
for ln, h, body in blocks:
    if '退回' in h:
        txt = '\n'.join(body)
        if ('已处理' not in txt) and ('有异议' not in txt):
            print(ln, h[:100])
print('---- 最后 5 个条目 ----')
for ln, h, body in blocks[-5:]:
    txt = '\n'.join(body)
    print(ln, h[:90], '| 已处理' if '已处理' in txt else '', '| 复核通过' if '复核通过' in txt else '')
