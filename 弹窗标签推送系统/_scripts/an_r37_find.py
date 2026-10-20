import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
base = _ROOT + '/'
files = ['环节1_现状盘点.html', '决策汇报.html', '分析/A3_回流与潜在付费画像.md', '分析/A7_目标人群重叠.md', '分析/A8_高卡活跃.md']
terms = ['9,786', '下限', '至少', '13,424', '15.71']
for f in files:
    p = base + f
    if not os.path.exists(p):
        print('缺', f); continue
    for i, line in enumerate(open(p, encoding='utf-8'), 1):
        if any(t in line for t in terms):
            print(f, i, line.strip()[:400])
