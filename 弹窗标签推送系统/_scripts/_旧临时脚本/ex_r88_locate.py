
# 只读：定位 R87–R89 要改的句子所在行号
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
targets = {
    '环节1_现状盘点.html': ['不是账号累计值', '本地按终身累计套门槛', '每回到大厅一次就触发一次', '更正记录（', '<details', '</details>', '<tr><td>67'],
    '决策汇报.html': ['看多长时间', '更正记录（', '决定 C', '原句见文末', '<details', '</details>'],
    '支撑文件/00_推进记录.md': ['看多长时间'],
}
for f, keys in targets.items():
    lines = open(BASE + f, encoding='utf-8').read().split('\n')
    print('=' * 20, f, len(lines))
    for i, l in enumerate(lines, 1):
        for k in keys:
            if k in l:
                print(i, k, '|', len(l))
