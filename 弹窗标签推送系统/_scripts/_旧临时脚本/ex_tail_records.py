"""执行者用：打印审查记录中未处理的退回条目编号，以及审查记录、进展日志、任务清单的行数。不带参数。"""
import os, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
rv = open(os.path.join(BASE, '过程记录', '审查记录.md'), encoding='utf-8').read().split('\n')
print('审查记录 行数', len(rv))
# 按 ### R 条目切分
cur = None; blocks = []
for i, l in enumerate(rv):
    if l.startswith('### '):
        cur = [i + 1, l, []]; blocks.append(cur)
    elif l.startswith('## '):
        cur = None
        print('节', i + 1, l)
    elif cur is not None:
        cur[2].append(l)
for ln, h, body in blocks:
    if '退回' in h:
        txt = '\n'.join(body)
        done = ('已处理' in txt) or ('有异议' in txt)
        passed = ('复核通过' in txt)
        if not done or not passed:
            print(f'行{ln} {h[:80]} | 已处理={done} 复核通过={passed}')
for name in [('进展日志.md',), ('过程记录', '任务清单.md'), ('过程记录', '迭代记录.md'), ('过程记录', '设计卡.md')]:
    p = os.path.join(BASE, *name)
    print(name[-1], '行数', len(open(p, encoding='utf-8').read().split('\n')))
