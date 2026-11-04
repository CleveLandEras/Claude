"""Q29：检查汇报、环节1 中「30.93%」「不是个别」「高卡偏 web」「31.21%」「23.97%」的上下文是否都带了口径限定（只读）。不带参数运行。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
keys = ['30.93%', '不是个别', '不是一两个', '高卡偏 web', '31.21%', '23.97%', '三成储值']
for name in ('决策汇报.html', '环节1_现状盘点.html'):
    s = open(B + name, encoding='utf-8').read()
    for k in keys:
        i = s.find(k)
        while i != -1:
            print(f'[{name}] [{k}] …{s[max(0, i-80):i+len(k)+60]}…'.replace('\n', ' '))
            print()
            i = s.find(k, i + len(k))
