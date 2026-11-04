"""只读：检查决策汇报.html 标签配对，并扫描折叠块（details）以外的正文里是否还有内部代号。"""
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
s = open(p, encoding='utf-8').read()
for t in ['details', 'div', 'section', 'table', 'p']:
    o = len(re.findall(r'<%s[\s>]' % t, s)); c = s.count('</%s>' % t)
    print(f'{t}: 开 {o} 闭 {c}', '' if o == c else '  ←不配对')
body = s[s.find('<body>'):]
# 去掉嵌套 details 内容
out, depth, i = [], 0, 0
toks = re.split(r'(<details[^>]*>|</details>)', body)
for tk in toks:
    if tk.startswith('<details'):
        depth += 1; continue
    if tk == '</details>':
        depth -= 1; continue
    if depth == 0:
        out.append(tk)
vis = re.sub(r'<script.*?</script>', '', ''.join(out), flags=re.S)
vis = re.sub(r'<a [^>]*>.*?</a>', '', vis)            # 链接文字算出处
vis = re.sub(r'<p class="src".*?</p>', '', vis, flags=re.S)
txt = re.sub(r'<[^>]+>', '', vis)
pat = r'(N[1-5]\b|P[1-5]\b|D[1-8][ab]?\b|E[12]\b|Dev\d|A\d{1,2}\b|R\d{2,3}\b|Q\d{2,3}\b|S\d\b|两把尺子|自查 ?[①②③④⑤⑥]|运营第 ?\d ?句|推迟到方案环节|0[2-9] ?[方配功标推效取])'
hits = [(m.group(0), txt[max(0, m.start()-30):m.end()+30].replace('\n', ' ')) for m in re.finditer(pat, txt)]
print('正文可见代号命中', len(hits))
for h in hits:
    print(' ', h[0], '|', h[1])
print('正文可见字数（去空白）', len(re.sub(r'\s', '', txt)))
