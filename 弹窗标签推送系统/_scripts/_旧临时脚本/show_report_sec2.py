"""打印决策汇报中含「谁大，取决于」「最重的一件」「待审查核对」「规划者写死」的行及行号，和第二节 h2 所在行号。不带参数运行。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
for f in ['决策汇报.html', '环节2_问题诊断.html']:
    lines = open(os.path.join(BASE, f), encoding='utf-8').read().split('\n')
    print('=====', f, len(lines))
    for i, l in enumerate(lines):
        for t in ['谁大，取决于', '最重的一件', '待审查核对', '规划者写死', '与这条链的关系取决于', '更正记录（', '<h2']:
            if t in l:
                print(i + 1, t, '｜', l.strip()[:200])
                break
