"""Q61 只读扫描：列出决策汇报与环节1 中所有含「原写」「更正」的全角括号段（按嵌套配对，取最内层含关键词的段及其外层），
并列出 h2/h3 标题行号，便于判断所在小节。不写文件。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = ('原写', '更正')

def spans(s):
    st, out = [], []
    for i, ch in enumerate(s):
        if ch == '（':
            st.append(i)
        elif ch == '）' and st:
            a = st.pop()
            out.append((a, i + 1, len(st)))
    return out

for f in ['决策汇报.html', '环节1_现状盘点.html']:
    L = open(os.path.join(BASE, f), encoding='utf-8').read().split('\n')
    print('=' * 30, f)
    for i, l in enumerate(L):
        if re.search(r'<h[1-3]|<details|<summary', l):
            print(f'  [标题] 行 {i+1}: {re.sub(r"<[^>]+>", "", l)[:70]}')
    n = 0
    for i, l in enumerate(L):
        sp = [x for x in spans(l) if any(k in l[x[0]:x[1]] for k in KEY)]
        # 只保留不包含其他命中段的最内层
        inner = [x for x in sp if not any(y != x and x[0] < y[0] and y[1] < x[1] for y in sp)]
        for a, b, dep in inner:
            n += 1
            seg = l[a:b]
            print(f'  #{n} 行 {i+1} 深 {dep} 长 {b-a}: {seg[:160]}{"…" if len(seg) > 160 else ""}')
        # 不在括号里的「原写」
        for m in re.finditer('原写', l):
            if not any(a <= m.start() < b for a, b, _ in sp):
                print(f'  !! 行 {i+1} 括号外「原写」: …{l[max(0,m.start()-60):m.start()+60]}…')
    print('  合计', n)
