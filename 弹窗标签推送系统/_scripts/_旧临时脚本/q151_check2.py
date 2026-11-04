import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '决策汇报.html', encoding='utf-8').read()
i = t.find('验收看哪几处')
j = t.find('</table>', i)
print(t[i - 300:j + 10])
