import os, re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['过程记录/审查记录.md', '过程记录/任务清单.md', '进展日志.md', '过程记录/迭代记录.md', '过程记录/设计卡.md', '归档/规则_旧/项目交接_对话要点.md', '归档/规则_旧/目标脑图.md', '先看这里.md']
for f in files:
    p = B + f
    with open(p, encoding='utf-8') as fh:
        lines = fh.readlines()
    print(f, len(lines), 'mtime', os.path.getmtime(p))
    heads = [(i + 1, l.strip()[:90]) for i, l in enumerate(lines) if l.startswith('#')]
    for h in heads[-12:]:
        print('   ', h)
