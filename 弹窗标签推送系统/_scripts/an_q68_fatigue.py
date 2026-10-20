"""Q68：弹窗疲劳与规则叠加（D7）。照设计卡 Q68 S1–S5；按推进计划 21:2x，不可参与的项一律跳过（问题 3 答复），普银不计月月抽。
只读，不带参数。模拟器 simulate() 供 Q69 复用。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

B = _ROOT + '/数据/'
EX = ['機器人', '測試帳號']

# ---------- 配置（环节1 第二节第 2、3 小节；02 附录一、三） ----------
# (名称, 每日次数, 冷却秒)
ID5 = [('月月抽', 1, 0), ('限时挑战', 2, 1800), ('卡别直升活动', 2, 1800), ('发信送奖', 1, 0),
       ('天天敲蛋礼V2', 1, 0), ('BOSS战', 1, 0), ('回流任务', 1, 0), ('每日补给计划', 1, 0),
       ('连线格格送', 1, 0), ('活动排行榜', 1, 0)]
ID10 = [('每日补给计划(ID10/11)', 20, 1800)]
D = {n: (d, c) for n, d, c in ID5}
NEW02 = [(n,) + D[n] for n in ['限时挑战', '卡别直升活动', '发信送奖', '天天敲蛋礼V2', 'BOSS战', '每日补给计划', '连线格格送', '活动排行榜']]
RET02 = [(n,) + D[n] for n in ['回流任务', '月月抽', '限时挑战', '卡别直升活动', '发信送奖', '天天敲蛋礼V2', 'BOSS战', '每日补给计划', '连线格格送', '活动排行榜']]


def simulate(order, entries, eligible=None, pick=2):
    """order: [(名称, 每日次数, 冷却秒)]；entries: 当天各次进大厅的时刻（秒，升序）；eligible: 可参与的项名集合（None = 全部）。
    规则：每次进大厅从第 1 项往下取，跳过不可参与、当天次数已用完、距上次弹出未满冷却的项，取满 pick 个或取完为止。
    返回每次进大厅弹出的项名列表。"""
    used, last, out = {}, {}, []
    for t in entries:
        got = []
        for name, daily, cd in order:
            if len(got) >= pick:
                break
            if eligible is not None and name not in eligible:
                continue
            if used.get(name, 0) >= daily:
                continue
            if name in last and t - last[name] < cd:
                continue
            got.append(name)
            used[name] = used.get(name, 0) + 1
            last[name] = t
        out.append(got)
    return out


def times(n, gap_min):
    return [i * gap_min * 60 for i in range(n)]


ALL = {n for n, _, _ in ID5}
PUYIN = ALL - {'月月抽'}          # 普卡、银卡：月月抽不可参与，按问题 3 答复跳过
NS = [1, 2, 3, 4, 6, 8, 12]
GAPS = [(10, '10 分钟（在冷却内）'), (31, '≥30 分钟（冷却已过）')]

print('===== S2 进大厅 N 次的后台弹窗上限曲线（累计个数）')
for gap, gl in GAPS:
    print(f'\n-- 间隔 {gl}')
    for label, order, elig, pick in [('ID5·普银', ID5, PUYIN, 2), ('ID5·金卡以上', ID5, ALL, 2),
                                     ('ID10/11', ID10, None, 1), ('02 新增规则', NEW02, None, 2),
                                     ('02 回流规则·普银', RET02, PUYIN, 2), ('02 回流规则·金卡以上', RET02, ALL, 2)]:
        r = simulate(order, times(12, gap), elig, pick)
        cum = [sum(len(x) for x in r[:n]) for n in NS]
        print(f'  {label}: ' + '  '.join(f'N={n}:{c}' for n, c in zip(NS, cum)))
    for label, order, elig in [('ID5·普银', ID5, PUYIN), ('ID5·金卡以上', ID5, ALL), ('02 新增规则', NEW02, None)]:
        total = sum(d for n, d, _ in order if elig is None or n in elig)
        r = simulate(order, times(40, gap), elig)
        c, k = 0, None
        for i, x in enumerate(r, 1):
            c += len(x)
            if c >= total:
                k = i
                break
        print(f'  {label}：当日可弹总数 {total}，第 {k} 次进大厅用完')

print('\n===== 提醒 35：回流任务第几次进大厅第一次出现')
for gap, gl in GAPS:
    for label, order, elig in [('现状 ID5·普卡回流', ID5, PUYIN), ('现状 ID5·金卡以上回流', ID5, ALL),
                               ('02 回流规则·普卡', RET02, PUYIN), ('02 回流规则·金卡以上', RET02, ALL)]:
        r = simulate(order, times(12, gap), elig)
        k = next((i for i, x in enumerate(r, 1) if '回流任务' in x), None)
        print(f'  {gl}｜{label}：第 {k} 次；前 {k} 次弹出 {r[:k]}')

print('\n===== 单次进大厅（第 1 次）弹出')
for label, order, elig, pick in [('ID5·普银', ID5, PUYIN, 2), ('ID5·金卡以上', ID5, ALL, 2), ('02 新增', NEW02, None, 2),
                                 ('02 回流·普银', RET02, PUYIN, 2)]:
    print(f'  {label}: {simulate(order, [0], elig, pick)[0]}')

# ---------- 人群规模（只引用 A7、A15，复算核对） ----------
print('\n===== S3 / S4 人数核对')
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(EX)].copy()
amt = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
gapd = (pd.Timestamp('2026-09-16') - pd.to_datetime(a['最後登入時間'], errors='coerce').dt.normalize()).dt.days
main = ~a['身份'].isin(['VIP', '黑名單'])
pay = amt > 0
py = a['卡别'].isin([1, 2])
gold = a['卡别'] >= 3
print('  活跃', len(a))
print('  普银有储值：含 VIP/黑名单', int((py & pay).sum()), '；主数', int((py & pay & main).sum()))
print('  金卡以上有储值：含', int((gold & pay).sum()), '；主数', int((gold & pay & main).sum()), '；主数且 0–7 天', int((gold & pay & main & (gapd <= 7)).sum()))
print('  全部有储值：含', int(pay.sum()), '；主数', int((pay & main).sum()), '；主数且 0–7 天', int((pay & main & (gapd <= 7)).sum()))
nr = a['身份'].isin(['新增', '回流'])
print('  新增、回流有储值', int((nr & pay).sum()), '；其中金卡以上', int((nr & pay & gold).sum()))
for idn in ['新增', '回流']:
    x = a['身份'] == idn
    print(f'  {idn}：人数 {int(x.sum())}；普银有储值 {int((x & py & pay).sum())}；金卡以上有储值 {int((x & gold & pay).sum())}')
