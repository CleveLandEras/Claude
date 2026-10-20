# 程序判卷（标准体系第二层「程序判」，见 规则与交接/标准体系.md）
# 用法：python judge_程序.py [--呈交] 文件...
#   html / md：本地链接与锚点是否有效
#   pptx：逗号句清单（逐句按意思判）
#   --呈交：再查呈交版禁用词；✘ 为明确违规，⚠ 为提醒，按意思判
# 输出每个文件一行结论，再列明细；有 ✘ 退出码为 1
import sys, os, re, html as H

args = [a for a in sys.argv[1:] if not a.startswith('--')]
CHENGJIAO = '--呈交' in sys.argv

HARD = [  # 呈交版明确不能出现
    (r'主管', '指称读者'),
    (r'(?<![A-Za-z])A\d{2,3}(?!\d)', '分析编号'),
    (r'判例', '内部用语'), (r'子任务', '内部用语'), (r'待核实', '内部用语'),
    (r'资料没写', '内部用语'), (r'请评审', '对话用语'), (r'待你', '对话用语'), (r'阶段\s*\d', '阶段编号'), (r'排期', '排期'),
]
SOFT = [  # 可能合法，按意思判
    (r'(?<!潜在)付费', '付费作目标或指标？'), (r'活跃', '活跃作目标或指标？'),
    (r'业绩', '业绩作目标或指标？'), (r'(?<!未)购买', '购买作目标或指标？'),
    (r'推荐|建议', '已定的事写成建议或推荐？'),
]

def pptx_lines(path):
    from pptx import Presentation
    out = []
    for i, s in enumerate(Presentation(path).slides, 1):
        for sh in s.shapes:
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    t = ''.join(r.text for r in p.runs).strip()
                    if t:
                        out.append(('p%d' % i, t))
    return out

def text_lines(path):
    s = open(path, encoding='utf-8').read()
    if path.endswith('.html'):
        s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
        s = re.sub(r'<(br|/p|/li|/tr|/h\d|/div)[^>]*>', '\n', s)
        s = H.unescape(re.sub(r'<[^>]+>', ' ', s))
    return [('L%d' % i, l.strip()) for i, l in enumerate(s.split('\n'), 1) if l.strip()]

def links(path):
    s = open(path, encoding='utf-8').read()
    base = os.path.dirname(path)
    found = re.findall(r'(?:href|src)="([^"]+)"', s) + re.findall(r'\]\(([^)\s]+)\)', s)
    bad = []
    for l in found:
        if l.startswith(('http', 'mailto:', 'data:', 'javascript:')):
            continue
        f, _, a = l.partition('#')
        tgt = os.path.normpath(os.path.join(base, f)) if f else path
        if not os.path.exists(tgt):
            bad.append('文件不存在：' + l)
        elif a and tgt.endswith(('.html', '.md')):
            t = open(tgt, encoding='utf-8').read()
            if not re.search(r'id="%s"' % re.escape(a), t):
                bad.append('锚点不存在：' + l)
    return len(found), bad

fail = False
for path in args:
    hard, soft, info = [], [], []
    if path.endswith('.pptx'):
        lines = pptx_lines(path)
        commas = [(k, t) for k, t in lines if '，' in t and not re.search(r'第 \d+ 页', t)]
        info.append('逗号句 %d 句，逐句判两边是否有关系' % len(commas))
    else:
        n, bad = links(path)
        hard += bad
        info.append('链接 %d 个' % n)
        lines = text_lines(path)
    if CHENGJIAO:
        for k, t in lines:
            for pat, why in HARD:
                if re.search(pat, t):
                    hard.append('%s %s：%s' % (k, why, t[:60]))
            for pat, why in SOFT:
                if re.search(pat, t):
                    soft.append('%s %s：%s' % (k, why, t[:60]))
    fail |= bool(hard)
    print('%s %s ｜ ✘ %d ｜ ⚠ %d ｜ %s' % ('✘' if hard else '✓', os.path.basename(path), len(hard), len(soft), '；'.join(info)))
    for x in hard:
        print('   ✘', x)
    for x in soft:
        print('   ⚠', x)
sys.exit(1 if fail else 0)
