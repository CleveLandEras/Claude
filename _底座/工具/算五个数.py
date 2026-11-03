#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""算五个数.py —— 每周四的五个数里，能由程序数出来的几项（让程序算数，不让被评的一方自己算）。

用法：
  python3 算五个数.py                                  近 7 天（含今天）
  python3 算五个数.py --从 2026-10-29 --到 2026-10-31   指定周期（含两端）
  python3 算五个数.py --用量 4 19 [--上限 5]            再算护栏「本圈用量」（周额度百分点：开始读数 结束读数；上限默认 5，首圈 15）
  python3 算五个数.py --已扫目录 <目录>                 复用已跑过的 扫会话记录.py 输出（省约 20 秒）
每项输出：数值｜分母｜口径｜数据来源。要判断才能填的项，输出「要判断：交便宜模型按定义填」并写明要什么输入。
五个数的定义见 ~/claude/用好Claude/先看这里.md「每周四算的五个数」，本脚本不改定义。
另输出两个护栏：本圈用量；同类重犯次数（读 _底座/失败类型表.md 的「次数」列）。
依据：任务/用好Claude/2026-10-29_自循环闭环_查顶尖做法并建起来/思考页.md 第 4.2 节⑦、第 7 节里程碑 2 第 4 项。
"""
import argparse
import collections
import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)                       # ~/claude/_底座
ROOT = os.path.dirname(BASE)                       # ~/claude
SCAN = ROOT + '/用好Claude/工具/扫会话记录.py'
PROJ = os.path.expanduser('~/.claude/projects')
DEF_DOC = '~/claude/用好Claude/先看这里.md「每周四算的五个数」'

# Dk 的消息语料里要剔除的：定时任务提示词、会话续接说明、子任务说明（不是 Dk 本人写的）
INJECT = ('<scheduled-task', 'This session is being continued', 'Background (from the session',
          'Task (from the session', 'Try again')
LONG_WORDS = ['太长', '读不完', '看不懂', '全是过程']                                   # 第 5 条「被嫌长或夹过程」
CORR_WORDS = ['不对', '什么鬼', '为什么没', '太长', '看不懂', '别', '不要']              # 纠正占比用词
CROSS_TOOLS = ('mcp__ccd_session_mgmt__send_message',)                                  # 对话之间发消息的工具


def load_ss():
    spec = importlib.util.spec_from_file_location('shouyangben', os.path.join(HERE, '收样本.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def local_date(ts):
    try:
        dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.astimezone().date()
    except Exception:
        return datetime.date.fromisoformat(ts[:10])


def pct(a, b):
    return '%.0f%%' % (100.0 * a / b) if b else '—'


def fmt_n(x):
    return '%d' % x if float(x).is_integer() else '%g' % x


def row(value, denom, basis, source):
    print('  %s｜%s｜%s｜%s' % (value, denom, basis, source))


def judge(what, need):
    print('  要判断：交便宜模型按定义填 —— %s｜需要的输入：%s｜定义：%s' % (what, need, DEF_DOC))


# ---------- 会话记录 ----------
def get_scan_dir(given):
    if given:
        return given
    d = tempfile.mkdtemp(prefix='算五个数_扫会话_')
    print('（调 扫会话记录.py 扫全部会话记录，约 20 秒；输出在 %s）' % d, file=sys.stderr)
    subprocess.run([sys.executable, SCAN, d], check=True, stdout=subprocess.DEVNULL)
    return d


def dk_messages(scan_dir, d0, d1):
    out = []
    p = os.path.join(scan_dir, 'user_msgs.jsonl')
    with open(p, encoding='utf-8') as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get('side'):
                continue
            t = (o.get('text') or '').lstrip()
            if t.startswith(INJECT):
                continue
            if d0 <= local_date(o['ts']) <= d1:
                out.append(o)
    return out


def pass2(scan_dir, d0, d1):
    """第二遍：只读周期内有活动的会话文件，数周期内的 cache_read 和对话之间的消息条数（扫会话记录.py 只给整段会话的总数）。"""
    sessions = json.load(open(os.path.join(scan_dir, 'sessions.json'), encoding='utf-8'))
    lo, hi = (d0 - datetime.timedelta(days=1)).isoformat(), (d1 + datetime.timedelta(days=1)).isoformat()
    picked = [s for s in sessions if s.get('first') and s.get('last') and s['last'][:10] >= lo and s['first'][:10] <= hi]
    tot = collections.Counter()
    names = collections.Counter()
    seen_msg, seen_tool = set(), set()
    for s in picked:
        path = os.path.join(PROJ, s['dir'], s['sid'] + '.jsonl')
        if not os.path.exists(path):
            continue
        with open(path, 'rb') as fh:
            for line in fh:
                if b'"assistant"' not in line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get('type') != 'assistant' or not o.get('timestamp'):
                    continue
                if not (d0 <= local_date(o['timestamp']) <= d1):
                    continue
                m = o.get('message') or {}
                mid = m.get('id')
                if mid and mid not in seen_msg:
                    seen_msg.add(mid)
                    u = m.get('usage') or {}
                    tot['cache_read'] += u.get('cache_read_input_tokens', 0) or 0
                    tot['cache_create'] += u.get('cache_creation_input_tokens', 0) or 0
                    tot['out'] += u.get('output_tokens', 0) or 0
                c = m.get('content')
                if isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get('type') == 'tool_use':
                            n = b.get('name', '')
                            if ('send_message' in n.lower() or n == 'SendMessage') and b.get('id') not in seen_tool:
                                seen_tool.add(b.get('id'))
                                names[n] += 1
    cross = sum(v for k, v in names.items() if k in CROSS_TOOLS)
    return dict(sessions=len(picked), cache_read=tot['cache_read'], cache_create=tot['cache_create'],
                out=tot['out'], cross=cross, names=dict(names))


# ---------- 任务文件 ----------
# 「Dk 退回」＝交接记录里状态变成「退回」的那一行（排除「由退回改回…」「仍为退回」这类退回之后的续写）
RET_EVENT = re.compile(r'状态[：:]\s*退回|状态(?:改为|改成|改)\s*退回|Dk[^。；\n]{0,8}验收退回')
DATED = re.compile(r'^\s*[-*]\s*(\d{1,2})/(\d{1,2})\b')


VERDICT = re.compile(r'(不通过|没过|(?<!没)有问题)|(通过(?!条件)|没有?问题)')


def last_verdict(line):
    """一行里最后一个结论词：不通过、没过、有问题 → False；通过、没问题 → True；没有 → None。
    「通过条件」不是结论；同一小句里前面有「连续」的（讲的是「连续…次都没问题才算过」这类条件）也不算。"""
    hits = []
    for m in VERDICT.finditer(line):
        clause = re.split(r'[，。；;,｜|（）()]', line[:m.start()])[-1]
        if '连续' in clause:
            continue
        hits.append(m)
    return None if not hits else bool(hits[-1].group(2))


def return_events(t, d0, d1):
    """数一个任务文件在周期内被 Dk 退回的每一次，并查每次退回前验收最近的结论（旧验收官、分角色验收的记录都认）。
    返回 (事件列表, 说明)。事件＝dict(line, date, text, verdict, vline)；verdict：True 通过／False 不通过／None 没有。"""
    text = t['text']
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith('## 交接记录')), None)
    if start is None:
        return [], '没有「交接记录」一节'
    fm = re.match(r'^(\d{4}-\d{2}-\d{2})_', os.path.basename(t['path']))
    cur = datetime.date.fromisoformat(fm.group(1)) if fm else None     # 没写日期的行沿用上一个有日期的行；最前面的用文件名日期
    year = (cur or datetime.date.today()).year
    events = []
    for i in range(start + 1, len(lines)):
        l = lines[i]
        if l.startswith('## '):
            break
        m = DATED.match(l)
        if m:
            try:
                cur = datetime.date(year, int(m.group(1)), int(m.group(2)))
            except ValueError:
                pass
        if not RET_EVENT.search(l):
            continue
        if cur is None or not (d0 <= cur <= d1):
            continue
        verdict, vline = None, None
        for j in range(i - 1, start, -1):
            if re.search(r'验收官|总验收人|分角色验收|验收跑完一轮', lines[j]):    # 旧验收官、分角色验收两种记录都认（「验收跑完一轮」是做法里交接记录的固定说法）
                v = last_verdict(lines[j])
                if v is not None:
                    verdict, vline = v, j + 1
                    break
        events.append(dict(line=i + 1, date=cur, text=l.strip(), verdict=verdict, vline=vline))
    return events, ''


def task_stats(ss, task_dir, d0, d1):
    tasks = ss.find_tasks(task_dir)
    judged, delivered = [], []
    counted, cands = [], []          # counted＝退回前验收已通过，计入；cands＝候选，没计入，写明原因
    ret_files = []                   # 周期内被 Dk 退回过的任务文件（不论退回前验收结论，给「数 4」用）
    reworked = []                    # 退回过、现已返工重交（当前状态不是退回）的件
    for t in tasks:
        st = t['status']
        text, path = t['text'], t['path']
        if not st.startswith(('待验收', '已完成', '退回')):
            continue
        ud = ss.update_date(text, path)
        rd = ss.to_review_date(text, path)
        is_judged = st.startswith(('已完成', '退回'))
        if d0 <= rd <= d1 or (is_judged and d0 <= ud <= d1):
            delivered.append(t)
        if is_judged and d0 <= ud <= d1:
            judged.append(t)
        evs, note = return_events(t, d0, d1)
        for e in evs:
            e['file'] = t['rel']
            if e['verdict'] is True:
                counted.append(e)
            elif e['verdict'] is False:
                cands.append(dict(e, why='退回前验收最近一次结论是「不通过」或「有问题」（第 %d 行），不算「验收通过后」' % e['vline']))
            else:
                cands.append(dict(e, why='退回行之前找不到验收的结论（通过／不通过、没问题／有问题），数不准'))
        if not evs and st.startswith('退回') and d0 <= ud <= d1:
            cands.append(dict(file=t['rel'], line=0, date=ud, text='（状态是退回，交接记录里没有退回行）', verdict=None, vline=None,
                              why='状态是退回，但交接记录里找不到记退回的那一行，没法查退回前验收结论'))
        if evs or (st.startswith('退回') and d0 <= ud <= d1):
            ret_files.append(t['rel'])
            if not st.startswith('退回'):
                reworked.append(t['rel'])
    counted_files = sorted(set(e['file'] for e in counted))
    return dict(tasks=tasks, judged=judged, delivered=delivered, counted=counted, counted_files=counted_files,
                cands=cands, ret_files=ret_files, reworked=reworked)


# ---------- 纠正记录、成绩单、失败类型表 ----------
def correction_stats(ss, path, d0, d1):
    if not os.path.exists(path):
        return None
    rows = [c for c in ss.table_rows(path) if c and re.match(r'^\d{4}-\d{2}-\d{2}$', c[0])]
    new = [c for c in rows if d0 <= datetime.date.fromisoformat(c[0]) <= d1]
    pending = [c for c in rows if c[-1].startswith('待整理')]
    return dict(total=len(rows), new=len(new), pending=len(pending))


def _frac(cell):
    """读一格里的「X÷Y＝N%」，返回 (x, y)；没有、分母 0、X 大于 Y、写了百分数但和 X÷Y 对不上，都返回 None（不猜）。"""
    m = re.search(r'(\d+(?:\.\d+)?)\s*[÷/／]\s*(\d+)(?:\s*[＝=]\s*\**\s*(\d+)\s*%)?', cell)
    if not m:
        return None
    x, y = float(m.group(1)), int(m.group(2))
    if y == 0 or x > y:
        return None
    if m.group(3) and abs(100.0 * x / y - int(m.group(3))) > 0.5:
        return None
    return (x, y)


PAIR_KEYS = ('拦下率', '误拦率', '误报')


def exam_pairs(body):
    """考后测一节的写法：「分数」表，表头是「指标｜考前｜考后」，拦下率、误拦率、误报各一行，考前、考后各写一个 X÷Y＝N%。
    没有这张表返回 None；有就返回 dict(vals：{指标: ((考前x, 考前y), (考后x, 考后y))}，bad：{指标: 读不出的原因})。
    核对：每格要读得出 X÷Y（百分数对得上）；行标题末尾「÷ N」的 N 要和两格的分母一致；对不上就读不出，不猜。"""
    vals, bad = {}, {}
    ci = cj = None
    found = False
    for l in body.splitlines():
        if not l.lstrip().startswith('|'):
            continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if cells and cells[0] == '指标' and '考前' in cells and '考后' in cells:
            ci, cj = cells.index('考前'), cells.index('考后')
            found = True
            continue
        if ci is None or len(cells) <= max(ci, cj):
            continue
        key = next((k for k in PAIR_KEYS if cells[0].startswith(k)), None)
        if not key or key in vals or key in bad:
            continue
        a, b = _frac(cells[ci]), _frac(cells[cj])
        lab = re.search(r'[÷/／]\s*(\d+)\s*[）)]?\s*$', cells[0])
        if not a or not b:
            bad[key] = '「%s」行的考前或考后格读不出 X÷Y' % key
        elif lab and (int(lab.group(1)) != a[1] or int(lab.group(1)) != b[1]):
            bad[key] = '「%s」行标题的分母 %s 和格里的分母 %d、%d 对不上' % (key, lab.group(1), a[1], b[1])
        else:
            vals[key] = (a, b)
    if not found:
        return None
    for k in PAIR_KEYS:
        if k not in vals and k not in bad:
            bad[k] = '「分数」表里没有「%s」这一行' % k
    return dict(vals=vals, bad=bad)


def exam_one(sec):
    """读成绩单里的一节。考前测的写法：误拦率只认该节评分区里「- 误拦率：… 判不通过 X 份 ÷ Y」这一行，
    并核对：Y 要和「合格样本 N 份」一致，写了百分数的要和 X÷Y 一致；对不上就读不出，不猜。
    考后测的写法不同（考前、考后并排写在「分数」表里），有这张表就走 exam_pairs，拦下率不再用下面那个只认第一个百分数的读法
    （它会读成「考前」那一列）。"""
    lines = sec.splitlines()
    head = lines[0].strip()
    body = '\n'.join(lines[1:])
    pr = exam_pairs(body)
    m = None if pr is not None else re.search(r'拦下率[^\n]{0,60}?(\d+)\s*%', body)
    out = dict(head=head, rate=m.group(1) + '%' if m else None, falseblock=None, why='', pairs=pr)
    if pr is not None:
        out['why'] = '；'.join(pr['bad'].values())
        return out
    mk = re.search(r'^\s*[-*]\s*误拦率[：:][^\n]*?判不通过\s*(\d+)\s*份\s*[÷/／]\s*(\d+)(?:\s*[＝=]\s*\**\s*(\d+)\s*%)?', body, re.M)
    if not mk:
        out['why'] = '该节没有「误拦率：… 判不通过 X 份 ÷ Y」这一行'
        return out
    x, y = int(mk.group(1)), int(mk.group(2))
    ns = re.findall(r'合格样本\s*(\d+)\s*份', body)
    if y == 0:
        out['why'] = '分母为 0'
    elif ns and int(ns[0]) != y:
        out['why'] = '误拦率行的分母 %d 和「合格样本 %s 份」对不上' % (y, ns[0])
    elif mk.group(3) and abs(100.0 * x / y - int(mk.group(3))) > 0.5:
        out['why'] = '行里写的 %s%% 和 %d÷%d 对不上' % (mk.group(3), x, y)
    elif x > y:
        out['why'] = '判不通过份数 %d 大于合格样本 %d' % (x, y)
    else:
        out['falseblock'] = (x, y)
    return out


def exam_stats(path):
    """返回 dict(head, rate：最新一节的标题和拦下率；rounds：要列出的节，考前在前、考后在后，没有同一圈的考前／考后时只有最新一节)。"""
    if not os.path.exists(path):
        return None
    text = open(path, encoding='utf-8').read()
    secs = re.split(r'^## ', text, flags=re.M)[1:]
    if not secs:
        return None
    parsed = [exam_one(sc) for sc in secs]            # 成绩单是最新在上
    latest = parsed[0]
    rounds = [latest]
    m = re.search(r'(第[^\s：:考]{1,6}圈)(考前测|考后测)', latest['head'])
    if m:
        pair = {}
        for p in parsed:
            mm = re.search(r'(第[^\s：:考]{1,6}圈)(考前测|考后测)', p['head'])
            if mm and mm.group(1) == m.group(1) and mm.group(2) not in pair:
                pair[mm.group(2)] = p                 # 同一圈同一种取最上面（最新）的一节
        rounds = [pair[k] for k in ('考前测', '考后测') if k in pair]
    return dict(head=latest['head'], rate=latest['rate'], rounds=rounds, latest=latest)


def fail_table(ss, path):
    if not os.path.exists(path):
        return None
    lines = open(path, encoding='utf-8').read().splitlines()
    hdr = None
    out = []
    for l in lines:
        if not l.startswith('|'):
            continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if '次数' in cells and hdr is None:
            hdr = cells
            continue
        if hdr is None or set(cells[0]) <= set('-: '):
            continue
        if len(cells) == len(hdr):
            out.append(dict(zip(hdr, cells)))
    return out


def main():
    today = datetime.date.today()
    ap = argparse.ArgumentParser(description='算五个数：能由程序数出来的项')
    ap.add_argument('--从', dest='start', default=(today - datetime.timedelta(days=6)).isoformat())
    ap.add_argument('--到', dest='end', default=today.isoformat())
    ap.add_argument('--用量', nargs=2, type=lambda s: float(s.strip().rstrip('%')), metavar=('开始%', '结束%'))
    ap.add_argument('--上限', type=float, default=5.0, help='每圈用量上限（个百分点），默认 5（稳定后），首圈 15')
    ap.add_argument('--已扫目录')
    ap.add_argument('--任务目录', default=BASE + '/任务')
    ap.add_argument('--纠正记录', default=BASE + '/纠正记录.md')
    ap.add_argument('--成绩单', default=BASE + '/考试/成绩单.md')
    ap.add_argument('--失败类型表', default=BASE + '/失败类型表.md')
    a = ap.parse_args()
    d0, d1 = datetime.date.fromisoformat(a.start), datetime.date.fromisoformat(a.end)
    ss = load_ss()

    ts = task_stats(ss, a.任务目录, d0, d1)
    nj, nd = len(ts['judged']), len(ts['delivered'])
    scan = get_scan_dir(a.已扫目录)
    msgs = dk_messages(scan, d0, d1)
    p2 = pass2(scan, d0, d1)

    print('统计周期 %s 至 %s（含两端）｜任务文件 %d 件｜本期交付件数 %d（改成待验收或被 Dk 判过）｜本期 Dk 判过 %d 件'
          % (d0, d1, len(ts['tasks']), nd, nj))
    print('每项格式：数值｜分母｜口径｜数据来源')
    can, need = 0, 0

    print('\n【数 1｜Dk 出现次数与时间／每件】')
    row('Dk 消息 %d 条，每件 %s 条' % (len(msgs), ('%.1f' % (len(msgs) / nd)) if nd else '—（分母 0）'), '本期交付件数 %d' % nd,
        '周期内 Dk 在各对话里发的消息条数（含一次退回），剔除定时任务提示词、会话续接说明、子任务说明；不含时间。'
        '每件＝总条数÷交付件数，没按任务拆（会话记录里没有任务编号）；基线：评审材料一天 6–7 版',
        '扫会话记录.py → user_msgs.jsonl；任务文件状态与交接记录')
    can += 1
    judge('时间（Dk 花的分钟数／每件）', '上面的消息条数，加每条消息的时间戳（user_msgs.jsonl 的 ts），按消息间隔估，或 Dk 自报')
    need += 1

    print('\n【数 2｜一次认可】')
    nc, nev = len(ts['counted_files']), len(ts['counted'])
    nd_done = sum(1 for t in ts['judged'] if t['status'].startswith('已完成'))
    nd_ret = sum(1 for t in ts['judged'] if t['status'].startswith('退回'))
    den = '本期 Dk 判过 %d 件（已完成 %d、退回 %d）' % (nj, nd_done, nd_ret)
    if ts['reworked']:
        den += '；另有 %d 件被 Dk 退回过、现已返工重交，当前状态不是退回，不在这 %d 件里' % (len(ts['reworked']), nj)
    row('验收通过后 Dk 退回 %d 件（共 %d 次）' % (nc, nev), den,
        '只数周期内交接记录里状态变成「退回」、且这一行之前验收最近一次结论是「通过」或「没问题」的件（旧验收官、分角色验收的记录都认）；同一件退回几次只算 1 件，次数另列；'
        '退回前验收不通过、有问题或找不到结论的，不计入，列在下面的候选；基线：退回 ≥2 次',
        '任务文件交接记录（%s）' % ('、'.join(ts['counted_files']) if ts['counted_files'] else '本期没有'))
    for e in ts['counted']:
        print('    计入：%s 第 %d 行（%s）：%s｜此前验收结论在第 %d 行，为通过' % (e['file'], e['line'], e['date'], e['text'][:70], e['vline']))
    for e in ts['cands']:
        print('    候选（没计入）：%s 第 %d 行（%s）：%s｜原因：%s' % (e['file'], e['line'], e['date'], e['text'][:70], e['why']))
    can += 1
    ex = exam_stats(a.成绩单)
    shown = False
    if ex and ex['latest']['pairs'] is not None:
        # 最新一节是考后测：误拦、误报按「考前→考后」并排读出；读不出的那项单独写读不出
        lt = ex['latest']
        for key, name, what in (('误拦率', '验收误拦', '用 Dk 判通过的稿考验收，它判「不通过」或「有问题」的份数÷合格样本份数'),
                                ('误报', '验收误报', '误报对照条里被评审再提出来的条数÷对照条数')):
            if key in lt['pairs']['vals']:
                (x0, y0), (x1, y1) = lt['pairs']['vals'][key]
                row('%s %s／%d（%s）→ %s／%d（%s）（考前→考后）' % (name, fmt_n(x0), y0, pct(x0, y0), fmt_n(x1), y1, pct(x1, y1)),
                    '分母 考前 %d、考后 %d' % (y0, y1), '%s；成绩单该节（最新一节）「分数」表：%s' % (what, lt['head']), '考试/成绩单.md')
            else:
                row('读不出，见成绩单', '—', '成绩单该节（最新一节）：%s；%s读不出的原因：%s' % (lt['head'], name, lt['pairs']['bad'].get(key, '—')), '考试/成绩单.md')
        shown = True
    elif ex:
        for i, r in enumerate(ex['rounds']):
            tag = '（最新一节）' if r is ex['latest'] else ''
            if r['falseblock']:
                x, y = r['falseblock']
                row('验收误拦 %d／%d（%s）' % (x, y, pct(x, y)), '合格样本 %d 份' % y,
                    '用 Dk 判通过的稿考验收，它判「不通过」或「有问题」的份数÷合格样本份数；成绩单该节%s：%s' % (tag, r['head']),
                    '考试/成绩单.md')
            else:
                row('读不出，见成绩单', '—', '成绩单该节%s：%s；读不出的原因：%s' % (tag, r['head'], r['why']), '考试/成绩单.md')
            shown = True
    if not shown:
        row('读不出，见成绩单', '—', '成绩单不存在或没有「## 」开头的节', '考试/成绩单.md')
    can += 1

    print('\n【数 3｜token】')
    cr = p2['cache_read']
    row('周期内 cache_read 共 %.2f 亿，每件 %s' % (cr / 1e8, ('%.2f 亿' % (cr / 1e8 / nd)) if nd else '—（分母 0）'),
        '本期交付件数 %d；读了 %d 个会话文件' % (nd, p2['sessions']),
        '周期内全部对话（含定时任务、非任务对话、子代理）的 cache_read 之和，按消息时间戳落在周期内的算；'
        '没按任务拆，所以每件是上界；基线：同类单对话 2.3–3.6 亿；另：输出 %.2f 亿、缓存写入 %.2f 亿' % (p2['out'] / 1e8, p2['cache_create'] / 1e8),
        '扫会话记录.py → sessions.json（选会话）＋逐条读 ~/.claude/projects/ 下会话记录的 usage')
    can += 1

    print('\n【数 5｜跨对话消息、越界、没要的产出、被嫌长、纠正占比】')
    row('对话之间发消息 %d 条，每件 %s 条' % (p2['cross'], ('%.1f' % (p2['cross'] / nd)) if nd else '—（分母 0）'),
        '本期交付件数 %d' % nd,
        '工具 mcp__ccd_session_mgmt__send_message 的调用次数（第一、二级之间的传话）；目标每件 ≤6；其他发消息工具计数：%s'
        % ('、'.join('%s %d 次' % kv for kv in p2['names'].items()) or '无'), '会话记录里的 tool_use')
    can += 1
    n_long = sum(1 for m in msgs if any(w in m['text'] for w in LONG_WORDS))
    row('被嫌长或夹过程的用词命中 %d 条' % n_long, 'Dk 消息 %d 条' % len(msgs),
        '含「%s」的 Dk 消息条数（只数用词命中，没逐条看是不是真嫌长）；目标 0' % '／'.join(LONG_WORDS), 'user_msgs.jsonl')
    can += 1
    short = [m for m in msgs if m.get('len', len(m['text'])) <= 1500]
    n_corr = sum(1 for m in short if any(w in m['text'] for w in CORR_WORDS))
    row('纠正占比 %d／%d（%s）' % (n_corr, len(short), pct(n_corr, len(short))), '非定时任务、非子任务、≤1,500 字的 Dk 消息 %d 条' % len(short),
        '含「%s」的比例（用词命中，会有误中）；基线 10/27–29 为 53／226（23%%）' % '／'.join(CORR_WORDS), 'user_msgs.jsonl')
    can += 1
    judge('对话做了不归它管的事（目标 0）', '会话记录里 Edit／Write 改过的文件路径，对照该任务文件「边界」写的范围')
    need += 1
    judge('Dk 没要的产出（目标 0）', '本期交付件清单（%d 件）对照各自对齐卡「要做的」' % nd)
    need += 1

    print('\n【数 4｜错误在哪一环发现】')
    judge('把 Dk 退回的每一处问题归到「对齐卡／思考页／验收／Dk」四类，目标 Dk 手里发现的 ≤20%（分母＝退回处数，要先判断才有）',
          '本期被退回的任务文件 %s，各自「验收结论」一节' % ('、'.join(ts['ret_files']) if ts['ret_files'] else '（本期没有，分母为 0）'))
    need += 1

    print('\n【辅助数（给上面要判断的项和归类用）】')
    cs = correction_stats(ss, a.纠正记录, d0, d1)
    if cs:
        row('纠正记录本期新增 %d 行；待整理共 %d 行' % (cs['new'], cs['pending']), '纠正记录共 %d 行' % cs['total'],
            '日期列落在周期内的行；「处理」列以「待整理」开头的行', '纠正记录.md')
    else:
        row('纠正记录.md 不存在', '—', '—', a.纠正记录)
    if ex and ex['latest']['pairs'] is not None:
        pv = ex['latest']['pairs']
        if '拦下率' in pv['vals']:
            (x0, y0), (x1, y1) = pv['vals']['拦下率']
            row('成绩单最新一节：%s，拦下率 %s÷%d＝%s → %s÷%d＝%s（考前→考后）' % (ex['head'], fmt_n(x0), y0, pct(x0, y0), fmt_n(x1), y1, pct(x1, y1)),
                '该节 %d 题' % y1, '成绩单最上面一节「分数」表（命中＋部分×0.5）÷题数', '考试/成绩单.md')
        else:
            row('成绩单最新一节：%s，拦下率读不出，见成绩单' % ex['head'], '—', '读不出的原因：%s' % pv['bad'].get('拦下率', '—'), '考试/成绩单.md')
    elif ex:
        row('成绩单最新一节：%s，拦下率 %s' % (ex['head'], ex['rate'] or '没写'), '见该节题数', '成绩单最上面一节', '考试/成绩单.md')

    print('\n【护栏 1｜本圈用量】')
    if a.用量:
        s0, s1 = a.用量
        used = s1 - s0
        row('本圈用了周额度 %.0f 个百分点（%.0f%% → %.0f%%）' % (used, s0, s1), '上限 %.0f 个百分点（%s）' % (a.上限, '已超' if used > a.上限 else '没超'),
            '周额度百分点相减，应用只显示整数，所以有 ±1 的误差；超上限先少考能力组新题，回归组和合格样本照考', '命令行 --用量 开始 结束（读数由分发从应用里读）')
    else:
        print('  没传 --用量 开始% 结束%，算不了（读数要分发开工和收工时各记一次）')

    print('\n【护栏 2｜同类重犯次数】')
    ft = fail_table(ss, a.失败类型表)
    if ft is None:
        print('  失败类型表还没建')
    else:
        def num(x):
            m = re.search(r'\d+', x.get('次数', ''))
            return int(m.group()) if m else 0
        tot = sum(num(x) for x in ft)
        rep = sum(max(num(x) - 1, 0) for x in ft)
        names = '、'.join('%s %d' % (x.get(next(iter(x)), '?'), num(x)) for x in ft)
        bad = [x for x in ft if x.get('状态', '').startswith('没生效')]
        row('同类重犯 %d 次（各类次数−1 之和）' % rep, '共 %d 类、出现 %d 次；状态「没生效」%d 类' % (len(ft), tot, len(bad)),
            '失败类型表「次数」列；规则落地后这一类接下来 4 周的次数应下降；各类：' + (names or '无'), '_底座/失败类型表.md')
        can += 1

    print('\n小结：能由程序算的 %d 项；要判断才能填的 %d 项（已写明要什么输入）。' % (can, need))


if __name__ == '__main__':
    sys.exit(main())
