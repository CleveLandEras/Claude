"""Q113 定位：A29「多弹 20」、A31「分两档不依赖价格」所在行与 A29 修改说明位置（只读）。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
for f, terms in [('分析/A29_评估与可检测幅度.md', ['多弹 20', '修改说明', '更正']), ('分析/A31_决策点选项.md', ['分两档不依赖价格'])]:
    lines = open(os.path.join(BASE, f), encoding='utf-8').read().split('\n')
    print('=' * 40, f, len(lines))
    for t in terms:
        for i, l in enumerate(lines, 1):
            j = l.find(t)
            if j != -1:
                print(f'  [{t}] L{i}: …{l[max(0, j-120):j+len(t)+200]}…')
