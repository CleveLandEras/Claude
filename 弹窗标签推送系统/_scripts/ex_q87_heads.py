import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import glob
import os
B = _ROOT + '/分析/'
for p in sorted(glob.glob(B + '*.md')):
    s = open(p, encoding='utf-8').read()
    print(f'{os.path.basename(p)}｜{len(s)} 字')
for name in ['A21', 'A22', 'A23', 'A24']:
    p = glob.glob(B + name + '_*.md')[0]
    s = open(p, encoding='utf-8').read()
    i = s.find('## 结论')
    j = s.find('\n## ', i + 5)
    print('=' * 30, os.path.basename(p))
    print(s[i:j][:3500])
