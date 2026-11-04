"""打印 A14 中含「更正」的行号与内容，以及总行数、最后 5 行。不带参数运行。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
lines = open(os.path.join(BASE, '分析', 'A14_问题清单与影响规模.md'), encoding='utf-8').read().split('\n')
print('总行数', len(lines))
for i, l in enumerate(lines):
    if '更正' in l:
        print(i + 1, l[:250])
for i in range(max(0, len(lines) - 5), len(lines)):
    print('末', i + 1, lines[i][:250])
