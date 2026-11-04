import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(base + '决策汇报.html', encoding='utf-8').read()
for m in re.finditer('影响哪几件|卡在哪个答复', s):
    print(m.start(), s[max(0, m.start() - 200):m.start() + 200].replace('\n', ' '))
i = s.find('影响哪几件')
print(s[i - 300:i + 3500])
