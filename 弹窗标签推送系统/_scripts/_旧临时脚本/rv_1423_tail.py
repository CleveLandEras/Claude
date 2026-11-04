import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/'
t = open(base + '审查记录.md', encoding='utf-8').read()
nums = [int(x) for x in re.findall(r'### R(\d+)', t)]
print('max R', max(nums), 'lines', t.count('\n'))
print(t[-2500:])
p = open('/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md', encoding='utf-8').read()
print('=== log tail ===')
print(p[-1500:])
