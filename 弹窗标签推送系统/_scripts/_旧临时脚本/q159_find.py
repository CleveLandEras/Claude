import io
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
with io.open(base + '环节3_方案.html', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        k = line.find('排除新增、回流')
        while k >= 0:
            print(i, line[max(0, k - 120):k + 120].replace('\n', ' '))
            k = line.find('排除新增、回流', k + 1)
