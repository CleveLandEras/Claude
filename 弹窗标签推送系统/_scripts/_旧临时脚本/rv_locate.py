# 只读：定位各文件中的标题行号
import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['过程记录/设计卡.md', '过程记录/审查记录.md', '规则与交接/工作原则.md']:
    lines = open(B + f, encoding='utf-8').read().split('\n')
    print('=====', f, len(lines))
    for i, l in enumerate(lines, 1):
        if f.endswith('设计卡.md') and l.startswith('## '):
            print(i, l[:80])
        if f.endswith('审查记录.md') and (l.startswith('## ') and '2026-09-28' in l):
            print(i, l[:80])
        if f.endswith('工作原则.md') and l.startswith('#'):
            print(i, l[:80])
# 审查记录中 R103-R107 位置
lines = open(B + '过程记录/审查记录.md', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines, 1):
    if re.match(r'### R10[3-9]', l) or re.match(r'### R1[1-9]\d', l):
        print(i, l[:100])
