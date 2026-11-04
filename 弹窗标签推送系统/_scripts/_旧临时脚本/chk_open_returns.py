import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
parts = re.split(r'\n(?=### R\d+)', t)
open_items = []
for s in parts:
    m = re.match(r'### (R\d+)｜(.*)', s)
    if not m:
        continue
    head = s.split('\n', 1)[0]
    if '状态：退回' in head and '已处理' not in s and '有异议' not in s:
        open_items.append(head)
    elif '状态：退回' in head and '复核通过' not in s and '已处理' in s:
        pass
print('未处理退回：', len(open_items))
for h in open_items:
    print(h)
secs = re.findall(r'\n## (20\d\d-\d\d-\d\d \d\d:\d\d 审查)', t)
print('最近审查：', secs[-3:])
