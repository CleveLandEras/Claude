"""Q50：决策汇报与环节1 中含「总充值」「从未储值」「漏记」的行号与片段（核对第一节是否还有旧口径）。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ['决策汇报.html', '环节1_现状盘点.html']:
    print('=' * 10, f)
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        for t in ['总充值', '漏记', '其实付过费']:
            j = l.find(t)
            while j != -1:
                print(i, t, '…' + l[max(0, j - 50):j + 60].strip() + '…')
                j = l.find(t, j + 1)
