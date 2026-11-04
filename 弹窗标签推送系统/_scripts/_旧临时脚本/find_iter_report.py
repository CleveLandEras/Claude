"""打印迭代记录中「决策汇报」「A14」节的标题行号与该节最后 3 行。不带参数运行。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
it = open(os.path.join(BASE, '过程记录', '迭代记录.md'), encoding='utf-8').read().split('\n')
for i, l in enumerate(it):
    if l.startswith('## ') and ('决策汇报' in l or 'A14' in l):
        j = i + 1
        while j < len(it) and not it[j].startswith('## '):
            j += 1
        print('节', i + 1, l, '→ 结束于', j)
        for k in range(max(i, j - 4), j):
            print('  ', k + 1, it[k][:300])
