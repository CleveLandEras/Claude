import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
text = open(p, encoding='utf-8').read()
lines = text.split('\n')
# split by ### R entries
entries = []
cur = None
for i, l in enumerate(lines):
    if l.startswith('### R') or l.startswith('## '):
        if cur: entries.append(cur)
        cur = [i + 1, l, []] if l.startswith('### R') else None
    elif cur is not None:
        cur[2].append(l)
if cur: entries.append(cur)
for ln, head, body in entries:
    last_reply = None
    last_check = None
    for j, b in enumerate(body):
        s = b.lstrip('- ').strip()
        if s.startswith('已处理') or s.startswith('有异议'):
            last_reply = j
        if s.startswith('复核通过') or s.startswith('复核未通过') or s.startswith('Dk'):
            last_check = j
    if last_reply is not None and (last_check is None or last_check < last_reply):
        print(ln, head)
        print('   ', body[last_reply][:300])
print('last lines:')
print('\n'.join(lines[-15:]))
