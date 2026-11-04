"""Q61 只读：为环节1 生成「移出更正括注」的逐条改法（旧串 → 新串）与更正记录条目。不写文件，只打印。
规则：全角括号段内按顶层「；」「。」切片；含 原写/更正（不含「更正版」）/原判断/原状态/上一版/曾写/作废/原各处/第一版 的片为更正片；
片内「原写」不在开头时，从其前一个顶层「，」起算更正。全部为更正片 → 整段删除；否则删更正片、保留其余。"""
import os, re, html
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(BASE, '环节1_现状盘点.html')
S = open(F, encoding='utf-8').read()
L = S.split('\n')
CORR = re.compile(r'原写|(?<!\S)更正(?!版)|更正(?!版)|原判断|原状态|上一版|曾写|作废|原各处|第一版|原「')
SKIP_LINES = set()  # 不处理的行

def spans(s):
    st, out = [], []
    for i, ch in enumerate(s):
        if ch == '（':
            st.append(i)
        elif ch == '）' and st:
            a = st.pop(); out.append((a, i + 1, len(st)))
    return out

def is_corr(t):
    t2 = t.replace('更正版', '')
    return bool(CORR.search(t2))

def split_top(t, seps='；。'):
    parts, buf, dq, dp, dt = [], '', 0, 0, 0
    for ch in t:
        if ch == '「': dq += 1
        elif ch == '」': dq -= 1
        elif ch == '（': dp += 1
        elif ch == '）': dp -= 1
        elif ch == '<': dt += 1
        elif ch == '>': dt -= 1
        if ch in seps and dq == 0 and dp == 0 and dt == 0:
            parts.append((buf, ch)); buf = ''
        else:
            buf += ch
    if buf: parts.append((buf, ''))
    return parts

def cut_inner(piece):
    # piece 中「原写」不在开头：从其前一个顶层「，」处截断
    i = piece.find('原写')
    if i <= 0: return piece, ''
    dq = dp = 0; last = -1
    for k, ch in enumerate(piece[:i]):
        if ch == '「': dq += 1
        elif ch == '」': dq -= 1
        elif ch == '（': dp += 1
        elif ch == '）': dp -= 1
        elif ch == '，' and dq == 0 and dp == 0: last = k
    if last < 0: return None, None
    return piece[:last], piece[last:]

def strip(t):
    return html.unescape(re.sub(r'<[^>]+>', '', t))

heads = [(i, strip(l).strip()) for i, l in enumerate(L) if re.search(r'<h[23]', l)]
def sect(i):
    h = [t for j, t in heads if j <= i]
    return h[-1][:40] if h else '开头'

items = []
for i, l in enumerate(L):
    sp = spans(l)
    hit = [x for x in sp if is_corr(l[x[0]:x[1]])]
    inner = [x for x in hit if not any(y != x and x[0] < y[0] and y[1] < x[1] for y in hit)]
    for a, b, dep in inner:
        seg = l[a:b]; t = seg[1:-1]
        parts = split_top(t)
        keep, drop = [], []
        for p, sep in parts:
            if is_corr(p):
                if p.lstrip().startswith(('原写', '审查', 'Q', 'R', '更正', '原', '上一版', '第一版')):
                    drop.append(p + sep)
                else:
                    k, d = cut_inner(p)
                    if k is None: drop.append(p + sep)
                    else:
                        keep.append((k, sep)); drop.append(d)
            else:
                keep.append((p, sep))
        if keep:
            new = '（' + ''.join(p + s for p, s in keep).rstrip('；，') + '）'
            new = new.replace('；）', '）').replace('，）', '）')
        else:
            new = ''
        # 现写：括注前的一句
        pre = l[:a]
        k = max(pre.rfind('。'), pre.rfind('>'))
        now = strip(pre[k + 1:])[-70:]
        items.append(dict(line=i + 1, a=a, b=b, seg=seg, new=new, sect=sect(i), now=now,
                          drop='；'.join(d.strip('；。') for d in drop) if keep else t,
                          refs=' '.join(sorted(set(re.findall(r'R\d+|Q\d+', seg))))))
print('条目数', len(items))
for n, it in enumerate(items, 1):
    cnt = S.count(it['seg'])
    print(f"#{n} 行{it['line']} 出现{cnt}次｜{it['sect']}")
    print('   旧:', it['seg'])
    print('   新:', it['new'] if it['new'] else '〈删除〉')
    print('   现写:', it['now'])
