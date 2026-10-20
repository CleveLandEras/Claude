import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
# 规划者只读：列出审查记录、设计卡、迭代记录中 10-10 的标题行与偏离警报、对计划的意见
root = _ROOT + '/过程记录/'
for name in ['审查记录.md', '设计卡.md', '迭代记录.md', '监督记录.md']:
    print('=' * 60, name)
    try:
        lines = open(root + name, encoding='utf-8').read().split('\n')
    except Exception as e:
        print(e); continue
    for i, l in enumerate(lines, 1):
        if l.startswith('#') and ('10-10' in l or '10/10' in l):
            print(i, l[:200])
    for i, l in enumerate(lines[-400:], len(lines) - 399):
        if ('偏离警报' in l or '对计划的意见' in l) and i > len(lines) - 400:
            print('  ', i, l[:200])
