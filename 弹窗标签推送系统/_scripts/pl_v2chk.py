import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
p = _ROOT + '/_scripts/an_呈交版V2_生成.py'
t = open(p, encoding='utf-8').read().split('\n')
for k in ['请主管定', '最不利', '可立即', '中期达成', '53.86', '推送没有数据']:
    for i, l in enumerate(t):
        if k in l:
            print(k, '|', i + 1, '|', l.strip()[:300])
