import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
terms = ['→ 丙', '条件式推荐', '按工作原则 v2 重理', '理由弱', '理由不成立', '不独立成立', '只能按成本和风险排']
s = open(base + '决策汇报.html', encoding='utf-8').read()
c = s.find('更正记录', 100000)
print('汇报 更正记录起点', c, '总长', len(s), 'details', s.count('<details'), s.count('</details>'), 'div', s.count('<div'), s.count('</div>'))
for t in terms:
    for m in re.finditer(re.escape(t), s[:c]):
        print('汇报 正文', t, m.start(), s[max(0, m.start()-80):m.end()+80].replace('\n', ' '))
s3 = open(base + '环节3_方案.html', encoding='utf-8').read()
print('环节3 details', s3.count('<details'), s3.count('</details>'))
for t in terms:
    for m in re.finditer(re.escape(t), s3):
        print('环节3', t, m.start(), s3[max(0, m.start()-80):m.end()+80].replace('\n', ' '))
print('环节3 更正记录起点', [m.start() for m in re.finditer('更正记录', s3)][:6])
