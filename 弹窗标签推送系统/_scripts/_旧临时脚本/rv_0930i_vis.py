# 审查 2026-09-30 11:49：折叠框外可见文字检索（只读，只打印）
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
TERMS = ['分了组也', '要靠分组实验', '才看得出', '不独立成立', '07 第一期更像', '补写中', '不能承诺', '不承诺', '不能用储值证明', '可代替随机分组', '只能按成本', '整体回退', '一起回到', '更正记录（', '修改记录']
for f in ['决策汇报.html', '环节2_问题诊断.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html']:
    t = vis(f)
    print('=====', f, '可见字数', len(t))
    for w in TERMS:
        hits = [m.start() for m in re.finditer(re.escape(w), t)]
        if not hits: continue
        print(f'  〈{w}〉{len(hits)} 处')
        for h in hits[:6]:
            print('     @' + str(h) + ' …' + t[max(0, h - 70):h + 50] + '…')
