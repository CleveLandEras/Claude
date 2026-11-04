# -*- coding: utf-8 -*-
"""判配与众数：读 草稿展平.tsv，逐行用框架弹窗段（功能框架_脑图.md 第194–414行）的字段去配，
并算草稿各项众数与框架默认值比较、待查1 两表重合、同一活动跨块出现。

用法：python3 -I 判配与众数.py
输出：本目录 判配结果.tsv；终端打印汇总（供写 嫌疑_a_真实配置试配.md 时引用）。

判定口径（框架字段，行号以 功能框架_脑图.md 为准）：
- 弹出时机（仅进大厅，行323、393）：单选，四个选项。草稿多个时机 → 绕路（选覆盖全部的「每次进大厅，含从游戏返回」，限定靠次数近似）。
- 弹窗形式：框架无此字段，用「点击后是否跳转」（行322、385）映射：活動本身＝跳转本活动页（行385–390 默认是），活動廣告頁＝只弹宣传图。能配（映射，待确认）。
- 每人每天几次（行324、402–405）：能配（本规则另设或活动设置）。
- 每人两次至少隔多久（行325、406–408）：冷却 0 ＝ 不限（行327、408）；1800 秒 ＝ 自定义 30 分钟。能配。
- 发送对象（行281–288）：群组（可多选）。玩家身份、未首储、已首储 能配（工作表2 C3–C5、C12–C13 有标签群组）；卡別 能配（前提：卡别群组已建，框架未写卡别，工作表2 C8–C10 写可直接配卡別）。
- 活动名（行309–310）：可多选，可选范围是未结束的活动和礼包。能配。
- 块级：彈窗權重 无对应字段（框架只有 优先级 拖动排序，行226、201）→ 绕路（按权重排优先级，数值不保存）。
- 块级：縂彈窗數量 → 每次最多弹几个（行305–308，默认 进大厅 3、其他 1）。能配。
- 块级：彈窗排序 → 固定的先后（行315–316）。能配。
- 块级：轮换池 无草稿对应，默认 否（行311–314）。能配。
- 块级：候选数 < 縂彈窗數量 → 嫌疑（每次最多弹的数超过能弹的活动数）。
"""
import csv
import os
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, '草稿展平.tsv')
OUT = os.path.join(HERE, '判配结果.tsv')

TIMING = collections.OrderedDict([
    ('進入大廳', '每次进大厅，含从游戏返回'),
    ('返回大廳', '只在从游戏返回时'),
    ('首次登入', '当天首次登录'),
    ('活動開啓', '活动开始后第一次进大厅（映射）'),
])
FORM = {'活動本身': '点击后跳转=是、跳本活动页', '活動廣告頁': '点击后跳转=否、只弹宣传图'}
DEFAULT_CNT = {'活动': 1, '礼包': 2, '未分': 1}          # 框架行 405、404；未分 按活动处理
DEFAULT_TIMING = {'活动': '進入大廳', '礼包': '返回大廳', '未分': '進入大廳'}
DEFAULT_TOTAL_ENTRY = 3                                    # 框架行 307，进大厅默认 3 个
GROUP_OK = {
    '玩家身份：新增': '群组「玩家身份-新增」（工作表2 C3）',
    '玩家身份：回流': '群组「玩家身份-回流」（工作表2 C13 / I67 同名）',
    '玩家身份：輕回流': '群组「玩家身份-輕回流」（工作表2 C12）',
    '未首儲用戶': '群组「未首储用户」（工作表2 C4）',
    '已首儲用戶': '群组「已首储用户」（工作表2 C5）',
    '普卡, 銀卡': '卡别群组（前提已建；框架未写卡别）',
    '金卡, 白金卡': '卡别群组（前提已建；框架未写卡别）',
    '鑽石卡, 黑卡, 至尊卡': '卡别群组（前提已建；框架未写卡别）',
}


def judge_row(r):
    toks = [t.strip() for t in r['弹出时机'].split(',') if t.strip()]
    if not toks or any(t not in TIMING for t in toks):
        t_v, t_how = '配不出', '未知时机词：' + r['弹出时机']
    elif len(toks) == 1:
        t_v, t_how = '能配', '单选「%s」' % TIMING[toks[0]]
    else:
        t_v = '绕路'
        t_how = ('选「每次进大厅，含从游戏返回」覆盖全部时机，草稿里「%s」的限定靠「每人每天几次」近似，'
                 '不完全等同' % '、'.join(t for t in toks if t != '進入大廳' and t != '返回大廳')
                 .replace('', '') if any(t in toks for t in ('首次登入', '活動開啓')) else
                 '选「每次进大厅，含从游戏返回」覆盖全部时机（草稿同时含进大厅与返回）')
    f = r['弹窗形式']
    if f in FORM:
        f_v, f_how = '能配', '映射：' + FORM[f] + '（框架无「弹窗形式」字段，映射待确认）'
    else:
        f_v, f_how = '配不出', '未知形式：' + f
    try:
        cnt = int(float(r['每日次数']))
        c_v, c_how = '能配', '本规则另设「每人每天几次」=%d' % cnt
    except ValueError:
        c_v, c_how = '配不出', '次数非数字'
    try:
        cool = int(float(r['冷却秒']))
        if cool == 0:
            k_v, k_how = '能配', '「每人两次至少隔多久」选「不限」'
        else:
            k_v, k_how = '能配', '「每人两次至少隔多久」选「自定义」%d 分钟' % (cool // 60)
    except ValueError:
        k_v, k_how = '配不出', '冷却非数字'
    g_v = '能配' if r['派发对象'] in GROUP_OK else '配不出'
    verdicts = [t_v, f_v, c_v, k_v, g_v]
    if '配不出' in verdicts:
        row_v = '配不出'
    elif '绕路' in verdicts:
        row_v = '绕路'
    else:
        row_v = '能配'
    return dict(时机判定=t_v, 时机怎么配=t_how, 形式判定=f_v, 形式怎么配=f_how,
                次数判定=c_v, 冷却判定=k_v, 冷却怎么配=k_how, 发送对象判定=g_v,
                发送对象怎么配=GROUP_OK.get(r['派发对象'], ''), 整行判定=row_v)


def mode(xs):
    c = collections.Counter(xs)
    if not c:
        return None, 0, 0
    top, n = c.most_common(1)[0]
    return top, n, len(xs)


def main():
    rows = list(csv.DictReader(open(TSV, encoding='utf-8'), delimiter='\t'))
    for r in rows:
        r.update(judge_row(r))
        r['去向'] = ''  # 第二级填：工作表2 的 43 行必填，工作表1 行可留空
    cols = list(rows[0].keys())
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in rows:
            fh.write('\t'.join(str(r[c]) for c in cols) + '\n')

    # 1. 行判定汇总
    print('== 行判定（按表）')
    for s in ['工作表1', '工作表2']:
        sub = [r for r in rows if r['表'] == s]
        cnt = collections.Counter(r['整行判定'] for r in sub)
        print('%s：行 %d；能配 %d，绕路 %d，配不出 %d' % (s, len(sub), cnt['能配'], cnt['绕路'], cnt['配不出']))
    sub = rows
    cnt = collections.Counter(r['整行判定'] for r in sub)
    print('合计：行 %d；能配 %d，绕路 %d，配不出 %d' % (len(sub), cnt['能配'], cnt['绕路'], cnt['配不出']))
    print('时机判定：', dict(collections.Counter(r['时机判定'] for r in rows)))
    print('形式判定：', dict(collections.Counter(r['形式判定'] for r in rows)))
    print('次数判定：', dict(collections.Counter(r['次数判定'] for r in rows)))
    print('冷却判定：', dict(collections.Counter(r['冷却判定'] for r in rows)))
    print('发送对象判定：', dict(collections.Counter(r['发送对象判定'] for r in rows)))

    # 2. 众数 vs 框架默认值（按类型，未分按活动）
    print('\n== 众数 vs 框架默认值')
    for typ in ['活动', '礼包', '未分']:
        sub = [r for r in rows if r['类型'].startswith(typ)]
        if not sub:
            continue
        cnts = [int(float(r['每日次数'])) for r in sub]
        cools = [int(float(r['冷却秒'])) for r in sub]
        tims = [r['弹出时机'] for r in sub]
        forms = [r['弹窗形式'] for r in sub]
        mc, nc, tc = mode(cnts)
        mt, nt, tt = mode(tims)
        mf, nf, tf = mode(forms)
        print('[%s] 行 %d' % (typ, len(sub)))
        print('  每日次数：分布 %s；众数 %s（%d/%d）；框架默认 %d；%s' % (
            dict(collections.Counter(cnts)), mc, nc, tc, DEFAULT_CNT[typ],
            '一致' if mc == DEFAULT_CNT[typ] else '不一致'))
        print('  弹出时机：众数 %s（%d/%d）；框架默认 %s；%s' % (
            mt, nt, tt, DEFAULT_TIMING[typ], '一致' if mt == DEFAULT_TIMING[typ] else '不一致'))
        print('  时机多选行 %d / %d' % (sum(1 for r in sub if ',' in r['弹出时机']), len(sub)))
        print('  弹窗形式：分布 %s；众数 %s（%d/%d）；框架默认 点击后是否跳转=是（对应活動本身）' % (
            dict(collections.Counter(forms)), mf, nf, tf))
    cools = [int(float(r['冷却秒'])) for r in rows if not r['与前块重复']]
    print('冷却（非重复行 %d）：分布 %s；框架默认 留空＝不限(0)；0 的行 %d，1800 的行 %d' % (
        len(cools), dict(collections.Counter(cools)), cools.count(0), cools.count(1800)))
    print('活动行中次数=2 的：%s' % '；'.join(sorted({r['活动或礼包'] for r in rows if r['类型']=='活动' and r['每日次数'] in ('2.0',) and not r['与前块重复']})))
    print('礼包行中次数=1 的（非重复）：%s' % '；'.join('%s(%s)' % (r['活动或礼包'], r['块ID']) for r in rows if r['类型']=='礼包' and r['每日次数']=='1.0'))

    blocks = collections.OrderedDict()
    for r in rows:
        if r['与前块重复']:
            continue
        blocks.setdefault(r['块ID'], dict(表=r['表'], tot=r['块總彈窗數量'], w=r['块权重'],
                                          aud=r['派发对象'], n=0, sec=r['区段']))
        blocks[r['块ID']]['n'] += 1
    tots = [float(b['tot']) for b in blocks.values()]
    mt2, nt2, tt2 = mode([int(t) for t in tots])
    print('块總彈窗數量（有行的非重复块 %d 块）：分布 %s；众数 %s（%d/%d）；框架进大厅默认 %d 个，其他场景 1 个' % (
        len(blocks), dict(collections.Counter(int(t) for t in tots)), mt2, nt2, tt2, DEFAULT_TOTAL_ENTRY))
    print('块权重：%s（框架无权重字段）' % sorted(set(b['w'] for b in blocks.values())))

    # 3. 块级：候选数 < 總彈窗數量；空块
    print('\n== 块级')
    dup_ids = {r['块ID'] for r in rows if r['与前块重复']}
    for bid, b in blocks.items():
        if bid in dup_ids:
            continue
    # 所有块（含空块）需要从原表读，这里只报告有行的块数量与候选数
    for bid, b in blocks.items():
        if float(b['tot']) > b['n']:
            print('候选数 %d < 总弹窗数 %d：%s（%s）' % (b['n'], int(float(b['tot'])), bid, b['aud']))

    # 4. 待查1：两表对照（工作表2 为分母）
    print('\n== 待查1：两表对照')
    s1 = [r for r in rows if r['表'] == '工作表1' and not r['与前块重复']]
    s2 = [r for r in rows if r['表'] == '工作表2']
    MAPPED = {  # 工作表1 派发对象 -> 工作表2 候选行
        '玩家身份：新增': lambda r: r['用户类型'] == '新用戶',
        '未首儲用戶': lambda r: r['派发对象'] == '未首儲用戶',
        '玩家身份：回流': lambda r: r['派发对象'] == '玩家身份：回流',
    }
    n_name = n_name_time = n_exact = 0
    detail = []
    for r in s1:
        cand = [c for c in s2 if MAPPED[r['派发对象']](c)] if r['派发对象'] in MAPPED else []
        same_name = [c for c in cand if c['活动或礼包'] == r['活动或礼包']]
        same_time = [c for c in same_name if c['弹出时机'] == r['弹出时机']]
        exact = [c for c in same_time if c['弹窗形式'] == r['弹窗形式'] and
                 c['每日次数'] == r['每日次数'] and c['冷却秒'] == r['冷却秒']]
        # 不限派发对象的活动名出现
        any_name = [c for c in s2 if c['活动或礼包'] == r['活动或礼包']]
        if same_name:
            n_name += 1
        if same_time:
            n_name_time += 1
        if exact:
            n_exact += 1
        detail.append((r['草稿行'], r['派发对象'], r['活动或礼包'], bool(same_name), bool(same_time),
                       bool(exact), len(any_name)))
    print('工作表1 非重复行 %d：派发对象+活动名 对上 %d，再加时机 对上 %d，再加形式/次数/冷却 全同 %d' % (
        len(s1), n_name, n_name_time, n_exact))
    for d in detail:
        if d[3]:
            print('  草稿行%s %s %s：名同=%s 时机同=%s 全同=%s；工作表2 同名行共 %d' % (d[0], d[1], d[2], d[3], d[4], d[5], d[6]))
    name_only = sorted({r['活动或礼包'] for r in s1} & {r['活动或礼包'] for r in s2})
    print('两表活动名交集（不论派发对象）%d 个：%s' % (len(name_only), '、'.join(name_only)))
    s1_only = sorted({r['活动或礼包'] for r in s1} - {r['活动或礼包'] for r in s2})
    print('只在工作表1 的活动名：%s' % '、'.join(s1_only))
    s2_only = sorted({r['活动或礼包'] for r in s2} - {r['活动或礼包'] for r in s1})
    print('只在工作表2 的活动或礼包名：%s' % '、'.join(s2_only))

    # 5. 同一活动跨块出现（用非重复块）
    print('\n== 同一活动出现在 2 个及以上规则块（非重复块）')
    where = collections.defaultdict(list)
    for r in rows:
        if r['与前块重复']:
            continue
        where[r['活动或礼包']].append('%s(%s)' % (r['块ID'], r['派发对象']))
    for name, lst in sorted(where.items(), key=lambda x: -len(x[1])):
        if len(lst) >= 2:
            print('%s：%d 块：%s' % (name, len(lst), '；'.join(lst)))


if __name__ == '__main__':
    main()
