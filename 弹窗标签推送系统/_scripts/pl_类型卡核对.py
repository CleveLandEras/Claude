# 类型卡与任务说明核对（10/19 建，规则见 规则与交接/标准体系.md 第〇节「某类稿件必须写什么、不写什么」「怎么写任务说明」）
#
# 用法：
#   python3 _scripts/pl_类型卡核对.py 卡 [文件…]
#       核对照贴条目：文件里每个〔路径:行号〕「原文」，原文要在注明的源文件那一行逐字找得到才算过
#       （源文件里的 ** 加粗记号忽略；原文里的「……」表示中间省略，各段须按顺序出现在同一行）。
#       不给文件时核对 规则与交接/类型卡/ 下全部卡片；也可以给 交付前必查.md 等任何用同一格式照贴规则的文件。
#       类型卡另查：四节齐全；「必须做到」「不写」两节里每一条都是照贴条目（不许转述）。
#   python3 _scripts/pl_类型卡核对.py 说明 <任务说明.md> <类型卡名或路径>
#       核对任务说明：含该类型卡全文（逐行、按顺序）；含冲突条款原句；没有让执行者跳过规则的写法；
#       「已定的改法」一节每条注了「依据：」或标了「主对话提议」。
# 有 ✘ 时退出码为 1。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, re, glob

BASE = _ROOT + ''
CARD_DIR = os.path.join(BASE, '规则与交接', '类型卡')
CLAUSE = '本说明、研究建议、参考库与写作标准或类型卡不一致时，以写作标准为准；发现不一致先回报，不照做。'
CARD_SECTIONS = ['## 读者与要做的判断', '## 必须做到', '## 不写', '## 这类稿件出过的问题']
QUOTE_ONLY = ['## 必须做到', '## 不写']

def resolve(p):
    p = p.strip()
    if os.path.isabs(p):
        return p
    return os.path.join(BASE, p)

def parse_quotes(text):
    """找出全部〔路径:行号〕「原文」，原文按「」配对取到与之配对的」为止。"""
    out = []
    for m in re.finditer(r'〔([^〔〕]+?):(\d+)〕', text):
        k = m.end()
        if k >= len(text) or text[k] != '「':
            out.append((m.group(1), int(m.group(2)), None, m.start()))
            continue
        depth, j = 0, k
        while j < len(text):
            if text[j] == '「':
                depth += 1
            elif text[j] == '」':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        quote = text[k + 1:j] if j < len(text) else None
        out.append((m.group(1), int(m.group(2)), quote, m.start()))
    return out

def in_line(quote, line):
    line = line.replace('**', '')
    pos = 0
    for seg in [x for x in quote.split('……') if x]:
        k = line.find(seg, pos)
        if k < 0:
            return False
        pos = k + len(seg)
    return True

_cache = {}
def src_lines(path):
    if path not in _cache:
        _cache[path] = open(path, encoding='utf-8').read().split('\n') if os.path.exists(path) else None
    return _cache[path]

def check_quotes(fn):
    text = open(fn, encoding='utf-8').read()
    rel = os.path.relpath(fn, BASE)
    bad = 0
    qs = parse_quotes(text)
    for src, ln, quote, at in qs:
        lineno_here = text.count('\n', 0, at) + 1
        tag = '%s 第 %d 行' % (rel, lineno_here)
        if quote is None:
            print('  ✘ %s：〔%s:%d〕后面没有「原文」' % (tag, src, ln)); bad += 1; continue
        L = src_lines(resolve(src))
        if L is None:
            print('  ✘ %s：源文件不存在 %s' % (tag, src)); bad += 1; continue
        short = quote if len(quote) <= 40 else quote[:40] + '…'
        if 1 <= ln <= len(L) and in_line(quote, L[ln - 1]):
            print('  ✔ %s：%s:%d「%s」' % (tag, src, ln, short))
        else:
            hits = [i + 1 for i, l in enumerate(L) if in_line(quote, l)]
            if hits:
                print('  ✘ %s：行号不对，原文在 %s 第 %s 行「%s」' % (tag, src, '、'.join(map(str, hits)), short))
            else:
                print('  ✘ %s：%s 里逐字找不到「%s」' % (tag, src, short))
            bad += 1
    return len(qs), bad

def check_card_shape(fn):
    lines = open(fn, encoding='utf-8').read().split('\n')
    bad = 0
    heads = [l.strip() for l in lines if l.startswith('## ')]
    for h in CARD_SECTIONS:
        if h not in heads:
            print('  ✘ 缺一节：%s' % h); bad += 1
    cur = None
    for i, l in enumerate(lines, 1):
        if l.startswith('## '):
            cur = l.strip()
        elif cur in QUOTE_ONLY and l.lstrip().startswith('- ') and not l.lstrip().startswith('- 〔'):
            print('  ✘ 第 %d 行：「%s」一节的条目要照贴原文（〔文件:行〕「原文」），不能转述' % (i, cur[3:])); bad += 1
    return bad

def mode_cards(files):
    if not files:
        files = sorted(glob.glob(os.path.join(CARD_DIR, '*.md')))
    total_q = total_bad = 0
    for fn in files:
        fn = resolve(fn)
        print('【%s】' % os.path.relpath(fn, BASE))
        n, bad = check_quotes(fn)
        if os.path.dirname(fn) == CARD_DIR:
            bad += check_card_shape(fn)
        print('  小计：照贴 %d 条，✘ %d' % (n, bad))
        total_q += n; total_bad += bad
    print('合计：%d 个文件，照贴 %d 条，✘ %d' % (len(files), total_q, total_bad))
    return total_bad

def mode_brief(brief, card):
    brief = resolve(brief)
    if not os.path.exists(card):
        c = os.path.join(CARD_DIR, card if card.endswith('.md') else card + '.md')
        card = c if os.path.exists(c) else resolve(card)
    btext = open(brief, encoding='utf-8').read()
    blines = [l.rstrip() for l in btext.split('\n')]
    clines = [l.rstrip() for l in open(card, encoding='utf-8').read().split('\n') if l.strip()]
    print('【%s 对照 %s】' % (os.path.relpath(brief, BASE), os.path.relpath(card, BASE)))
    bad = 0
    # 1 类型卡全文，逐行按顺序
    pos, missing = 0, []
    for cl in clines:
        k = next((i for i in range(pos, len(blines)) if blines[i] == cl), None)
        if k is None:
            missing.append(cl)
        else:
            pos = k + 1
    if missing:
        bad += 1
        print('  ✘ 类型卡全文：%d 行中缺 %d 行（或顺序不对），例：%s' % (len(clines), len(missing), missing[0][:50]))
    else:
        print('  ✔ 类型卡全文：%d 行都在，顺序一致' % len(clines))
    # 2 冲突条款
    if CLAUSE in btext:
        print('  ✔ 冲突条款原句在')
    else:
        bad += 1; print('  ✘ 缺冲突条款原句：%s' % CLAUSE)
    # 3 让执行者跳过规则的写法
    for i, l in enumerate(blines, 1):
        for pat, why in [(r'(?<!不)照做', '「照做」'), (r'不通读', '「不通读」')]:
            if re.search(pat, l):
                bad += 1; print('  ✘ 第 %d 行有%s：%s' % (i, why, l.strip()[:50]))
    # 4 已定的改法：每条注依据或标主对话提议
    sec, level, items, nobasis = False, 0, 0, []
    for i, l in enumerate(blines, 1):
        m = re.match(r'^(#+)\s', l)
        if m:
            if sec and len(m.group(1)) <= level:
                sec = False
            if '已定的改法' in l:
                sec, level = True, len(m.group(1))
            continue
        if sec and re.match(r'^\s*(- |\d+[.、] )', l):
            items += 1
            if '依据：' not in l and '主对话提议' not in l:
                nobasis.append(i)
    if items == 0:
        bad += 1; print('  ✘ 没有「已定的改法」一节或其中没有条目')
    elif nobasis:
        bad += 1; print('  ✘ 「已定的改法」%d 条中 %d 条没注依据也没标主对话提议（第 %s 行）' % (items, len(nobasis), '、'.join(map(str, nobasis))))
    else:
        print('  ✔ 「已定的改法」%d 条都注了依据或标了主对话提议' % items)
    print('合计 ✘ %d' % bad)
    return bad

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('卡', '说明'):
        print(__doc__ or '用法见文件开头'); sys.exit(2)
    if a[0] == '卡':
        sys.exit(1 if mode_cards(a[1:]) else 0)
    if len(a) < 3:
        print('用法：python3 _scripts/pl_类型卡核对.py 说明 <任务说明.md> <类型卡名或路径>'); sys.exit(2)
    sys.exit(1 if mode_brief(a[1], a[2]) else 0)
