"""用 Pillow 画图（项目里没有 matplotlib）。

fig_场景_*.png：各策略人数占比随代数变化。粗线 = 代表性种子（离各种子中位数最近的那次），细淡线 = 其余种子。
fig_敏感性表.png：参数敏感性小表。
fig_你.png：“你”每一代的分数和策略。
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from sim import STRATS, COLORS, PLOT_ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')
FIG = os.path.join(HERE, 'figs')
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
SURF = (252, 252, 251)
INK = (11, 11, 11)
INK2 = (82, 81, 78)
GRID = (226, 225, 220)
SS = 2  # 超采样

NAME = {k: v['name'] for k, v in STRATS.items()}
NAME['WSLS'] = 'Pavlov（赢不变输就换）'


def font(px, bold=False):
    return ImageFont.truetype(FONT, int(px * SS), index=1 if bold else 0)


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def col(k):
    return hex2rgb(COLORS[k][0])


def line_chart(path, title, subtitle, runs, rep_idx, noise_from=None, note=None):
    keys = runs[0]['strategies']
    order = [k for k in PLOT_ORDER if k in keys]
    W, H = 1600, 1020
    L, Rm, Tp, B = 110, 250, 250, 110
    img = Image.new('RGB', (W * SS, H * SS), SURF)
    d = ImageDraw.Draw(img)
    G = len(runs[0]['shares']) - 1
    pw, ph = W - L - Rm, H - Tp - B
    X = lambda g: (L + pw * g / G) * SS
    Y = lambda v: (Tp + ph * (1 - v)) * SS

    d.text((L * SS, 46 * SS), title, font=font(40, True), fill=INK)
    for li, line in enumerate(subtitle.split('\n')):
        d.text((L * SS, (104 + li * 34) * SS), line, font=font(23), fill=INK2)
    # 图例
    x = L
    for k in order:
        d.line([(x * SS, 196 * SS), ((x + 28) * SS, 196 * SS)], fill=col(k), width=5 * SS)
        d.text(((x + 36) * SS, 196 * SS), NAME[k], font=font(22), fill=INK2, anchor='lm')
        x += 36 + d.textlength(NAME[k], font=font(22)) / SS + 34
    # 网格和坐标
    for v in (0, .25, .5, .75, 1):
        d.line([(L * SS, Y(v)), ((L + pw) * SS, Y(v))], fill=GRID, width=SS)
        d.text(((L - 14) * SS, Y(v)), f'{int(v * 100)}%', font=font(20), fill=INK2, anchor='rm')
    step = 50 if G <= 400 else 200
    for g in range(0, G + 1, step):
        d.text((X(g), (Tp + ph + 22) * SS), str(g), font=font(20), fill=INK2, anchor='mt')
    d.text(((L + pw / 2) * SS, (H - 40) * SS), '代数', font=font(22), fill=INK2, anchor='mm')
    d.text(((L - 14) * SS, (Tp - 22) * SS), '人数占比', font=font(20), fill=INK2, anchor='rm')
    if noise_from:
        x0 = X(noise_from)
        for y in range(Tp, Tp + ph, 16):
            d.line([(x0, y * SS), (x0, (y + 8) * SS)], fill=INK2, width=2 * SS)
        d.text((x0 + 10 * SS, (Tp + 12) * SS), f'第 {noise_from} 代起：5% 误会', font=font(22), fill=INK, anchor='lt')

    # 淡线：其余种子
    over = Image.new('RGBA', img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for ri, r in enumerate(runs):
        if ri == rep_idx:
            continue
        s = np.array(r['shares'])
        for k in order:
            i = keys.index(k)
            pts = [(X(g), Y(s[g, i])) for g in range(G + 1)]
            od.line(pts, fill=col(k) + (55,), width=2 * SS, joint='curve')
    img = Image.alpha_composite(img.convert('RGBA'), over).convert('RGB')
    d = ImageDraw.Draw(img)
    # 粗线：代表性种子
    s = np.array(runs[rep_idx]['shares'])
    ends = []
    for k in order:
        i = keys.index(k)
        pts = [(X(g), Y(s[g, i])) for g in range(G + 1)]
        d.line(pts, fill=col(k), width=4 * SS, joint='curve')
        ends.append([float(s[-1, i]), k])
    # 直接标注：线尾
    ends.sort(key=lambda t: -t[0])
    ys, last = [], -1e9
    for v, k in ends:
        y = Tp + ph * (1 - v)
        y = max(y, last + 30)
        ys.append((y, v, k))
        last = y
    # 从下往上再推一遍：只把挤出底边的那一串往上挪
    lim = Tp + ph + 12
    for j in range(len(ys) - 1, -1, -1):
        y, v, k = ys[j]
        y = min(y, lim)
        ys[j] = (y, v, k)
        lim = y - 30
    for y, v, k in ys:
        d.ellipse([((L + pw) * SS - 6 * SS, Y(v) - 6 * SS), ((L + pw) * SS + 6 * SS, Y(v) + 6 * SS)], fill=col(k))
        d.text(((L + pw + 16) * SS, y * SS), f'{NAME[k].split("（")[0]} {v * 100:.0f}%', font=font(21), fill=INK, anchor='lm')
    if note:
        d.text((L * SS, (H - 40) * SS), note, font=font(18), fill=INK2, anchor='lm')
    img = img.resize((W, H), Image.LANCZOS)
    img.save(path)


def table_image(path, title, header, rows, widths, note=None):
    pad = 18
    rh = 46
    W = sum(widths) + 2 * pad
    H = 120 + rh * (len(rows) + 1) + (30 + 30 * len(note.split('\n')) if note else 30)
    img = Image.new('RGB', (W * SS, H * SS), SURF)
    d = ImageDraw.Draw(img)
    d.text((pad * SS, 30 * SS), title, font=font(32, True), fill=INK)
    y = 100
    x = pad
    for h, w in zip(header, widths):
        d.text(((x + 8) * SS, (y + rh / 2) * SS), h, font=font(20, True), fill=INK2, anchor='lm')
        x += w
    d.line([(pad * SS, (y + rh) * SS), ((W - pad) * SS, (y + rh) * SS)], fill=INK2, width=SS)
    y += rh
    prev_grp = None
    for r in rows:
        if r[0] != prev_grp and prev_grp is not None:
            d.line([(pad * SS, y * SS), ((W - pad) * SS, y * SS)], fill=GRID, width=SS)
        x = pad
        for ci, (c, w) in enumerate(zip(r, widths)):
            txt = c if not (ci == 0 and c == prev_grp) else ''
            d.text(((x + 8) * SS, (y + rh / 2) * SS), txt, font=font(19), fill=INK, anchor='lm')
            x += w
        prev_grp = r[0]
        y += rh
    if note:
        for li, line in enumerate(note.split('\n')):
            d.text((pad * SS, (y + 24 + li * 30) * SS), line, font=font(17), fill=INK2, anchor='lm')
    img = img.resize((W, H), Image.LANCZOS)
    img.save(path)


def you_chart(path, you, title, subtitle):
    W, H = 1600, 790
    L, Rm, Tp, B = 110, 60, 220, 150
    img = Image.new('RGB', (W * SS, H * SS), SURF)
    d = ImageDraw.Draw(img)
    G = len(you) - 1
    pw, ph = W - L - Rm, H - Tp - B
    X = lambda g: (L + pw * g / G) * SS
    Y = lambda v: (Tp + ph * (1 - v / 5)) * SS
    d.text((L * SS, 40 * SS), title, font=font(36, True), fill=INK)
    for li, line in enumerate(subtitle.split('\n')):
        d.text((L * SS, (92 + li * 32) * SS), line, font=font(22), fill=INK2)
    for v in (0, 1, 2, 3, 4, 5):
        d.line([(L * SS, Y(v)), ((L + pw) * SS, Y(v))], fill=GRID, width=SS)
        d.text(((L - 14) * SS, Y(v)), str(v), font=font(20), fill=INK2, anchor='rm')
    d.text((24 * SS, (Tp - 34) * SS), '每轮平均得分', font=font(20), fill=INK2, anchor='lm')
    for g in range(0, G + 1, 50):
        d.text((X(g), (Tp + ph + 16) * SS), str(g), font=font(20), fill=INK2, anchor='mt')
    # 全体平均
    pts = [(X(r['gen']), Y(r['pop_mean'])) for r in you]
    d.line(pts, fill=(160, 159, 152), width=3 * SS)
    # 你：按当代策略上色
    for a, b in zip(you[:-1], you[1:]):
        d.line([(X(a['gen']), Y(a['score'])), (X(b['gen']), Y(b['score']))], fill=col(a['strategy']), width=4 * SS)
    # 策略色带
    yb = Tp + ph + 56
    for r in you:
        x0, x1 = X(r['gen']), X(min(r['gen'] + 1, G))
        d.rectangle([(x0, yb * SS), (x1 + SS, (yb + 18) * SS)], fill=col(r['strategy']))
    d.text((L * SS, (yb + 40) * SS), '下面的色带 = 你那一代用的打法；灰线 = 全体平均分', font=font(18), fill=INK2, anchor='lm')
    # 改打法的地方
    for r in you:
        if r.get('switched_to'):
            g = r['gen'] + 1
            d.line([(X(g), Tp * SS), (X(g), (Tp + ph) * SS)], fill=(200, 199, 192), width=SS)
            d.text((X(g) + 6 * SS, (Tp + 6) * SS), f'第{g}代 改学{NAME[r["switched_to"]].split("（")[0]}',
                   font=font(18), fill=INK, anchor='lt')
    img = img.resize((W, H), Image.LANCZOS)
    img.save(path)


def main():
    os.makedirs(FIG, exist_ok=True)
    summ = json.load(open(os.path.join(RES, 'summary.json')))
    specs = [
        ('无误会', '没有误会：骗子先涨，再被挤掉，之后谁也赢不了谁', None),
        ('误会5%', '每一步都有 5% 的误会：最后宽容的以牙还牙占多数', None),
        ('转折_第100代起误会5%', '前 100 代没有误会，第 100 代起加 5% 误会', 100),
    ]
    for name, title, nf in specs:
        d = json.load(open(os.path.join(RES, f'main_{name}.json')))
        runs = d['runs']
        seed = summ['main'][name]['representative_seed']
        idx = [r['seed'] for r in runs].index(seed)
        sub = (f'1000 人，每人每代随机碰 10 个人，每对打 200 轮；开局老实人 50%，其余五种各 10%。\n'
               f'粗线：种子 {seed}（20 个种子里最接近中位数的一次）；淡线：其余 {len(runs) - 1} 个种子')
        line_chart(os.path.join(FIG, f'fig_场景_{name}.png'), title, sub, runs, idx, noise_from=nf)
    print('scenario figs done')



def sensitivity_figure():
    from experiments import VARIANTS, NOISE_VARIANTS
    summ = json.load(open(os.path.join(RES, 'summary.json')))
    short = {k: NAME[k].split('（')[0] for k in NAME}
    short['GTFT'] = '宽容'
    short['GTFT33'] = '宽容1/3'
    short['GTFT10'] = '宽容10%'

    def mk(grp, label, e, a, n=10):
        st = a['steps']
        f = lambda k: f'{round(st[k] * n)}' if k in st else '–'
        win = '  '.join(f'{short.get(k, k)} {v}' for k, v in a['winners'].items())
        pk = f"{a['alld_peak']['med'] * 100:.0f}%" if 'alld_peak' in a else '–'
        cp = f"{a['coop_final']['med'] * 100:.0f}%"
        es = e if isinstance(e, str) else f'{e * 100:g}%'
        return [grp, label, es, f(STEPS[1]), f(STEPS[2]), f(STEPS[3]), f(STEPS[4]), pk, cp, win]

    from analyze import agg, STEPS as _S
    rows = []
    for name, e in [('无误会', 0.0), ('误会5%', 0.05)]:
        d = json.load(open(os.path.join(RES, f'main_{name}.json')))
        a = agg([r['metrics'] for r in d['runs'][:10]])
        rows.append(mk('基准', '老实人 50%，n=200，K=10，N=1000', e, a))
    for grp, label, over in VARIANTS:
        for e in (0.0, 0.05):
            rows.append(mk(grp, label, e, summ['sweep'][f'{grp}|{label}|{e}']))
    for grp, label, over in NOISE_VARIANTS:
        e = over.get('e', 0.0)
        a = summ['sweep'][f'{grp}|{label}|{e}']
        rows.append(mk(grp, label, f"看错{over['e_perc'] * 100:g}%" if over.get('e_perc') else e, a))
    header = ['分组', '变体', '误会', '①', '②', '③', '④', '骗子峰值', '终局合作率', '终局第一（10 次里几次）']
    widths = [130, 400, 80, 50, 50, 50, 50, 110, 120, 420]
    table_image(os.path.join(FIG, 'fig_敏感性表.png'), '参数敏感性：情节每一步在 10 个种子里成立几次', header, rows, widths,
                note='①老实人被骗光（跌破 1%）②骗子变多（峰值≥初始 1.5 倍）③以牙还牙起来、骗子消失（<1%）④宽容的以牙还牙终局第一且多于以牙还牙。\n'
                     '“看错”一行：动作不出错，但 5% 看反。μ=0.01 时①③因为突变一直补人，按阈值判不成立。')


STEPS = ['1a_老实人减半', '1b_老实人被骗光', '2_骗子变多', '3_以牙还牙起来_骗子消失', '4_宽容赢过以牙还牙']


def you_figure(scn='误会5%'):
    y = json.load(open(os.path.join(HERE, 'visual', f'you_{scn}.json')))
    path = ' → '.join(NAME[k].split('（')[0] for k in y['how_chosen']['chosen_path'])
    sub = (f'“你”= 1000 人里的第 {y["you_id"]} 号，开局是老实人。走的路：{path}。\n'
           f'开局 500 个老实人里，{y["how_chosen"]["chosen_path_share"] * 100:.0f}% 走的是这条路（最常见的一条）')
    you_chart(os.path.join(FIG, f'fig_你_{scn}.png'), y['generations'], '“你”这一辈子：每一代的分数', sub)


if __name__ == '__main__':
    main()
    sensitivity_figure()
    you_figure('误会5%')
    you_figure('转折_第100代起误会5%')
