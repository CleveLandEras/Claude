#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
追链.py  弹窗来源链：任务 T → 功能清单行 清N → 分析卡字段 → 控件 → 框架节点 / 源.html 行 / 面包板行 / 走查步

用法（本夹/程序/ 下）：
  python3 追链.py 全表            打印来源链索引（同 本夹/来源链索引.md 的表）
  python3 追链.py 上游 编号        编号可以是 字段(B1-F03)／控件(P4-05)／清单行(清12 或 12)／任务(T7)／框架行(框L239)
  python3 追链.py 下游 编号        同上，列出所有被它连带的下游
  python3 追链.py 自检            断链检查 + 第 0 步「删掉新列后与 第0步前 逐字相同」检查
  python3 追链.py 写索引          重写 本夹/来源链索引.md
  python3 追链.py 加编号 [--试]    第 0 步：从 改前底本/第0步前/ 复制出发，给 9 个文件只加列（--试＝只打印不写）

编号规则（思考页第 6 节第 5 条）：任务 T1–T34、清单「清N」沿用；字段「卡-F两位」（B1-F03）；
  入口 卡-E n（卡 C 的入口①②③）；规则 卡-R n；异常 卡-X n；卡里第 n 栏（第 n 节）卡-S n；
  控件沿用 G-01、P1-01；框架节点「框L行号」（行号随框架改动而变，以改前底本为准）；源.html「源L行号」；面包板「板L行号」；走查「步 n」。
  卡 A 里四张子卡分别是 A1 A2 A3 A4。

链的存放：
  卡字段表首列「编号」（本程序写入）；功能清单第一节末列「对应字段」；控件回指表末列「字段编号」。
  三处都是只加列，删掉新列即是 第0步前 的原文。名字对不上、靠人对的记在 人工对.json，索引里标「人工对」。
  框架行是按字段名在框架弹窗段里找的（找不到的在 人工对.json「框架」里指定），不写进框架文件。
"""
import re, sys, os, json, glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEN = HERE.parent
ORIG = Path.home() / 'claude/_底座/任务/弹窗标签推送系统/2026-10-30_弹窗按六步重排'
DIG = ORIG / '里程碑1_底稿'
FRAME = Path.home() / 'claude/弹窗标签推送系统/评审版_定稿改_1027/推送系统后台集成需求/功能框架_脑图.md'
SRC_HTML = Path.home() / 'claude/弹窗标签推送系统/评审版_定稿改_1027/推送系统后台集成需求/需求评审版源.html'
PRE = BEN / '改前底本/第0步前'
MANUAL = HERE / '人工对.json'

CARD_KEYS = ['A', 'B1', 'B2', 'B3', 'B4', 'B5', 'C']
CODE_RE = re.compile(r'(?<![A-Za-z0-9])((?:A[1-4]|B[1-5]|C)-(?:F\d{2}|E\d+|R\d+|X\d+|X\*|S\d+|D))')
ID_RE = re.compile(r'(?<![A-Za-z0-9])([GP]\d*-\d+)')


def card_file(base, key):
    pat = {'A': '卡A_*.md'}.get(key, f'卡{key}_*.md')
    r = sorted(glob.glob(str(base / pat)))
    return Path(r[0]) if r else None


def rd(p):
    return Path(p).read_text(encoding='utf-8').split('\n')


def cells(l):
    return [c.strip() for c in l.strip().strip('|').split('|')]


def manual():
    if MANUAL.exists():
        return json.loads(MANUAL.read_text(encoding='utf-8'))
    return {'清单对应字段': {}, '回指字段编号': {}, '框架': {}}


def norm(s):
    s = re.sub(r'〔[^〕]*〕', '', s)
    for _ in range(3):
        s = re.sub(r'（[^（）]*）', '', s)
    return re.sub(r'[\s　（）()、，,：:｜|·]', '', s)


def parse_refs(text):
    """从一段文字里取「（功能）清单第 N 行」引用的清单行号"""
    out = []
    for m in re.finditer(r'清单第\s*([0-9、，,–\-～~ 和]+?)\s*行', text):
        for part in re.split(r'[、，,和 ]+', m.group(1)):
            if not part:
                continue
            r = re.split(r'[–\-～~]', part)
            try:
                if len(r) == 2 and r[0] and r[1]:
                    out += list(range(int(r[0]), int(r[1]) + 1))
                elif r[0]:
                    out.append(int(r[0]))
            except ValueError:
                pass
    return out


# ---------------------------------------------------------------- 分析卡
def parse_cards(base):
    """返回 fields, rules, excepts, mentions, tasks
    fields: dict(code, card, name, line, kind, src, file, tline)；兼容有／无「编号」列两种格式（无编号列时按序生成编号）。
    """
    fields, rules, excepts, mentions = [], [], [], []
    tasks = {}
    for key in CARD_KEYS:
        p = card_file(base, key)
        if p is None:
            continue
        L = rd(p)
        cur = key if key != 'A' else None
        sec = 0
        cnt = {}
        xcnt = {}
        in_tbl = None  # (kind, has_code, fcount)
        for i, l in enumerate(L):
            m = re.match(r'^## 卡 (A\d)', l)
            if m:
                cur = m.group(1); sec = 0; in_tbl = None
            m2 = re.match(r'^## (\d+)\.', l) or re.match(r'^\*\*(\d+)\. ', l)
            if m2:
                sec = int(m2.group(1))
            if sec == 1 and cur and '对应任务' not in l and re.search(r'｜.*T\d+', l):
                tasks.setdefault(cur, set()).update(re.findall(r'T\d+', l))
            # 表头
            if l.startswith('|') and i + 1 < len(L) and L[i + 1].startswith('|---'):
                c = cells(l)
                has = c[0] == '编号'
                h = c[1] if has else c[0]
                if h in ('字段名', '入口'):
                    in_tbl = ('F' if h == '字段名' else 'E', has)
                else:
                    in_tbl = None
                continue
            if l.startswith('|---'):
                continue
            if in_tbl and l.startswith('|'):
                c = cells(l)
                kind, has = in_tbl
                k = (cur, kind)
                cnt[k] = cnt.get(k, 0) + 1
                n = cnt[k]
                code = c[0] if has else (f'{cur}-F{n:02d}' if kind == 'F' else f'{cur}-E{n}')
                name = c[1] if has else c[0]
                fields.append(dict(code=code, card=cur, name=name, line=i + 1, kind=kind,
                                   src=c[-1], file=str(p), idx=n))
                for r in parse_refs(c[-1]):
                    mentions.append((r, code, cur, 'src'))
                continue
            in_tbl = None if not l.startswith('|') else in_tbl
            # 规则、异常、去掉的旧设置
            if cur:
                mr = re.match(r'^(\d+)\. ', l)
                if sec == 5 and mr:
                    n = int(mr.group(1))
                    rules.append(dict(code=f'{cur}-R{n}', card=cur, n=n, line=i + 1, text=l))
                    for r in parse_refs(l):
                        mentions.append((r, f'{cur}-R{n}', cur, 'rule'))
                    continue
                if sec == 6 and l.startswith('- '):
                    xcnt[cur] = xcnt.get(cur, 0) + 1
                    n = xcnt[cur]
                    excepts.append(dict(code=f'{cur}-X{n}', card=cur, n=n, line=i + 1, text=l))
                    for r in parse_refs(l):
                        mentions.append((r, f'{cur}-X{n}', cur, 'exc'))
                    continue
                if l.startswith('去掉的旧设置'):
                    for r in parse_refs(l):
                        mentions.append((r, f'{cur}-D', cur, 'drop'))
                    continue
    return fields, rules, excepts, mentions, tasks


# ---------------------------------------------------------------- 功能清单
def parse_list(path):
    L = rd(path)
    rows = {}
    start = None
    for i, l in enumerate(L):
        if l.startswith('| 行 |'):
            start = i; hdr = cells(l)
            continue
        if start is not None and i > start + 1:
            if not l.startswith('|'):
                break
            c = cells(l)
            if re.fullmatch(r'\d+', c[0]):
                d = dict(row=int(c[0]), text=c[1], src=c[2], dest=c[3], why=c[4], tasks=re.findall(r'T\d+', c[5]),
                         cards=c[6], line=i + 1, fields=[])
                if len(c) > 7:
                    d['fields'] = CODE_RE.findall(c[7]); d['fcell'] = c[7]
                rows[d['row']] = d
    return rows


# ---------------------------------------------------------------- 回指表
def parse_ref(path):
    L = rd(path)
    out = []
    start = None
    for i, l in enumerate(L):
        if l.startswith('| 编号 | 原型页 |'):
            start = i; continue
        if start is not None and i > start + 1:
            if not l.startswith('|'):
                break
            c = cells(l)
            d = dict(id=c[0], page=c[1], ctrl=c[2], card=c[3], field=c[4], line=i + 1, codes=[], cell='')
            if len(c) > 5:
                d['cell'] = c[5]; d['codes'] = CODE_RE.findall(c[5])
            out.append(d)
    return out


def split_pairs(card, field):
    cs = [x.strip() for x in card.split('；')]
    fs = [x.strip() for x in field.split('；')]
    if len(cs) != len(fs):
        if len(cs) == 1:
            cs = cs * len(fs)
        else:
            cs = cs + [cs[-1]] * (len(fs) - len(cs))
    return list(zip(cs, fs))


def resolve_label(card, lab, fields, rules, excepts):
    """回指表「卡＋字段」一对 → 编号（找不到返回 None）"""
    nl = norm(lab)
    m = re.match(r'规则第\s*([\d、，,和 ]+)\s*条', lab)
    if m:
        return [f'{card}-R{int(n)}' for n in re.split(r'[、，,和 ]+', m.group(1)) if n]
    m = re.match(r'第\s*(\d+)\s*栏', lab)
    if m:
        return [f'{card}-S{m.group(1)}']
    if lab.startswith('入口') and card == 'C':
        return [f'C-E{"①②③".index(ch) + 1}' for ch in lab if ch in '①②③'] or None
    cand = [f for f in fields if f['card'] == card and f['kind'] == 'F']
    best = None
    for f in cand:
        nf = norm(f['name'])
        if nf == nl:
            return [f['code']]
    for f in cand:
        nf = norm(f['name'])
        if nf and nl and (nl.startswith(nf) or nf.startswith(nl)) and min(len(nf), len(nl)) >= 2:
            if best is None or len(nf) > len(norm(best['name'])):
                best = f
    if best:
        return [best['code']]
    if lab.startswith('异常'):
        key = re.findall(r'[（(]([^）)]*)[）)]', lab)
        ex = [e for e in excepts if e['card'] == card]
        if key:
            words = [w for w in re.split(r'[：:，,、 ]+', key[0]) if len(w) >= 2]
            for e in ex:
                if any(w in e['text'] for w in words):
                    return [e['code']]
        return [f'{card}-X*']
    return None


# ---------------------------------------------------------------- 框架 / 源.html / 面包板 / 走查
def frame_nodes():
    L = rd(FRAME)
    mods = {}
    for i, l in enumerate(L):
        if re.match(r'^  - (弹窗场景设置|弹窗规则列表|新建弹窗规则|活动或礼包的弹窗设置)\s*$', l):
            mods[l.strip()[2:]] = i
    order = sorted(mods.items(), key=lambda kv: kv[1])
    end = None
    last = order[-1][1]
    for j in range(last + 1, len(L)):
        if re.match(r'^  - \S', L[j]):
            end = j; break
    ranges = {}
    for k, (name, s) in enumerate(order):
        e = order[k + 1][1] if k + 1 < len(order) else end
        ranges[name] = (s, e)
    nodes = []
    for i, l in enumerate(L):
        m = re.match(r'^( *)- (.*)$', l)
        if m:
            nodes.append((i + 1, len(m.group(1)) // 2, m.group(2).strip()))
    return nodes, {k: (a + 1, b) for k, (a, b) in ranges.items()}


MODULE_OF = {'A1': '弹窗场景设置', 'A2': '弹窗规则列表', 'B1': '新建弹窗规则', 'B2': '新建弹窗规则',
             'B3': '新建弹窗规则', 'B4': '新建弹窗规则', 'B5': '新建弹窗规则', 'C': '活动或礼包的弹窗设置'}


def frame_lines_for(f, nodes, ranges, man):
    if f['code'] in man.get('框架', {}):
        return man['框架'][f['code']], True
    mod = MODULE_OF.get(f['card'])
    if not mod:
        return [], False
    a, b = ranges[mod]
    scope = [n for n in nodes if a <= n[0] <= b]
    if f['card'] == 'B3':
        st = [n for n in scope if n[2].startswith('本规则另设')]
        if st:
            s0 = st[0]
            sub = []
            for n in scope:
                if n[0] > s0[0]:
                    if n[1] <= s0[1]:
                        break
                    sub.append(n)
            scope = sub
    elif f['card'] in ('B1', 'B2', 'B4', 'B5'):
        # 去掉本规则另设子树，避免与 C 同名项混
        pass
    name = f['name']
    keys = [norm(name)]
    if '·' in name:
        keys.append(norm(name.split('·')[-1]))
    for sep in ('、', '｜', '→'):
        if sep in name:
            keys += [norm(x) for x in name.split(sep)]
    hits = []
    for k in keys:
        if len(k) < 2:
            continue
        for n in scope:
            nn = norm(n[2].split('：')[0]) if n[2].startswith('搜索') else norm(n[2])
            if nn == k or nn.startswith(k) or (len(nn) >= 4 and k.startswith(nn)):
                hits.append(n[0])
        if hits:
            break
    return sorted(set(hits)), False


def html_lines():
    return rd(SRC_HTML)


def page_names(cell):
    c = re.sub(r'（[^）]*）', '', cell)
    return [x.strip() for x in re.split(r'[、]', c) if x.strip() and x.strip() not in ('全部页', '不单画')]


def board_lines():
    L = rd(ORIG / '面包板.md')
    d = {}
    for i, l in enumerate(L):
        m = re.match(r'^\| ((?:G|P\d+)-\d+) \|', l)
        if m:
            d[m.group(1)] = i + 1
    return d


def walk_steps():
    L = rd(ORIG / '场景走查记录.md')
    d = {}
    for l in L:
        m = re.match(r'^\| (\d+) \|', l)
        if not m:
            continue
        step = int(m.group(1))
        ids = set(ID_RE.findall(l))
        for a, b in re.findall(r'((?:P\d+)-\d+)\s*至\s*((?:P\d+)-\d+)', l):
            pa, na = a.split('-'); pb, nb = b.split('-')
            if pa == pb:
                for k in range(int(na), int(nb) + 1):
                    ids.add(f'{pa}-{k:02d}')
        for i in ids:
            d.setdefault(i, set()).add(step)
    return d


# ---------------------------------------------------------------- 构图
class Chain:
    def __init__(self, base_cards=DIG, ref_path=None):
        self.fields, self.rules, self.excepts, self.mentions, self.ctasks = parse_cards(base_cards)
        self.list = parse_list(base_cards / '功能清单.md')
        self.ref = parse_ref(ref_path or (ORIG / '控件回指表.md'))
        self.man = manual()
        self.nodes, self.ranges = frame_nodes()
        self.html = html_lines()
        self.board = board_lines()
        self.steps = walk_steps()
        self.byfield = {f['code']: f for f in self.fields}
        # 边
        self.fwd, self.rev = {}, {}

        def e(a, b):
            self.fwd.setdefault(a, set()).add(b); self.rev.setdefault(b, set()).add(a)
        for r in self.list.values():
            for t in r['tasks']:
                e(t, f'清{r["row"]}')
            for c in r['fields']:
                e(f'清{r["row"]}', c)
        self.ctrl = {}
        for r in self.ref:
            self.ctrl[r['id']] = r
            for c in r['codes']:
                e(c, r['id'])
            pages = page_names(r['page'])
            for pg in pages:
                key = '需求评审版_图/' + pg + '.jpg'
                hl = [i + 1 for i, l in enumerate(self.html) if key in l]
                hl = [x for x in hl if 362 <= x <= 466] or hl
                for x in hl:
                    e(r['id'], f'源L{x}')
            if r['id'] in self.board:
                e(r['id'], f'板L{self.board[r["id"]]}')
            for s in sorted(self.steps.get(r['id'], [])):
                e(r['id'], f'步{s}')
        self.fl = {}
        for f in self.fields:
            ls, hand = frame_lines_for(f, self.nodes, self.ranges, self.man)
            self.fl[f['code']] = (ls, hand)
            for x in ls:
                e(f['code'], f'框L{x}')

    def norm_id(self, s):
        s = s.strip()
        if re.fullmatch(r'\d+', s):
            return '清' + s
        return s

    def closure(self, start, graph):
        seen, stack = set(), [start]
        while stack:
            x = stack.pop()
            for y in sorted(graph.get(x, [])):
                if y not in seen:
                    seen.add(y); stack.append(y)
        return seen

    def label(self, x):
        if x in self.byfield:
            f = self.byfield[x]
            return f'{x}  {f["name"]}（{Path(f["file"]).name} 第{f["line"]}行）'
        if x.startswith('清') and x[1:].isdigit():
            r = self.list.get(int(x[1:]))
            return f'{x}  {r["text"][:40]}（{r["dest"]}）' if r else x
        if x in self.ctrl:
            c = self.ctrl[x]
            return f'{x}  {c["ctrl"][:40]}（{c["page"][:20]}）'
        return x

    def index_rows(self):
        rows = []
        for f in self.fields:
            c = f['code']
            ups = self.rev.get(c, set())
            lst = sorted([int(u[1:]) for u in ups if u.startswith('清')])
            tasks = set()
            for n in lst:
                tasks.update(self.list[n]['tasks'])
            tk = sorted(tasks, key=lambda t: int(t[1:]))
            if not tk:
                tk = sorted(self.ctasks.get(f['card'], set()), key=lambda t: int(t[1:]))
                tkmark = '（卡级）' if tk else ''
            else:
                tkmark = ''
            ctrls = sorted(self.fwd.get(c, set()) & set(self.ctrl),
                           key=lambda x: (x[0], [int(y) if y.isdigit() else 0 for y in re.findall(r'\d+', x)]))
            html = sorted({int(y[2:]) for k in ctrls for y in self.fwd.get(k, []) if y.startswith('源L')})
            board = sorted({int(y[2:]) for k in ctrls for y in self.fwd.get(k, []) if y.startswith('板L')})
            steps = sorted({int(y[1:]) for k in ctrls for y in self.fwd.get(k, []) if y.startswith('步')})
            fl, hand = self.fl[c]
            handmark = []
            if hand: handmark.append('框架行')
            if any(('清%d' % n) and self.man['清单对应字段'].get(str(n)) for n in lst): handmark.append('清单行')
            if any(c in self.man['回指字段编号'].values() or c in str(self.man['回指字段编号']) for _ in [0]): handmark.append('回指')
            rows.append(dict(code=c, name=f['name'], tasks=tk, tkmark=tkmark, lst=lst, ctrls=ctrls, fl=fl, html=html,
                             board=board, steps=steps, hand=hand))
        return rows

    def fmt_index(self):
        out = ['| 任务 | 清单行 | 字段编号 | 字段名 | 控件 | 框架行 | 源.html 行 | 面包板行 | 走查步 | 备注 |', '|---|---|---|---|---|---|---|---|---|---|']
        mh = self.man
        for r in self.index_rows():
            notes = []
            if r['hand']: notes.append('框架行：人工对')
            if any(r['code'] in mh['清单对应字段'].get(str(n), []) + mh.get('清单对应字段追加', {}).get(str(n), []) for n in r['lst']): notes.append('清单行：人工对')
            if r['code'] in json.dumps(mh['回指字段编号'], ensure_ascii=False): notes.append('控件：人工对')
            if not r['ctrls']: notes.append('无控件')
            if not r['fl']: notes.append('框架无此节点')
            if not r['lst']: notes.append('无清单行')
            out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                '、'.join(r['tasks']) + r['tkmark'] if r['tasks'] else '—',
                '、'.join(str(x) for x in r['lst']) or '—', r['code'], r['name'].replace('|', '／'),
                '、'.join(r['ctrls']) or '—', '、'.join(map(str, r['fl'])) or '—',
                '、'.join(map(str, r['html'])) or '—', '、'.join(map(str, r['board'])) or '—',
                '、'.join(map(str, r['steps'])) or '—', '；'.join(notes) or ''))
        return out

    def ctrl_kind(self, f):
        if f['card'] == 'A4':
            return '迁移说明，无界面'
        if f['card'] == 'B5' or re.search(r'每行·|展开·|（只读）|^对应的活动或礼包|记录范围|时间、操作人|改的是哪个|每次最多（发送测试）', f['name']):
            return '只读显示项，页面上以文字出现，无可点控件'
        return '待查'

    # ------------------------------------------------ 自检
    def selfcheck(self):
        issues = {'清单行无字段': [], '字段无清单行': [], '字段无控件': [], '控件无字段': [], '字段编号不存在': [],
                  '字段无框架节点': [], '清单行无任务': [], '字段无可点控件（只读显示项或迁移说明，不算断链）': []}
        allcodes = set(self.byfield) | {r['code'] for r in self.rules} | {e['code'] for e in self.excepts}
        sc = set()
        for r in self.ref:
            for c in r['codes']:
                card = c.split('-')[0]
                if re.search(r'-S\d+$', c) or c.endswith('-X*') or c.endswith('-D'):
                    sc.add(c)
        for r in self.list.values():
            if not r['fields'] and not re.match(r'(—|无)[（(](去掉|移出本任务)', r.get('fcell', '')):
                issues['清单行无字段'].append(f'清{r["row"]}（{r["dest"]}）{r["text"][:30]}')
            if not r['tasks']:
                issues['清单行无任务'].append(f'清{r["row"]}')
            for c in r['fields']:
                if c not in allcodes and c not in sc and not c.endswith('-D') and not re.search(r'-S\d+$', c):
                    issues['字段编号不存在'].append(f'清{r["row"]}→{c}')
        for f in self.fields:
            c = f['code']
            ups = self.rev.get(c, set())
            if not ups:
                issues['字段无清单行'].append(f'{c} {f["name"]}')
            if not (self.fwd.get(c, set()) & set(self.ctrl)):
                k = self.ctrl_kind(f)
                issues['字段无控件' if k == '待查' else '字段无可点控件（只读显示项或迁移说明，不算断链）'].append(f'{c} {f["name"]}  〔{k}〕')
            gone = ups and all(self.list[int(u[1:])]['dest'] in ('去掉', '移出本任务') for u in ups if u.startswith('清'))
            if f['kind'] == 'F' and not self.fl[c][0] and f['card'] not in ('A3', 'A4') and not gone:
                issues['字段无框架节点'].append(f'{c} {f["name"]}')
        for r in self.ref:
            if not r['codes']:
                issues['控件无字段'].append(f'{r["id"]} {r["ctrl"][:30]}')
            for c in r['codes']:
                if c not in allcodes and c not in sc and c not in self.byfield:
                    issues['字段编号不存在'].append(f'{r["id"]}→{c}')
        return issues


# ---------------------------------------------------------------- 第 0 步：加列
def add_columns(dry=False):
    ch = Chain(PRE, PRE / '控件回指表.md')  # 从底本算
    man = ch.man
    report = []
    # 1 卡：首列「编号」
    for key in CARD_KEYS:
        src = card_file(PRE, key)
        dst = card_file(DIG, key)
        L = rd(src)
        codes = {f['line']: f['code'] for f in ch.fields if f['file'] == str(src)}
        out = []
        for i, l in enumerate(L):
            ln = i + 1
            nxt = L[i + 1] if i + 1 < len(L) else ''
            if ln in codes:
                out.append('| %s %s' % (codes[ln], l))
            elif l.startswith('|') and nxt.startswith('|---') and cells(l)[0] in ('字段名', '入口') and \
                    any(f['line'] == ln + 2 for f in ch.fields if f['file'] == str(src)):
                out.append('| 编号 ' + l)
            elif l.startswith('|---') and i > 0 and L[i - 1].startswith('|') and cells(L[i - 1])[0] in ('字段名', '入口') \
                    and any(f['line'] == ln + 1 for f in ch.fields if f['file'] == str(src)):
                out.append('|---' + l)
            else:
                out.append(l)
        report.append((dst.name, sum(1 for a, b in zip(L, out) if a != b)))
        if not dry:
            dst.write_text('\n'.join(out), encoding='utf-8')
    # 2 功能清单：末列「对应字段」
    src = PRE / '功能清单.md'
    L = rd(src)
    rowmap, how = map_list_rows(ch)
    out = []
    in_t = False
    n_changed = 0
    for i, l in enumerate(L):
        if l.startswith('| 行 | 旧设置或评审稿设置 |'):
            out.append(l + ' 对应字段 |'); in_t = True; n_changed += 1; continue
        if in_t and l.startswith('|---'):
            out.append(l + '---|'); n_changed += 1; continue
        if in_t and l.startswith('|'):
            c = cells(l)
            if re.fullmatch(r'\d+', c[0]):
                out.append(l + ' ' + rowmap[int(c[0])] + ' |'); n_changed += 1; continue
        if in_t and not l.startswith('|'):
            in_t = False
        out.append(l)
    report.append(('功能清单.md', n_changed))
    if not dry:
        (DIG / '功能清单.md').write_text('\n'.join(out), encoding='utf-8')
    # 3 回指表：末列「字段编号」
    src = PRE / '控件回指表.md'
    L = rd(src)
    refrows = {r['id']: r for r in ch.ref}
    out = []
    in_t = False
    n_changed = 0
    unmatched = []
    for i, l in enumerate(L):
        if l.startswith('| 编号 | 原型页 | 控件 | 卡 | 字段 |') and not in_t:
            out.append(l + ' 字段编号 |'); in_t = True; n_changed += 1; continue
        if in_t and l.startswith('|---'):
            out.append(l + '---|'); n_changed += 1; continue
        if in_t and l.startswith('|'):
            c = cells(l)
            r = refrows.get(c[0])
            if r:
                cell = ref_codes(ch, r, man, unmatched)
                out.append(l + ' ' + cell + ' |'); n_changed += 1; continue
        if in_t and not l.startswith('|'):
            in_t = False
        out.append(l)
    report.append(('控件回指表.md', n_changed))
    if not dry:
        (ORIG / '控件回指表.md').write_text('\n'.join(out), encoding='utf-8')
    return report, how, unmatched


def map_list_rows(ch):
    """清单每行 → 对应字段单元格文字；返回 (rowmap, how)"""
    man = ch.man
    by_row = {}
    for r, code, card, kind in ch.mentions:
        by_row.setdefault(r, []).append((code, kind))
    rowmap, how = {}, {'来源列': 0, '规则异常等': 0, '人工对': 0, '去掉无字段': 0, '待人工对': []}
    for n, r in ch.list.items():
        if str(n) in man['清单对应字段']:
            rowmap[n] = '、'.join(man['清单对应字段'][str(n)]); how['人工对'] += 1; continue
        ms = by_row.get(n, [])
        extra = man.get('清单对应字段追加', {}).get(str(n), [])
        f_codes = sorted({c for c, k in ms if k == 'src'})
        o_codes = sorted({c for c, k in ms if k != 'src'})
        if f_codes:
            rowmap[n] = '、'.join(f_codes + [c for c in extra if c not in f_codes]); how['来源列'] += 1
        elif o_codes:
            rowmap[n] = '、'.join(o_codes + [c for c in extra if c not in o_codes]); how['规则异常等'] += 1
        elif extra:
            rowmap[n] = '、'.join(extra); how['人工对'] += 1
        elif r['dest'] in ('去掉', '移出本任务'):
            rowmap[n] = '无（%s）' % r['dest']; how['去掉无字段'] += 1
        else:
            rowmap[n] = '待人工对'; how['待人工对'].append(n)
    return rowmap, how


def ref_codes(ch, r, man, unmatched):
    pairs = split_pairs(r['card'], r['field'])
    out = []
    for k, (card, lab) in enumerate(pairs):
        key = f'{r["id"]}|{k + 1}'
        if key in man['回指字段编号']:
            out += [x + '〔人工对〕' for x in man['回指字段编号'][key]]
            continue
        res = resolve_label(card, lab, ch.fields, ch.rules, ch.excepts)
        if res is None:
            unmatched.append((key, card, lab))
            out.append('待人工对')
        else:
            out += res
    return '；'.join(out)


# ---------------------------------------------------------------- 自检：删列后逐字相同
def strip_check():
    bad = []
    pairs = [(card_file(PRE, k), card_file(DIG, k)) for k in CARD_KEYS]
    pairs += [(PRE / '功能清单.md', DIG / '功能清单.md'), (PRE / '控件回指表.md', ORIG / '控件回指表.md')]
    res = []
    for old, new in pairs:
        a, b = rd(old), rd(new)
        if len(a) != len(b):
            bad.append(f'{new.name}: 行数 {len(b)} ≠ {len(a)}'); continue
        ncol = 0
        card = new.name.startswith('卡')
        for i, (x, y) in enumerate(zip(a, b)):
            if x == y:
                continue
            ncol += 1
            if card:
                if y.startswith('|---'):
                    z = y[4:]
                else:
                    code = cells(y)[0]
                    z = y[2 + len(code) + 1:]
            else:
                z = y.rstrip()[:-1].rsplit('|', 1)[0] + '|'
            if z != x:
                bad.append(f'{new.name} 第{i + 1}行: 删列后与第0步前不同')
        res.append((new.name, ncol))
    return bad, res


# ---------------------------------------------------------------- 入口
def main(argv):
    if len(argv) < 2:
        print(__doc__); return
    cmd = argv[1]
    if cmd == '加编号':
        rep, how, um = add_columns(dry='--试' in argv)
        for n, k in rep:
            print(f'{n}: 改动 {k} 行')
        print('清单对应字段:', {k: v for k, v in how.items() if k != '待人工对'}, '待人工对', how['待人工对'])
        print('回指字段编号 待人工对:', um)
        return
    ch = Chain()
    if cmd == '全表':
        print('\n'.join(ch.fmt_index()))
    elif cmd in ('上游', '下游'):
        x = ch.norm_id(argv[2])
        if re.fullmatch(r'框L\d+', x) and x not in ch.rev:
            pass
        g = ch.rev if cmd == '上游' else ch.fwd
        s = ch.closure(x, g)
        order = lambda y: (re.sub(r'\d+', '', y)[:2], int(re.findall(r'\d+', y)[-1]) if re.findall(r'\d+', y) else 0)
        print(f'{cmd} {x}：共 {len(s)} 项')
        for y in sorted(s, key=order):
            print('  ', ch.label(y))
    elif cmd == '写索引':
        rows = ch.index_rows()
        head = ['# 弹窗来源链索引', '',
                '由 `程序/追链.py 写索引` 生成（%d 个字段／入口）。一行一个字段或入口：任务｜清单行｜字段编号｜控件｜框架行｜源.html 行｜面包板行｜走查步。' % len(rows),
                '编号规则见 `程序/追链.py` 文件头。框架行以改前底本（10/30 13:44 版）为准，第 4 波改动后会变，追链时重新算。',
                '源.html 行：源.html 里弹窗段是「截图＋图注」，一页一行，所以这一列是控件所在页的图在源.html 的行号；字段落到哪一页看控件。',
                '「人工对」：名字对不上、靠人对的格子，记在 `程序/人工对.json`。任务栏标「（卡级）」＝该字段在清单里没有对应行，任务取自卡的「功能名｜对应任务」。', '']
        body = ch.fmt_index()
        p = BEN / '来源链索引.md'
        p.write_text('\n'.join(head + body) + '\n', encoding='utf-8')
        print('已写', p, len(rows), '行')
    elif cmd == '自检':
        iss = ch.selfcheck()
        bad, res = strip_check()
        print('== 自检 =='); n = 0
        for k, v in iss.items():
            print(f'{k}: {len(v)}')
            for x in (v if not k.startswith('字段无可点控件') else v[:3] + (['…'] if len(v) > 3 else [])):
                print('   ', x)
            if not k.startswith('字段无可点控件'):
                n += len(v)
        print('删掉新列后与第0步前逐字相同：', '全部相同' if not bad else f'不同 {len(bad)} 处')
        for b in bad:
            print('   ', b)
        print('各文件加列行数：', res)
        print('断链合计：', n)
    else:
        print(__doc__)


if __name__ == '__main__':
    main(sys.argv)
