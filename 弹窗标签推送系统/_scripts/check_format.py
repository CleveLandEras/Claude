"""阶段产出格式检查（过审硬条件之一，见 归档/规则_旧/阶段产出格式规范.md 第五节 A）。不带参数运行，检查根目录全部 阶段N_*.html。
有任何 ✘ 即「不通过」。⚠ 为提醒，不阻塞。"""
import os, re, glob, html as H
from _textify import BASE

def text(s):
    s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    return H.unescape(re.sub(r'<[^>]+>', '', s)).strip()

plan = open(os.path.join(BASE, '阶段产出规划.html'), encoding='utf-8').read()
STRUCT = {}
for m in re.finditer(r'<tr><td>(\d)(?:<br>.*?)?</td>(.*?)</tr>', plan, re.S):
    STRUCT[m.group(1)] = re.findall(r'<li><b>([^<]+)</b>', m.group(2))

def check(path):
    s = open(path, encoding='utf-8').read()
    name = os.path.basename(path)
    n = re.match(r'阶段(\d)', name).group(1)
    body = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    res = []
    def add(ok, item, detail=''):
        res.append(('✔' if ok is True else ('⚠' if ok == 'warn' else '✘'), item, detail))
    add('阶段产出模板样式' in s, '1 使用模板样式')
    h1 = re.findall(r'<h1[^>]*>(.*?)</h1>', body, re.S)
    add(bool(re.search(r'<p class="meta"', body)) and len(h1) == 1 and '待写' not in ''.join(h1), '2 meta 行、唯一 h1、无占位',
        '' if len(h1) == 1 else f'h1 数量 {len(h1)}')
    add(bool(re.search(r'class="(core|tree|summary)"', body)), '3 首屏有核心内容区（核心表、层级总览或摘要）')
    secs = re.findall(r'<section class="sec"[^>]*>(.*?)</section>', body, re.S)
    bad = []
    h2s = []
    for sec in secs:
        h2 = re.search(r'<h2[^>]*>(.*?)</h2>', sec, re.S)
        t = text(h2.group(1)) if h2 else ''
        h2s.append(t)
        if not re.search(r'class="sec-no"', sec) or not h2 or '：' not in t or len(t.split('：', 1)[1]) < 6:
            bad.append(t[:20] or '（无 h2）')
    add(len(secs) >= 3 and not bad, '4 至少 3 节；每节有编号和「节名：结论」式 h2', '；'.join(bad))
    want = STRUCT.get(n, [])
    heads = [x.split('：', 1)[0] for x in h2s]
    missing = [w for w in want if not any(w in h for h in heads)]
    order = [next((i for i, h in enumerate(heads) if w in h), -1) for w in want if w not in missing]
    add(not missing and order == sorted(order), '5 节名与规划表「结构」一一对应、顺序一致',
        ('缺：' + '、'.join(missing)) if missing else ('' if order == sorted(order) else '顺序与规划表不一致'))
    if n not in ('7', '8'):
        add(any('关键假设' in h for h in heads), '6 有「关键假设」节')
    add('待写' not in text(body), '7 无「待写」占位')
    vis = text(re.sub(r'href="[^"]*"', '', body))
    codes = sorted(set(re.findall(r'(?<![A-Za-z0-9])(?:Q\d{3}|R\d{3}|K\d{2,3}|A\d{1,2})(?![0-9_])', vis)))
    add(not codes, '8 正文无内部编号', '、'.join(codes[:8]))
    long_cells, warn_cells = [], []
    for c in re.findall(r'<td[^>]*>(.*?)</td>', body, re.S):
        t = text(re.sub(r'<span class="src">.*?</span>', '', c, flags=re.S))
        if len(t) > 140: long_cells.append(t[:18] + '…')
        elif len(t) > 100: warn_cells.append(t[:18] + '…')
    add(not long_cells, '9 单元格不超过 140 字', '；'.join(long_cells[:5]))
    if warn_cells: add('warn', '   单元格超过 100 字（建议拆短）', '；'.join(warn_cells[:5]))
    walls = []
    for cls, p in re.findall(r'<p(?: class="([^"]*)")?[^>]*>(.*?)</p>', body, re.S):
        if cls in ('meta', 'links'): continue
        t = text(p)
        if len(t) > 200: walls.append(f'{cls or "p"}:' + t[:16] + '…')
    add(not walls, '10 无文字墙（段落不超过 200 字）', '；'.join(walls[:5]))
    broken = []
    for h in re.findall(r'href="([^"#][^"]*)"', body):
        if h.startswith('http'): continue
        if not os.path.exists(os.path.join(BASE, H.unescape(h.split('#')[0]))): broken.append(h)
    add(not broken, '11 本地链接都能打开', '、'.join(broken[:5]))
    # 12 首屏核心＋节标题阅读量（Dk 10/8 认可 3 分钟版：「好很多了」；10/9：「昨天就应该做好的」）
    i = body.find('<h1'); j = body.find('<section class="sec"')
    first = text(body[i:j] if j > i else '') + ' ' + ' '.join(h2s)
    nfirst = len(re.findall(r'[\u4e00-\u9fff]', first))
    add(nfirst <= 1000, '12 首屏核心＋节标题约 3 分钟读完（不超过 1000 字）', f'现在 {nfirst} 字')
    if 900 < nfirst <= 1000: add('warn', '   首屏接近上限', f'{nfirst} 字')
    # 13 明细折叠：全文超过 3000 字时，各节正文放进 details.more
    nall = len(re.findall(r'[\u4e00-\u9fff]', text(body)))
    folded = sum(1 for sec in secs if '<details class="more"' in sec)
    add(nall <= 3000 or folded >= max(1, len(secs) - 1), '13 明细默认折叠（全文超过 3000 字时各节用「展开」）', f'全文 {nall} 字，折叠 {folded}/{len(secs)} 节')
    return name, res

any_fail = False
for p in sorted(glob.glob(os.path.join(BASE, '阶段[0-9]*.html'))):
    name, res = check(p)
    fail = any(r[0] == '✘' for r in res)
    any_fail |= fail
    print(f'== {name}：{"不通过" if fail else "通过"}')
    for mark, item, detail in res:
        print(f'  {mark} {item}' + (f'　〔{detail}〕' if detail and mark != '✔' else ''))
print('结论：' + ('有不通过的文件，按 ✘ 项修改' if any_fail else '全部通过机器检查；过审还需人工检查（格式规范第五节 B）'))
