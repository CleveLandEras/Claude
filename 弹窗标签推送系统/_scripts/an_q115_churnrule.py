"""Q115：潜在流失扩到金卡以上，怎么配才能有覆盖、又不比现状多弹。照设计卡 Q115 S1–S6。
只读，不带参数。模拟器 simulate() 直接复用 an_q68_fatigue.py 的写法（此处原样搬入，避免执行那个脚本的输出）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

B = _ROOT + '/数据/'
EX = ['機器人', '測試帳號']

ID5 = [('月月抽', 1, 0), ('限时挑战', 2, 1800), ('卡别直升活动', 2, 1800), ('发信送奖', 1, 0),
       ('天天敲蛋礼V2', 1, 0), ('BOSS战', 1, 0), ('回流任务', 1, 0), ('每日补给计划', 1, 0),
       ('连线格格送', 1, 0), ('活动排行榜', 1, 0)]
D = {n: (d, c) for n, d, c in ID5}
NEW02 = [(n,) + D[n] for n in ['限时挑战', '卡别直升活动', '发信送奖', '天天敲蛋礼V2', 'BOSS战', '每日补给计划', '连线格格送', '活动排行榜']]
RET02 = [(n,) + D[n] for n in ['回流任务', '月月抽', '限时挑战', '卡别直升活动', '发信送奖', '天天敲蛋礼V2', 'BOSS战', '每日补给计划', '连线格格送', '活动排行榜']]
ID10 = [('每日补给计划(ID10/11)', 20, 1800)]
ALL = {n for n, _, _ in ID5}
PUYIN = ALL - {'月月抽'}


def simulate(order, entries, eligible=None, pick=2):
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


def single(order, elig, pick):
    return len(simulate(order, [0], elig, pick)[0])


def daily(order, elig, pick):
    r = simulate(order, [i * 31 * 60 for i in range(60)], elig, pick)
    return sum(len(x) for x in r)


def ident_rules(identity, gold, id5=ID5, new02=NEW02, ret02=RET02):
    """身份规则（02 第一张卡修正后：新增 1 个、回流 2 个、其余 = ID5 2 个）。返回 [(order, elig, pick)]"""
    elig = ALL if gold else PUYIN
    if identity == '新增':
        return [(new02, None, 1)]
    if identity == '回流':
        return [(ret02, elig, 2)]
    return [(id5, elig, 2)]


def cell(scen, identity, gold, hit, k=1):
    """返回 (单次后台最多, 活动类每日上限, 储值位每次) ；scen: 现状/基线02/甲/乙/乙压/丙"""
    id5 = ID5
    if scen == '现状':
        rules = [(ID5, ALL if gold else PUYIN, 2)]
        if (not gold) and hit:
            rules.append((ID10, None, 1))
        stor = 1
    else:
        if scen == '乙压':
            id5 = [(n, (1 if n == '限时挑战' else d), c) for n, d, c in ID5]
            ret = [(n, (1 if n == '限时挑战' else d), c) for n, d, c in RET02]
            new = [(n, (1 if n == '限时挑战' else d), c) for n, d, c in NEW02]
            rules = ident_rules(identity, gold, id5, new, ret)
        else:
            rules = ident_rules(identity, gold)
        stor = 1
        if hit:
            if not gold:
                rules.append((ID10, None, 1))          # 普银：ID10/ID11 不变
            elif scen == '甲':
                rules.append((ID10, None, 1))
            elif scen in ('乙', '乙压'):
                rules.append(([('活动位·运营指定', k, 1800)], None, 1))
            elif scen == '丙':
                stor = 1                                # 新储值规则替换 ID6，仍 1 个
    s = sum(single(o, e, p) for o, e, p in rules) + stor
    dl = sum(daily(o, e, p) for o, e, p in rules)
    return s, dl, stor


print('===== S1 复现（与 A21 表 3 对照）')
for ident in ['新增', '回流', '其余']:
    for hit in [False, True]:
        a = cell('现状', ident, True, hit)
        b = cell('甲', ident, True, hit)
        print(f'  金卡以上·{ident}·{"下滑" if hit else "未下滑"}：现状 单次 {a[0]} / 活动类每日 {a[1]}；原写法(甲) 单次 {b[0]} / 每日 {b[1]}')
for hit in [False, True]:
    a = cell('现状', '其余', False, hit)
    print(f'  普银·{"下滑" if hit else "未下滑"}（现状）：单次 {a[0]} / 活动类每日 {a[1]}（A21：普银下滑 4 / 11 + 20 = 31）')

print('\n===== S2 各配法 × 身份 × 是否命中（金卡以上）：单次后台最多 / 活动类每日上限 / 储值位每次；括号为与现状之差')
for scen, k in [('甲', 1), ('乙', 1), ('乙', 2), ('乙压', 1), ('丙', 1)]:
    lab = scen + (f'(k={k})' if scen in ('乙', '乙压') else '')
    for ident in ['新增', '回流', '其余']:
        base = cell('现状', ident, True, True)
        c = cell(scen, ident, True, True, k)
        ok = all(x <= y for x, y in zip(c, base))
        print(f'  {lab}｜{ident}·下滑：单次 {c[0]}({c[0]-base[0]:+d}) 每日 {c[1]}({c[1]-base[1]:+d}) 储值 {c[2]}({c[2]-base[2]:+d}) → {"三项都不高于现状" if ok else "有一格更高"}')

print('\n===== 反例检查 ①：主推(丙)下，普银下滑者、未下滑的金卡以上，与「只做 02 第一张卡」的基线逐格对比（应完全相同）')
for gold, hit, lab in [(False, True, '普银·下滑'), (False, False, '普银·未下滑'), (True, False, '金卡以上·未下滑')]:
    for ident in ['新增', '回流', '其余']:
        a = cell('基线02', ident, gold, hit)
        b = cell('丙', ident, gold, hit)
        print(f'  {lab}·{ident}：基线 {a}；丙 {b}；{"相同" if a == b else "不同"}')

print('\n===== 反例检查 ②：主推(丙)下，金卡以上下滑者同时命中的规则')
print('  身份规则（新增 / 回流 / 其余，三选一）+ 高卡储值下滑（储值类，1 个）；ID6 与「通用弹窗·金卡以上」都排除了下滑者；ID7 只在破产时触发。每次进大厅储值类 = 1 个。')

print('\n===== 规则条数（新增 / 修改 / 停用）')
print('  甲：新增 0 / 修改 1（ID10 去掉普卡限定）/ 停用 1（ID11）')
print('  乙：新增 1 / 修改 0 / 停用 0')
print('  乙压：新增 1 / 修改 3（ID5、回流规则、新增规则里的限时挑战次数 2 → 1，且全员受影响）/ 停用 0')
print('  丙：新增 2（高卡储值下滑；通用弹窗·金卡以上）/ 修改 1（ID6 对象改为普卡、银卡）/ 停用 0；ID10、ID11 不变')
print('  丁：三条身份规则各拆成（普银 / 金卡以上排除下滑 / 金卡以上下滑副本）共 9 条，比只做 02 第一张卡的 3 条多 6 条')

print('\n===== 人数上界（复算 A21）')
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(EX)].copy()
amt = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
gapd = (pd.Timestamp('2026-09-16') - pd.to_datetime(a['最後登入時間'], errors='coerce').dt.normalize()).dt.days
main = ~a['身份'].isin(['VIP', '黑名單'])
pay = amt > 0
gold = a['卡别'] >= 3
nr = a['身份'].isin(['新增', '回流'])
print('  活跃', len(a))
print('  金卡以上有储值（主数）', int((gold & pay & main).sum()), '；其中 0–7 天', int((gold & pay & main & (gapd <= 7)).sum()))
print('  金卡以上有储值（主数）中：新增、回流', int((gold & pay & main & nr).sum()), '；其余（含持续）', int((gold & pay & main & ~nr).sum()))
print('  金卡以上（含 VIP、黑名单）有储值', int((gold & pay).sum()), '；金卡以上全部', int(gold.sum()))
for c in range(3, 8):
    print(f'  卡别 {c}：有储值（主数）{int(((a["卡别"] == c) & pay & main).sum())}')
