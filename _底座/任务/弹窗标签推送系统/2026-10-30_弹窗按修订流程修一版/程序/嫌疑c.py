#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嫌疑c.py  来源 c：交界处——被 ≥2 张分析卡引用的字段，或一个设置会影响另一个设置的字段

怎么找：
  锚点＝卡字段表里有可点控件的字段（只读显示项不做锚点），键＝字段名去掉括号和「·」前缀；键长 ≥3，去掉太泛的词（场景、名称、编号、搜索、筛选、入口等，见 STOP）。
  引用＝卡 A1–A4、B1–B5、C 里「字段表（第 4 节）、规则（第 5 节）、异常（第 6 节）」中含该键的句子（按「。」「；」切）。
  组 G＝同键的字段（如 B3「点击后是否跳转（本规则）」和 C「点击后是否跳转」同键）＋所有引用它的卡。引用它的卡（含定义卡）≥2 张才成组。
  交互对 P＝一个句子里同时出现两个锚点键，并带关系词（覆盖、沿用、合计、扣除、优先、先…再、取较小、以…为准）；按键对归并。
每组一张总表：字段｜各卡原句和行号｜叠加关系｜判定先后。
  叠加关系＝句子里的关系词归类（覆盖／沿用、合计、扣除、优先／排序、先…再、取较小／以…为准）；判定先后＝带「先、再、优先、为准、取较小、最后、之后」的句子摘要。
  整行都没有就写「卡里没写」，并记一条嫌疑。嫌疑按组归并：整组都没写＝一条；有的卡写了有的没写＝一条，列没写的卡。
严重度（思考页第 6 节第 4 条）：判定先后没写、且组里有卡写了合计／覆盖／优先／扣除／先…再／取较小＝高（叠加存在却没说先后，研发会做错）；
  判定先后没写、组里也没有这类关系词＝中（两张卡都提到却没说谁管谁）；叠加关系没写、判定先后有＝低。
用法：python3 嫌疑c.py → 写 本夹/嫌疑_c_交界处.md
"""
import re, sys, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('zl', HERE / '追链.py')
z = importlib.util.module_from_spec(spec); spec.loader.exec_module(z)

STOP = {'场景', '名称', '编号', '搜索', '筛选', '入口', '状态', '操作', '顺序', '复制规则', '预览', '先后', '改前改后', '确认'}
REL = [('覆盖／沿用', r'覆盖|沿用|跟着(变|改)|不跟着|恢复沿用'),
       ('合计', r'合计|加成|相加|加起来|共用一个数|累计'),
       ('扣除', r'扣除|扣掉|排掉'),
       ('优先／排序', r'优先|排在前|排最后|排在后|先于'),
       ('先…再', r'先[^，。；]{0,14}再|先弹|再弹|先按|再按'),
       ('取较小／以…为准', r'取较小|较小|不超过|不能超过|以[^，。；]{0,8}为准|以.{0,6}算')]
ORDER_RE = re.compile(r'先[^，。；]{0,14}再|优先|为准|取较小|较小|最后|先于|排在前|排最后|之后')


def rel_of(sent):
    return [n for n, p in REL if re.search(p, sent)]


def key_of(f):
    n = f['name']
    if '·' in n:
        n = n.split('·')[-1]
    return z.norm(n)


def sentences(text):
    out = []
    for s in re.split(r'[。；]', text):
        s = s.strip()
        if s:
            out.append(s)
    return out


def scan_lines(ch):
    """返回 [(sub-card, 文件名, 行号, 句子, 所在行是哪个字段的定义行(或None))]"""
    out = []
    for key in z.CARD_KEYS:
        p = z.card_file(z.DIG, key)
        L = z.rd(p)
        cur = key if key != 'A' else None
        sec = 0
        defrow = {f['line']: f['code'] for f in ch.fields if f['file'] == str(p)}
        for i, l in enumerate(L):
            m = re.match(r'^## 卡 (A\d)', l)
            if m:
                cur = m.group(1); sec = 0
            m2 = re.match(r'^## (\d+)\.', l) or re.match(r'^\*\*(\d+)\. ', l)
            if m2:
                sec = int(m2.group(1))
            if sec not in (4, 5, 6) or not cur:
                continue
            if l.startswith('|---') or not l.strip():
                continue
            fcode = defrow.get(i + 1)
            if fcode:
                c = z.cells(l)
                body = ' ； '.join(c[2:7])   # 选项和默认值、为什么、不填、更简单、旧后台
            else:
                body = l
            for s in sentences(body):
                out.append((cur, p.name, i + 1, s, fcode))
    return out


def snippet(s, k, n=84):
    j = s.find(k)
    a = max(0, j - 28) if j >= 0 else 0
    t = s[a:a + n]
    return ('…' if a > 0 else '') + t + ('…' if a + n < len(s) else '')


def main():
    ch = z.Chain()
    lines = scan_lines(ch)
    # 锚点
    anchors = {}
    for f in ch.fields:
        if f['kind'] != 'F' or f['card'] == 'A4':
            continue
        if not (ch.fwd.get(f['code'], set()) & set(ch.ctrl)):
            continue
        k = key_of(f)
        if len(k) < 3 or k in STOP:
            continue
        anchors.setdefault(k, []).append(f)
    groups = []
    for k, fs in anchors.items():
        defs = {f['code']: f for f in fs}
        rows = []  # (card, file, line, sent, fcode)
        for (card, fn, ln, s, fcode) in lines:
            if k in z.norm(s):
                rows.append((card, fn, ln, s, fcode))
        # 引用：不是自己的定义行，或是自己的定义行（定义卡）
        cards = []
        for r in rows:
            if r[0] not in cards:
                cards.append(r[0])
        for f in fs:
            if f['card'] not in cards:
                cards.append(f['card'])
        if len(cards) >= 2:
            groups.append((k, fs, rows, cards))
    groups.sort(key=lambda g: (-len(g[3]), g[0]))
    # 交互对
    pairs = {}
    keys = list(anchors.keys())
    for (card, fn, ln, s, fcode) in lines:
        if not rel_of(s):
            continue
        ns = z.norm(s)
        hit = [k for k in keys if k in ns]
        # 去掉被更长键包含的键
        hit = [k for k in hit if not any(k != o and k in o for o in hit)]
        if len(hit) >= 2:
            for a in range(len(hit)):
                for b in range(a + 1, len(hit)):
                    pairs.setdefault(tuple(sorted((hit[a], hit[b]))), []).append((card, fn, ln, s, fcode))
    pairs = sorted(pairs.items(), key=lambda kv: -len(kv[1]))
    out_md = []
    sus = []

    def code_of(k):
        return '、'.join(f['code'] for f in anchors.get(k, []))

    def fill_row(label, rows_):
        sents = []
        seen = set()
        for r in rows_:
            tag = '卡%s 第%d行' % (r[0], r[2])
            if (tag, r[3]) in seen:
                continue
            seen.add((tag, r[3]))
            sents.append((tag, r[3]))
        rel = sorted({x for _, s in sents for x in rel_of(s)})
        od = [t + '：' + snippet(s, '先' if '先' in s else ('优先' if '优先' in s else s[:2]), 70) for t, s in sents if ORDER_RE.search(s)]
        return sents, rel, od

    gi = 0
    body = []
    gsus = []
    for (k, fs, rows, cards) in groups:
        gi += 1
        gid = 'c-G%02d' % gi
        fn = fs[0]['name']
        body.append('### %s　%s　（涉及 %d 张卡：%s）' % (gid, '、'.join(sorted({f['name'] for f in fs}))[:60], len(cards), '、'.join(cards)))
        body.append('')
        body.append('| 字段 | 各卡原句和行号 | 叠加关系 | 判定先后 |')
        body.append('|---|---|---|---|')
        lack_rel, lack_ord, any_rel, any_ord = [], [], False, False
        for card in cards:
            rs = [r for r in rows if r[0] == card]
            if not rs:
                fd = [f for f in fs if f['card'] == card]
                body.append('| %s（卡%s） | 卡里没写：字段在本卡定义，但本卡第 4–6 节没有句子提到它 | 卡里没写 | 卡里没写 |' % (fd[0]['name'] if fd else k, card))
                lack_rel.append(card); lack_ord.append(card)
                continue
            sents, rel, od = fill_row('', rs)
            shown = '<br>'.join('%s：%s' % (t, snippet(s, k, 84).replace('|', '／')) for t, s in sents[:3]) + ('<br>…另 %d 句' % (len(sents) - 3) if len(sents) > 3 else '')
            if rel:
                any_rel = True
            else:
                lack_rel.append(card)
            if od:
                any_ord = True
            else:
                lack_ord.append(card)
            fd = [f['name'] for f in fs if f['card'] == card]
            body.append('| %s（卡%s） | %s | %s | %s |' % ((fd[0] if fd else fn + '（引用）'), card, shown, '；'.join(rel) or '卡里没写',
                                                            '<br>'.join(o.replace('|', '／') for o in od[:2]) or '卡里没写'))
        body.append('')
        all_rel_words = any_rel
        loc = '〔%s〕' % code_of(k)
        first = rows[0] if rows else None
        locs = ('；'.join('卡%s 第%d行' % (r[0], r[2]) for r in rows[:2]))
        # 嫌疑：按组归并，最多三条
        card_rel = {c: bool({x for r in rows if r[0] == c for x in rel_of(r[3])}) for c in cards}
        card_ord = {c: any(ORDER_RE.search(r[3]) for r in rows if r[0] == c) for c in cards}
        rel_words = sorted({x for r in rows for x in rel_of(r[3])})
        if not any_rel:
            gsus.append(('「%s」被 %d 张卡提到（%s），但所有卡都没写叠加关系和判定先后（谁管谁、冲突时听谁的）' % (fn, len(cards), '、'.join(cards)), loc + locs, '中'))
        else:
            noord = [c for c in cards if card_rel[c] and not card_ord[c]]
            if noord:
                gsus.append(('「%s」卡 %s 写了叠加关系（%s）但没写判定先后（谁先谁后、冲突时听谁的）' % (fn, '、'.join(noord), '、'.join(rel_words)), loc + locs, '高'))
            norel = [c for c in cards if not card_rel[c]]
            if norel:
                gsus.append(('「%s」卡 %s 提到它，但没写和卡 %s 讲的叠加关系（%s）怎么对上' % (fn, '、'.join(norel), '、'.join(c for c in cards if card_rel[c]), '、'.join(rel_words)), loc + locs, '低'))
    # 交互对表
    pbody = []
    pi = 0
    for (a, b), rs in pairs[:30]:
        pi += 1
        pid = 'c-P%02d' % pi
        cards = []
        for r in rs:
            if r[0] not in cards:
                cards.append(r[0])
        pbody.append('### %s　「%s」×「%s」　（%d 句，卡 %s）' % (pid, a, b, len(rs), '、'.join(cards)))
        pbody.append('')
        pbody.append('| 字段 | 各卡原句和行号 | 叠加关系 | 判定先后 |')
        pbody.append('|---|---|---|---|')
        lack = []
        seen = set()
        for r in rs[:6]:
            tag = '卡%s 第%d行' % (r[0], r[2])
            if (tag, r[3]) in seen:
                continue
            seen.add((tag, r[3]))
            od = ORDER_RE.search(r[3])
            if not od:
                lack.append(tag)
            pbody.append('| %s × %s（卡%s） | %s：%s | %s | %s |' % (a, b, r[0], tag, snippet(r[3], a, 100).replace('|', '／'), '；'.join(rel_of(r[3])) or '卡里没写',
                                                                  snippet(r[3], '先', 60).replace('|', '／') if od else '卡里没写'))
        pbody.append('')
        if lack and len(lack) == len(seen):
            gsus.append(('「%s」与「%s」同句出现并带关系词（%s），但这些句子都没写先后（%s）' % (a, b, '、'.join(sorted({x for r in rs for x in rel_of(r[3])})), '、'.join(lack[:3])), '〔%s、%s〕%s' % (code_of(a), code_of(b), lack[0]), '中'))
    # 输出
    sevorder = {'高': 0, '中': 1, '低': 2}
    gsus.sort(key=lambda x: sevorder[x[2]])
    out_md.append('# 嫌疑清单 c：交界处')
    out_md.append('')
    out_md.append('**查了多少**：七张分析卡（A1–A4、B1–B5、C，共 %d 个字段／入口）第 4–6 节共 %d 个句子；锚点字段 %d 个（有可点控件、键长 ≥3、去掉太泛的词）；被 ≥2 张卡提到成组 **%d 组**，一个句子里同时提到两个锚点并带关系词的键对 **%d 对**（总表只列句数最多的前 %d 对）。命中 **%d 条嫌疑**（高 %d，中 %d，低 %d）。' % (
        len(ch.fields), len(lines), len(anchors), len(groups), len(pairs), min(30, len(pairs)), len(gsus),
        sum(1 for g in gsus if g[2] == '高'), sum(1 for g in gsus if g[2] == '中'), sum(1 for g in gsus if g[2] == '低')))
    out_md.append('判法和严重度写在 `程序/嫌疑c.py` 文件头。「卡里没写」＝整行没有关系词或先后词；机器判的是文字，不是语义，第二级看去向时可把误报标「不改」。去向列留空。')
    out_md.append('')
    out_md.append('| 编号 | 嫌疑 | 出处 | 严重度 | 去向 |')
    out_md.append('|---|---|---|---|---|')
    for i, (t, loc, sev) in enumerate(gsus, 1):
        out_md.append('| c-%02d | %s | %s | %s |  |' % (i, t.replace('|', '／'), loc.replace('|', '／'), sev))
    out_md.append('')
    out_md.append('## 一、被 ≥2 张卡引用的字段，每组一张总表')
    out_md.append('')
    out_md += body
    out_md.append('## 二、一个设置影响另一个设置（同一句里出现两个字段和关系词）')
    out_md.append('')
    out_md += pbody
    p = HERE.parent / '嫌疑_c_交界处.md'
    p.write_text('\n'.join(out_md) + '\n', encoding='utf-8')
    print('c: 分组', len(groups), '交互对', len(pairs), '嫌疑', len(gsus), '→', p)


if __name__ == '__main__':
    main()
