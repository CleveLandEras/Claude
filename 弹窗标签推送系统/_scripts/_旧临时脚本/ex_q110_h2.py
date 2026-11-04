"""只读：打印环节2 全部 h2 全文，并标出含代号的。"""
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/环节2_问题诊断.html'
pat = r'(N[1-5]\b|P[1-7]\b|D[1-8][ab]?\b|E[12]\b|Dev\d|A\d{1,2}\b|Q\d{2,3}\b|两把尺子|（S）|（R）|\bS\b|自查|0[2-9]\b)'
for i, l in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
    if '<h2>' in l:
        m = re.findall(pat, re.sub(r'<[^>]+>', '', l))
        print(i, '代号' if m else '    ', m, '|', l.strip())
