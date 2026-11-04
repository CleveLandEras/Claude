import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
parts = re.split(r'\n(?=### R\d+)', t)
for s in parts:
    m = re.match(r'### (R\d+)', s)
    if not m:
        continue
    head = s.split('\n')[0]
    if '退回' in head and '已处理' not in s and '有异议' not in s:
        print('未处理：', head[:200])
print('条目数', sum(1 for s in parts if s.startswith('### R')))
