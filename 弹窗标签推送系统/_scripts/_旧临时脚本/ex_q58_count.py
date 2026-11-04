"""Q58：列出汇报、环节1、00 中「3 件」「自查 3」字样的行，便于把 Dk 自查件数同步为 4。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ['决策汇报.html', '环节1_现状盘点.html', '支撑文件/00_推进记录.md']:
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        for t in ['3 件', '三件', '自查 3']:
            j = l.find(t)
            if j != -1:
                print(f, i, t, '…' + l[max(0, j - 60):j + 40].strip() + '…')
