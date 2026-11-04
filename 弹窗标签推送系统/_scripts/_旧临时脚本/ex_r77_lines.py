"""R77、R78 定位：机制描述与「最多约 2%」的出现位置。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A8_卡别与最后登录.md', '分析/A11_会员等级.md',
         '分析/A13_八月离开的用户.md', '分析/A3_回流与潜在付费画像.md']
TERMS = ['近期活跃', '近两个月不活跃', '近期玩得多', '近期不活跃', '最多约 2%', '最多再打约 2%']
for f in FILES:
    print('=' * 10, f)
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        for t in TERMS:
            j = l.find(t)
            while j != -1:
                print(i, t, '…' + l[max(0, j - 70):j + 60].strip() + '…')
                j = l.find(t, j + 1)
