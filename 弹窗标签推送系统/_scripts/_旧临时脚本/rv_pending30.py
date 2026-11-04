import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
parts = re.split(r'\n(?=### R\d+)', t)
print('总长', len(t), '条目', len(parts) - 1)
for s in parts[1:]:
    head = s.split('\n')[0]
    if '状态：退回' in head and '已处理' not in s and '有异议' not in s:
        print('未处理:', head)
    elif '状态：退回' in head and '复核通过' not in s and '已处理' in s:
        print('已处理待复核:', head)
secs = re.findall(r'\n## (20\d\d-\d\d-\d\d \d\d:\d\d[^\n]*)', t)
print('最近小节:', secs[-3:])
