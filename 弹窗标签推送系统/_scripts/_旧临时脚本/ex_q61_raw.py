# 只读：输出 Q61 要处理的每条更正括注的原始 HTML（含标签）与所在小节标题，供逐条 Edit
import re, os
root = '/Users/decheng.huang/claude/弹窗标签推送系统/'
kw = re.compile(r'原写|更正|按审查|审查 ?R\d+|曾写|旧写|原为|原判断|原状态|原「|原问题|上一版|一度写')
skip = re.compile(r'^（[^（）]*更正版）$')
def strip(s): return re.sub(r'<[^>]+>', '', s)
for f in ['决策汇报.html', '环节1_现状盘点.html']:
    s = open(os.path.join(root, f), encoding='utf-8').read()
    mask = list(s)
    for m in re.finditer(r'<(style|script).*?</\1>', s, flags=re.S):
        for k in range(m.start(), m.end()): mask[k] = ' '
    t = ''.join(mask)
    heads = [(m.start(), strip(m.group(2))[:40]) for m in re.finditer(r'<(h[1-4])[^>]*>(.*?)</\1>', t, flags=re.S)]
    pairs = {}; st = []
    for i, ch in enumerate(t):
        if ch == '（': st.append(i)
        elif ch == '）' and st: pairs[st.pop()] = i
    spans = sorted(pairs.items())
    found = {}
    for m in kw.finditer(t):
        lt = t.rfind('<', 0, m.start()); gt = t.rfind('>', 0, m.start())
        if lt > gt: continue
        inner = None
        for a, b in spans:
            if a < m.start() < b and (inner is None or a > inner[0]): inner = (a, b)
        if inner: found[inner] = 1
    keys = sorted(found)
    outer = [k for k in keys if not any(o != k and o[0] < k[0] and k[1] < o[1] for o in keys)]
    outer = [k for k in outer if not skip.match(strip(s[k[0]:k[1] + 1]))]
    print('=' * 70); print(f, '条数', len(outer))
    for n, (a, b) in enumerate(outer, 1):
        h = [x[1] for x in heads if x[0] < a]
        cnt = s.count(s[a:b + 1])
        print(f'--- #{n} 小节：{h[-1] if h else "首屏"}｜出现次数 {cnt}\n{s[a:b + 1]}')
