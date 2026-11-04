BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(BASE + '决策汇报.html', encoding='utf-8').read()
k = '能力线（04、05、07 与数据能力）：优先级按能力线逻辑链重排（待做，排在 02、03 验收之后）'
i = 0
while True:
    i = h.find(k, i)
    if i < 0: break
    print(i, repr(h[max(0, i - 220):i + len(k) + 260]))
    print('----')
    i += 1
r = h.find('<tr><td>96</td>')
print(repr(h[r:r + 100]))
