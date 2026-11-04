"""Q108 整合扫描 2：「已经不来」「依赖什么」「三样」在更正记录以外的命中（只读）。"""
import os, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
p = os.path.join(BASE, '决策汇报.html')
lines = open(p, encoding='utf-8').read().split('\n')
corr_start = next((i for i, l in enumerate(lines, 1) if '<summary>更正记录' in l), 10**9)
for t in ['已经不来', '依赖什么', '三样', '第 4 条']:
    n = 0
    for i, l in enumerate(lines, 1):
        if i >= corr_start:
            continue
        for m in re.finditer(re.escape(t), l):
            j = m.start(); n += 1
            print(f'[{t}] L{i}: …{re.sub("<[^>]+>", "", l[max(0, j-60):j+len(t)+60])}…')
    if n == 0:
        print(f'[{t}] 0')
