import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
"""列出迭代记录.md 的标题与版本行的行号（只读，不带参数）。"""
p = _ROOT + '/迭代记录.md'
with open(p, encoding='utf-8') as f:
    lines = f.readlines()
print('总行数', len(lines))
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('#') or (s.startswith('v') and '（2026' in s[:12]):
        print(i, s[:80])
