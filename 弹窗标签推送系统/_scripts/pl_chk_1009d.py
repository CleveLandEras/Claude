import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
base = _ROOT + '/'
t = open(base + '过程记录/任务清单.md', encoding='utf-8').read()
k = t.find('## 四')
e = t.find('\n## ', k + 5)
sec = t[k:e]
print(len(sec))
lines = sec.split('\n')
print('\n'.join(lines[:8]))
print('......')
hits = [l for l in lines if ('10-09' in l or '10/9' in l or '2026-10-09' in l)]
for l in hits:
    print(l[:1500])
    print('---')
