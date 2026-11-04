"""Q54 定位与核对：首储相关旧数与「问题 25 d」在各文件中的位置。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A10_储值回馈比与礼包指纹.md', '分析/A2_储值档位分布.md',
         '分析/A3_回流与潜在付费画像.md', '分析/A12_活动赠点与新增参与.md', '支撑文件/00_推进记录.md']
TERMS = ['523', '588', '15,000', '16,800', '首储弹窗', '问题 25 d', '50@300', '50 @ 300']
for f in FILES:
    print('=' * 10, f)
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        for t in TERMS:
            j = l.find(t)
            while j != -1:
                print(i, t, '…' + l[max(0, j - 70):j + 60].strip().replace('\n', ' ') + '…')
                j = l.find(t, j + 1)
