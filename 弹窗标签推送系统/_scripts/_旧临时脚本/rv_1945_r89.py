# 只读：审查 19:36 轮核对 R87/R88/R89
import re, os, glob, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'

def text(p):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<(script|style)[\s\S]*?</\1>', '', s)
    s = re.sub(r'<br\s*/?>|</(p|div|li|tr|td|th|h\d|summary|section)>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return [l.strip() for l in s.split('\n') if l.strip()]

files = [B+'决策汇报.html', B+'环节1_现状盘点.html'] + glob.glob(B+'支撑文件/*.md') + glob.glob(B+'支撑文件/*.html') + glob.glob(B+'分析/*.md') + [B+'先看这里.md']
terms = ['保级看什么', '不是账号累计值', '「看多长时间」一并问', '升级、保级看的储值和押注', '卡别会不会降级']
for t in terms:
    print('=== ', t)
    for f in files:
        if not os.path.exists(f):
            continue
        L = text(f) if f.endswith('.html') else [l for l in open(f, encoding='utf-8').read().split('\n')]
        for i, l in enumerate(L):
            if t in l:
                k = l.find(t)
                print('  ', os.path.basename(f), i, '…', l[max(0, k-60):k+60])

# 环节1 更正记录：按条号列出依据
L = text(B+'环节1_现状盘点.html')
start = None
for i, l in enumerate(L):
    if l.startswith('更正记录（70 条'):
        start = i
print('=== 环节1 更正记录起点', start)
seg = L[start:]
rows = {}
i = 0
while i < len(seg):
    if re.fullmatch(r'\d{1,2}', seg[i]) and i+4 < len(seg):
        n = int(seg[i])
        if n not in rows:
            rows[n] = (seg[i+1][:40], seg[i+4][:60])
        i += 5
    else:
        i += 1
for n in [4, 10, 18, 22, 25, 60, 24, 68, 69, 7, 33, 34, 59, 6, 40, 42, 43, 57, 58, 62, 8, 52, 53, 54]:
    print(n, rows.get(n))
print('rows found', len(rows), max(rows) if rows else None)

# 汇报 更正记录
L = text(B+'决策汇报.html')
for i, l in enumerate(L):
    if l.startswith('更正记录（第一节与附录'):
        print('\n'.join(L[i:i+45]))
# 锚点
s = open(B+'环节1_现状盘点.html', encoding='utf-8').read()
print('id=u4d', 'id="u4d"' in s, 'href="#u4d"', s.count('href="#u4d"'))
