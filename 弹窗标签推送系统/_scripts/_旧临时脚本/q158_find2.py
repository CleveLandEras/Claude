import io
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['决策汇报.html', '环节3_方案.html']
terms = ['三条判读线', '三条都按现值', '这三条', '三条是', '判读线']
for fn in files:
    print('=====', fn)
    with io.open(base + fn, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            for t in terms:
                k = line.find(t)
                while k >= 0:
                    print(i, t, '…' + line[max(0, k - 50):k + 70].replace('\n', ' ') + '…')
                    k = line.find(t, k + 1)
