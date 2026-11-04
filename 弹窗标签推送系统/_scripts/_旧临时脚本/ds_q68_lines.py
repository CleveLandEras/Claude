# 只读：打印若干文件的行数，以及审查记录中各节标题所在行、环节2 中 D5/D6/D7 所在行
import os, re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['过程记录/审查记录.md', '过程记录/设计卡.md', '环节2_问题诊断.html', '环节1_现状盘点.html', '数据/说明.md']:
    p = base + f
    if not os.path.exists(p):
        print(f, '不存在'); continue
    lines = open(p, encoding='utf-8').read().split('\n')
    print('==', f, len(lines), '行')
    for i, l in enumerate(lines, 1):
        if f.endswith('审查记录.md') and l.startswith('## '):
            print(i, l[:80])
        if f.endswith('设计卡.md') and l.startswith('## '):
            print(i, l[:80])
        if f.startswith('环节2') and re.search(r'D5 · |D6 · |D7 · |D8 · ', l):
            print(i, l[:80])
        if f.startswith('环节1') and ('时机与次数' in l or '每日次数' in l):
            print(i, l[:80])
