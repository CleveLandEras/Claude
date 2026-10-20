# -*- coding: utf-8 -*-
"""汇总某一晚（本地 19:00 至次日 08:35）定时任务各轮的 token 用量与子任务。
用法：python3 _scripts/an_夜间用量.py 2026-10-17 [任务名 ...]（默认统计设计主线与夜间监督）；结果另存 _versions/夜间推进/用量_<日期>.json"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import glob, json, os, datetime as dt

P = '/Users/decheng.huang/.claude/projects/-Users-decheng-huang-claude---------'
NIGHT = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today() - dt.timedelta(days=1)
NAMES = sys.argv[2:] or ['push-backend-design-mainline', 'popup-tag-push-night-global']
T0 = dt.datetime(NIGHT.year, NIGHT.month, NIGHT.day, 11, 0, tzinfo=dt.timezone.utc)
T1 = T0 + dt.timedelta(hours=13, minutes=35)
TZ = dt.timezone(dt.timedelta(hours=8))


def parse(path):
    seen, tot, first, last, first_user = {}, dict(new=0, cache=0, out=0), None, None, None
    for line in open(path, encoding='utf-8', errors='ignore'):
        try:
            d = json.loads(line)
        except Exception:
            continue
        ts = d.get('timestamp')
        if ts:
            t = dt.datetime.fromisoformat(ts.replace('Z', '+00:00'))
            first = first or t
            last = t
        if first_user is None and d.get('type') == 'user':
            c = d.get('message', {}).get('content')
            if isinstance(c, list):
                c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict))
            first_user = (c or '')[:400]
        m = d.get('message') or {}
        u = m.get('usage')
        if not u or d.get('type') != 'assistant':
            continue
        key = m.get('id') or d.get('requestId') or d.get('uuid')
        cur = seen.get(key, (0, 0, 0))
        seen[key] = (max(cur[0], u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0)),
                     max(cur[1], u.get('cache_read_input_tokens', 0)), max(cur[2], u.get('output_tokens', 0)))
    for a, b, c in seen.values():
        tot['new'] += a; tot['cache'] += b; tot['out'] += c
    return tot, first, last, first_user


runs = []
for f in glob.glob(os.path.join(P, '*.jsonl')):
    head = open(f, encoding='utf-8', errors='ignore').read(3000)
    task = next((n for n in NAMES if n in head), None)
    if not task:
        continue
    tot, first, last, _ = parse(f)
    if not first or not (T0 <= first <= T1):
        continue
    sid = os.path.basename(f)[:-6]
    subs = []
    for sf in glob.glob(os.path.join(P, sid, 'subagents', '*.jsonl')):
        st, sfirst, slast, sprompt = parse(sf)
        label = (sprompt or '').strip().replace('\n', ' ')
        subs.append(dict(label=label[:160], **st,
                         start=sfirst.astimezone(TZ).strftime('%H:%M') if sfirst else '',
                         mins=round((slast - sfirst).total_seconds() / 60) if sfirst and slast else 0))
    runs.append(dict(task=task, sid=sid, start=first.astimezone(TZ).strftime('%m-%d %H:%M'),
                     end=last.astimezone(TZ).strftime('%H:%M'), main=tot, subs=subs))

runs.sort(key=lambda r: r['start'])
out = f'{_ROOT}/_versions/夜间推进/用量_{NIGHT.isoformat()}.json'
json.dump(runs, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def s(t):
    return t['new'] + t['cache'] + t['out']

G = dict(new=0, cache=0, out=0)
for r in runs:
    sub = dict(new=sum(x['new'] for x in r['subs']), cache=sum(x['cache'] for x in r['subs']), out=sum(x['out'] for x in r['subs']))
    for k in G:
        G[k] += r['main'][k] + sub[k]
    if s(r['main']) + s(sub) < 300000:
        continue
    print(f"{r['task'][:12]} {r['start']}-{r['end']} 主对话 {s(r['main'])/1e6:.1f}M（新读入 {r['main']['new']/1e6:.2f}M 输出 {r['main']['out']/1e3:.0f}k）｜子任务 {len(r['subs'])} 个 {s(sub)/1e6:.1f}M（新读入 {sub['new']/1e6:.2f}M 输出 {sub['out']/1e3:.0f}k）")
small = [r for r in runs if s(r['main']) + sum(s(x) for x in r['subs']) < 300000]
print(f"空转唤醒 {len(small)} 次，合计 {sum(s(r['main']) for r in small)/1e6:.2f}M")
print(f"总计 {s(G)/1e6:.1f}M：读缓存 {G['cache']/1e6:.1f}M，新读入 {G['new']/1e6:.1f}M，输出 {G['out']/1e6:.2f}M")
