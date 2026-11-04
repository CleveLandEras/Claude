"""Q55 定位：触发时机、曝光点击缺口、新手礼包 1,000 / 2,000 相关词在各文件的行号与片段。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A12_活动赠点与新增参与.md']
TERMS = ['触发时机', '4 个时机', '四个时机', '4 种时机', '首次登入', '返回大厅', '曝光', '埋点', '2,000', '绑手机', '新手礼包']
for f in FILES:
    print('=' * 10, f)
    for i, l in enumerate(open(os.path.join(B, f), encoding='utf-8'), 1):
        hits = [t for t in TERMS if t in l]
        if hits:
            j = min(l.find(t) for t in hits)
            print(i, hits, '…' + l[max(0, j - 60):j + 90].strip() + '…')
