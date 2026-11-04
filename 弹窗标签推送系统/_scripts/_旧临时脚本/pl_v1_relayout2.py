"""一次性：呈交版阅读体验二次调整（Dk 10/9「稍有点紧凑，看的还是吃力……看得省力，还有节省阅读时间」）。
只改排法与样式，不改文字：放大留白与字号、收窄行宽；改动按短期／中期／长期分组；证据里的数字加粗；
首屏总览的长句拆成标签；各节标注大约阅读时间。原稿备份：_versions/呈交版_版面重排2前_1009.html。"""
import os, re, math
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(BASE, '弹窗标签推送方案_V1.html')
s = open(P, encoding='utf-8').read()

# ---------- 1. 改动按层分组 ----------
TIER = {'t1': ('短期', '现有后台即可做，无需开发'), 't2': ('中期', '后台加字段、开关或汇总'), 't3': ('长期', '较大开发')}
row = re.compile(r'<div class="cr ([a-z ]+)"><span class="ty">(.*?)</span><b>(.*?)</b><span class="ef">(.*?)</span></div>', re.S)
def regroup(m):
    body = m.group(1)
    rows = row.findall(body)
    if not rows or not re.search(r'<i class="lv t\d">', body):
        return m.group(0)                      # 验收清单没有层级，原样保留
    assert len(rows) == len(re.findall(r'<div class="cr ', body))
    groups = {'t1': [], 't2': [], 't3': []}
    for cls, ty, name, ef in rows:
        t = re.search(r'<i class="lv (t\d)">.*?</i>', ef).group(1)
        ef = re.sub(r'<i class="lv t\d">.*?</i>', '', ef).strip()
        groups[t].append(f'<div class="cr {cls}"><span class="ty">{ty}</span><div class="cx"><b>{name}</b><span class="ef">{ef}</span></div></div>')
    out = ['<div class="crs grouped">']
    for t in ('t1', 't2', 't3'):
        if groups[t]:
            nm, note = TIER[t]
            out.append(f'<div class="tg {t}"><div class="tgh"><span>{nm}</span><em>{note} · {len(groups[t])} 项</em></div>' + ''.join(groups[t]) + '</div>')
    out.append('</div></div>')
    return ''.join(out)
s = re.sub(r'<div class="crs">(.*?)</div></div>', regroup, s, flags=re.S)

# ---------- 2. 首屏总览：长句拆成标签 ----------
def chips(m):
    cls, inner = m.group(1), m.group(2)
    text, tail = (inner.split('<s>', 1) + [''])[:2]
    tail = ('<s>' + tail) if tail else ''
    if text.strip() in ('—', ''):
        return m.group(0)
    parts = [p.strip() for p in text.split('；') if p.strip()]
    return f'<span class="{cls}"><span class="chips">' + ''.join(f'<i>{p}</i>' for p in parts) + f'</span>{tail}</span>'
ov = re.search(r'<div class="ov2">.*?<div class="ovn">', s, re.S)
seg = re.sub(r'<span class="(s|l)">(.*?)</span>(?=<span class="l">|</a>)', chips, ov.group(0), flags=re.S)
s = s[:ov.start()] + seg + s[ov.end():]

# ---------- 3. 证据里的数字加粗 ----------
NUM = re.compile(r'(\d[\d,]*(?:\.\d+)?\s?(?:%|人|个|项|天|条|次|倍|类|行))')
def bold_li(m):
    inner = m.group(1)
    parts = re.split(r'(<[^>]+>)', inner)
    parts = [p if p.startswith('<') else NUM.sub(r'<b class="num">\1</b>', p) for p in parts]
    return '<li>' + ''.join(parts) + '</li>'
def bold_fx(m):
    return re.sub(r'<li>(.*?)</li>', bold_li, m.group(0), flags=re.S)
s = re.sub(r'<ul class="fx">.*?</ul>', bold_fx, s, flags=re.S)

# ---------- 4. 样式：放大留白、收窄行宽、分组样式 ----------
EXTRA = r"""
/* —— 阅读体验二次调整 —— */
body{font-size:16px;line-height:1.85}
.home,.doc{max-width:800px}
@media (min-width:1180px){ .home,.doc{margin-left:max(240px,calc(50% - 360px))!important} }
.hrow{margin:0 0 84px}
.hlab{margin:0 0 28px}
.hlab span.rt{margin-left:auto;font-size:12.5px;color:var(--mute);background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:1px 10px}
.guide{font-size:13.5px;color:var(--ink2);background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;margin:0 0 30px}
.guide b{color:var(--ink)}
.hero-h{font-size:24px;line-height:1.6;margin:0 0 24px}
.caps{gap:10px;margin:0 0 24px}
.cap{padding:12px 14px}
.hero-g{gap:14px;margin:0 0 20px}
.hb{padding:16px 18px}
.acc3 li{margin:0 0 10px}
.pbk{padding:30px 32px 24px;margin:0 0 32px}
.pbk>header{margin:0 0 22px}
.pbk h3{font-size:20px;line-height:1.55}
.ev{gap:28px;margin:0 0 24px}
.evf{padding:18px 20px}
.fx li{font-size:15px;line-height:1.8;margin:0 0 14px;padding-left:18px}
.fx li b.num{color:var(--ink);font-weight:700}
.chg{padding:20px 0 0}
.ck2{margin:0 0 12px}
.crs.grouped{display:flex;flex-direction:column;gap:12px}
.tg{border-radius:10px;padding:4px 16px 6px;border-left:4px solid var(--line);background:var(--soft)}
.tg.t1{border-left-color:var(--t1)} .tg.t2{border-left-color:var(--t2)} .tg.t3{border-left-color:var(--t3)}
.tgh{display:flex;align-items:baseline;gap:10px;padding:10px 0 6px}
.tgh span{font-weight:700;font-size:14.5px}
.tg.t1 .tgh span{color:var(--t1)} .tg.t2 .tgh span{color:var(--t2)} .tg.t3 .tgh span{color:var(--t3)}
.tgh em{font-style:normal;font-size:12.5px;color:var(--mute)}
.grouped .cr{grid-template-columns:48px 1fr;padding:10px 0;border-bottom:1px solid var(--line)}
.grouped .cr:last-child{border-bottom:none}
.cx b{display:block;font-size:15px;line-height:1.55}
.cx .ef{display:block;font-size:13.5px;color:var(--mute);line-height:1.65;margin-top:2px}
.ov2 .oh,.ov2>a{gap:16px;padding:16px 18px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chips i{font-style:normal;font-size:13px;line-height:1.5;background:var(--soft);border:1px solid var(--line);border-radius:6px;padding:2px 8px;color:var(--ink2)}
.ov2 .s s,.ov2 .l s{margin-top:8px}
details.pf>summary{padding:16px 0 4px}
.pfb{gap:18px;padding:16px 0 6px}
.dl2{gap:8px 16px}
.opts{gap:14px;margin:0 0 20px}
.opt{padding:16px 18px}
details.apx>summary{padding:15px 18px}
.layer{margin:0 0 34px}
@media (max-width:860px){
  .ov2>a{gap:8px 12px}
}
@media (max-width:560px){
  body{font-size:16px}
  .hrow{margin:0 0 64px}
  .pbk{padding:22px 18px 18px}
  .hero-h{font-size:21px}
  .tg{padding:2px 12px 4px}
}
"""
s = s.replace('</style>', EXTRA + '</style>', 1)

open(P, 'w', encoding='utf-8').write(s)

# ---------- 5. 各节阅读时间（按正文可见字数，折叠明细不计，每分钟约 400 字） ----------
def visible_chars(html):
    html = re.sub(r'<details.*?</details>', '', html, flags=re.S)
    html = re.sub(r'<(style|script)\b.*?</\1>', '', html, flags=re.S)
    txt = re.sub(r'<[^>]+>', '', html)
    return len(re.sub(r'\s', '', txt))
s = open(P, encoding='utf-8').read()
hrows = [(m.start(), m.group(0)) for m in re.finditer(r'<div class="hrow[^"]*"[^>]*>', s)]
mins = {}
for k, (pos, tag) in enumerate(hrows):
    end = hrows[k + 1][0] if k + 1 < len(hrows) else s.find('<!-- ══ 附录 ══ -->')
    chunk = s[pos:end]
    lab = re.search(r'<div class="hlab"><b>(.*?)</b>', chunk).group(1)
    n = visible_chars(chunk)
    mins[lab] = n
def fmt(n):
    m = n / 400
    return '不到 1 分钟' if m < 1 else f'约 {math.ceil(m)} 分钟'
for lab, n in mins.items():
    if lab == '附录':
        continue
    s = re.sub(rf'(<div class="hlab"><b>{re.escape(lab)}</b><span>[^<]*</span>)', rf'\1<span class="rt">{fmt(n)}</span>', s, count=1)
total = sum(n for lab, n in mins.items() if lab != '附录')
guide = (f'<p class="guide"><b>读法</b>：首屏「结论」{fmt(mins.get("结论", 0))}读完；五个问题各一张卡片，标题就是结论，'
         f'只看标题和加粗数字也能抓住要点；改动按短期、中期、长期分组；明细和附录需要时再展开。正文合计{fmt(total)}。</p>')
s = s.replace('<div class="home" id="home">', '<div class="home" id="home">\n' + guide, 1)
open(P, 'w', encoding='utf-8').write(s)
print({k: v for k, v in mins.items()}, 'total', total)
