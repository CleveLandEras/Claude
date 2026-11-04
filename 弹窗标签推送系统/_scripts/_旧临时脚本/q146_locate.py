import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
terms = ['理由弱', '理由不成立', '不独立成立', '只能按成本和风险排', '不能承诺', '不承诺']
s = open(base + '决策汇报.html', encoding='utf-8').read()
print('总长', len(s))
for t in terms:
    for m in re.finditer(re.escape(t), s):
        a = max(0, m.start() - 160)
        b = min(len(s), m.end() + 160)
        print('##', t, m.start())
        print(s[a:b].replace('\n', ' '))
        print()
