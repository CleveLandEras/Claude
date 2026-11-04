base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(base + '环节3_方案.html', encoding='utf-8').read()
for a, b in [(5800, 7700), (9000, 9700), (11000, 11700), (25800, 26300), (29500, 30100), (41200, 41800)]:
    print('=====', a)
    print(s[a:b])
