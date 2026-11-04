#!/usr/bin/env python3
# 把需求评审版源.html 转成 4_需求文档.md；第 2、3、5-8 章读 分章/ 下文件。可反复跑。
import re, html, os, sys
from html.parser import HTMLParser

D = '/Users/decheng.huang/claude/弹窗标签推送系统/评审版_定稿改_1027/推送系统后台集成需求/'
F = '/Users/decheng.huang/claude/_底座/任务/弹窗标签推送系统/2026-11-04_需求文档/分章/'
SRC = D + '需求评审版源.html'
PEND = D + '研发评审待确认.md'
OUT = D + '4_需求文档.md'

class T(HTMLParser):
    def __init__(s): super().__init__(); s.o = []
    def handle_data(s, d): s.o.append(d)
    def handle_starttag(s, t, a):
        if t == 'br': s.o.append(' ')
def txt(h):
    p = T(); p.feed(h); p.close()
    return re.sub(r'\s+', ' ', ''.join(p.o)).strip()

src = open(SRC, encoding='utf-8').read()

# ---- 待确认表 ----
rows = {}   # n -> (问题, 出处文字)
secs = []
cur = ''
for ln in open(PEND, encoding='utf-8'):
    if ln.startswith('## '): cur = ln.strip()
    m = re.match(r'\|\s*(\d+)\s*\|(.*)\|\s*$', ln)
    if m:
        c = [x.strip() for x in m.group(2).split('|')]
        rows[int(m.group(1))] = c
def pages_of(n):
    c = rows[n]; ps = set()
    ref = c[1] if len(c) > 1 else ''
    for m in re.finditer(r'第\s*([\d、，, ]+?)\s*页', ref):
        ps |= {int(x) for x in re.findall(r'\d+', m.group(1))}
    if not ps:
        if re.search(r'会员标签|群组', ref): ps.add(1)
        if re.search(r'新建推播', ref): ps |= {1, 2}
        if re.search(r'快显', ref): ps.add(5)
        if re.search(r'弹窗|活动或礼包', ref): ps.add(4)
    return ps
page_pend = {p: sorted(n for n in rows if p in pages_of(n)) for p in range(1, 11)}

# ---- 无编号的“待研发确认” ----
unmatched = []
def bg(s): s = re.sub(r'[\s，。、；：（）「」\d]', '', s); return {s[i:i+2] for i in range(len(s)-1)}
KEEP = [('数值范围（暂按，待研发确认）','数值范围（暂按，待研发确认，待确认清单暂无此条）'),
 ('暂按，待研发确认客户端能否在大厅直接弹事件类弹窗）','暂按，待研发确认客户端能否在大厅直接弹事件类弹窗，待确认清单暂无此条）'),
 ('暂按 100,000 条，待研发确认）','暂按 100,000 条，待研发确认，待确认清单暂无此条）')]
def fix_pending(t, page, where):
    hold = {}
    for i, (a, b) in enumerate(KEEP):
        if a in t: t = t.replace(a, '\x00%d\x00' % i); hold[i] = b
    r = _fix(t, page, where)
    for i, b in hold.items(): r = r.replace('\x00%d\x00' % i, b)
    return r
def _fix(t, page, where):
    t = re.sub(r'待研发确认，?\s*[（(]?见?研发评审待确认第\s*(\d+)\s*条[）)]?', r'待研发确认第 \1 条', t)
    def rep(m):
        a, b = m.start(), m.end()
        ctx = t[max(0, a-60):a]
        ctx = ctx[ctx.rfind('。')+1:] + t[b:b+30].split('。')[0]
        best, bs = None, 0
        for n in page_pend.get(page, []):
            sc = len(bg(ctx) & bg(rows[n][0] + rows[n][1]))
            if sc > bs: best, bs = n, sc
        if best and bs >= 6:
            return '待研发确认第 %d 条' % best
        unmatched.append((where, t[max(0, a-20):b+20], best, bs))
        return m.group(0)
    return re.sub(r'待研发确认(?!第)', rep, t)

# ---- 转换 ----
def rules_md(block, page, where):
    out = ['#### 业务规则', '']
    for part in re.split(r'(?=<h4 class="rg">)', block):
        m = re.match(r'<h4 class="rg">(.*?)</h4>', part, re.S)
        if not m: continue
        out += ['##### ' + txt(m.group(1)), '']
        for tb in re.findall(r'<table.*?</table>', part, re.S):
            trs = [[txt(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)] for tr in re.findall(r'<tr>(.*?)</tr>', tb, re.S)]
            if all(len(r) == 1 for r in trs):
                for r in trs: out.append('- ' + fix_pending(r[0], page, where))
            else:
                w = max(len(r) for r in trs)
                trs = [r + [''] * (w - len(r)) for r in trs]
                f = lambda r: '| ' + ' | '.join(fix_pending(c, page, where).replace('|', '\\|') for c in r) + ' |'
                out += [f(trs[0]), '|' + '---|' * w] + [f(r) for r in trs[1:]]
            out.append('')
    return out

def figs(block, page, where, label):
    out = []
    for m in re.finditer(r'<h3 class="sg">(.*?)</h3>|<figure>(.*?)</figure>', block, re.S):
        if m.group(1) is not None:
            out += ['#### ' + txt(m.group(1)), '']; continue
        f = m.group(2)
        alt = re.search(r'alt="([^"]*)"', f).group(1)
        st = re.search(r'<div class="stt[^>]*>(.*?)</div>', f, re.S)
        cap = txt(re.search(r'<figcaption>(.*?)</figcaption>', f, re.S).group(1))
        name = alt + ('（' + txt(st.group(1)) + '）' if st else '')
        out += ['**界面：%s**（%s）' % (name, label), '', fix_pending(cap, page, where), '']
        stats['figs'] += 1
    return out

stats = {'figs': 0, 'rules': 0, 'tr': 0, 'sections': 0}
secs_html = re.findall(r'<section[^>]*>.*?</section>', src, re.S)
stats['sections'] = len(secs_html)
ch4, trace = ['## 4 功能说明', ''], []
for sec in secs_html:
    h2 = txt(re.search(r'<h2>(.*?)</h2>', sec, re.S).group(1))
    pm = re.search(r'id="p(\d+)"', sec)
    if not pm:
        where, label = '4.0', '见原型后台首页'
        ch4 += ['### 4.0 ' + h2 + '（后台结构，不属于某一页）', '']
        ch4 += figs(sec, 0, where, label)
        ch4 += ['| 菜单分组 | 菜单项 | 页签 | 页码 |', '|---|---|---|---|']
        for g in re.findall(r'<div class="sgp[^>]*>.*?</div></div>(?=\s*<div class="sgp|\s*</div>\s*</section>)', sec, re.S):
            gn = txt(re.search(r'<div class="sgn">(.*?)</div>', g, re.S).group(1))
            for r in re.findall(r'<div class="sr">.*?</span></div>', g, re.S):
                nm = txt(re.search(r'<b>(.*?)</b>', r).group(1))
                tb = re.search(r'<span class="tb">(.*?)</span><span class="pp">', r, re.S)
                tabs = ('、'.join(txt(x) for x in re.findall(r'<i>(.*?)</i>', tb.group(1))) or '—') if tb else '—'
                pg = '；'.join(txt(a) for a in re.findall(r'<a[^>]*>(.*?)</a>', r, re.S))
                ch4.append('| %s | %s | %s | %s |' % (gn, nm, tabs, pg))
        ch4 += ['']
        continue
    p = int(pm.group(1)); where = '4.%d' % p; label = '见原型第 %d 页' % p
    ch4 += ['### 4.%d %s（原型第 %d 页）' % (p, h2, p), '']
    shots = sec.split('<details')[0]
    ch4 += figs(shots, p, where, label)
    names = [txt(x) for x in re.findall(r'alt="([^"]*)"', shots)]
    d = re.search(r'<details.*?</details>', sec, re.S).group(0)
    nr = len(re.findall(r'<h4 class="rg">', d)); stats['rules'] += nr
    stats['tr'] += len(re.findall(r'<tr>', d))
    ch4 += rules_md(d, p, where)
    pe = page_pend[p]
    ch4 += ['本页相关待确认：' + ('、'.join('第 %d 条' % n for n in pe) if pe else '无'), '']
    trace.append((p, h2, '、'.join(names), '、'.join(txt(x) for x in re.findall(r'<h4 class="rg">(.*?)</h4>', d)), ('、'.join(str(n) for n in pe) or '无')))

# 第 9 章：原样带编号
pend_raw = open(PEND, encoding='utf-8').read()
body = pend_raw.split('\n', 1)[1].lstrip('\n').replace('命中方式「轮流」', '命中方式「依次换用」').replace('需求评审稿（`需求评审版源.html`）','需求评审稿（原型的业务规则）')
ch9 = ['## 9 评审时请确认', '', body.replace('\n## ', '\n### ').rstrip(), '']
ch10 = ['## 10 追溯表', '', '| 页码 | 标题 | 界面（图说明） | 规则小节 | 相关待确认 |', '|---|---|---|---|---|']
for p, h, f, r, pe in trace: ch10.append('| 第 %d 页 | %s | %s | %s | %s |' % (p, h, f, r, pe))
ch10.append('')

def chap(n, title):
    fp = F + '%d.md' % n
    if os.path.exists(fp):
        t = open(fp, encoding='utf-8').read().strip()
        return [t if t.startswith('## ') else '## %d %s\n\n%s' % (n, title, t), '']
    return ['## %d %s' % (n, title), '', '（未写）', '']

head = ['# 推送系统后台集成需求文档', '',
 '| 项目 | 内容 |', '|---|---|',
 '| 需求名称 | 推送系统后台集成 |',
 '| 对应原型 | `3_原型_需求评审版.html`（第 1–10 页） |',
 '| 说明 | 页面上的数字只作示例；全文时间均为台湾时间 |', '',
 '## 文档结构与模块索引', '',
 '1 修改记录；2 需求背景；3 需求目标；4 功能说明（4.0 后台结构，4.1–4.10 对应原型第 1–10 页）；5 后台需求（字段表）；6 资源需求；7 验收标准；8 范围分级；9 评审时请确认；10 追溯表。', '',
 '## 1 修改记录', '', '| 日期 | 说明 |', '|---|---|',
 '| 11/04 | 按 16:08 版原型重写；旧稿对旧原型写，不再用。 |', '']
out = head + chap(2, '需求背景') + chap(3, '需求目标') + ch4 + chap(5, '后台需求') + chap(6, '资源需求') + chap(7, '验收标准') + chap(8, '范围分级') + ch9 + ch10
open(OUT, 'w', encoding='utf-8').write('\n'.join(out))

# ---- 核对 ----
print('section', stats['sections'], '图说', stats['figs'], '规则小节', stats['rules'], 'tr(规则表)', stats['tr'],
      '源文件 tr', len(re.findall(r'<tr>', src)), '源 h4', len(re.findall(r'<h4', src)))
c4 = '\n'.join(ch4)
src_text = sum(len(txt(x)) for x in re.findall(r'<figcaption>.*?</figcaption>|<td>.*?</td>|<h4 class="rg">.*?</h4>', src, re.S))
md_text = len(re.sub(r'\s', '', c4))
print('第4章字数(去空白)', md_text, '源正文(图说+td+h4,去标签)', len(re.sub(r'\s', '', ''.join(txt(x) for x in re.findall(r'<figcaption>.*?</figcaption>|<td>.*?</td>|<h4 class="rg">.*?</h4>', src, re.S)))))
print('待确认未配编号:')
for u in unmatched: print(' ', u)
for w in ['先按场景', '注册后第一次', '按人交接', '负责人', '优先级被改', '建实验', '加进更多规则', '保存冲突', '轮流', '每 X 天', '场景·发送对象']:
    for m in re.finditer(w, '\n'.join(out)): print('禁词', w, ''.join(out)[max(0, m.start()-15):m.end()+15].replace('\n', ' '))
