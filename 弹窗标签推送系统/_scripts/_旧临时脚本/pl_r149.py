"""只读：看 R149–R152 在审查记录中的处理状态，以及决策汇报里 R151 要求的评估句、第 6 件块和交主管块是否在。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rv = open(os.path.join(BASE, '过程记录', '审查记录.md'), encoding='utf-8').read().split('\n')
for i, l in enumerate(rv):
    if l.startswith('### R149') or l.startswith('### R15'):
        print(i + 1, l[:160])
    if '已处理' in l and any(k in l for k in ('R149', 'R150', 'R151', 'R152')):
        print('  ', i + 1, l[:200])
for i, l in enumerate(rv[2480:], start=2481):
    if l.startswith('- 已处理'):
        print('  已处理行', i, l[:200])
h = open(os.path.join(BASE, '决策汇报.html'), encoding='utf-8').read()
t = re.sub(r'<[^>]+>', ' ', h)
t = re.sub(r'\s+', ' ', t)
for k in ['发送、到达', '小幅差别测不出', '交主管', '你要定的事', '更正记录', '选项在写', '到环节4 再定']:
    idx = [m.start() for m in re.finditer(re.escape(k), t)]
    print('==', k, len(idx))
    for j in idx[:3]:
        print('   …', t[max(0, j - 120):j + 160])
print('汇报字符数', len(t))
