# 只读：定位 Q62 目标句；并查汇报、00 里有无把等级门槛写成「推断 / 待证实」的同类过时说法
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
keys = ['能否由「推断」改「已证实」', '750', '等级门槛', '等级下限', '门槛待', '门槛（推断', '下限（推断']
for f in ['环节1_现状盘点.html', '决策汇报.html', '支撑文件/00_推进记录.md']:
    lines = open(base + f, encoding='utf-8').read().split('\n')
    print('==', f, len(lines))
    for i, l in enumerate(lines):
        for k in keys:
            j = l.find(k)
            while j >= 0:
                print(i + 1, k, '|', l[max(0, j - 70): j + 80].replace('\n', ' '))
                j = l.find(k, j + 1)
