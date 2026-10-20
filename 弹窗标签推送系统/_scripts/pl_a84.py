import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import glob
for p in glob.glob(_ROOT + '/分析/A84*'):
    with open(p, encoding='utf-8') as f:
        lines = f.readlines()
    print(p, len(lines))
    for i, l in enumerate(lines, 1):
        if l.startswith('#') or i <= 12:
            print(i, l.rstrip()[:300])
    # print last section fully
    start = max(i for i, l in enumerate(lines, 1) if l.startswith('## '))
    print('---- last section from', start)
    for i, l in enumerate(lines[start - 1:], start):
        print(i, l.rstrip()[:500])
