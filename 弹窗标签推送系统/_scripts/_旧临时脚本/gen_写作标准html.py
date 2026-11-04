"""写作标准 md → html：读 规则与交接/写作标准_合并版.md，生成同目录同名 .html（版面沿用 Dk 10/10 给的 写作标准-2.html）。
改标准只改 md，再运行本脚本：python3 _scripts/_旧临时脚本/gen_写作标准html.py"""
import os, re, html
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(BASE, '规则与交接', '写作标准_合并版.md')
OUT = MD[:-3] + '.html'
CSS = r"""
:root{--text:#1d2129;--muted:#6b7079;--soft:#4a4f57;--line:#e7e6e1;--bg:#f7f7f4;--card:#fff;
--red:#b42318;--blue:#1f4fc9;--blue-bg:#eef3ff;--chip:#efefea}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:32px}
body{margin:0;background:var(--bg);color:var(--text);
font:16px/1.8 -apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",sans-serif}
.layout{display:grid;grid-template-columns:200px minmax(0,1fr);gap:64px;max-width:1440px;margin:0 auto;padding:64px 48px 160px}
nav{position:sticky;top:48px;align-self:start}
nav a{display:flex;justify-content:space-between;gap:8px;padding:5px 10px;border-radius:6px;color:var(--muted);text-decoration:none}
nav a:hover{background:var(--chip);color:var(--text)}
nav a.sub{padding-left:24px}
nav a .num{color:#a3a7ad}
nav a.alert{color:var(--red);font-weight:600}
nav a.alert .num{color:var(--red)}
h1{font-size:26px;line-height:1.4;margin:0}
.date{color:var(--muted);margin-top:4px}
h2,summary{font-size:20px;font-weight:700;line-height:1.5}
h2{margin:72px 0 24px}
section:first-of-type h2{margin-top:48px}
h3{font-size:16px;font-weight:700;margin:44px 0 12px;display:flex;gap:10px;align-items:baseline}
.num{color:var(--muted);font-weight:400}
.principles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.p-card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:22px 24px}
.p-card b{display:block;margin-bottom:6px}
.p-card span{color:var(--soft)}
.rules{background:var(--card);border:1px solid var(--line);border-radius:10px}
.rule{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr) 64px;gap:32px;padding:20px 28px;border-top:1px solid var(--line)}
.rule:first-child,.q:first-child,.chg:first-child,.srcrow:first-child{border-top:0}
.ex{color:var(--soft)}
.ex>div{display:flex;gap:12px}
.ex>div+div{margin-top:8px}
.items>div+div{margin-top:4px}
.note{color:var(--muted)}
.tag{flex:none;font-weight:600}
.bad .tag{color:var(--red)}
.good .tag,.new .tag,.sug .tag{color:var(--blue)}
.src{color:#a3a7ad;text-align:right;cursor:default}
.q{display:grid;grid-template-columns:44px minmax(0,1fr) minmax(0,1fr);gap:28px;padding:22px 28px;border-top:1px solid var(--line)}
.q .no{font-weight:700;color:var(--red)}
.basis{color:var(--muted);margin-top:4px}
.q>.basis{margin-top:0}
.sug{background:var(--blue-bg);color:#17378f;border-radius:8px;padding:10px 16px;align-self:start}
.sug .tag{margin-right:10px}
.sug.empty{background:var(--chip);color:var(--muted)}
.opts{margin-top:10px;color:var(--soft)}
.opts>div+div{margin-top:4px}
details{margin-top:72px}
summary{cursor:pointer;list-style:none;display:flex;gap:10px;align-items:baseline;margin-bottom:20px}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸";color:var(--muted);font-weight:400}
details[open] summary::before{content:"▾"}
.chg{padding:20px 28px;border-top:1px solid var(--line)}
.chg .old,.chg .new{display:flex;gap:12px;margin-top:4px}
.chg .old{color:var(--muted)}
.chg .old .tag{color:var(--muted)}
.chg .meta{color:#a3a7ad;margin-top:4px}
.srcrow{display:grid;grid-template-columns:40px minmax(0,1fr);gap:20px;padding:14px 28px;border-top:1px solid var(--line)}
.srcrow span{color:var(--soft)}
.defs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.order{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 28px}
.order ol{margin:0;padding-left:1.4em}
.h3src{margin-left:auto;color:#a3a7ad;font-weight:400}
"""
SRC = {'甲': '记忆记录与账号偏好设置：通行证报告修改过程与决策评审偏好',
       '乙': '《2026-10-09_写作标准汇总》：本机 7 段对话',
       '丙': '《写作标准汇总》：偏好、平台、交接资料、V4／V9',
       '丁': '《写作标准与修改意见汇总》：偏好、平台、通行证、弹窗、交接',
       '戊': '10/9 对待确认项的逐条确认',
       '己': '10/10 对合并后冲突与缺口的取舍决定'}
NOTE = ('丙与丁大量引用同一份偏好记录和平台记录，出处只表示在哪份整理中出现，不代表出现次数。来自甲的引文是记录转述，不是逐字原话。'
        '只来自上级或评审转述、交接文档撰写方推论、agent 起草条文的内容不算我的标准，未收录；经我确认收录的标「己」。'
        '通行证、弹窗等项目的业务结论不属于写作标准，未收录。')
e = html.escape

def split_items(t):
    """按顶层「；」切分，「」内的分号不切"""
    out, buf, depth = [], '', 0
    for ch in t:
        if ch == '「': depth += 1
        elif ch == '」': depth = max(0, depth - 1)
        if ch == '；' and depth == 0:
            out.append(buf); buf = ''
        else:
            buf += ch
    out.append(buf)
    return [x.strip() for x in out if x.strip() and x.strip() != '—']

def src(code):
    return f'<div class="src" title="{e("；".join(SRC[c] for c in code if c in SRC))}">{e(code)}</div>'

def exblock(cls, tag, items):
    if not items: return ''
    return f'<div class="{cls}"><span class="tag">{tag}</span><div class="items">' + ''.join(f'<div>{e(i)}</div>' for i in items) + '</div></div>'

def rule(rt, bad, good, code, goodtag='改成'):
    return (f'<div class="rule"><div class="rt">{e(rt)}</div><div class="ex">' + exblock('bad', '否决', bad) +
            exblock('good', goodtag, good) + f'</div>{src(code)}</div>')

def rows(lines):
    return [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines if l.startswith('|') and not l.startswith('|---')][1:]

# 解析 md：按 ## / ### 切块
text = open(MD, encoding='utf-8').read()
date = re.search(r'^\d{4}-\d{2}-\d{2}$', text, re.M).group(0)
blocks, cur = [], None
for l in text.split('\n'):
    if l.startswith('## ') or l.startswith('### '):
        cur = {'h': l.lstrip('#').strip(), 'lvl': l.count('#', 0, 3), 'lines': []}; blocks.append(cur)
    elif cur is not None:
        cur['lines'].append(l)
title = lambda h: re.sub(r'^[一二三四五六七八九十]+、|^\d+\. ', '', h)

nav, main = [], []
gen_subs, type_subs = [], []
sid = 0
for b in blocks:
    h = title(b['h']); L = b['lines']
    if h == '核心原则':
        # 拆三段：原则表、稿件档位、取舍顺序
        part, parts = 'p', {'p': [], 'd': [], 'o': []}
        for l in L:
            if l.startswith('**稿件档位**'): part = 'd'; continue
            if l.startswith('**规则冲突时的取舍顺序**'): part = 'o'; continue
            parts[part].append(l)
        pr = rows(parts['p'])
        cards = ''.join(f'<div class="p-card"><b>{e(r[0])}</b><span>{e(r[1])}</span></div>' for r in pr)
        defs = ''.join(f'<div class="p-card"><b>{e(r[0])}</b><span>{e(r[1])}</span></div>' for r in rows(parts['d']))
        items = [re.sub(r'^\d+\.\s*', '', l) for l in parts['o'] if re.match(r'^\d+\.', l)]
        order = ''.join(f'<li>{e(i)}</li>' for i in items)
        h3 = lambda t: f'<h3>{t}<span class="h3src" title="{e(SRC["己"])}">己</span></h3>'
        main.append(f'<section id="core"><h2>核心原则</h2><div class="principles">{cards}</div>'
                    f'{h3("稿件档位")}<div class="defs">{defs}</div>'
                    f'{h3("规则冲突时的取舍顺序")}<div class="order"><ol>{order}</ol></div></section>')
        nav.append(('core', '核心原则', len(pr), ''))
    elif h == '通用标准':
        main.append('<section id="general"><h2>通用标准</h2>'); nav.append(('general', '通用标准', None, '')); gen_i = len(nav) - 1
    elif h == '按文档类型的补充规则':
        main.append('</section><section id="types"><h2>按文档类型的补充规则</h2>'); nav.append(('types', '文档类型规则', None, '')); typ_i = len(nav) - 1
    elif h == '协作与交付':
        rs = rows(L)
        main.append('</section><section id="collab"><h2>协作与交付</h2><div class="rules">' +
                    ''.join(rule(r[0], [], split_items(r[1]), r[2], '原话') for r in rs) + '</div></section>')
        nav.append(('collab', '协作与交付', len(rs), ''))
    elif h == '观点变化记录':
        rs = rows(L)
        chg = ''.join(f'<div class="chg"><b>{e(r[0])}</b><div class="old"><span class="tag">旧</span><span>{e(r[1])}</span></div>'
                      f'<div class="new"><span class="tag">现行</span><span>{e(r[2])}</span></div><div class="meta">{e(r[3])} · {e(r[4])}</div></div>' for r in rs)
        main.append(f'<section id="changes"><details><summary>观点变化<span class="num">{len(rs)}</span></summary><div class="rules">{chg}</div></details></section>')
        nav.append(('changes', '观点变化', len(rs), ''))
    elif b['lvl'] == 3:
        sid += 1; rs = rows(L)
        if len(rs[0]) == 4:   # 通用标准：标准｜否决｜改成｜出处
            body = ''.join(rule(r[0], split_items(r[1]), split_items(r[2]), r[3]) for r in rs)
            gen_subs.append(len(rs))
        else:                 # 文档类型：标准｜原句｜出处
            body = ''
            for r in rs:
                if r[1].startswith('否决：'):
                    body += rule(r[0], split_items(r[1][3:]), [], r[2])
                else:
                    body += rule(r[0], [], split_items(r[1]), r[2], '原话')
            type_subs.append(len(rs))
        main.append(f'<h3 id="s{sid}">{e(h)}<span class="num">{len(rs)}</span></h3><div class="rules">{body}</div>')
        nav.append((f's{sid}', h, len(rs), 'sub'))
nav[gen_i] = ('general', '通用标准', sum(gen_subs), '')
nav[typ_i] = ('types', '文档类型规则', sum(type_subs), '')
nav.append(('sources', '出处', None, ''))
srcs = ''.join(f'<div class="srcrow"><b>{k}</b><span>{e(v)}</span></div>' for k, v in SRC.items()) + f'<div class="srcrow"><b></b><span>{e(NOTE)}</span></div>'
main.append(f'<section id="sources"><details><summary>出处</summary><div class="rules srcs">{srcs}</div></details></section>')

navh = ''.join(f'<a class="{c}" href="#{i}"><span>{e(t)}</span>' + (f'<span class="num">{n}</span>' if n is not None else '') + '</a>' for i, t, n, c in nav)
page = ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>报告与方案写作标准</title><style>{CSS}</style>\n<body><div class="layout"><nav>{navh}</nav><main>\n'
        f'<h1>报告与方案写作标准</h1><div class="date">{date}</div>\n' + ''.join(main) + '\n</main></div></body></html>\n')
open(OUT, 'w', encoding='utf-8').write(page)
print('写入', OUT, len(page), '字节')
