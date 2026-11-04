import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
lines = t.split('\n')
print('总行数', len(lines))
heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
print('最后三节：', heads[-3:])
blocks = re.split(r'\n(?=### R\d+)', t)
for b in blocks:
    m = re.match(r'### (R\d+)', b)
    if not m:
        continue
    body = b.split('\n## ')[0]
    has_resp = ('已处理' in body) or ('有异议' in body)
    last_resp = max(body.rfind('- 已处理'), body.rfind('- 有异议'))
    last_rev = max(body.rfind('复核通过'), body.rfind('复核未通过'), body.rfind('交 Dk'))
    if has_resp and last_resp > last_rev:
        print('待复核', m.group(1), body.split('\n')[0])
    elif not has_resp:
        print('未回应', m.group(1), body.split('\n')[0][:80])
