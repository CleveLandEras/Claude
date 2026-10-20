# 只读：在指定阶段产出中按关键词输出所在行号与片段
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
BASE = _ROOT + '/'
JOBS = [
    ('阶段6_方案设计.html', ['两种建设顺序', '按层推进的顺序', '待 Dk 确认', '图文与点击去向开放']),
    ('阶段5_方案选型.html', ['先建后迁', '互斥', '子集']),
    ('阶段7_方案验证.html', ['待 Dk', '判断标准', '35 项', '历史遗留']),
    ('弹窗标签推送方案_V1.html', ['34', '35', '先看覆盖', '两种推进']),
]
for fn, kws in JOBS:
    p = BASE + fn
    if not os.path.exists(p):
        print('缺文件', fn); continue
    lines = open(p, encoding='utf-8').read().split('\n')
    print('=' * 20, fn, len(lines), '行')
    for i, l in enumerate(lines, 1):
        t = re.sub(r'<[^>]+>', ' ', l)
        for k in kws:
            if k in t:
                j = t.find(k)
                print(f'{i} [{k}] …{t[max(0,j-80):j+120].strip()}…')
