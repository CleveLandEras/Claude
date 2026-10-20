import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
# 规划者只读：打印答复登记中 10/9、10/10 的行全文，以及已定事项、进展日志的相关行
root = _ROOT + ''
for name, keys in [('过程记录/任务清单.md', ['2026-10-10', '2026-10-09']),
                   ('规则与交接/已定事项.md', ['10/10', '10/9']),
                   ('进展日志.md', ['10-10 10:', '10-10 09:5', '10-10 11', '10-10 12', '10-10 13', '10-10 14'])]:
    print('=' * 60, name)
    for i, line in enumerate(open(root + '/' + name, encoding='utf-8'), 1):
        if any(k in line for k in keys):
            print(i, line.rstrip()[:3000])
