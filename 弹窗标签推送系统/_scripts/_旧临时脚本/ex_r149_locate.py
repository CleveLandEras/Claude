"""R149–R155 回归核对：决策汇报正文（折叠依据与更正记录以外也会列出，人工判读）的剩余命中（只读）。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
p = os.path.join(BASE, '决策汇报.html')
lines = open(p, encoding='utf-8').read().split('\n')
terms = ['已经不来的高卡有', '已经不来的 927', '三样外部答复', '三样答复', '选项在写', '每件一行推荐', '第 2、3 件见', '一到就能收成', '改推乙', '三成以上', '放第一批', '看清标签条件']
for t in terms:
    n = 0
    for i, l in enumerate(lines, 1):
        j = l.find(t)
        while j != -1:
            n += 1
            print(f'  [{t}] L{i}: …{l[max(0, j-40):j+len(t)+40]}…')
            j = l.find(t, j + len(t))
    if n == 0:
        print(f'  [{t}] 无命中')
