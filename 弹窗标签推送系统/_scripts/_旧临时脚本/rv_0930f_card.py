"""打印设计卡 Q130 一节（只读）。"""
t = open('/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/设计卡.md', encoding='utf-8').read()
i = t.find('## Q130')
j = t.find('\n## Q', i + 5)
print(t[i:j if j > 0 else len(t)])
