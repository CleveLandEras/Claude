"""只读：环节2、环节3 两份文件标签配对，以及首屏（h1 到第一个 section 前、折叠块以外）与各 h2 的代号扫描。"""
import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
pat = r'(N[1-5]\b|P[1-7]\b|D[1-8][ab]?\b|E[12]\b|Dev\d|A\d{1,2}\b|R\d{2,3}\b|Q\d{2,3}\b|两把尺子|（S）|（R）|自查 ?[①②③④⑤⑥]|运营第 ?\d ?句|\b0[2-9] ?[的方配功标推效取统])'
for f in ['环节2_问题诊断.html', '环节3_方案.html']:
    s = open(base + f, encoding='utf-8').read()
    print('=' * 10, f)
    for t in ['details', 'div', 'section', 'table', 'ol', 'p']:
        o = len(re.findall(r'<%s[\s>]' % t, s)); c = s.count('</%s>' % t)
        print(f'  {t}: 开 {o} 闭 {c}', '' if o == c else '  ←不配对')
    head = s[s.find('<h1'):s.find('<section')]
    out, depth = [], 0
    for tk in re.split(r'(<details[^>]*>|</details>)', head):
        if tk.startswith('<details'): depth += 1; continue
        if tk == '</details>': depth -= 1; continue
        if depth == 0: out.append(tk)
    txt = re.sub(r'<[^>]+>', '', re.sub(r'<a [^>]*>(.*?)</a>', r'\1', ''.join(out)))
    hits = [m.group(0) for m in re.finditer(pat, txt)]
    print('  首屏可见代号：', hits)
    h2 = ' '.join(re.sub(r'<[^>]+>', '', x) for x in re.findall(r'<h2>.*?</h2>', s))
    print('  h2 代号：', [m.group(0) for m in re.finditer(pat, h2)])
