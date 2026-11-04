import re, html
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'

def text(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '\n', s)
    s = html.unescape(s)
    return re.sub(r'\n\s*\n+', '\n', s)

rep = open(BASE + '决策汇报.html', encoding='utf-8').read()
t = text(rep)
cut = t.find('更正记录（顶部总结论')
body = t[:cut] if cut > 0 else t
print('汇报正文长度', len(body), '更正记录起点', cut)
for kw in ['都是按上面的诊断推出来的', '其余照原设计', 'A、B、C 按推荐', '怎么回复', '统一后台（07）要开发', '推送定向要不要开发',
           '本节是问题诊断之前写的', '按原设计推进', '已可交研发', '可提交', '建议照原设计', '照原设计']:
    idx = [m.start() for m in re.finditer(re.escape(kw), body)]
    print(f'[{kw}] 正文命中 {len(idx)}')
    for i in idx:
        print('    …' + body[max(0, i-60):i+80].replace('\n', ' ⏎ ') + '…')

# 顶部总结论
m = re.search(r'现状：普卡.*?月储值——.*?。', t, flags=re.S)
print('\n顶部总结论：', m.group(0) if m else '未找到')

# 各节标题与提示的位置关系
for h in ['三 · 方案', '四 · 进度与卡点', '五 · 需要你决定']:
    i = body.find(h)
    print('\n', h, '→', body[i:i+260].replace('\n', ' ⏎ ') if i >= 0 else '未找到')

# 存档框 / details 里是否还残留回复模板
for d in re.findall(r'<details.*?</details>', rep, flags=re.S):
    dt = text(d)
    if '怎么回复' in dt or '其余照原设计' in dt:
        print('\n[details 内残留]', dt[:200].replace('\n', ' ⏎ '))

# 环节2：折叠框条目顺序 vs section 顺序
e2 = open(BASE + '环节2_问题诊断.html', encoding='utf-8').read()
ids = re.findall(r'<section[^>]*id="([^"]+)"', e2)
allids = set(re.findall(r'id="([^"]+)"', e2))
print('\n环节2 section 顺序：', ids)
i = e2.find('各节一句话')
j = e2.find('</details>', i)
box = e2[i:j]
hrefs = re.findall(r'href="#([^"]+)"', box)
print('折叠框链接顺序：', hrefs)
print('折叠框缺失锚点：', [h for h in hrefs if h not in allids])
items = re.findall(r'<li[^>]*>(.*?)</li>', box, flags=re.S)
print('折叠框条数：', len(items))
for it in items:
    print('  -', text(it).replace('\n', '')[:70])
mt = re.search(r'逻辑链第 2 环[^<]*', e2)
print('\nmeta：', mt.group(0) if mt else '未找到')
