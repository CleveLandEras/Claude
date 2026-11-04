"""Q57 定位：汇报、环节1 正文里「问题 N」形式的编号，标出前面是否有「原」字或处于「原写」括注里。只读，不带参数。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ['决策汇报.html', '环节1_现状盘点.html']:
    print('=' * 10, f)
    lines = open(os.path.join(B, f), encoding='utf-8').read().split('\n')
    for i, l in enumerate(lines, 1):
        t = re.sub(r'<[^>]+>', '', l)
        for m in re.finditer(r'问题 (\d+(?:-\d+)?)( [a-e](?:、[a-e])*)?', t):
            pre = t[max(0, m.start() - 160):m.start()]
            if pre.endswith('原') or pre.endswith('诊断') or pre.endswith('诊断问题'):
                continue
            k = max(pre.rfind('原写'), pre.rfind('原「'), pre.rfind('原为'), pre.rfind('原各处'), pre.rfind('更正：'), pre.rfind('原状态'))
            if k != -1 and pre[k:].count('）') == 0 and pre[k:].count('」') < pre[k:].count('「') + 1:
                continue
            print(i, m.group(0), '…' + t[max(0, m.start() - 60):m.end() + 30] + '…')
