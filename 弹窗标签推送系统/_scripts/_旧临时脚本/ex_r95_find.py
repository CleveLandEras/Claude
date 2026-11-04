import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['决策汇报.html', '环节2_问题诊断.html', '分析/A16_高卡流失风险.md', '分析/A19_首储与储值位.md', '分析/A14_问题清单与影响规模.md']
terms = ['还会登录', '还会回来', '已知不转化', '维持现状', '58%', '58.11%', '长期在']
for f in files:
    t = open(base + f, encoding='utf-8').read()
    for term in terms:
        for m in re.finditer(re.escape(term), t):
            s = t[max(0, m.start() - 70):m.end() + 50].replace('\n', ' ')
            print(f'[{f}] {term} :: {s}')
