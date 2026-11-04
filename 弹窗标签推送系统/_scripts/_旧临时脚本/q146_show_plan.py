base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '过程记录/推进计划.md', encoding='utf-8').read()
i = t.find('- [ ] Q146')
j = t.find('- [ ] Q147')
print(t[i:j])
print(t[:600])
