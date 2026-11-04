"""R69–R71 定位与核对：列出相关词在各文件的行号与片段。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A9_登录平台分布.md', '分析/A1_用户价值结构.md',
         '分析/A11_会员等级.md', '分析/A13_八月离开的用户.md']
TERMS = ['可以覆盖', '可覆盖', '其他通路补', '问题 25 d', '15 天以后变化小得多']
for f in FILES:
    print('=' * 10, f)
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        for t in TERMS:
            j = l.find(t)
            while j != -1:
                print(i, t, '…' + l[max(0, j - 90):j + 70].strip() + '…')
                j = l.find(t, j + 1)
