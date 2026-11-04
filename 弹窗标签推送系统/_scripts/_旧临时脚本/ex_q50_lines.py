"""Q50 定位：列出各文件中与 25 a（总充值金额口径）相关词所在的行号与片段。只读，不带参数。"""
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A1_用户价值结构.md', '分析/A3_回流与潜在付费画像.md',
         '分析/A10_储值回馈比与礼包指纹.md', '分析/A11_会员等级.md', '分析/A7_目标人群重叠.md', '支撑文件/00_推进记录.md']
TERMS = ['代储', '转帐', '储值通路', '25 a', '运营第 1 句', '运营 3 句', '对应原问题', '想确认三件事', 'Cowork']
for f in FILES:
    p = os.path.join(B, f)
    print('=' * 20, f)
    for i, l in enumerate(open(p, encoding='utf-8'), 1):
        hit = [t for t in TERMS if t in l]
        if hit:
            s = l.strip()
            j = min(s.find(t) for t in hit)
            print(i, hit, '…' + s[max(0, j - 60):j + 100] + '…')
