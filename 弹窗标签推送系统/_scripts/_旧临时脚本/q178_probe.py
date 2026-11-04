import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['环节3_方案.html', '决策汇报.html', '支撑文件/08_弹窗效果评估方案.md', '分析/A36_验证计划.md', '支撑文件/09_取数需求_上线前基线.xlsx']:
    if f.endswith('.xlsx'):
        continue
    t = open(BASE + f, encoding='utf-8').read()
    for m in re.finditer('按玩家看', t):
        print(f, m.start(), repr(t[max(0, m.start() - 90):m.start() + 90]))
