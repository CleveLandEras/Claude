"""只读：R447 复核——阶段 4、5、6 原始 HTML 中根因、缺口、场景计数的出现位置。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os, re
BASE = _ROOT + ''
pats = [r'\d+\s*(?:&nbsp;)?\s*个根因', r'\d+\s*(?:&nbsp;)?\s*个缺口', r'\d+\s*(?:&nbsp;)?\s*个场景', '另两个', '原「推送数据', '依据不足在于']
for f in ['阶段4_问题诊断.html', '阶段5_方案选型.html', '阶段6_方案设计.html']:
    s = open(os.path.join(BASE, f), encoding='utf-8').read()
    lines = s.split('\n')
    print('=' * 50, f)
    for i, ln in enumerate(lines, 1):
        for p in pats:
            for m in re.finditer(p, ln):
                a = max(0, m.start() - 60); b = m.end() + 40
                txt = re.sub(r'<[^>]+>', '', ln[a:b])
                print(f'  L{i} [{m.group(0)}] …{txt}…')
