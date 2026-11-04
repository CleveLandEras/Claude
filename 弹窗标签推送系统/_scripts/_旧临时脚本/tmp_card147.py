p='/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/设计卡.md'
t=open(p,encoding='utf-8').read()
i=t.rfind('Q147')
j=t.find('\n## ',i)
heads=[k for k in range(len(t)) if t.startswith('\n## ',k)]
starts=[h for h in heads if h<=t.find('Q147')]
s=starts[-1] if starts else 0
print(len(t))
print(t[s:s+12000])
