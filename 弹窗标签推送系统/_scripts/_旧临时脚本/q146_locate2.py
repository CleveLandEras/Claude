import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(base + '决策汇报.html', encoding='utf-8').read()
def show(a, b):
    print(s[a:b])
    print('=' * 30)
for key in ['id="d5"', 'id="d8"', 'id="d11"']:
    i = s.find(key)
    print('##', key, i)
    j = s.find('<div class="dec"', i + 10)
    show(i - 20, j)
for t in ['推到第二期', '存档', '原则 v3']:
    print('##', t, [m.start() for m in re.finditer(t, s)])
i = s.find('<h3>推送：高卡流失')
print('## panel push', i)
show(i, i + 2200)
