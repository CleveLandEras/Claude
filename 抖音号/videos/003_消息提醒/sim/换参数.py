"""换参数核结论：一次只动一个参数，再加两组极端组合。结论三条：
C1 全开的打断次数是另两种的 1.5 倍以上；C2 分批的平均带宽和全关差不到 5 个点，且比全开高 8 个点以上；C3 分批的要紧事平均晚到比全关短。"""
import copy, json, importlib.util, sys
spec = importlib.util.spec_from_file_location('m', '一天三遍.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base = m.P
def var(**kw):
    p = copy.deepcopy(base)
    for k, v in kw.items():
        if k == 'group': p['share'] = dict(group=v, private=round((1 - v) * 0.44 / 0.69, 3), app=round((1 - v) * 0.25 / 0.69, 3))
        elif k == 'urgent_noat': p['urgent_src'] = dict(private_white=1 - v - 0.1, group_at=0.1, group_noat=v - 0.1 if v > 0.1 else 0.0, app=0.1 if v > 0.1 else v)
        else: p[k] = v
    return p
cases = [('基准', {})]
cases += [(f'一天 {n} 条', dict(msgs_per_day=n)) for n in (30, 100)]
cases += [(f'缓 {r} 分钟', dict(recover=r)) for r in (10, 25)]
cases += [(f'拿手机时看到要紧事 {c}', dict(see_on_pickup=c)) for c in (0.2, 1.0)]
cases += [(f'私聊白名单 {w}', dict(white_private_share=w)) for w in (0.15, 0.5)]
cases += [('群消息占一半', dict(group=0.5))]
cases += [('要紧事一半不在白名单', dict(urgent_noat=0.5))]
cases += [('极端：100 条、群占一半、缓 25 分钟', dict(msgs_per_day=100, group=0.5, recover=25))]
cases += [('极端：30 条、缓 10 分钟、拿手机必看到', dict(msgs_per_day=30, recover=10, see_on_pickup=1.0))]
rows = []
for name, kw in cases:
    r = m.summarize(var(**kw), days=800, seed=7)
    a, b, c = r['全开'], r['全关'], r['分批']
    c1 = a['打断_全天'] >= 1.5 * max(b['打断_全天'], c['打断_全天'])
    c2 = abs(c['平均带宽'] - b['平均带宽']) < 5 and c['平均带宽'] - a['平均带宽'] > 8
    c3 = c['要紧的事_平均晚到_分'] < b['要紧的事_平均晚到_分']
    rows.append((name, a['打断_全天'], b['打断_全天'], c['打断_全天'], a['平均带宽'], b['平均带宽'], c['平均带宽'], a['最长连续专注_分'], b['最长连续专注_分'], c['最长连续专注_分'], b['要紧的事_平均晚到_分'], c['要紧的事_平均晚到_分'], c1, c2, c3))
print('| 情形 | 打断 开/关/分 | 带宽 开/关/分 | 最长专注 开/关/分 | 要紧晚到 关/分 | C1 | C2 | C3 |')
print('|---|---|---|---|---|---|---|---|')
for r in rows:
    print(f'| {r[0]} | {r[1]:.0f}/{r[2]:.0f}/{r[3]:.0f} | {r[4]:.0f}/{r[5]:.0f}/{r[6]:.0f}% | {r[7]:.0f}/{r[8]:.0f}/{r[9]:.0f} 分 | {r[10]:.0f}/{r[11]:.0f} 分 | {"✓" if r[12] else "✗"} | {"✓" if r[13] else "✗"} | {"✓" if r[14] else "✗"} |')
