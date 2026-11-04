"""Q56 定位与核对：汇报第二至四节的旧指向。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = ['待研发确认', '没有任何数据', '问题 1）', '问题 23 b、c', '问题 6 b、23 e', '问题 23', '问题 3）']
for f in ['决策汇报.html', '环节1_现状盘点.html', '分析/A1_用户价值结构.md', '分析/A8_卡别与最后登录.md',
          '分析/A10_储值回馈比与礼包指纹.md', '分析/A11_会员等级.md', '分析/A13_八月离开的用户.md']:
    print('=' * 10, f)
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        for t in TERMS:
            j = l.find(t)
            while j != -1:
                print(i, t, '…' + l[max(0, j - 80):j + 50].strip() + '…')
                j = l.find(t, j + 1)
