import re
s = open('/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html', encoding='utf-8').read()
for m in re.finditer(r'<a[^>]*href="([^"]*环节3[^"]*)"[^>]*>', s):
    print(m.group(0))
i = s.find('方案环节已开始')
print(s[i-50:i+200])
