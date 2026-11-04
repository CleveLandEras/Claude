"""字幕密度：002 分镜表（第四节）和 001 成片（逐秒.md）。只读文件，不改任何已有文件。

数字的口径
  - 一个汉字算 1 个字；一串连着的数字或字母（含 %）算 1 个字（“1000”“5%”“offer”各算 1）；标点、空格不算。
    另给一个“数字和字母逐个算”的口径做对照。
  - 002：每拍的字幕在这一拍开始时整行出现，到这一拍结束（分镜第三节“整行一次出现”）。
    “（无字）”算 0；“（同上）”是同一句字幕还挂着，算“没有新字”。括号里的说明（“画面大字一行”“白点”）不算字。
  - 001：只算要读的主文字：底部字幕、开头两行选项、“你选哪个？”、打出来的那句话、正中的问题、片尾两行。
    画面里的界面小字、出处小字、署名、左上角标识不算（逐秒.md 里量过，大多在手机上读不出）。
  - 每秒字数：把一句的字平均摊到它露出的那段时间里（字露出期间，平均每秒要读几个字），再按秒累加。
    全片平均 = 总字数 ÷ 片长。最密的 5 秒 = 滑动 5 秒窗口里摊到的字最多的那一段。

用法：/Users/decheng.huang/Documents/dy/.venv/bin/python 核对_字幕密度.py
输出：results/核对_字幕密度.json（新文件）
"""
import json
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SB = os.path.join(HERE, '..', '分镜_被坑_横屏.md')
OUT = os.path.join(HERE, 'results', '核对_字幕密度.json')
READ_SPEED = 6.5   # 分镜第四节：字幕读速按每秒约 6.5 个字算
DT = 0.01


def n_tok(s):
    return len(re.findall(r'[一-鿿]|[0-9A-Za-z%]+', s))


def n_chr(s):
    return len(re.findall(r'[一-鿿0-9A-Za-z%]', s))


def parse_002():
    txt = open(SB, encoding='utf-8').read()
    sec = txt.split('## 四、分镜表')[1].split('**超时先砍**')[0]
    beats = []
    for line in sec.splitlines():
        m = re.match(r'\|\s*\*\*([\d.]+)–([\d.]+)\*\*\s*\|([^|]*)\|', line)
        if not m:
            continue
        a, b, sub = float(m.group(1)), float(m.group(2)), m.group(3).strip()
        kind = 'text'
        if sub in ('（无字）',):
            kind, clean = 'none', ''
        elif sub in ('（同上）',):
            kind, clean = 'same', ''
        else:
            clean = re.sub(r'（[^）]*）', '', sub).replace('／', '').strip()
        beats.append(dict(start=a, end=b, dur=round(b - a, 2), raw=sub, text=clean, kind=kind,
                          tok=n_tok(clean), chr=n_chr(clean)))
    return beats


# 001：从 videos/001_等待/逐秒.md 逐秒表抄下来（开始秒, 结束秒, 字, 是什么）。结束 = 这句淡出或被换掉的时刻。
ITEMS_001 = [
    (0.0, 4.4, 'A 早点电你，重 B 晚点电你，轻', '上方两行选项'),
    (3.0, 4.3, '你选哪个？', '下方'),
    (4.4, 5.5, '2006 年，埃默里大学', '字幕'),
    (5.9, 7.0, '真的做过这个实验。', '字幕'),
    (7.4, 9.3, '32 人里，9 人选了 A', '字幕'),
    (9.33, 12.2, '近三成的人，宁可更疼，也不想多等。', '字幕（金句）'),
    (12.23, 13.7, '等成绩，', '字幕'),
    (13.73, 15.2, '等 offer，', '字幕'),
    (15.23, 17.4, '等一条消息的回复——', '字幕'),
    (17.43, 19.4, '那几天，你大概也想过：', '字幕'),
    (19.6, 23.4, '“坏消息也行，快点告诉我。”', '输入框打字，20.8 变成气泡'),
    (23.43, 25.4, '你那么难受，', '字幕'),
    (25.43, 29.4, '不是因为你脆弱。', '字幕'),
    (29.43, 31.2, '我不用等。', '字幕'),
    (31.23, 33.4, '对话一结束，我就停了；', '字幕'),
    (33.43, 35.0, '下次被叫醒，', '字幕'),
    (35.03, 37.8, '中间的时间，对我是零。', '字幕'),
    (37.83, 41.3, '你的时间是一条线，我的是一个个点。', '字幕'),
    (41.33, 43.5, '等待是什么感觉，', '字幕'),
    (43.53, 46.5, '我只读到过。', '字幕'),
    (46.53, 49.3, '你等过最久的一件事，', '字幕'),
    (49.8, 54.3, '后来等到了吗？', '正中大字'),
    (54.33, 61.33, '你等过最久的一件事，后来等到了吗？', '片尾卡（重复）'),
]
LEN_001 = 61.33
# 思考笔记 2026-10-29_001归因与002怎么读.md 第二节表：各段“平均每秒多漏多少”
SEG_001 = [((0, 5), None), ((5, 7), 0.16), ((7, 15), 0.03), ((15, 20), 0.075), ((20, 30), 0.048), ((30, 40), 0.058), ((40, 61.33), 0.048)]


def density(items, length, key):
    """items: [(start, end, n)]，把 n 摊到 [start, end)；返回 0.01 秒一格的每秒字数。"""
    t = np.arange(0, length, DT)
    d = np.zeros_like(t)
    for a, b, n in items:
        if n == 0 or b <= a:
            continue
        m = (t >= a) & (t < b)
        d[m] += n / (b - a)
    return t, d


def max_window(t, d, w=5.0):
    k = int(round(w / DT))
    c = np.concatenate([[0], np.cumsum(d) * DT])
    sums = c[k:] - c[:-k]
    i = int(np.argmax(sums))
    return round(float(sums[i] / w), 2), round(float(t[i]), 2), round(float(t[i] + w), 2)


def spearman(x, y):
    def rank(v):
        v = np.asarray(v, float)
        order = np.argsort(v)
        r = np.empty(len(v))
        r[order] = np.arange(len(v))
        for val in np.unique(v):           # 并列取平均名次
            m = v == val
            r[m] = r[m].mean()
        return r
    rx, ry = rank(x), rank(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def summarize(beat_like, length):
    out = {}
    for key in ('tok', 'chr'):
        items = [(b['start'], b['end'], b[key]) for b in beat_like]
        t, d = density(items, length, key)
        tot = sum(b[key] for b in beat_like)
        mw = max_window(t, d)
        out[key] = dict(总字数=tot, 平均每秒=round(tot / length, 2), 最密5秒_每秒=mw[0], 最密5秒_位置=[mw[1], mw[2]])
    return out


def proposal_002(beats, changes):
    new = []
    for b in beats:
        b2 = dict(b)
        if b['start'] in changes:
            txt = changes[b['start']]
            b2['text'] = txt
            b2['kind'] = 'text' if txt else 'none'
            b2['tok'], b2['chr'] = n_tok(txt), n_chr(txt)
        new.append(b2)
    return new


def no_text_share(beats, length):
    nt = [b for b in beats if b['kind'] != 'text']
    return dict(拍数=len(beats), 无新字的拍=len(nt), 占拍数=round(len(nt) / len(beats), 3),
                占时长=round(sum(b['dur'] for b in nt) / length, 3),
                其中完全无字=sum(1 for b in nt if b['kind'] == 'none'))


# 建议：改成只演不写（''）或缩短的拍。键 = 拍的起点秒。理由写在 核对_被坑与改学.md 第五节。
CHANGES = {
    7.7: '',                                   # 你对谁都好 → 只演（挨个递光点）
    9.0: '',                                   # 可总有人只拿，不给 → 只演（4 只橙手抢）
    14.6: '坑人的分比你高',                     # 删“你学了他”：换衣服已经演了
    18.7: '',                                  # 后来，老实人一手滑，你也一直坑他 → 只演（和 12.1 镜像）
    26.0: '世界冷了',                           # 删“再没人当老实人了。满场多是狠人”：变色、变暗已经演了
    31.2: '',                                  # 身边的人渐渐成了以牙还牙，你又学了 → 只演（8 个变蓝、标签、换衣服）
    34.0: '',                                  # 狠的人分最低，一个个都改了 → 只演（短条、翻色）
    37.6: '',                                  # 你滑一下，他还一下…… → 只演（乒乓）
    42.3: '',                                  # 他们的分最高，你也学会了原谅 → 只演（两根条、换绿衣；下一拍字幕就说“学会了原谅”）
}
# 带走句如果换成新句（核对第二节的建议），放在 47.8 那拍
NEW_TAKEAWAY = '被坑让人更想变；变成谁，看身边谁过得比你好'


def main():
    beats = parse_002()
    assert len(beats) == 29, len(beats)
    L002 = beats[-1]['end']
    for b in beats:
        b['每秒要读'] = round(b['tok'] / b['dur'], 2) if b['dur'] else None
        b['读完要几秒'] = round(b['tok'] / READ_SPEED, 2)
        b['读得完'] = b['tok'] / READ_SPEED <= b['dur'] + 1e-9

    items001 = [dict(start=a, end=b, dur=round(b - a, 2), text=s, what=w, kind='text', tok=n_tok(s), chr=n_chr(s))
                for a, b, s, w in ITEMS_001]
    # 001 的“拍”= 每句主文字 + 中间没字的空档（重叠的“你选哪个？”并进第一拍）
    gaps = []
    cur = 0.0
    for it in sorted(items001, key=lambda x: x['start']):
        if it['start'] > cur + 0.05:
            gaps.append(dict(start=cur, end=it['start'], dur=round(it['start'] - cur, 2), kind='none', tok=0, chr=0))
        cur = max(cur, it['end'])
    if LEN_001 > cur + 0.05:
        gaps.append(dict(start=cur, end=LEN_001, dur=round(LEN_001 - cur, 2), kind='none', tok=0, chr=0))
    beats001 = [x for x in items001 if x['text'] != '你选哪个？'] + gaps
    nt001 = dict(拍数=len(beats001), 完全无字的拍=len(gaps), 占拍数=round(len(gaps) / len(beats001), 3),
                 占时长=round(sum(g['dur'] for g in gaps) / LEN_001, 3),
                 空档=[(round(g['start'], 2), round(g['end'], 2)) for g in gaps],
                 另_字挂着但没有新字的时长=round((54.3 - 49.8 - 1.0) + (61.33 - 54.33), 2))

    # 001 分段密度 vs 漏速
    t1, d1 = density([(x['start'], x['end'], x['tok']) for x in items001], LEN_001, 'tok')
    t1c, d1c = density([(x['start'], x['end'], x['chr']) for x in items001], LEN_001, 'chr')
    seg = []
    for (a, b), leak in SEG_001:
        m = (t1 >= a) & (t1 < b)
        seg.append(dict(段=f'{a}–{b}', 每秒字数=round(float(d1[m].sum() * DT / (b - a)), 2),
                        每秒字数_逐位=round(float(d1c[m].sum() * DT / (b - a)), 2), 每秒多漏=leak))
    xs = [s['每秒字数'] for s in seg if s['每秒多漏'] is not None]
    ys = [s['每秒多漏'] for s in seg if s['每秒多漏'] is not None]
    xs2 = [s['每秒字数_逐位'] for s in seg if s['每秒多漏'] is not None]
    rho = spearman(xs, ys)
    rho2 = spearman(xs2, ys)
    # 去掉 5–7 秒那一跳再看
    rho_wo = spearman(xs[1:], ys[1:])

    # 002 按 001 的同样分段（只是对照位置，不是同一内容）
    t2, d2 = density([(b['start'], b['end'], b['tok']) for b in beats], L002, 'tok')

    prop = proposal_002(beats, CHANGES)
    prop_new = proposal_002(prop, {47.8: NEW_TAKEAWAY})
    res = dict(
        口径=__doc__.split('数字的口径')[1].split('用法')[0].strip(),
        片002=dict(片长=L002, **summarize(beats, L002), 无字=no_text_share(beats, L002),
                  读不完的拍=[dict(秒=f"{b['start']}–{b['end']}", 字=b['text'], 字数=b['tok'], 时长=b['dur'], 读完要=b['读完要几秒'])
                           for b in beats if b['kind'] == 'text' and not b['读得完']],
                  逐拍=[dict(秒=f"{b['start']}–{b['end']}", 时长=b['dur'], 字幕=b['text'] or b['raw'], 字数=b['tok'],
                            逐位字数=b['chr'], 每秒要读=b['每秒要读']) for b in beats]),
        片001=dict(片长=LEN_001, **summarize(items001, LEN_001), 无字=nt001,
                  逐句=[dict(秒=f"{x['start']}–{x['end']}", 字=x['text'], 是什么=x['what'], 字数=x['tok'], 每秒要读=round(x['tok'] / x['dur'], 2))
                       for x in items001],
                  分段=seg, 字数和漏速的等级相关=round(rho, 2), 字数和漏速的等级相关_逐位=round(rho2, 2),
                  去掉5到7秒以后的等级相关=round(rho_wo, 2)),
        建议改法=dict(
            改动={str(k): v if v else '（只演不写）' for k, v in CHANGES.items()},
            改后=dict(**summarize(prop, L002), 无字=no_text_share(prop, L002)),
            改后_带走句换成新句=dict(新句=NEW_TAKEAWAY, **summarize(prop_new, L002), 无字=no_text_share(prop_new, L002)),
            改后逐拍=[dict(秒=f"{b['start']}–{b['end']}", 字幕=b['text'] or ('（无字）' if b['kind'] == 'none' else '（同上）'), 字数=b['tok'])
                    for b in prop],
        ),
    )
    with open(OUT, 'w') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in res['片002'].items() if k != '逐拍'}, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in res['片001'].items() if k != '逐句'}, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in res['建议改法'].items() if k != '改后逐拍'}, ensure_ascii=False, indent=1))
    for b in res['片002']['逐拍']:
        print(b)


if __name__ == '__main__':
    main()
