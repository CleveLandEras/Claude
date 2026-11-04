import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '决策汇报.html', encoding='utf-8').read()
i = t.find('id="d12"')
s = t.find('<p class="small" style="margin:6px 0', i)
print(s)
print(t[s:s + 2600].replace('\n', ' '))
print('======== 首屏候选')
for m in re.finditer('建不了时按退路全量上线', t):
    print(m.start(), t[max(0, m.start() - 260):m.start() + 120].replace('\n', ' '))
    print('..')
k = t.find('id="d17"')
print(k)
print(t[k:k + 3800].replace('\n', ' '))
