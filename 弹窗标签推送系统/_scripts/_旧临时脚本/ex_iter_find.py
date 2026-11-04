"""定位迭代记录中「完成标准自查」各节的行号。只读。"""
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
lines = open(BASE + '过程记录/迭代记录.md', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines, 1):
    if '完成标准自查' in l or l.startswith('## ') or '结论更正' in l:
        print(i, l[:100])
print('总行数', len(lines))
