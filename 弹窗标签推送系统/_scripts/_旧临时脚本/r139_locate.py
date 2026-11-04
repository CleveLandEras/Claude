"""R139–R141 回归定位：列出决策汇报、环节3 中含指定词的行号（只读）。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
files = ['决策汇报.html', '环节3_方案.html']
terms = ['卡 5–7', '卡 5、卡 6+7', '降级', '剩下的本地工作']
for f in files:
    p = os.path.join(BASE, f)
    for i, line in enumerate(open(p, encoding='utf-8'), 1):
        if '<tr><td>' in line and ('审查 R' in line or '推进计划 Q' in line):
            continue  # 更正记录行跳过
        for t in terms:
            if t in line:
                s = line.strip()
                j = s.find(t)
                print(f'{f}:{i} [{t}] …{s[max(0, j-80):j+60]}…')
