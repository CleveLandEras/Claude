"""Q53 定位与核对：卡别读法相关词在各文件的行号与片段。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A8_卡别与最后登录.md', '分析/A11_会员等级.md',
         '分析/A3_回流与潜在付费画像.md', '分析/A13_八月离开的用户.md', '分析/A1_用户价值结构.md', '分析/A2_储值档位分布.md']
TERMS = ['跟储值走', '按储值定级', '按储值评', '卡别怎么升', '怎么升降', '问题 25 c', '近期评定', '会降卡', '升卡门槛', '门槛之一',
         '问题 25 d', '卡别权益', '玩得多才升卡', '120 名普卡', '120 人', '130 人', '130 名']
for f in FILES:
    print('=' * 10, f)
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        hits = [t for t in TERMS if t in l]
        for t in hits:
            j = l.find(t)
            while j != -1:
                print(i, t, '…' + l[max(0, j - 70):j + 50].strip() + '…')
                j = l.find(t, j + 1)
