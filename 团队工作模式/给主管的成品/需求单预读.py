"""营运需求单预读：读 Jira 只读查询存下的原始 JSON 和 AI 写的 建议.json，校验证据后生成一页 HTML 和 Teams 摘要。

用法：python3 -I 需求单预读.py 数据/<日期> --起 2026-10-26 --止 2026-11-01 [--补来源核对] [--自检]
输入：数据/<日期>/原始/q5*.json、q6*.json、q7*.json、原始/变更记录/<单号>.json；数据/<日期>/建议.json；
      数据/<日期>/查询时间_需求单.txt（没有就读 查询时间.txt）；数据/来源核对*.json
输出：<日期>_需求单预读.html、<日期>_需求单预读_Teams摘要.txt（放在本脚本所在文件夹）
查询方法、建议.json 格式和四类判断见 README.md。
"""
import argparse, glob, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BROWSE = 'https://xsg-game.atlassian.net/browse/'
OWNER = '崔峰龙'  # 新需求单由 Automation 自动指派给他；负责人不是他就算已派人
K_ASK, K_GO, K_DUP, K_NO = '要他定', '建议立项', '重复或已有单在做', '营运已说不用'
ORDER = [K_ASK, K_GO, K_DUP, K_NO]
SHOW = {K_ASK: '要你定', K_GO: K_GO, K_DUP: K_DUP, K_NO: K_NO}  # 页面上对主管说「你」
OPENING = '峰龙，上周新进的需求单我先过了一遍、标了建议，你立项时可以直接看；另外这 3 张营运已经说不用了或已被别的单做掉，你看能不能关。'
BAN_ADVICE = r'已决定|请关闭|应挂|挂到 ?V|派给.{0,6}(吧|即可)|直接关'
BAN_TONE = r'待验收|替你定|验收官|子代理|自评|制作过程|对照表|轮次'


def load_nodes(raw, prefix):
    out = {}
    for p in sorted(glob.glob(os.path.join(raw, prefix + '*.json'))):
        for x in json.load(open(p))['issues']['nodes']:
            out[x['key']] = x
    return out


def person(u):
    if not u:
        return '未指派'
    m = re.search(r'\(([^)]+)\)\s*$', u.get('displayName', ''))
    return m.group(1) if m else u.get('displayName', '')


def md(d):  # 2026-11-05 -> 11/5
    return f'{int(d[5:7])}/{int(d[8:10])}' if d else '—'


def vshort(name):  # 08_V50_11.5 -> V50
    return name.split('_')[1] if '_' in name else name


def link(k):
    return f'<a href="{BROWSE}{k}">{k}</a>'


def esc(s):
    return html.escape(s or '')


def is_epic(f):
    return f['issuetype'].get('hierarchyLevel') == 1 or f['issuetype']['name'] in ('Epic', '长篇故事')


def src_files(data_dir):
    known = {}
    for p in sorted(glob.glob(os.path.join(data_dir, '..', '来源核对*.json'))):
        known.update(json.load(open(p)))
    return known


def update_src(data_dir):
    """读 原始/变更记录/<单号>.json，把 Q5 里还没核对的长篇故事补进 数据/来源核对_需求单.json。"""
    path = os.path.join(data_dir, '..', '来源核对_需求单.json')
    known = src_files(data_dir)
    mine = json.load(open(path)) if os.path.exists(path) else {}
    q5 = load_nodes(os.path.join(data_dir, '原始'), 'q5')
    added = []
    for k, x in sorted(q5.items()):
        cp = os.path.join(data_dir, '原始', '变更记录', k + '.json')
        if not is_epic(x['fields']) or k in known or not os.path.exists(cp):
            continue
        n = json.load(open(cp))['issues']['nodes'][0]
        cl = n['changelog']
        if cl['total'] != len(cl['histories']):
            sys.exit(f'{k} 变更记录不全（{len(cl["histories"])}/{cl["total"]}），要分页补齐')
        hit = [(h['created'], h['author']['displayName']) for h in cl['histories'] for it in h['items']
               if it.get('field') == 'issuetype' and it.get('fromString') == 'Requirement' and it.get('toString') == 'Epic']
        clone = [l['outwardIssue']['key'] for l in x['fields'].get('issuelinks') or []
                 if l['type']['name'] == 'Cloners' and l.get('outwardIssue')]
        mine[k] = {'由需求单转来': bool(hit), '改类型时间': hit[0][0][:16].replace('T', ' ') if hit else None,
                   '改类型人': hit[0][1] if hit else None, '克隆自': clone[0] if clone else None}
        added.append(k)
    json.dump(mine, open(path, 'w'), ensure_ascii=False, indent=1)
    print(f'来源核对补了 {len(added)} 张：{added}')


def comments(f):
    return (f.get('comment') or {}).get('comments') or []


def find_quote(f, text):
    for c in comments(f):
        if text and text in (c.get('body') or ''):
            return c
    return None


def build(data_dir, start, end):
    raw = os.path.join(data_dir, '原始')
    tp = os.path.join(data_dir, '查询时间_需求单.txt')
    if not os.path.exists(tp):
        tp = os.path.join(data_dir, '查询时间.txt')
    asof = open(tp).read().strip()
    q5, q6, q7 = (load_nodes(raw, p) for p in ('q5', 'q6', 'q7'))
    adv = json.load(open(os.path.join(data_dir, '建议.json')))
    src = src_files(data_dir)
    errs = []

    done, todo, dropped, unchecked, outside = [], [], [], [], []
    for k, x in sorted(q5.items(), key=lambda kv: kv[1]['fields']['created']):
        f = x['fields']
        day = f['created'][:10]
        if not (start <= day <= end):
            outside.append(k)
            continue
        who = person(f.get('assignee'))
        vers = '、'.join(vshort(v['name']) for v in f.get('fixVersions') or [])
        if is_epic(f):
            s = src.get(k)
            if s is None:
                unchecked.append(k)
                continue
            if not s['由需求单转来']:
                dropped.append((k, s.get('克隆自')))
                continue
            when = md(s['改类型时间'][:10]) if s.get('改类型时间') else ''
            st = f'{when} 已转长篇故事，' + (f'派给{who}' if who != OWNER else '还没派人')
            st += f'，挂 {vers}' if vers else '，还没挂版本'
            done.append({'key': k, 'f': f, 'state': st})
        elif who != OWNER:
            st = f'已派给{who}' + (f'，挂 {vers}' if vers else '')
            done.append({'key': k, 'f': f, 'state': st})
        else:
            a = adv['新单'].get(k)
            if not a or not a.get('建议'):
                errs.append(f'{k} 还停在待受理，但 建议.json 里没有它的建议')
                continue
            todo.append({'key': k, 'f': f, 'a': a})
    for d in done:  # 已转或已派的也要一句话需求（只转述正文）
        d['one'] = (adv['新单'].get(d['key']) or {}).get('一句话需求')
        if not d['one']:
            errs.append(f'{d["key"]} 已转或已派，但 建议.json 里没有它的「一句话需求」')

    # 校验建议
    hits = set(q5) | set(q7)
    names = set()
    for p in glob.glob(os.path.join(raw, '*.json')):
        names |= set(re.findall(r'"displayName":\s*"[^"]*\(([^)]+)\)"', open(p).read()))
    for t in todo:
        k, a = t['key'], t['a']
        if a.get('建议') not in ORDER:
            errs.append(f'{k} 建议不在四类里：{a.get("建议")}')
        for n in a.get('对应单号') or []:
            if n not in hits:
                errs.append(f'{k} 对应单号 {n} 不在 Q5、Q7 的查询结果里')
        if a['建议'] == K_DUP and not a.get('对应单号'):
            errs.append(f'{k} 判「{K_DUP}」但没给对应单号')
        if a['建议'] == K_NO:
            q = (a.get('评论原话') or {}).get('原文')
            c = find_quote(t['f'], q)
            if not c:
                errs.append(f'{k} 判「{K_NO}」但评论原话不在该单评论原文里')
            t['quote'] = c
        if a['建议'] == K_GO and not (a.get('要点草稿') or '').strip():
            errs.append(f'{k} 判「{K_GO}」但没写要点草稿')
        if a['建议'] == K_ASK and not ((a.get('要他定的问题') or '').strip() and (a.get('建议做法') or '').strip()):
            errs.append(f'{k} 判「{K_ASK}」但没写「要他定的问题」和「建议做法」')
        ext = a.get('外部资料')
        if ext:  # 需求写在外部表格里的：链接要出自单子正文，原话要逐字出现在摘录里
            if ext.get('链接') not in (t['f'].get('description') or ''):
                errs.append(f'{k} 外部资料的链接不在单子正文里')
            xp = os.path.join(data_dir, ext.get('摘录') or '')
            text = open(xp).read() if os.path.isfile(xp) else ''
            if not text:
                errs.append(f'{k} 外部资料的摘录文件不存在：{ext.get("摘录")}')
            for q in ext.get('原话') or []:
                if q not in text:
                    errs.append(f'{k} 外部资料原话「{q}」不在摘录里')
        draft = a.get('要点草稿') or ''
        if len(draft) > 200:
            errs.append(f'{k} 要点草稿超过 200 字（{len(draft)}）')
        if re.search(r'V\d{2}', draft):
            errs.append(f'{k} 要点草稿里出现了版本号')
        for n in names:
            if n in draft:
                errs.append(f'{k} 要点草稿里出现了人名：{n}')
        for fld in ('建议', '理由', '要点草稿', '要他定的问题', '建议做法'):
            if re.search(BAN_ADVICE, a.get(fld) or ''):
                errs.append(f'{k} 「{fld}」里有替他拍板的说法')
    todo.sort(key=lambda t: (ORDER.index(t['a']['建议']) if t['a'].get('建议') in ORDER else 9, t['f']['created']))
    stale = sorted({k for k, v in adv['新单'].items() if v.get('建议')} - {t['key'] for t in todo})

    # 老单
    old, closed = [], []
    for k, spec in adv.get('老单', {}).items():
        x = q6.get(k)
        if not x:
            errs.append(f'老单 {k} 不在 Q6 里')
            continue
        f = x['fields']
        if f['status']['statusCategory']['key'] == 'done':
            closed.append(k)
            continue
        ev = []
        for q in spec.get('原话') or []:
            c = find_quote(f, q)
            if not c:
                errs.append(f'老单 {k} 的原话「{q}」不在评论原文里')
                continue
            ev.append(f'{esc(person(c["author"]))} {c["created"][:10]} 评论「{esc(q)}」')
        by = spec.get('做掉它的单')
        if by:
            y = q6.get(by)
            if not y or y['fields']['status']['statusCategory']['key'] != 'done':
                errs.append(f'老单 {k} 的「做掉它的单」{by} 不在 Q6 里或还没完成')
            else:
                ev.append(f'已被 {link(by)}「{esc(y["fields"]["summary"])}」做掉（{(y["fields"].get("resolutiondate") or "")[:10]} 完成）')
        if not ev:
            errs.append(f'老单 {k} 没有证据')
        old.append({'key': k, 'f': f, 'ev': '；'.join(ev)})

    return dict(asof=asof, start=start, end=min(end, asof[:10]), done=done, todo=todo, dropped=dropped,
                unchecked=unchecked, outside=outside, stale=stale, old=old, closed=closed, errs=errs)


CSS = '''
body{margin:0;background:#fff;color:#1f2328;font:14px/1.55 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:20px 20px 32px}
h1{font-size:22px;margin:0 0 2px}
.sub{color:#59636e;margin:0 0 14px}
.first{border:1px solid #d1242f;border-left:6px solid #d1242f;background:#fff5f5;border-radius:6px;padding:10px 16px;margin:0 0 20px}
.first h2{font-size:15px;margin:0 0 4px;color:#a40e26}
.first ul{margin:0;padding-left:18px}
.first li{margin:2px 0}
h2.sec{font-size:16px;margin:22px 0 6px;padding-top:6px;border-top:1px solid #d1d9e0}
.note{color:#59636e;margin:0 0 6px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border:1px solid #d1d9e0;padding:4px 7px;text-align:left;vertical-align:top}
th{background:#f6f8fa;font-weight:600;white-space:nowrap}
td.n{white-space:nowrap}
td.adv{white-space:nowrap;font-weight:600;color:#a40e26}
tr.draft td{background:#f6f8fa;color:#1f2328}
tr.draft b{display:block;margin-bottom:2px}
a{color:#0550ae;text-decoration:none}
.foot{color:#59636e;font-size:12px;margin-top:20px;border-top:1px solid #d1d9e0;padding-top:8px}
@media print{.wrap{max-width:none}}
'''


def counts(m):
    c = {k: sum(1 for t in m['todo'] if t['a']['建议'] == k) for k in ORDER}
    return c, len(m['todo']) + len(m['done'])


def reason_html(t):
    a = t['a']
    r = ''
    if a['建议'] == K_ASK:
        r += f'<b>要你定：</b>{esc(a["要他定的问题"])}<br><b>建议：</b>{esc(a["建议做法"])}<br>'
    r += esc(a.get('理由'))
    ext = a.get('外部资料')
    if ext:
        r += f'<br>营运的表格：<a href="{esc(ext["链接"])}">{esc(ext["名称"])}</a>（「{esc(ext["分页"])}」页）'
    nums = a.get('对应单号') or []
    if nums:
        r += '<br>对应单：' + '、'.join(link(n) for n in nums)
    if t.get('quote'):
        c = t['quote']
        r += f'<br>{esc(person(c["author"]))} {c["created"][:10]} 评论：「{esc(a["评论原话"]["原文"])}」'
    return r


def render(m):
    c, n = counts(m)
    title = f'营运需求单预读：{md(m["start"])}—{md(m["end"])} 新进'
    out = []
    a = out.append
    a('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width,initial-scale=1">')
    a(f'<title>{title}</title><style>{CSS}</style></head><body><div class="wrap">')
    a(f'<h1>{title}</h1>')
    a(f'<p class="sub">数据截至 {esc(m["asof"])}（Jira）</p>')

    a('<div class="first" id="first"><h2>先看这里</h2><ul>')
    a(f'<li>新进 <b data-n="all">{n}</b> 张：要你定 <b data-n="{K_ASK}">{c[K_ASK]}</b>、建议立项 <b data-n="{K_GO}">{c[K_GO]}</b>、'
      f'重复或已有单在做 <b data-n="{K_DUP}">{c[K_DUP]}</b>、营运已说不用 <b data-n="{K_NO}">{c[K_NO]}</b>；'
      f'已转长篇故事或已派人 <b data-n="done">{len(m["done"])}</b></li>')
    ask = [t for t in m['todo'] if t['a']['建议'] == K_ASK]
    for t in ask:
        a(f'<li>要你定：{link(t["key"])} {esc(t["f"]["summary"])}——{esc(t["a"]["要他定的问题"])}建议：{esc(t["a"]["建议做法"])}</li>')
    if m['old']:
        a(f'<li>建议关的老单 <b data-n="old">{len(m["old"])}</b> 张：' + '、'.join(link(o['key']) for o in m['old']) + '，回一句关不关（第 3 节）</li>')
    a('</ul></div>')

    a(f'<h2 class="sec">1　逐张建议（{len(m["todo"])} 张）</h2>')
    a('<table id="t-advice"><tr><th>单号</th><th>标题</th><th>类型</th><th>提单人</th><th>一句话需求</th><th>建议</th><th>理由</th></tr>')
    for t in m['todo']:
        f = t['f']
        a(f'<tr class="r"><td class="n">{link(t["key"])}</td><td>{esc(f["summary"])}</td><td class="n">{esc(f["issuetype"]["name"])}</td>'
          f'<td class="n">{esc(person(f.get("reporter")))}</td><td>{esc(t["a"]["一句话需求"])}</td>'
          f'<td class="adv">{SHOW[t["a"]["建议"]]}</td><td>{reason_html(t)}</td></tr>')
        if t['a']['建议'] == K_GO:
            d = '<br>'.join(esc(x) for x in t['a']['要点草稿'].split('\n'))
            a(f'<tr class="draft"><td></td><td colspan="6"><b>要点草稿（可贴进长篇故事）</b>{d}</td></tr>')
    a('</table>')

    a(f'<h2 class="sec">2　已转长篇故事或已派人（{len(m["done"])} 张）</h2>')
    a('<table id="t-done"><tr><th>单号</th><th>标题</th><th>提单人</th><th>一句话需求</th><th>现状</th></tr>')
    for d in m['done']:
        f = d['f']
        a(f'<tr class="r"><td class="n">{link(d["key"])}</td><td>{esc(f["summary"])}</td>'
          f'<td class="n">{esc(person(f.get("reporter")))}</td><td>{esc(d["one"])}</td><td>{esc(d["state"])}</td></tr>')
    a('</table>')

    a(f'<h2 class="sec">3　建议关的老单（{len(m["old"])} 张）</h2>')
    a('<p class="note">都还是需求单、待办。</p>')
    a('<table id="t-old"><tr><th>单号</th><th>标题</th><th>建单日</th><th>证据</th></tr>')
    for o in m['old']:
        f = o['f']
        a(f'<tr class="r"><td class="n">{link(o["key"])}</td><td>{esc(f["summary"])}</td><td class="n">{f["created"][:10]}</td><td>{o["ev"]}</td></tr>')
    a('</table>')
    if m['closed']:
        a('<p class="note">' + '、'.join(link(k) for k in m['closed']) + ' 已关。</p>')

    a('<div class="foot">新进 = RICH 项目在这段时间新建的 Requirement、ACC，加上已由需求单改成长篇故事的单（策划克隆的单不算）。</div>')
    a('</div></body></html>')
    return '\n'.join(out) + '\n'


def teams(m):
    c, n = counts(m)
    ask = '、'.join(t['key'] for t in m['todo'] if t['a']['建议'] == K_ASK)
    lines = [OPENING,
             f'{md(m["start"])}—{md(m["end"])} 新进 {n} 张：要你定 {c[K_ASK]}' + (f'（{ask}）' if ask else '') +
             f'、建议立项 {c[K_GO]}、重复或已有单在做 {c[K_DUP]}、营运已说不用 {c[K_NO]}；已转长篇故事或已派人 {len(m["done"])}。',
             '建议关的老单：' + '、'.join(o['key'] for o in m['old']) + '。']
    return '\n'.join(lines) + '\n'


def selfcheck(page, tx, data_dir):
    errs = []
    raw_keys = set()
    for p in glob.glob(os.path.join(data_dir, '原始', '*.json')):
        raw_keys |= set(re.findall(r'"key":\s*"(RICH-\d+)"', open(p).read()))
    for k in sorted(set(re.findall(r'RICH-\d+', page + tx))):
        if k not in raw_keys:
            errs.append(f'单号不在原始 JSON 里：{k}')
    first = page.find('id="first"')
    if first < 0 or first > page.find('<table'):
        errs.append('「先看这里」不在第一个表格前面')

    def tbl(tid):
        s = page.find(f'<table id="{tid}"')
        return page[s:page.find('</table>', s)]

    def n(name):
        mm = re.search(rf'data-n="{re.escape(name)}">(\d+)<', page)
        return int(mm.group(1)) if mm else None
    adv = tbl('t-advice')
    checks = [('all', adv.count('<tr class="r"') + tbl('t-done').count('<tr class="r"')),
              ('done', tbl('t-done').count('<tr class="r"'))]
    for k in ORDER:
        checks.append((k, adv.count(f'<td class="adv">{SHOW[k]}</td>')))
    if n('old') is not None:
        checks.append(('old', tbl('t-old').count('<tr class="r"')))
    for name, got in checks:
        if n(name) != got:
            errs.append(f'计数不符：{name} 框里 {n(name)}，表格 {got}')
    if page.count('数据截至') < 1:
        errs.append('没写数据截至')
    plain = re.sub(r'<[^>]+>', '', page)
    for where, text in (('HTML', plain), ('Teams 摘要', tx)):
        mm = re.search(BAN_TONE, text)
        if mm:
            errs.append(f'{where} 里出现了不该给上级看的词：{mm.group(0)}')
        mm = re.search(r'(To Check|Checking|Blocked)\s*[（(]', text)
        if mm:
            errs.append(f'{where} 里状态名后面跟了括号解释：{mm.group(0)}')
    nl = len(tx.strip().split('\n'))
    if not 3 <= nl <= 5:
        errs.append(f'Teams 摘要 {nl} 行，要 3—5 行')
    if OPENING.replace('峰龙，', '') not in tx:
        errs.append('Teams 摘要没有用第 05 节的开场句')
    return errs


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('data_dir')
    ap.add_argument('--起', required=True, dest='start')
    ap.add_argument('--止', required=True, dest='end')
    ap.add_argument('--自检', action='store_true', dest='check')
    ap.add_argument('--补来源核对', action='store_true', dest='src')
    a = ap.parse_args()
    data_dir = os.path.abspath(a.data_dir)
    day = os.path.basename(data_dir.rstrip('/'))
    if a.src:
        update_src(data_dir)
    m = build(data_dir, a.start, a.end)
    if m['unchecked']:
        print(f'这些长篇故事还没查变更记录，先补 来源核对_需求单.json：{m["unchecked"]}', file=sys.stderr)
        sys.exit(2)
    for e in m['errs']:
        print('建议校验不过：', e, file=sys.stderr)
    if m['errs']:
        sys.exit(1)
    page, tx = render(m), teams(m)
    hp = os.path.join(HERE, f'{day}_需求单预读.html')
    tp = os.path.join(HERE, f'{day}_需求单预读_Teams摘要.txt')
    open(hp, 'w').write(page)
    open(tp, 'w').write(tx)
    c, n = counts(m)
    print(f'新进 {n}：' + '，'.join(f'{k} {c[k]}' for k in ORDER) + f'；已转或已派 {len(m["done"])}')
    print(f'剔掉（不是由需求单转来）{len(m["dropped"])}：{m["dropped"]}；时间窗外 {m["outside"]}')
    print(f'建议.json 里已不用的条目（单子已被转走或派人）：{m["stale"]}')
    print(f'老单 {[o["key"] for o in m["old"]]}；已关 {m["closed"]}')
    print('输出：', hp, tp, sep='\n  ')
    if a.check:
        errs = selfcheck(page, tx, data_dir)
        for e in errs:
            print('自检不过：', e, file=sys.stderr)
        print('自检：' + ('通过' if not errs else f'{len(errs)} 项不过'))
        sys.exit(1 if errs else 0)
