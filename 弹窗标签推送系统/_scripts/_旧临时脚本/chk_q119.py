"""Q119 自查：标签配对、锚点顺序、首屏与交主管块禁用词、a 链接目标是否存在。只读，不带参数。"""
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
t = open(p, encoding='utf-8').read()
for tag in ['div', 'details', 'summary', 'table', 'tr', 'p', 'pre', 'ol', 'li', 'section']:
    o = len(re.findall(rf'<{tag}[\s>]', t))
    c = len(re.findall(rf'</{tag}>', t))
    print(f'{tag}: 开 {o} 闭 {c}', '' if o == c else '  <-- 不平衡')
ids = re.findall(r'id="([^"]+)"', t)
dup = {i for i in ids if ids.count(i) > 1}
print('重复 id:', dup or '无')
links = set(re.findall(r'href="#([^"]+)"', t))
print('缺失锚点:', sorted(l for l in links if l not in ids) or '无')
for m in re.finditer(r'id="(d\d+|d78|to-boss|to-me|s\d)"', t):
    h = re.search(r'<h[23][^>]*>(.*?)</h[23]>', t[m.end(): m.end() + 400])
    print(f'{m.start():>7} {m.group(1):<9}', re.sub(r'<[^>]+>', '', h.group(1))[:60] if h else '')
i0 = t.index('<div class="verdict plain">')
i1 = t.index('<div class="chain">')
top = t[i0:i1]
ib = t.index('<div class="panel" id="to-boss">')
ib2 = t.index('存档：原交主管的一段')
boss = t[ib:ib2]
for w in ['换主线', '首期不交', '首期缩小', '主线换', '盯住高卡', '降级', 'A26']:
    print(f'首屏 {w}: {top.count(w)}；交主管块 {w}: {boss.count(w)}')
print('cp 函数:', re.findall(r'function cp\([^)]*\)\{.*?\}', t, flags=re.S)[:1])
