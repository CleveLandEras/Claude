import glob
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for p in glob.glob(base + '分析/A35*'):
    t = open(p, encoding='utf-8').read()
    print(p, len(t))
    print(t[:1800])
    i = t.find('## 对 02 的提案')
    if i < 0:
        i = t.find('对 02 的提案')
    print('-----')
    print(t[i:i+2200])
