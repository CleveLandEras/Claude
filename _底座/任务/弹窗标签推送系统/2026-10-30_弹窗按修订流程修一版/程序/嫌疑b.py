#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嫌疑b.py  来源 b：理由只来自「旧后台有」「评审稿有」的字段（分析卡「为什么要填」列＋功能清单「理由」列）

同义词表（命中任一条，且全卡全行没有独立依据，才算「理由只剩旧后台有／评审稿有」）：
  旧后台有 ＝ 旧后台(就|原)有｜线上(就|原)有｜现网(就|原)有｜旧后台对应 为「2.2 第 N 项」且来源只有〔截〕〔文〕｜截图里有｜原来就有｜沿用旧
  评审稿有 ＝ 评审稿(已|里)?(有|列|写|新加)｜照评审稿｜和评审稿一致｜沿用评审稿｜评审稿原有｜〔评〕只此一处
独立依据（出现任一个，不算嫌疑）：RICH-数字｜〔J〕｜草稿｜运营原话｜已定事项｜竞品｜顶尖｜弹-数字｜参考库｜Dk 10/｜研发评审待确认｜走查｜玩家｜客服
判法四路：
  R1 理由文字：字段「为什么要填」或所挂清单行「理由」命中上面同义词，且字段与清单行的来源列都没有独立依据；
  R4 过渡期第 5 条（任务文件完成标准第 9 条⑤）：所挂清单行是〔旧〕原词且去向「保留」＝试配时和旧后台说法一一对上，列为嫌疑交验收官逐条看；
  R2 来源只有旧后台／评审稿：字段来源列和所挂清单行来源列的标签都在 {〔截〕〔文〕〔评〕〔框〕「2.2 第 N 项」} 里，没有独立依据。
严重度（思考页第 6 节第 4 条）：R1 或 R3（卡里写了运营原话没找到）＝中；仅 R2＝低（理由没写错，但缺外部依据）。
  R3 卡里自己承认没找到运营原话（字段行或所挂清单行里有「运营原话没找到」之类），即使别处有依据也列出。
用法：python3 嫌疑b.py            → 写 本夹/嫌疑_b_理由只来自旧后台或评审稿.md
"""
import re, sys, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('zl', HERE / '追链.py')
z = importlib.util.module_from_spec(spec); spec.loader.exec_module(z)

OLD_RE = re.compile(r'旧后台(就|原)?有|线上(就|原)?有|现网(就|原)?有|截图(里)?有|原来就有|沿用旧')
NEW_RE = re.compile(r'评审稿(已|里)?(有|列|写|新加)|照评审稿|和评审稿一致|沿用评审稿|评审稿原有')
INDEP = re.compile(r'RICH-\d+|〔J〕|草稿|运营原话|已定事项|竞品|顶尖|弹-\d+|参考库|Dk 10/|研发评审待确认|走查|玩家|客服')
ADMIT = re.compile(r'没找到运营原话|运营原话没找到|没有运营原话|无运营原话|运营原话没有')
TAG_ONLY = re.compile(r'〔截〕|〔文〕|〔评〕|〔框〕|2\.2 第 \d+ 项|A86 第 [\d、–\-]+ 行')


def only_old_or_review(src):
    """来源列里没有独立依据，且至少有一个旧后台／评审稿标签"""
    if INDEP.search(src):
        return False
    return bool(TAG_ONLY.search(src))


def main():
    ch = z.Chain()
    out = []
    n_list = sum(1 for r in ch.list.values() if r['dest'] in ('保留', '简化', '新增'))
    rows = []  # (code, kind, text, loc, sev)
    seen = set()
    for f in ch.fields:
        L = z.rd(f['file'])
        c = z.cells(L[f['line'] - 1])
        reason = c[3] if len(c) >= 8 else c[2]
        old_ref = c[6] if len(c) >= 8 else ''
        src = c[-1]
        ups = sorted(int(u[1:]) for u in ch.rev.get(f['code'], []) if u.startswith('清'))
        lrows = [ch.list[n] for n in ups if ch.list[n]['dest'] in ('保留', '简化', '新增')]
        all_src = src + ' ' + ' '.join(r['src'] for r in lrows)
        indep = bool(INDEP.search(all_src))
        r1 = bool((OLD_RE.search(reason) or NEW_RE.search(reason) or any(OLD_RE.search(r['why']) or NEW_RE.search(r['why']) for r in lrows)) and not indep)
        r2 = (not indep) and bool(TAG_ONLY.search(all_src)) and all(only_old_or_review(x) for x in [src] + [r['src'] for r in lrows])
        rowtext = ' '.join(c) + ' ' + ' '.join(r['text'] + r['why'] + r['src'] for r in lrows)
        r3 = bool(ADMIT.search(rowtext))
        # R4 过渡期第 5 条：和旧后台说法一一对上（所挂清单行写〔旧〕原词、去向「保留」）
        r4rows = [n for n in ups if ch.list[n]['text'].startswith('〔旧〕') and ch.list[n]['dest'] == '保留']
        r4 = bool(r4rows)
        if not (r1 or r2 or r3 or r4):
            continue
        fname = Path(f['file']).name
        sev = '中' if (r1 or r3) else '低'
        why = []
        if r4:
            why.append('和旧后台说法一一对上（清单第 %s 行〔旧〕原词、去向保留）' % '、'.join(str(n) for n in r4rows))
        if r3:
            why.append('卡里自己写了「运营原话没找到」，只靠评审稿或推播的写法')
        if r1:
            why.append('理由文字写的是旧后台／评审稿有')
        if r2:
            why.append('来源只有旧后台／评审稿（%s）' % '；'.join(sorted(set(re.findall(r'〔[截文评框]〕|2\.2 第 \d+ 项|A86', all_src)))) or '旧后台截图')
        lr = ('；清单第 ' + '、'.join(str(n) for n in ups) + ' 行') if ups else ''
        txt = '字段「%s」：%s；它保留的理由要补一条运营原话、工单、草稿或顶尖做法的依据，或明说「只是沿用」' % (f['name'][:24], '，'.join(why))
        loc = '〔%s〕%s 第 %d 行%s' % (f['code'], fname, f['line'], lr)
        rows.append((f['code'], txt, loc, sev))
    # 清单里没挂到字段的保留／简化／新增行
    for n, r in ch.list.items():
        if r['dest'] not in ('保留', '简化', '新增'):
            continue
        if any(c for c in r['fields'] if c in ch.byfield):
            continue
        if INDEP.search(r['src']):
            continue
        if (OLD_RE.search(r['why']) or NEW_RE.search(r['why'])) or only_old_or_review(r['src']):
            rows.append((','.join(r['fields']) or '清%d' % n, '清单行：「%s」去向「%s」，来源只有旧后台／评审稿，理由「%s」' % (r['text'][:30], r['dest'], r['why'][:40]),
                         '〔%s〕功能清单 第 %d 行（清%d）' % ('、'.join(r['fields']) or '无字段', r['line'], n), '低'))
    sevorder = {'高': 0, '中': 1, '低': 2}
    rows.sort(key=lambda x: (sevorder[x[3]], x[0]))
    out.append('# 嫌疑清单 b：理由只来自旧后台或评审稿')
    out.append('')
    out.append('**查了多少**：分析卡字段／入口 %d 行（卡 A1–A4、B1–B5、C）＋功能清单 %d 行（其中去向保留／简化／新增 %d 行）。判法四路：R1 理由文字写「旧后台有／评审稿有」，R2 来源标签只有〔截〕〔文〕〔评〕〔框〕「2.2 第 N 项」，R3 卡里自己写了「运营原话没找到」，R4 和旧后台说法一一对上（过渡期第 9 条⑤，清单行〔旧〕原词且去向保留）；同义词表和独立依据表写在 `程序/嫌疑b.py` 文件头。命中 **%d 条**（中 %d，低 %d）。' % (
        len(ch.fields), len(ch.list), n_list, len(rows), sum(1 for r in rows if r[3] == '中'), sum(1 for r in rows if r[3] == '低')))
    out.append('严重度：中＝理由文字就是「旧后台有／评审稿有」，或卡里自己写了运营原话没找到，要补依据或改写；低＝理由没问题，只是来源没有运营原话、工单、草稿、已定事项或顶尖做法，或字段只是旧后台原词照留（R4）。去向列留空，第二级填。')
    out.append('')
    out.append('| 编号 | 嫌疑 | 出处 | 严重度 | 去向 |')
    out.append('|---|---|---|---|---|')
    for i, (code, txt, loc, sev) in enumerate(rows, 1):
        out.append('| b-%02d | %s | %s | %s |  |' % (i, txt.replace('|', '／'), loc, sev))
    p = HERE.parent / '嫌疑_b_理由只来自旧后台或评审稿.md'
    p.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print('b: 命中', len(rows), '条 → ', p)


if __name__ == '__main__':
    main()
