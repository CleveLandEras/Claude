"""Q54 核对：523 / 588 / 「问题 25 d」在汇报、环节1、A10 中每处出现的上下文，标出是否处于「原写 / 更正 / 条件句」语境。只读，不带参数。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ['决策汇报.html', '环节1_现状盘点.html', '分析/A10_储值回馈比与礼包指纹.md']:
    s = re.sub(r'<[^>]+>', '', open(os.path.join(B, f), encoding='utf-8').read())
    print('=' * 10, f)
    for t in ['523', '588', '问题 25 d', '很可能是首储', '很可能就是首储']:
        for m in re.finditer(re.escape(t), s):
            pre = s[max(0, m.start() - 160):m.start()]
            ok = any(k in pre for k in ['原写', '原判断', '原结论', '原「', '更正', '若 ', '若它', '条件句', '档位未知', '15,000 点'])
            print(('  括注/条件 ' if ok else '★正文    ') + t + '：…' + s[max(0, m.start() - 50):m.end() + 30].replace('\n', ' ') + '…')
