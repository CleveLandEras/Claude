# 审查 2026-09-30：只取折叠框（details）外的可见文字，检索旧代号与状态措辞（只读，不写文件）
import re
from html.parser import HTMLParser
R = '/Users/decheng.huang/claude/弹窗标签推送系统/'
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.depth = 0; s.skip = 0; s.out = []
    def handle_starttag(s, t, a):
        if t == 'details': s.depth += 1
        if t in ('script', 'style'): s.skip += 1
    def handle_endtag(s, t):
        if t == 'details': s.depth -= 1
        if t in ('script', 'style'): s.skip -= 1
        if t in ('p', 'li', 'tr', 'div', 'h2', 'h3', 'td', 'th'): s.out.append(' ')
    def handle_data(s, d):
        if s.depth == 0 and s.skip == 0: s.out.append(d)
def vis(f):
    p = P(); p.feed(open(R + f, encoding='utf-8').read())
    return re.sub(r'\s+', ' ', ''.join(p.out))
TERMS = ['次线', '主线', 'N1', 'P4', 'N3', '原样转发', '可交研发', '可交数据组', '今天就能发', '多弹', '25 人']
for f in ['决策汇报.html', '环节3_方案.html', '环节2_问题诊断.html']:
    t = vis(f)
    print('=====', f, '可见字数', len(t))
    for w in TERMS:
        hits = [m.start() for m in re.finditer(re.escape(w), t)]
        print(f'  〈{w}〉{len(hits)} 处')
        for h in hits[:8]:
            print('     …' + t[max(0, h - 60):h + 40] + '…')
