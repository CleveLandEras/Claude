"""V49 未完成 80 张单的去向：对照 10/28 快照，把 Jira 只读查询结果分成四类。

用法：python3 -I 查去向.py <Jira 查询结果.json> <输出名，如 发版后_1030>
Jira 查询：key in (快照里的 80 个编号)，字段 status, fixVersions, resolutiondate, resolution, updated
"""
import json, sys, collections, os

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, '..', '补查_1028', 'V49未完成_快照_1028.json')
RELEASE = '2026-10-29'  # V49 发版日；Jira 上 V46–V49 都没标「已发布」，只能按日期判断


def ver_no(name):
    # 08_V49_10.29 -> 49
    try:
        return int(name.split('_')[1].lstrip('V'))
    except (IndexError, ValueError):
        return 0


def classify(src):
    snap = {i['key']: i for i in json.load(open(SNAP))['issues']}
    nodes = json.load(open(src))['issues']['nodes']
    rows = []
    for x in nodes:
        f = x['fields']
        names = [v['name'] for v in f['fixVersions']]
        nos = [ver_no(n) for n in names]
        old = snap[x['key']]
        done = f['status']['statusCategory']['key'] == 'done'
        resolved = (f.get('resolutiondate') or '')[:10]
        if done:
            cat = '已关闭（发版日及之前）' if resolved and resolved <= RELEASE else '已关闭（发版后）'
        elif 49 not in nos:
            cat = '未完成，已从 V49 移除'
        elif max(nos) > 49:
            added = set(names) - set(old['fixVersions'])
            cat = '未完成，挂了 V50 或更晚（10/28 后新加挂）' if any(ver_no(n) > 49 for n in added) else '未完成，挂了 V50 或更晚（10/28 前已挂）'
        else:
            cat = '未完成，仍只挂到 V49'
        rows.append({'key': x['key'], 'type': old['type'], 'summary': old['summary'],
                     'statusNow': f['status']['name'], 'statusAt1028': old['status'],
                     'fixVersionsNow': names, 'fixVersionsAt1028': old['fixVersions'],
                     'resolved': resolved or None, 'category': cat})
    missing = set(snap) - {r['key'] for r in rows}
    return rows, missing


if __name__ == '__main__':
    src, name = sys.argv[1], sys.argv[2]
    rows, missing = classify(src)
    cats = collections.Counter(r['category'] for r in rows)
    by_type = collections.defaultdict(collections.Counter)
    for r in rows:
        by_type[r['category']][r['type']] += 1
    out = {'queriedFor': name, 'release': RELEASE, 'total': len(rows), 'missing': sorted(missing),
           'summary': dict(cats), 'byType': {k: dict(v) for k, v in by_type.items()}, 'issues': rows}
    json.dump(out, open(os.path.join(HERE, name + '.json'), 'w'), ensure_ascii=False, indent=1)
    for k, v in sorted(cats.items()):
        print(f'{v:3d}  {k}  {dict(by_type[k])}')
    if missing:
        print('查询里缺这些单：', sorted(missing))
