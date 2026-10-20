# 统计推送后台核心五件（10/17–10/19）的 token 用量：主对话派出的子任务按开始时间归到各件，夜间监督按定时任务另计
# 用法：python3 _scripts/an_核心用量.py   结果写 _versions/夜间推进/核心用量_1019.json
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import glob, json, os, datetime as dt

P = '/Users/decheng.huang/.claude/projects/-Users-decheng-huang-claude---------'
MAIN = 'bf80b515-f484-4425-ac61-c04af1f0e08c'
TZ = dt.timezone(dt.timedelta(hours=8))
W = [('10/17 待改与原型评审', '2026-10-17 15:00', '2026-10-18 01:00'),
     ('核心① 数据', '2026-10-18 13:00', '2026-10-18 16:25'),
     ('核心② 整体控制', '2026-10-18 16:25', '2026-10-18 22:50'),
     ('核心③ 按人群发', '2026-10-18 22:50', '2026-10-19 04:02'),
     ('核心④ 一个入口', '2026-10-19 04:02', '2026-10-19 06:20'),
     ('核心⑤ 写死迁入（进行中）', '2026-10-19 06:20', '2026-10-20 00:00')]
W = [(n, dt.datetime.fromisoformat(a).replace(tzinfo=TZ), dt.datetime.fromisoformat(b).replace(tzinfo=TZ)) for n, a, b in W]


def parse(path):
    seen, first = {}, None
    for line in open(path, encoding='utf-8', errors='ignore'):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if first is None and d.get('timestamp'):
            first = dt.datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00'))
        m = d.get('message') or {}
        u = m.get('usage')
        if not u or d.get('type') != 'assistant':
            continue
        k = m.get('id') or d.get('uuid')
        a = seen.get(k, (0, 0, 0))
        seen[k] = (max(a[0], u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0)),
                   max(a[1], u.get('cache_read_input_tokens', 0)), max(a[2], u.get('output_tokens', 0)))
    new = sum(x[0] for x in seen.values()); cache = sum(x[1] for x in seen.values()); out = sum(x[2] for x in seen.values())
    return first, new, cache, out


res = {n: dict(new=0, cache=0, out=0, agents=0) for n, _, _ in W}
for f in glob.glob(os.path.join(P, MAIN, 'subagents', '*.jsonl')):
    first, new, cache, out = parse(f)
    if not first:
        continue
    for n, a, b in W:
        if a <= first < b:
            r = res[n]; r['new'] += new; r['cache'] += cache; r['out'] += out; r['agents'] += 1
            break

sup = dict(new=0, cache=0, out=0, agents=0)
for f in glob.glob(os.path.join(P, '*.jsonl')):
    head = open(f, encoding='utf-8', errors='ignore').read(3000)
    if 'popup-tag-push-night-global' not in head:
        continue
    first, new, cache, out = parse(f)
    if not first or first < W[0][1]:
        continue
    sid = os.path.basename(f)[:-6]
    for sf in [f] + glob.glob(os.path.join(P, sid, 'subagents', '*.jsonl')):
        _, n2, c2, o2 = parse(sf)
        sup['new'] += n2; sup['cache'] += c2; sup['out'] += o2
    sup['agents'] += 1
res['夜间监督（两晚）'] = sup

out = _ROOT + '/_versions/夜间推进/核心用量_1019.json'
json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for n, r in res.items():
    t = r['new'] + r['cache'] + r['out']
    print(f"{n}\t{t/1e6:.1f}M\t新读入 {r['new']/1e6:.1f}M\t读缓存 {r['cache']/1e6:.1f}M\t输出 {r['out']/1e6:.2f}M\t{r['agents']}")
