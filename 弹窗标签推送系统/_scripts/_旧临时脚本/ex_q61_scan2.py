"""Q61 只读扫描 2：两份文件中含 R\\d+ / Q\\d+ / 「曾写」「上一版」「作废」的括号段（不含 原写/更正 的），以及「更正记录」字样出现位置。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r'(审查 ?R\d+|\bR\d{2}\b|\bQ\d{2}\b|曾写|上一版|作废|第一版)')

def spans(s):
    st, out = [], []
    for i, ch in enumerate(s):
        if ch == '（':
            st.append(i)
        elif ch == '）' and st:
            a = st.pop(); out.append((a, i + 1))
    return out

for f in ['决策汇报.html', '环节1_现状盘点.html']:
    L = open(os.path.join(BASE, f), encoding='utf-8').read().split('\n')
    print('=' * 30, f)
    for i, l in enumerate(L):
        if '更正记录' in l:
            j = l.find('更正记录'); print(f'  [更正记录] 行 {i+1}: …{l[max(0,j-80):j+80]}…')
    for i, l in enumerate(L):
        for a, b in spans(l):
            seg = l[a:b]
            if PAT.search(seg) and not ('原写' in seg or '更正' in seg):
                print(f'  行 {i+1}: {seg[:200]}')
        # 括号外的 R/Q 编号
        sp = spans(l)
        for m in PAT.finditer(l):
            if not any(a <= m.start() < b for a, b in sp):
                print(f'  !! 行 {i+1} 括号外: …{re.sub(r"<[^>]+>", "", l[max(0,m.start()-70):m.start()+70])}…')
