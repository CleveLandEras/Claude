# Q175 子问题一：在 分析/A37 第三部分写逐项「有 / 没有 / 未知」表。
# 用法：先运行 q174_build_A37.py（生成第一、二部分），再运行本脚本（替换第三部分）。可重复运行。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, sys, json
BASE = _ROOT + '/'
sys.path.insert(0, BASE + '_scripts')
from q174_data_k import K
from q175_data import ROWS
from q180_data import CONFLICTS, EXIST, NEW

OUT = BASE + '分析/A37_能力线现有能力.md'
txt = open(OUT, encoding='utf-8').read()
head = txt.split('## 第三部分')[0]
BLOCKS = ['弹窗', '标签', '推送', '数据']

Kn = [('K%02d' % i,) + t for i, t in enumerate(K, 1)]   # (id, text, block, actions, rec, src)
used = [0] * len(ROWS)
res = {}
fails = []
for kk in Kn:
    hit = [i for i, rw in enumerate(ROWS) if rw[0] in kk[1]]
    if len(hit) != 1:
        fails.append((kk[0], kk[1], [ROWS[i][0] for i in hit]))
        continue
    used[hit[0]] += 1
    res[kk[0]] = ROWS[hit[0]]
if fails:
    for f_ in fails:
        print('匹配失败', f_)
    print('未被使用的键', [ROWS[i][0] for i, u in enumerate(used) if u == 0])
    raise SystemExit(1)
bad = [(ROWS[i][0]) for i, u in enumerate(used) if u != 1]
assert not bad, ('键没有恰好匹配一个 K 项', bad)
assert len(res) == len(Kn)

def esc(s):
    return str(s).replace('|', '｜').replace('\n', ' ')

def lab(rw):
    return rw[1] + (('（' + rw[2] + '）') if rw[2] else '')

# ---------- 统计 ----------
def stat(ids):
    a = sum(1 for k in ids if res[k][1] == '有')
    b = sum(1 for k in ids if res[k][1] == '没有')
    c = sum(1 for k in ids if res[k][1] == '未知')
    d = sum(1 for k in ids if res[k][2] == '推断有')
    e = sum(1 for k in ids if res[k][2] == '推断没有')
    f = sum(1 for k in ids if res[k][2] == '无法推断')
    assert a + b + c == len(ids) and d + e + f == c
    return a, b, c, d, e, f
allids = [kk[0] for kk in Kn]
S_all = stat(allids)
S_blk = {b: stat([kk[0] for kk in Kn if kk[2] == b]) for b in BLOCKS}

# ---------- 自检：反例检查 1–6 + 通用规则 ----------
def K_of(needle):
    c = [kk[0] for kk in Kn if needle in kk[1]]
    assert len(c) == 1, (needle, c)
    return c[0]
chk = []
k_ = K_of('弹窗规则的对象可以选带排除栏的群组'); chk.append((1, k_, '未知', '推断有'))
k_a = K_of('平台有弹窗曝光的埋点记录'); k_b = K_of('平台有弹窗点击的埋点记录'); chk.append((2, k_a + '、' + k_b, '未知', '推断有'))
k_ = K_of('取每人每自然月储值'); chk.append((3, k_, '未知', '无法推断'))
k_ = K_of('每个排序项可以设每日次数与冷却时间'); chk.append((4, k_, '有', ''))
k_ = K_of('玩家关闭后当日不再弹出'); chk.append((5, k_, '未知', '推断没有'))
k_ = K_of('标签群组可以引用另一个群组'); chk.append((6, k_, '没有', ''))
chk_ok = []
for n, ks, st, dr in chk:
    ok_ = all(res[x][1] == st and res[x][2] == dr for x in ks.split('、'))
    chk_ok.append(ok_)
# 出处位置、出处类型里不得出现不能当出处的文件
BAN = re.compile(r'(?<![0-9A-Za-z])0[2-9](?![0-9])|C1|C2|A\d{2}|汇报|同事草稿|设计卡|推进计划|审查')
ban_hits = [(k, res[k][4], res[k][5]) for k in allids if BAN.search(res[k][4] + res[k][5])]
# 有 / 没有 必须有出处原话（带引号）与出处位置
yn_noquote = [k for k in allids if res[k][1] in ('有', '没有') and ('「' not in res[k][3] or res[k][4] in ('—', ''))]
# 推断有 / 推断没有 必须写了依据
infer_nobasis = [k for k in allids if res[k][2] in ('推断有', '推断没有') and ('推断依据' not in res[k][3] and '很可能' not in res[k][3] and '待问' not in res[k][3] and '字面' not in res[k][3] and '按推断推进' not in res[k][3] and '推断）' not in res[k][3])]
# 「无出处」的必须是未知
noloc_not_unknown = [k for k in allids if res[k][4] == '—' and res[k][1] != '未知']
print('统计', S_all, S_blk)
print('反例检查', list(zip([c[0] for c in chk], chk_ok)))
print('出处位置/类型里的禁用文件：', ban_hits)
print('有/没有缺引文或位置：', yn_noquote)
print('推断方向缺依据：', infer_nobasis)
print('无出处但不是未知：', noloc_not_unknown)
all_pass = all(chk_ok) and not ban_hits and not yn_noquote and not noloc_not_unknown

# ---------- Q180：未知项的去向（确认人 + 问句或已在哪里问）----------
unk = [k for k in allids if res[k][1] == '未知']
assign = {}
dups, extra = [], []
covered_exist, covered_new = [], []
for ks, where, quote_, who in EXIST:
    for k in ks:
        if k in assign:
            dups.append(k)
        if k not in unk:
            extra.append(k)
        assign[k] = (who, '已在 ' + where + ' 问')
        covered_exist.append(k)
for qid, who, qtext, ks, note in NEW:
    for k in ks:
        if k in assign:
            dups.append(k)
        if k not in unk:
            extra.append(k)
        assign[k] = (who, '新问句 ' + qid)
        covered_new.append(k)
miss = [k for k in unk if k not in assign]
overlap = [k for k in covered_new if k in covered_exist]
BADQ = re.compile(r'请尽快|今天|马上|立刻|急|邮箱|电话|手机号|@')
bad_q = [q[0] for q in NEW if BADQ.search(q[2])]
multi_q = [q[0] for q in NEW if re.search(r'，且|以及', q[2])]
two_q = [q[0] for q in NEW if q[2].count('？') > 1]
print('Q180：未知', len(unk), '去向', len(assign), '已在别处', len(covered_exist), '新问句覆盖', len(covered_new), '新问句', len(NEW), '重复', dups, '缺', miss, '多出', extra, '违规问句', bad_q, '两问号', two_q, '重叠', overlap)
assert not dups and not miss and not extra and not overlap

L = []
w = L.append
w('## 第三部分　逐项有 / 没有 / 未知（Q175），冲突清单与确认人、问句（Q180）')
w('')
w('> 状态：**Q175（逐项定性）、Q180（冲突清单、确认人与问句）已执行，待审查复核；待 Dk 验收**。脚本：`_scripts/q175_data.py`（逐项数据）、`_scripts/q180_data.py`（冲突与问句）、`_scripts/q175_build_part3.py`（生成本部分，先运行 `q174_build_A37.py` 再运行它）。设计卡：`过程记录/设计卡.md` Q175。')
w('> 出处只限工作原则 v3 约束 120：盘点、答复登记（含「Dk 既有资料」「Cowork 汇总 v2」两行）、截图（只用已被描述过的内容）、`数据/` 字段与说明。04、05、06、07、02、03、08、09、C1、C2、A 编号分析、决策汇报、同事草稿都不当出处；它们引用了某个事实时，已顺着找原始出处。')
w('')
w('### 结论（判读规则 5）')
w('')
w(f'K 项共 {len(allids)} 项中，**有 {S_all[0]} 项、没有 {S_all[1]} 项、未知 {S_all[2]} 项**（其中推断有 {S_all[3]}、推断没有 {S_all[4]}、无法推断 {S_all[5]}）。')
w('')
w('| 块 | K 项数 | 有 | 没有 | 未知 | 其中推断有 | 其中推断没有 | 其中无法推断 |')
w('|---|---|---|---|---|---|---|---|')
for b in BLOCKS:
    s = S_blk[b]
    n = sum(1 for kk in Kn if kk[2] == b)
    w(f'| {b} | {n} | {s[0]} | {s[1]} | {s[2]} | {s[3]} | {s[4]} | {s[5]} |')
s = S_all
w(f'| 合计 | {len(allids)} | {s[0]} | {s[1]} | {s[2]} | {s[3]} | {s[4]} | {s[5]} |')
w('')
w('本节只记状态与出处，不判断哪些能力够用、哪些该开发，不按状态给能力排先后（那是第二至四环的事）。「未知」项的确认人与问句、与 04、05、06、07 现文的冲突清单见后面两节（Q180）。')
w('')
w('**三种状态的含义**：**有** = 出处直接记载平台现在能做，且没有其他出处矛盾；**没有** = 出处直接记载现在不能做、没有、写死或「计划增加」，且没有其他出处矛盾；**未知** = 其余一切（无出处；出处只有推断、「很可能」、Dk 同意按推断推进；出处之间矛盾；出处只覆盖相近但不同的一件事；只有「本项目的导出里没有」）。未知项的**推断方向**是推断，写「推断有 / 推断没有」时在「出处原话」列写了依据，依据不足写「无法推断」；任何推断都不升格为有或没有。')
w('')
w('### 逐项定性表（顺序同第二部分）')
w('')
for b in BLOCKS:
    w(f'#### {b}')
    w('')
    w('| 编号 | 能力项 | 状态 | 推断方向 | 出处原话 | 出处位置 | 出处类型 | 与其他出处冲突 |')
    w('|---|---|---|---|---|---|---|---|')
    for kk in Kn:
        if kk[2] != b:
            continue
        rw = res[kk[0]]
        w(f'| {kk[0]} | {esc(kk[1])} | {rw[1]} | {rw[2] or "—"} | {esc(rw[3])} | {esc(rw[4])} | {esc(rw[5])} | {esc(rw[6]) if rw[6] else "—"} |')
    w('')
w('### 与 04、05、07（及 06）现文的冲突清单（Q180）')
w('')
w('只列，不改 04、05、06、07（冻结，能力线第二环起按结论解冻）。冲突类型：04/05/07 写成确定而本表是未知 / 写成未知或推断而本表有出处定了 / 两者方向相反（本次没有发现方向相反的）。')
w('')
w('| 编号 | 文件 | 原句 | 本表状态与出处 | 冲突类型 |')
w('|---|---|---|---|---|')
for i_, c_ in enumerate(CONFLICTS, 1):
    w(f'| C{i_} | {esc(c_[0])} | {esc(c_[1])} | {esc(c_[2])} | {c_[3]} |')
w('')
w(f'共 {len(CONFLICTS)} 行。其余各处（04 功能 3 新手弹窗、05 交集与排除栏、07 快显写死与定向）与本表一致，没有列。')
w('')
w('### 未知项的确认人与问句（Q180）')
w('')
w('**是否转问、何时转问由 Dk 决定**（工作原则第一点五节）；本节只是把问句写好、查过重，agent 不对外发送。确认人按「谁最可能几分钟答得出」四选一：后台能不能选 / 设某项 → 运营；接口、埋点、通路能力 → 研发；能不能取某字段 → 数据组；Dk 看一眼后台截图就能定的 → Dk 自查。')
w('')
w(f'未知项 {len(unk)} 项：**已被现有问句覆盖 {len(covered_exist)} 项（不写新问句，只写「已在 X 问」）**；**新问句 {len(NEW)} 句，覆盖 {len(covered_new)} 项**。问句数量不设目标，能合并的合并（同一件事一并答），不为了少几句把两件事塞进一句。')
w('')
for who in ('运营', '研发', '数据组', 'Dk 自查'):
    nw = [q for q in NEW if q[1] == who]
    ex = [e for e in EXIST if e[3] == who]
    w(f'#### 确认人：{who}（新问句 {len(nw)} 句；已在别处问的 {sum(len(e[0]) for e in ex)} 项）')
    w('')
    if nw:
        w('| 问句编号 | 问句原话 | 覆盖的能力项 | 说明 |')
        w('|---|---|---|---|')
        for q in nw:
            w(f'| {q[0]} | {esc(q[2])} | {"、".join(q[3])} | {esc(q[4]) if q[4] else "—"} |')
        w('')
    if ex:
        w('| 已在哪里问 | 覆盖的能力项 | 原话或位置 |')
        w('|---|---|---|')
        for e in ex:
            w(f'| {esc(e[1])} | {"、".join(e[0])} | {esc(e[2])} |')
        w('')
w('**逐项对照（未知项 → 确认人 → 问句或已在哪里问）**')
w('')
w('| 编号 | 确认人 | 处理 |')
w('|---|---|---|')
for k in sorted(unk, key=lambda s: int(s[1:])):
    w(f'| {k} | {assign[k][0]} | {esc(assign[k][1])} |')
w('')
w('方案线同一件、已在等答复的有：K01、K03（03 K5 第 0 步）、K06（Dk 自查④）、K29 与 K97（Dk 自查③）、K94（Dk 自查①）、K35、K36、K131（Dk 自查③）、K22 与 K13（Dk 已定按推断推进），这些不重复加问。')
w('')
w('##### 检查（Q180）')
w('')
w(f'1. 每个未知项恰好有一处去向：未知 {len(unk)} 项，去向 {len(assign)} 项，重复 {len(dups)}，缺 {len(miss)}，多出（不是未知的）{len(extra)}。' + ('通过。' if (not dups and not miss and not extra) else '未通过：' + str((dups, miss, extra))))
w(f'2. 新问句无催促语、无联系方式、无会员编号以外的个人信息：命中 {len(bad_q)} 句。' + ('通过。' if not bad_q else '未通过：' + str(bad_q)))
w(f'3. 新问句与「已在别处问」不重复：新问句覆盖的项里，有 {len(overlap)} 项同时出现在「已在别处问」。' + ('通过。' if not overlap else '未通过：' + str(overlap)))
w(f'4. 新问句一句一事：问句里出现「，且」「以及」连接两件事的 {len(multi_q)} 句；一句里有两个问号的 {len(two_q)} 句。数据类问句统一写成「按会员编号，能不能取到……」一问，答「不能」时 K 项里「平台有没有」一半同时有了线索，仍是未知，不升格。' + ('通过。' if (not multi_q and not two_q) else '未通过：' + str((multi_q, two_q))))
w('')
w('### 反例检查（Q175）')
w('')
EX = [
    '虚构「弹窗对象可以选带排除栏的群组；出处：答复登记「对外问题精简」①「问题 4 弹窗对象能用排除……按推断推进」」→ 应为未知（推断有）',
    '虚构「平台有弹窗曝光、点击埋点；出处：「Dk 既有资料」④「很可能已经存在」」→ 应为未知（推断有）',
    '虚构「数据组能取每人每月储值；出处：数据/说明「金额都是账号累计值，不能按月拆分」」→ 应为未知（无法推断），不是没有',
    '虚构「单个弹窗项可设每日次数与冷却；出处：盘点第一节「可限单个弹窗每日次数上限与冷却时间」」→ 应为有',
    '虚构「玩家关闭弹窗后当日不再弹出；出处：盘点第一节「不支持负反馈降权（无法做到连续关闭 N 次后自动静默）」」→ 应为未知（推断没有），不是没有',
    '虚构「群组之间可以取交集；出处：盘点「计划增加交集」」→ 应为没有',
]
real = {1: 'K%s', }
for (n, ks, st, dr), ok_ in zip(chk, chk_ok):
    w(f'{n}. **{EX[n-1]}**。本表对应 {ks}：{st}{("（" + dr + "）") if dr else ""}。' + ('通过。' if ok_ else '未通过。'))
w(f'7. **出处位置与出处类型里没有不能当出处的文件**（04、05、06、07、02、03、08、09、C1、C2、A 编号分析、汇报、同事草稿、设计卡）：脚本逐行检索，命中 {len(ban_hits)} 处。' + ('通过。' if not ban_hits else '未通过：' + str(ban_hits)))
w(f'8. **「有」「没有」都带出处原话（引号）与出处位置**：缺的 {len(yn_noquote)} 项。' + ('通过。' if not yn_noquote else '未通过：' + str(yn_noquote)))
w(f'9. **「无出处」的都是未知**：不是未知的 {len(noloc_not_unknown)} 项。' + ('通过。' if not noloc_not_unknown else '未通过：' + str(noloc_not_unknown)))
w(f'10. **每个 K 项恰好有一行定性**：K 项 {len(Kn)} 项，定性行 {len(res)} 行，脚本断言一一对应。通过。')
w('')
w('### 局限（Q175）')
w('')
w('1. 出处只限约束 120。我们自己写的 04、05、06、07、02、03、08、09、C1、C2 和同事草稿里的说法，凡找不到盘点、答复登记、截图、`数据/` 的原始出处，一律按「无出处」处理为未知；这不等于平台没有，只是本项目手里没有可引的原始记载。')
w('2. 截图只用答复登记 Cowork 汇总 v2 ②③ 已描述过的内容。截图里没看到某一项（如排除栏），只说明没看到，没有据此定「没有」。')
w('3. 「推断没有」的几项（如附录一「标签全清单」里没有某标签）依据是清单里没写，而清单是否完整盘点没有说明（盘点正文称「约 100 个」，Cowork 汇总 v2 ② 称「共 106 个标签」）；它们保持未知，不能当作没有。')
w('4. 盘点是 2026-09-24 的快照，Dk 既有资料是 8/31–9/02 的文档，二者在弹窗时机个数上不一致（4 个与 5 个），本表按「未知」处理并写出两处原话。')
w('5. 「语义不明的五条卡别标签……口径已经能读懂」标「没有」，是指盘点记录的当前状态（口径读不懂），不是平台功能缺失；对照标签脚本即可核对。')
w('6. 问句答复之前，第二环（缺口卡住了什么）对「未知」项只能按未知写，不得按推断方向当作有或没有。')
w('')
new = head + '\n'.join(L)
# 顶部状态行同步
new = new.replace('Q181 按审查 R249、R250、R251 修订；待审查复核；待 Dk 验收**。设计卡', 'Q181 按审查 R249、R250、R251 修订；Q175、Q180 在第三部分续写；待审查复核；待 Dk 验收**。设计卡')
new = new.replace('第三部分（逐项有 / 没有 / 未知）由 Q175 在本文件续写，本节不判断任何一项能力有没有，不排优先级，不写需求。', '第三部分（逐项有 / 没有 / 未知）由 Q175 在本文件续写；第一、二部分不判断任何一项能力有没有，不排优先级，不写需求。')
open(OUT, 'w', encoding='utf-8').write(new)
print('written part3', len(L), 'lines; all_pass', all_pass)
json.dump({'S_all': S_all, 'S_blk': S_blk, 'all_pass': all_pass}, open(BASE + '_versions/q175_counts.json', 'w', encoding='utf-8'), ensure_ascii=False)
