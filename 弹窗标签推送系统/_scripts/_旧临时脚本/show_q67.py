p2 = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/推进计划.md'
t2 = open(p2, encoding='utf-8').read()
a = t2.find('Q66｜')
s = t2.rfind('\n', 0, a)
e = t2.find('\n', a)
print(repr(t2[s + 1:s + 80]))
print(repr(t2[e - 160:e]))
