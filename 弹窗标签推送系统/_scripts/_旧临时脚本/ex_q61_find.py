# 只读：在决策汇报与环节1 原始 HTML 中，找出含「原写 / 更正 / 按审查 / 审查 Rxx」的最内层全角括注（括号配对），
# 输出每条的所在行、原始片段；不在括号里的命中单列。供 Q61 移括注用。
import re, os
root = '/Users/decheng.huang/claude/弹窗标签推送系统/'
kw = re.compile(r'原写|更正|按审查|审查 ?R\d+|曾写|旧写|原为')
def strip(s): return re.sub(r'<[^>]+>', '', s)
for f in ['决策汇报.html', '环节1_现状盘点.html']:
    s = open(os.path.join(root, f), encoding='utf-8').read()
    # 屏蔽 style / script
    mask = list(s)
    for m in re.finditer(r'<(style|script).*?</\1>', s, flags=re.S):
        for k in range(m.start(), m.end()): mask[k] = ' '
    t = ''.join(mask)
    # 括号配对
    pairs = {}; st = []
    for i, ch in enumerate(t):
        if ch == '（': st.append(i)
        elif ch == '）' and st: pairs[st.pop()] = i
    spans = sorted(pairs.items())
    found = {}; loose = []
    for m in kw.finditer(t):
        # 不在标签内
        lt = t.rfind('<', 0, m.start()); gt = t.rfind('>', 0, m.start())
        if lt > gt: continue
        inner = None
        for a, b in spans:
            if a < m.start() < b and (inner is None or a > inner[0]): inner = (a, b)
        if inner: found[inner] = 1
        else: loose.append(m.start())
    # 去掉被其他命中括注包含的（保留最外层的命中括注）
    keys = sorted(found)
    outer = [k for k in keys if not any(o != k and o[0] < k[0] and k[1] < o[1] for o in keys)]
    print('=' * 70); print(f, '命中括注（最外层）', len(outer), '｜括号外命中', len(loose))
    for n, (a, b) in enumerate(outer, 1):
        line = t.count('\n', 0, a) + 1
        raw = s[a:b + 1]
        print(f'--- #{n} L{line} 长{len(strip(raw))}\n{strip(raw)[:600]}')
    for p in loose:
        line = t.count('\n', 0, p) + 1
        print(f'--- 括号外 L{line}：…{strip(s[max(0,p-120):p+120])}…')
