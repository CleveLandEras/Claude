import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
# Q318 复核：A81 中作废口径词的出现位置（只读）
P = _ROOT + '/分析/A81_人群定义回溯.md'
lines = open(P, encoding='utf-8').read().splitlines()
for t in ['登录不少于 4 天', '少一半', '50%–75%', '75% 以上', '140,000', '14 万', '14万', '821', '29,653', '4,692']:
    hits = [(i + 1, l[:60]) for i, l in enumerate(lines) if t in l]
    print(t, len(hits), [h[0] for h in hits])
