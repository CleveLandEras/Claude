"""每周版本状态清单：读 Jira 只读查询存下的原始 JSON，离线算出各版本未完成需求、逾期风险、已转长篇故事未挂版本，生成一页 HTML 和 Teams 摘要。

用法：python3 -I 版本清单.py 数据/<日期> --版本 08_V50_11.5 08_V51_11.12 [--补来源核对] [--自检]
输入：数据/<日期>/原始/q1*.json、q2*.json、q3*.json、q4*.json；数据/<日期>/查询时间.txt；数据/来源核对*.json
输出：<日期>_版本清单.html、<日期>_版本清单_Teams摘要.txt（放在本脚本所在文件夹）
查询方法和口径见 README.md。
"""
import argparse, collections, glob, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BROWSE = 'https://xsg-game.atlassian.net/browse/'
STATUS_ORDER = ['待办', '正在执行', 'To Check', 'Checking', 'Blocked']
R_OVERDUE, R_LATE, R_BLOCKED = '已过截止日', '截止日晚于发版日', 'Blocked'
REASON_RANK = {R_OVERDUE: 0, R_BLOCKED: 1, R_LATE: 2}
OPENING = '峰龙，我用 AI 把这周和下周两个版本的未完成和逾期风险整理了一份，你看看有没有用；有用我每周一给你。'


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
    return name.split('_')[1]


def is_done(f):
    return f['status']['statusCategory']['key'] == 'done'


def link(k):
    return f'<a href="{BROWSE}{k}">{k}</a>'


def esc(s):
    return html.escape(s or '')


def cut(s, n):
    s = (s or '').strip()
    return s if len(s) <= n else s[:n].rstrip() + '…'


def update_src(data_dir):
    """读 原始/变更记录/<单号>.json，把 Q4 里还没核对的长篇故事补进 数据/来源核对_版本清单.json。"""
    path = os.path.join(data_dir, '..', '来源核对_版本清单.json')
    known = {}
    for p in sorted(glob.glob(os.path.join(data_dir, '..', '来源核对*.json'))):
        known.update(json.load(open(p)))
    mine = json.load(open(path)) if os.path.exists(path) else {}
    q4 = load_nodes(os.path.join(data_dir, '原始'), 'q4')
    added = []
    for k, x in sorted(q4.items()):
        cp = os.path.join(data_dir, '原始', '变更记录', k + '.json')
        if k in known or not os.path.exists(cp):
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


def build(data_dir, targets):
    raw = os.path.join(data_dir, '原始')
    asof = open(os.path.join(data_dir, '查询时间.txt')).read().strip()
    today = asof[:10]
    q1, q2, q3, q4 = (load_nodes(raw, p) for p in ('q1', 'q2', 'q3', 'q4'))
    src = {}
    for p in sorted(glob.glob(os.path.join(data_dir, '..', '来源核对*.json'))):
        src.update(json.load(open(p)))

    # 版本发版日：从任一单的 fixVersions 里取 releaseDate
    rel = {}
    for x in list(q1.values()) + list(q2.values()) + list(q3.values()):
        for v in x['fields'].get('fixVersions') or []:
            if v.get('releaseDate'):
                rel[v['name']] = v['releaseDate']
    targets = sorted(targets, key=lambda n: rel[n])

    def vers(f):
        return [v['name'] for v in f.get('fixVersions') or []]

    # 长篇故事归到它所挂目标版本里最早的那个；Legend 只计数
    epics, legends = {}, []
    for k, x in q1.items():
        f = x['fields']
        if f['issuetype']['name'] == 'Legend':
            legends.append(k)
            continue
        mine = [t for t in targets if t in vers(f)]
        epics[k] = {'key': k, 'f': f, 'ver': mine[0], 'vers': mine}

    children = collections.defaultdict(list)
    for x in q2.values():
        children[x['fields']['parent']['key']].append(x)

    def last_release(f, fallback):
        ds = [rel.get(n) for n in vers(f) if rel.get(n)] or [rel.get(n) for n in fallback if rel.get(n)]
        return max(ds) if ds else None

    def reasons(f, fallback):
        r, due = [], f.get('duedate')
        if due and due < today:
            r.append(R_OVERDUE)
        lr = last_release(f, fallback)
        if due and lr and due > lr:
            r.append(R_LATE)
        if f['status']['name'] == 'Blocked':
            r.append(R_BLOCKED)
        return r

    risks = []
    nodue = collections.Counter()
    undone_cnt = collections.Counter()
    # 长篇故事下的子单（不限是否挂本版）
    for ek, e in epics.items():
        for x in children.get(ek, []):
            f = x['fields']
            if is_done(f):
                continue
            undone_cnt[e['ver']] += 1
            if not f.get('duedate'):
                nodue[e['ver']] += 1
            r = reasons(f, vers(e['f']))
            if r:
                risks.append({'ver': e['ver'], 'key': x['key'], 'f': f, 'parent': ek,
                              'parent_sum': e['f']['summary'], 'why': r})
        r = reasons(e['f'], [])  # 长篇故事本身填了截止日的，同样三条
        if r:
            risks.append({'ver': e['ver'], 'key': ek, 'f': e['f'], 'parent': None, 'parent_sum': None, 'why': r})
    # 挂了本版、但不在以上长篇故事下的单
    q3_noparent = 0
    for k, x in q3.items():
        f = x['fields']
        mine = [t for t in targets if t in vers(f)]
        v = mine[0]
        undone_cnt[v] += 1
        if not f.get('duedate'):
            nodue[v] += 1
        p = f.get('parent')
        if not p:
            q3_noparent += 1
        r = reasons(f, [])
        if r:
            risks.append({'ver': v, 'key': k, 'f': f, 'parent': p['key'] if p else None,
                          'parent_sum': p['fields']['summary'] if p else None, 'why': r})
    vidx = {t: i for i, t in enumerate(targets)}
    risks.sort(key=lambda r: (vidx[r['ver']], min(REASON_RANK[w] for w in r['why']),
                              r['f'].get('duedate') or '9999', r['key']))

    # 已转成长篇故事、还没挂版本：来源核对为 true 的，按建单时间倒序
    unsched = [x for k, x in q4.items() if src.get(k, {}).get('由需求单转来') is True]
    unsched.sort(key=lambda x: x['fields']['created'], reverse=True)
    q4_false = [k for k in q4 if src.get(k, {}).get('由需求单转来') is False]
    q4_unchecked = [k for k in q4 if k not in src]

    # 每张长篇故事的子单统计
    risk_child = collections.Counter(r['parent'] for r in risks if r['parent'] in epics and r['key'] != r['parent'])
    erows = collections.defaultdict(list)
    for ek, e in epics.items():
        ch = children.get(ek, [])
        done = sum(1 for x in ch if is_done(x['fields']))
        st = collections.Counter(x['fields']['status']['name'] for x in ch if not is_done(x['fields']))
        odd = {(x['fields']['status']['name'], x['fields']['issuetype']['name']) for x in ch
               if not is_done(x['fields']) and x['fields']['status']['name'] not in STATUS_ORDER}
        erows[e['ver']].append({'e': e, 'done': done, 'total': len(ch), 'st': st, 'risk': risk_child[ek], 'odd': odd})
    for v in erows:
        erows[v].sort(key=lambda r: (-r['risk'], r['e']['key']))

    return dict(asof=asof, today=today, targets=targets, rel=rel, epics=epics, legends=legends, risks=risks,
                nodue=nodue, undone=undone_cnt, unsched=unsched, q4_false=q4_false, q4_unchecked=q4_unchecked,
                erows=erows, q3_total=len(q3), q3_noparent=q3_noparent)


ME = '712020:fd4c2aca-03b3-4cad-8de8-fc1e0c53ef27'  # 崔峰龙（读者本人）
HARD_WORDS = ('不可延期', '不可逾期')  # 标题里写了硬期限的需求
TESTED = ('To Check', 'Checking')  # 已提测：做完待测、测试中


def type_label(t):
    return '需求变更申请 ACC' if t == 'ACC' else t


def st_text(r):
    if r['total'] == 0:
        return '还没拆子单'
    parts = [f'{s} {r["st"][s]}' for s in STATUS_ORDER if r['st'].get(s)]
    parts += [f'{s}* {n}' for s, n in sorted(r['st'].items()) if s not in STATUS_ORDER]
    tail = '；未完成：' + ' · '.join(parts) if parts else ''
    return f'已完成 {r["done"]}/{r["total"]}{tail}'


def need_of(r, epics):
    if r['parent'] in epics:
        return r['parent']
    return r['key'] if r['key'] in epics else None


def need_groups(risks, epics):
    g, loose = collections.defaultdict(list), []
    for r in risks:
        k = need_of(r, epics)
        (g[k] if k else loose).append(r)
    order = sorted(g, key=lambda k: (-len(g[k]), -sum(1 for r in g[k] if R_BLOCKED in r['why']), k))
    return g, order, loose


def reason_txt(rs):
    c = collections.Counter(w for r in rs for w in r['why'])
    return '、'.join(f'{w} {c[w]}' for w in (R_BLOCKED, R_OVERDUE, R_LATE) if c[w])


def unsched_split(un):
    doing = [x for x in un if x['fields']['status']['statusCategory']['key'] != 'new']
    rest = [x for x in un if x not in doing]
    mine = [x for x in rest if (x['fields'].get('assignee') or {}).get('accountId') == ME]
    nobody = [x for x in rest if not x['fields'].get('assignee')]
    others = [x for x in rest if x not in mine and x not in nobody]
    return mine, nobody, others, doing


CSS = '''
body{margin:0;background:#fff;color:#1f2328;font:14px/1.55 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:20px 20px 32px}
h1{font-size:22px;margin:0 0 2px}
.sub{color:#59636e;margin:0 0 14px}
.first{border:1px solid #d1242f;border-left:6px solid #d1242f;background:#fff5f5;border-radius:6px;padding:10px 16px;margin:0 0 20px}
.first h2{font-size:15px;margin:0 0 4px;color:#a40e26}
.first ul{margin:0;padding-left:18px}
.first li{margin:3px 0}
h2.sec{font-size:16px;margin:22px 0 6px;padding-top:6px;border-top:1px solid #d1d9e0}
.note{color:#59636e;margin:6px 0}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border:1px solid #d1d9e0;padding:4px 7px;text-align:left;vertical-align:top}
th{background:#f6f8fa;font-weight:600;white-space:nowrap}
td.n{white-space:nowrap}
a{color:#0550ae;text-decoration:none}
.why{color:#a40e26;font-weight:600;white-space:nowrap}
.tag{display:inline-block;font-size:12px;color:#59636e;border:1px solid #d1d9e0;border-radius:4px;padding:0 4px;margin-left:4px;white-space:nowrap}
.foot{color:#59636e;font-size:12px;margin-top:20px;border-top:1px solid #d1d9e0;padding-top:8px}
@media print{.wrap{max-width:none}}
'''


def render(m):
    T, rel, epics = m['targets'], m['rel'], m['epics']
    vt = lambda v: f'{vshort(v)}（{md(rel[v])}）'
    risks = m['risks']
    by_reason = {w: sum(1 for r in risks if w in r['why']) for w in (R_OVERDUE, R_LATE, R_BLOCKED)}
    by_ver = collections.Counter(r['ver'] for r in risks)
    g, order, loose = need_groups(risks, epics)
    out = []
    a = out.append
    a('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width,initial-scale=1">')
    a(f'<title>{"、".join(vt(v) for v in T)}版本状态</title><style>{CSS}</style></head><body><div class="wrap">')
    a(f'<h1>{"、".join(vt(v) for v in T)}版本状态</h1>')
    a(f'<p class="sub">数据截至 {esc(m["asof"])}（Jira）</p>')

    # 先看这里（≤5 行）
    a('<div class="first" id="first"><h2>先看这里</h2><ul>')
    ver_part = '、'.join(f'{vshort(v)} <b data-n="risk-{vshort(v)}">{by_ver[v]}</b> 张' for v in T)
    if loose:
        lw = '没有所属需求' if all(not r['parent'] for r in loose) else '不属于这两版的需求'
        loose_txt = f'，另 <b data-n="loose">{len(loose)}</b> 张{lw}'
    else:
        loose_txt = '<b data-n="loose" hidden>0</b>'
    od = [r for r in risks if R_OVERDUE in r['why']]
    odc = collections.Counter(r['f']['status']['name'] for r in od)
    tested = sum(odc[s] for s in TESTED)
    od_parts = []
    if tested:
        od_parts.append(f'已提测 <b data-n="od-tested">{tested}</b> 张：' + '、'.join(f'{s} {odc[s]}' for s in TESTED if odc[s]))
    od_parts += [f'{s} {n} 张' for s, n in sorted(odc.items()) if s not in TESTED]
    od_txt = f'（{"；".join(od_parts)}）' if od_parts else ''
    a(f'<li>逾期风险子单 <b data-n="risk">{len(risks)}</b> 张（{ver_part}），分布在 <b data-n="needs">{len(g)}</b> 个需求里{loose_txt}。'
      f'按原因：已过截止日 <b data-n="risk-{R_OVERDUE}">{by_reason[R_OVERDUE]}</b> 张{od_txt}，'
      f'截止日晚于发版日 <b data-n="risk-{R_LATE}">{by_reason[R_LATE]}</b> 张，Blocked <b data-n="risk-{R_BLOCKED}">{by_reason[R_BLOCKED]}</b> 张。</li>')
    if order:
        top = order[:3]
        head = f'风险最集中的 {len(top)} 个需求' if len(top) > 1 else '风险所在的需求'
        items = '；'.join(f'{link(k)} {esc(cut(epics[k]["f"]["summary"], 18))}（{vshort(epics[k]["ver"])}）'
                         f'<b data-n="top-{k}">{len(g[k])}</b> 张：{reason_txt(g[k])}' for k in top)
        a(f'<li>{head}（按风险子单数从多到少排，一样多时先排有 Blocked 的）：{items}</li>')
    nd_rows = [r for v in T for r in m['erows'].get(v, []) if any(w in r['e']['f']['summary'] for w in HARD_WORDS)]
    if nd_rows:
        hit = [r for r in nd_rows if r['st'].get('Blocked') or r['st'].get('待办')]
        if hit:
            items = '；'.join(
                f'{link(r["e"]["key"])} {esc(cut(r["e"]["f"]["summary"], 22))}，已完成 {r["done"]}/{r["total"]}，'
                + '、'.join(f'{s} {r["st"][s]} 张' for s in ('Blocked', '待办') if r['st'].get(s)) for r in hit)
            a(f'<li>标题写了「不可延期／不可逾期」、还有 Blocked 或待办子单的需求 <b data-n="nodelay">{len(hit)}</b> 个：{items}</li>')
        else:
            a('<li>标题写了「不可延期／不可逾期」的需求，子单都没有 Blocked 或待办。</li>')
    mine, nobody, others, doing = unsched_split(m['unsched'])
    a(f'<li>已转成长篇故事、还没挂版本的需求 <b data-n="unsched">{len(m["unsched"])}</b> 个（第 2 节）：'
      f'负责人是你的 <b data-n="un-mine">{len(mine)}</b> 个、未指派 <b data-n="un-none">{len(nobody)}</b> 个、'
      f'已派给别人 <b data-n="un-other">{len(others)}</b> 个，都还没开始；另 <b data-n="un-doing">{len(doing)}</b> 个已在执行。</li>')
    nd = []
    for v in T:
        rows = m['erows'].get(v, [])
        kids = sum(r['total'] - r['done'] for r in rows)
        other = m['undone'][v] - kids
        nd.append(f'{vshort(v)} 未完成的单 <b data-n="undone-{vshort(v)}">{m["undone"][v]}</b> 张'
                  f'（{len(rows)} 个需求下的子单 <b data-n="kids-{vshort(v)}">{kids}</b> 张，加上挂 {vshort(v)} 但不在这些需求下的 '
                  f'<b data-n="other-{vshort(v)}">{other}</b> 张）里 {m["nodue"][v]} 张没填截止日')
    a(f'<li>{"；".join(nd)}。这些没法判逾期。</li>')
    a('</ul></div>')

    # 1 逾期风险子单
    a(f'<h2 class="sec">1　逾期风险子单（{len(risks)} 张）</h2>')
    a('<table id="t-risk"><tr><th>版本</th><th>单号</th><th>标题</th><th>所属需求</th><th>负责人</th><th>状态</th><th>截止日</th><th>原因</th></tr>')
    for r in risks:
        f = r['f']
        par = f'{link(r["parent"])} {esc(cut(r["parent_sum"], 22))}' if r['parent'] else '—'
        a(f'<tr class="r"><td class="n">{vshort(r["ver"])}</td><td class="n">{link(r["key"])}</td><td>{esc(f["summary"])}</td>'
          f'<td>{par}</td><td class="n">{esc(person(f.get("assignee")))}</td><td class="n">{esc(f["status"]["name"])}</td>'
          f'<td class="n">{md(f.get("duedate"))}</td><td class="why">{"、".join(r["why"])}</td></tr>')
    a('</table>')

    # 2 已转未挂版本
    a(f'<h2 class="sec">2　已转成长篇故事、还没挂版本的需求（{len(m["unsched"])} 个）</h2>')
    a('<p class="note">都由营运需求单改成长篇故事，还没挂任何版本；按建单时间从新到旧。</p>')
    a('<table id="t-unsched"><tr><th>单号</th><th>标题</th><th>提单人</th><th>负责人</th><th>状态</th><th>建单日</th></tr>')
    for x in m['unsched']:
        f = x['fields']
        a(f'<tr class="r"><td class="n">{link(x["key"])}</td><td>{esc(f["summary"])}</td><td class="n">{esc(person(f.get("reporter")))}</td>'
          f'<td class="n">{esc(person(f.get("assignee")))}</td><td class="n">{esc(f["status"]["name"])}</td><td class="n">{f["created"][:10]}</td></tr>')
    a('</table>')

    # 3.. 各版本未完成需求
    for i, v in enumerate(T):
        rows = m['erows'].get(v, [])
        a(f'<h2 class="sec">{3 + i}　{vshort(v)}（{md(rel[v])} 发版）未完成需求（{len(rows)} 个）</h2>')
        a(f'<table id="t-{vshort(v)}"><tr><th>单号</th><th>标题</th><th>负责人</th><th>状态</th><th>子单</th><th>风险子单</th></tr>')
        for r in rows:
            f = r['e']['f']
            tags = ''.join(f'<span class="tag">也挂 {vshort(t)}</span>' for t in r['e']['vers'] if t != r['e']['ver'])
            a(f'<tr class="r"><td class="n">{link(r["e"]["key"])}</td><td>{esc(f["summary"])}{tags}</td><td class="n">{esc(person(f.get("assignee")))}</td>'
              f'<td class="n">{esc(f["status"]["name"])}</td><td>{st_text(r)}</td><td class="n">{r["risk"] or ""}</td></tr>')
        a('</table>')
        kids = sum(r['total'] - r['done'] for r in rows)
        a(f'<p class="note">这 {len(rows)} 个需求下未完成子单 {kids} 张；另有挂 {vshort(v)}、但不在这些需求下的未完成单 '
          f'{m["undone"][v] - kids} 张，命中风险的已列进第 1 节。</p>')
        odd = collections.defaultdict(set)
        for r in rows:
            for s, t in r['odd']:
                odd[s].add(type_label(t))
        if odd:
            names = '、'.join(f'{s}（{"、".join(sorted(ts))}{" " if sorted(ts)[-1][-1].isascii() else ""}的状态）' for s, ts in sorted(odd.items()))
            a(f'<p class="note">带 * 的状态，Jira 归为进行中，所以算未完成：{names}。</p>')
        if i > 0:
            also = sorted(e['key'] for e in epics.values() if v in e['vers'] and e['ver'] != v)
            if also:
                earlier = '、'.join(sorted({vshort(epics[k]['ver']) for k in also}))
                a(f'<p class="note">另 <b data-n="also-{vshort(v)}">{len(also)}</b> 个需求同时挂 {earlier}'
                  f'（{"、".join(link(k) for k in also)}），列在上面 {earlier} 那节，标了「也挂 {vshort(v)}」。</p>')

    other = m['q3_total']
    a('<div class="foot">')
    a('口径：逾期风险只认三条——截止日早于数据截至当天；截止日晚于这张单所挂版本里最晚的发版日；状态是 Blocked。一张单挂两个版本不算风险。<br>')
    leg = '、'.join(m['legends'])
    a(f'只列长篇故事，Legend（{leg}）不列；挂了本版、但不在以上需求下的 {other} 张（其中没有父单 {m["q3_noparent"]} 张）只在命中风险时列出。')
    a('</div></div></body></html>')
    return '\n'.join(out) + '\n'


def teams(m):
    lines = [OPENING]
    epics = m['epics']
    for v in m['targets']:
        rs = [r for r in m['risks'] if r['ver'] == v]
        g, order, _ = need_groups(rs, epics)
        n = len(m['erows'].get(v, []))
        also = [e for e in epics.values() if v in e['vers'] and e['ver'] != v]
        extra = f'（另 {len(also)} 个同时挂 {"、".join(sorted({vshort(e["ver"]) for e in also}))}）' if also else ''
        if not rs:
            risk = '没有逾期风险子单'
        elif len(order) == 1:
            risk = f'逾期风险子单 {len(rs)} 张，在需求 {order[0]} 下'
        else:
            risk = f'逾期风险子单 {len(rs)} 张，最集中的需求是 ' + '、'.join(f'{k}（{len(g[k])} 张）' for k in order[:3])
        lines.append(f'{vshort(v)}（{md(m["rel"][v])}）：未完成需求 {n} 个{extra}；{risk}。')
    mine = unsched_split(m['unsched'])[0]
    lines.append(f'已转长篇故事、还没挂版本的需求 {len(m["unsched"])} 个在第 2 节，其中负责人是你的 {len(mine)} 个。')
    return '\n'.join(lines) + '\n'


def selfcheck(page, data_dir, m):
    errs = []
    raw_keys = set()
    for p in glob.glob(os.path.join(data_dir, '原始', '*.json')):
        raw_keys |= set(re.findall(r'"key":\s*"(RICH-\d+)"', open(p).read()))
    for k in sorted(set(re.findall(r'RICH-\d+', page))):
        if k not in raw_keys:
            errs.append(f'单号不在原始 JSON 里：{k}')
    first = page.find('id="first"')
    if first < 0 or first > page.find('<table'):
        errs.append('「先看这里」不在第一个表格前面')
    box = page[first:page.find('</div>', first)]
    if box.count('<li>') > 5:
        errs.append(f'「先看这里」超过 5 行：{box.count("<li>")}')

    def table(tid):
        s = page.find(f'<table id="{tid}"')
        return page[s:page.find('</table>', s)] if s >= 0 else ''

    def rows(tid):  # 每行的单元格纯文本，以及所属需求单号
        out = []
        for tr in re.findall(r'<tr class="r">(.*?)</tr>', table(tid)):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', tr)
            out.append([re.sub(r'<[^>]+>', '', c) for c in cells])
        return out

    def n(name):
        mm = re.search(rf'data-n="{re.escape(name)}"[^>]*>(\d+)<', page)
        return int(mm.group(1)) if mm else None

    def need(cells):  # 风险表一行属于哪个需求
        par = re.match(r'(RICH-\d+)', cells[3])
        if par and par.group(1) in m['epics']:
            return par.group(1)
        return cells[1] if cells[1] in m['epics'] else None

    risk = rows('t-risk')
    un = rows('t-unsched')
    checks = [('risk', len(risk)), ('unsched', len(un))]
    for w in (R_OVERDUE, R_LATE, R_BLOCKED):
        checks.append((f'risk-{w}', sum(1 for c in risk if w in c[7].split('、'))))
    for vv in set(re.findall(r'data-n="risk-(V\d+)"', page)):
        checks.append((f'risk-{vv}', sum(1 for c in risk if c[0] == vv)))
    needs = collections.Counter(need(c) for c in risk)
    checks.append(('needs', len([k for k in needs if k])))
    checks.append(('loose', needs.get(None, 0)))
    for k in re.findall(r'data-n="top-(RICH-\d+)"', page):
        checks.append((f'top-{k}', needs[k]))
    if n('od-tested') is not None:
        checks.append(('od-tested', sum(1 for c in risk if R_OVERDUE in c[7] and c[5] in TESTED)))
    checks += [('un-mine', sum(1 for c in un if c[3] == '崔峰龙' and c[4] == '待办')),
               ('un-none', sum(1 for c in un if c[3] == '未指派' and c[4] == '待办')),
               ('un-doing', sum(1 for c in un if c[4] != '待办'))]
    for name, got in checks:
        if n(name) != got:
            errs.append(f'计数不符：{name} 框里 {n(name)}，表格 {got}')
    if sum(n(x) or 0 for x in ('un-mine', 'un-none', 'un-other', 'un-doing')) != n('unsched'):
        errs.append('已转未挂版本的拆分加起来不等于总数')
    for vv in set(re.findall(r'data-n="kids-(V\d+)"', page)):
        got = sum(int(b) - int(a_) for a_, b in re.findall(r'已完成 (\d+)/(\d+)', table(f't-{vv}')))
        if n(f'kids-{vv}') != got:
            errs.append(f'计数不符：kids-{vv} 框里 {n(f"kids-{vv}")}，{vv} 表合计 {got}')
        if n(f'undone-{vv}') != n(f'kids-{vv}') + n(f'other-{vv}'):
            errs.append(f'{vv} 未完成合计不等于子单加其他')
    for vv in set(re.findall(r'data-n="also-(V\d+)"', page)):
        if n(f'also-{vv}') != page.count(f'<span class="tag">也挂 {vv}</span>'):
            errs.append(f'also-{vv} 和「也挂 {vv}」标记数不符')
    reasons = set()
    for c in risk:
        reasons |= set(c[7].split('、'))
    if reasons - {R_OVERDUE, R_LATE, R_BLOCKED}:
        errs.append(f'原因列出现三条以外的取值：{reasons}')
    rt = table('t-risk')
    if '同时挂' in rt or '两个版本' in rt:
        errs.append('风险表里出现「同时挂/两个版本」')
    if '*' in page and '带 * 的状态' not in page:
        errs.append('有带 * 的状态但没写说明')
    if page.count('数据截至') < 1:
        errs.append('没写数据截至')
    return errs


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('data_dir')
    ap.add_argument('--版本', nargs='+', required=True, dest='versions')
    ap.add_argument('--自检', action='store_true', dest='check')
    ap.add_argument('--补来源核对', action='store_true', dest='src')
    a = ap.parse_args()
    data_dir = os.path.abspath(a.data_dir)
    day = os.path.basename(data_dir.rstrip('/'))
    if a.src:
        update_src(data_dir)
    m = build(data_dir, a.versions)
    page, tx = render(m), teams(m)
    hp = os.path.join(HERE, f'{day}_版本清单.html')
    tp = os.path.join(HERE, f'{day}_版本清单_Teams摘要.txt')
    open(hp, 'w').write(page)
    open(tp, 'w').write(tx)
    for v in m['targets']:
        print(f'{vshort(v)}：未完成长篇故事 {len(m["erows"].get(v, []))}，风险 {sum(1 for r in m["risks"] if r["ver"] == v)}，'
              f'未填截止日 {m["nodue"][v]}/{m["undone"][v]}')
    print(f'风险合计 {len(m["risks"])}：' + '，'.join(f'{w} {sum(1 for r in m["risks"] if w in r["why"])}' for w in (R_OVERDUE, R_LATE, R_BLOCKED)))
    print(f'已转未挂版本 {len(m["unsched"])}（来源核对为否 {len(m["q4_false"])}：{m["q4_false"]}；未核对 {len(m["q4_unchecked"])}：{m["q4_unchecked"]}）')
    print(f'Legend {m["legends"]}；不在以上需求下的单 {m["q3_total"]}（没有父单 {m["q3_noparent"]}）')
    print('输出：', hp, tp, sep='\n  ')
    if m['q4_unchecked']:
        print('有长篇故事还没查变更记录，先补 来源核对_版本清单.json', file=sys.stderr)
        sys.exit(2)
    if a.check:
        errs = selfcheck(page, data_dir, m)
        for e in errs:
            print('自检不过：', e, file=sys.stderr)
        print('自检：' + ('通过' if not errs else f'{len(errs)} 项不过'))
        sys.exit(1 if errs else 0)
