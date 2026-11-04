import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/设计卡.md'
t = open(p, encoding='utf-8').read()
i = t.find('## Q147')
j = t.find('\n## ', i + 5)
print(t[i:j if j > 0 else len(t)])
