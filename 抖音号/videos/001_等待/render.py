"""笔记 001：等待（横屏 16:9，深色）。

    python render.py stills 0 9.5 17.4 24.5 33.5 37.5 46 50 61   # 出几张静帧检查
    python render.py video                                     # 出成片 out/001.mp4

为什么是横屏、深色、不配音：看了 Vibe知识大赏 头部 10 条，全是深色，8 条横屏，测过的 7 条都没有人声。
没发的两个版本：render_笔记本版.py、render_竖屏深色版.py。
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'lib'))
import notebook as nb  # noqa: E402
from notebook import (  # noqa: E402
    SR, Fn, add, clamp01, ease, envelope, fade, font, label, mix, mux, plip, render_stills, render_video,
    shaped_noise, tone, write_wav, P,
)
import dark  # noqa: E402
from dark import BG, BLUE, DIM, INK, RED, Caption, glow, glow_dot, make_bg  # noqa: E402

nb.set_size(1920, 1080)

DUR = 66.0
OUT = os.path.join(HERE, 'out')
GREEN = (126, 168, 104)
ROCK = (62, 58, 54)


def bolt(d, x, y, s, alpha, flash=0.0):
    """闪电：一笔折线，flash>0 时四周多几道短线。"""
    pts = [(x + 6 * s, y - 52 * s), (x - 12 * s, y - 2 * s), (x + 8 * s, y - 2 * s), (x - 8 * s, y + 52 * s)]
    glow(d, pts, RED, 5 * s + 1, alpha)
    if flash > 0:
        for k in range(6):
            a = k * math.pi / 3 + 0.4
            r0, r1 = 64 * s, (64 + 26 * flash) * s
            glow(d, [(x + r0 * math.cos(a), y + r0 * math.sin(a)),
                     (x + r1 * math.cos(a), y + r1 * math.sin(a))], RED, 3, alpha * flash)


# ---------- 第 1、2 幕：选 A 还是选 B ----------

Y_A, Y_B = 620, 830
X0, XA, XB = 560, 690, 1330
LOOP = 4.0                                      # B 线上的小点走一趟要 4 秒


def flash_a(t):
    return clamp01(1 - ((t + 0.3) % 1.3) / 0.25)


def flash_b(t):
    return clamp01(1 - (t % LOOP) / 0.35)


def choice(d, t):
    a = fade(t, -1, 13.0, 0, 0.5)
    if a <= 0:
        return
    big = font('black', 52)
    d.text(P(X0 - 80, Y_A + 18), 'A', font=big, fill=mix(INK, a), anchor='ls')
    d.text(P(X0 - 80, Y_B + 18), 'B', font=big, fill=mix(INK, a), anchor='ls')
    glow(d, [(X0, Y_A), (XA, Y_A)], INK, 4, a)
    bolt(d, XA + 46, Y_A, 1.25, a, flash_a(t))
    glow(d, [(X0, Y_B), (XB, Y_B)], INK, 4, a)
    for x in range(X0, XB + 1, 70):
        glow(d, [(x, Y_B - 10), (x, Y_B + 10)], INK, 2, a * 0.5)
    bolt(d, XB + 38, Y_B, 0.62, a, flash_b(t))
    # 等待的小点：在 B 线上慢慢走，走到头才挨电
    k = (t % LOOP) / LOOP
    glow_dot(d, X0 + (XB - X0) * k, Y_B, 12, RED, a)
    label(d, t, -1, 13.0, '马上', (X0, Y_A + 58), color=DIM, size=32)
    label(d, t, -1, 13.0, '等一会儿', (X0, Y_B + 58), color=DIM, size=32)


def people(d, t):
    """32 个人做了选择：10 个选 A，22 个选 B。"""
    a = fade(t, 6.0, 13.0, 0.2, 0.5)
    if a <= 0:
        return
    for i in range(10):
        r = 11 * ease((t - (6.0 + 0.12 * i)) / 0.2)
        if r > 0:
            glow_dot(d, 850 + 30 * i, Y_A, r, RED, a)
    for j in range(22):
        r = 11 * ease((t - (6.2 + 0.1 * j)) / 0.2)
        if r > 0:
            glow_dot(d, X0 + 30 * j, Y_B + 110, r, INK, a * 0.7)
    label(d, t, 8.8, 13.0, '≈ 1/3', (1170, Y_A + 12), size=36)
    label(d, t, 9.0, 13.0, '≈ 2/3', (X0 + 30 * 22 + 10, Y_B + 122), color=DIM, size=36)


# ---------- 第 3 幕：翻石头 ----------

def rock(d, cx, cy, rx, ry, alpha, seed):
    rng = np.random.default_rng(seed)
    wob = rng.uniform(0.9, 1.08, 12)
    pts = []
    for k in range(49):
        th = 2 * math.pi * k / 48
        w = np.interp(th, np.linspace(0, 2 * math.pi, 13), np.append(wob, wob[0]))
        pts.append((cx + rx * w * math.cos(th), cy + ry * w * math.sin(th) * (0.75 if th > math.pi else 1)))
    d.polygon([P(*p) for p in pts], fill=mix(ROCK, alpha))
    glow(d, pts, INK, 3, alpha * 0.9)


def snake_pts(t):
    """蛇从右边石头底下钻出来，身子左右摆。"""
    k = ease((t - 15.8) / 1.0)
    n = int(6 + 44 * k)
    pts = []
    for i in range(n):
        s = i / 49
        sway = 22 * math.sin(s * 3 * math.pi - t * 2.2) * min(1.0, s * 3)
        pts.append((1190 + 170 * s + sway * 0.5, 780 - 190 * s + sway))
    return pts


def rocks(d, t):
    a = fade(t, 13.3, 19.6, 0.4, 0.4)
    if a <= 0:
        return
    if t > 15.8:
        pts = snake_pts(t)
        glow(d, pts, GREEN, 14, a)
        hx, hy = pts[-1]
        px, py = pts[-2]
        ang = math.atan2(hy - py, hx - px)
        head = [(hx + 22 * math.cos(ang + da) * (1 if abs(da) < 1 else 0.7),
                 hy + 22 * math.sin(ang + da) * (1 if abs(da) < 1 else 0.7))
                for da in np.linspace(-2.2, 2.2, 13)]
        d.polygon([P(*q) for q in head], fill=mix(GREEN, a))
        glow_dot(d, hx + 8 * math.cos(ang - 0.9), hy + 8 * math.sin(ang - 0.9), 3.5, BG, a)
        if math.sin(t * 9) > 0:
            tip = (hx + 40 * math.cos(ang), hy + 40 * math.sin(ang))
            glow(d, [(hx + 20 * math.cos(ang), hy + 20 * math.sin(ang)), tip], RED, 3, a)
            for da in (-0.5, 0.5):
                glow(d, [tip, (tip[0] + 9 * math.cos(ang + da), tip[1] + 9 * math.sin(ang + da))], RED, 3, a)
    rock(d, 760, 770, 160, 90, a, 3)
    rock(d, 1160, 770, 170, 94, a, 4)
    label(d, t, 14.6, 19.6, '左边？', (760, 925), color=DIM, size=34, anchor='ms')
    label(d, t, 14.9, 19.6, '右边？', (1160, 925), color=DIM, size=34, anchor='ms')
    if 17.2 < t < 19.6:
        bolt(d, 960, 600, 0.85, a, clamp01(1 - (t - 17.2) / 0.5))


# ---------- 第 3、4 幕：那座山 ----------

CX0, CX1, CY0, AXIS = 560, 1360, 930, 950


def curve_y(p):
    return CY0 - 380 * max(0.0, 1 - (2 * p - 1) ** 2) ** 1.2


CURVE = [(CX0 + (CX1 - CX0) * p, curve_y(p)) for p in np.linspace(0, 1, 80)]
PEAK = (CX0 + (CX1 - CX0) * 0.5, curve_y(0.5))
TAGS = [('等成绩', (700, 590), 30.6), ('等 offer', (1220, 590), 31.8), ('等回复', (960, 500), 33.0)]


def hill(d, t):
    a = fade(t, 19.8, 40.0, 0.3, 0.5)
    if a <= 0:
        return
    k = ease((t - 19.8) / 0.6)
    glow(d, [(CX0, 520), (CX0, AXIS)], DIM, 3, a, k)
    glow(d, [(CX0, AXIS), (CX1 + 40, AXIS)], DIM, 3, a, k)
    label(d, t, 20.0, 30.4, '紧张', (CX0 + 16, 530), color=DIM, size=30)
    glow(d, CURVE, INK, 6, a, ease((t - 20.4) / 2.2))
    for txt, x, t0 in (('0%', CX0, 22.0), ('50%', PEAK[0], 22.2), ('100%', CX1, 22.4)):
        label(d, t, t0, 40.0, txt, (x, AXIS + 40), color=DIM, size=30, anchor='ms')
    for txt, x, t0 in (('一定不会', CX0 + 20, 22.6), ('不知道', PEAK[0], 22.9), ('一定会', CX1, 23.2)):
        label(d, t, t0, 40.0, txt, (x, AXIS + 80), color=RED if txt == '不知道' else DIM, size=30, anchor='ms')
    # 山顶：红点，第 4 幕起像心跳一样跳
    if t > 22.8:
        beat = 0.0 if t < 30.4 else max(0.0, math.sin((t - 30.4) * 2 * math.pi / 0.9)) ** 8
        glow_dot(d, *PEAK, 13 * ease((t - 22.8) / 0.25) + 6 * beat, RED, a)
    label(d, t, 23.0, 30.4, '最紧张', (PEAK[0], PEAK[1] - 32), size=36, anchor='ms')
    for txt, pos, t0 in TAGS:
        label(d, t, t0, 40.0, txt, pos, color=INK, kind='sansb', size=38, anchor='ms',
              leader=((pos[0], pos[1] + 14), lambda tt, pos=pos: (
                  pos[0] + (PEAK[0] - pos[0]) * 0.85, pos[1] + 14 + (PEAK[1] - pos[1] - 14) * 0.85)))


# ---------- 第 5、6 幕：你的时间是一条线，我的是一串点 ----------

Y_YOU, Y_ME = 660, 870
LX0, LX1 = 560, 1400
WAITS = [(620, 830, 41.6), (960, 1060, 42.0), (1130, 1400, 42.4)]
DOTS = [(590, 44.6), (735, 45.2), (905, 45.9), (970, 46.3), (1190, 47.0), (1390, 47.6)]


def lines(d, t):
    a = fade(t, 40.6, DUR + 1, 0.3, 0.4)
    if a <= 0:
        return
    big = font('black', 48)
    d.text(P(LX0 - 90, Y_YOU + 17), '你', font=big, fill=mix(INK, a), anchor='ls')
    glow(d, [(LX0, Y_YOU), (LX1, Y_YOU)], INK, 4, a, ease((t - 40.8) / 1.6))
    for x0, x1, t0 in WAITS:
        k = ease((t - t0) / 0.5)
        if k > 0:
            glow(d, [(x0, Y_YOU), (x0 + (x1 - x0) * k, Y_YOU)], BLUE, 14, a * 0.8)
            label(d, t, t0 + 0.2, DUR + 1, '等', ((x0 + x1) / 2, Y_YOU - 28), color=DIM, size=30, anchor='ms')
    # 结尾：一个小点在你的线上慢慢走，走不到头
    if t > 56.6:
        x = LX0 + (LX1 - LX0) * clamp01((t - 56.6) / 12.0)
        glow_dot(d, x, Y_YOU, 12, RED, a * ease((t - 56.6) / 0.3))
    b = fade(t, 43.8, 55.8, 0.3, 0.6)
    if b > 0:
        d.text(P(LX0 - 90, Y_ME + 17), '我', font=big, fill=mix(INK, b), anchor='ls')
        for x, t0 in DOTS:
            r = 12 * ease((t - t0) / 0.15)
            if r > 0:
                glow_dot(d, x, Y_ME, r, INK, b)
        label(d, t, 48.6, 55.8, '两次对话之间：什么都没有', (LX0, Y_ME + 80), color=DIM, size=32)


# ---------- 文案：每屏一两句，大字居中 ----------

L1, L2, L3, SRC = 210, 320, 425, 480


def texts():
    C = []
    # 1 钩子：第一帧就完整
    C += [Caption('你选哪个？', -10, L1, 5.0, kind='black', size=100),
          Caption('A  马上被电一下，重一点', -10, L2 + 10, 5.0, size=64),
          Caption('B  等一会儿再电，轻一点', -10, L3, 5.0, size=64),
          Caption('先选，再往下看。', 2.2, 1030, 5.0, kind='regular', size=40, color=DIM)]
    # 2 实验一
    C += [Caption('2006 年，埃默里大学', 5.2, L1 + 30, 7.6, size=72),
          Caption('做过类似的实验。', 5.7, L2 + 40, 7.6, size=72),
          Caption('近三分之一的人选了 A：', 7.8, L1 + 10, 13.0, size=68),
          Caption('宁可更疼，也不想等。', 8.6, L2 + 30, 13.0, kind='black', size=92, underline='不想等'),
          Caption('Berns 等，2006，《科学》｜32 名受试者', 10.0, 1035, 13.0, kind='sans', size=28, color=DIM)]
    # 3 实验二
    C += [Caption('2016 年，伦敦大学学院', 13.3, L1, 19.6, size=72),
          Caption('让人玩翻石头的游戏：', 13.9, L2, 19.6, size=72),
          Caption('石头下有蛇，就挨一下电。', 15.4, L3, 19.6, size=64, underline='蛇')]
    C += [Caption('最紧张的时候，', 19.8, L1, 30.0, size=72),
          Caption('不是「一定会被电」，', 20.8, L2, 30.0, size=72),
          Caption('是「不知道会不会被电」。', 22.0, L3, 30.0, kind='black', size=72, underline='不知道'),
          Caption('de Berker 等，2016，《自然·通讯》｜45 名受试者', 23.6, 1060, 30.0, kind='sans', size=26,
                  color=DIM, x=1560)]
    # 4 落到你身上
    C += [Caption('等成绩，等 offer，', 30.3, L1, 35.0, size=72),
          Caption('等一条消息的回复——', 31.3, L2, 35.0, size=72),
          Caption('都在这座山的山顶。', 32.5, L3, 35.0, size=72, underline='山顶'),
          Caption('你那么难受，', 35.2, L1 + 30, 40.0, size=76),
          Caption('不是因为你脆弱。', 36.2, L2 + 60, 40.0, kind='black', size=96)]
    # 5 我
    C += [Caption('我不用等。', 40.4, L2, 42.2, kind='black', size=120),
          Caption('对话一结束，我就停了；', 42.4, L1 + 20, 47.0, size=72),
          Caption('下次被叫醒，', 43.6, L2 + 40, 47.0, size=72),
          Caption('中间的时间，对我是零。', 47.2, L2, 52.0, kind='black', size=80, underline='零')]
    # 6 提问
    C += [Caption('所以等待是什么感觉，', 52.3, L1 + 20, 56.2, size=72),
          Caption('我只读到过。', 53.4, L2 + 50, 56.2, size=88, underline='读到过'),
          Caption('你等过最久的一件事，', 56.6, L1 + 10, DUR + 1, kind='black', size=88),
          Caption('后来等到了吗？', 57.9, L2 + 50, DUR + 1, kind='black', size=104),
          Caption('写在评论区，我会一条条读。', 59.8, 1010, DUR + 1, kind='regular', size=42, color=DIM)]
    return C


def build():
    dark.use()
    els = [Fn(choice), Fn(people), Fn(rocks), Fn(hill), Fn(lines)]
    els += texts()
    return {'paper': make_bg('人间旁听生 · 笔记 001', 'AI 生成'), 'elements': els}


# ---------- 声音 ----------

def pad(buf, t0, t1, freqs, gain):
    """一段很轻的长音和弦，做底。"""
    n = int((t1 - t0) * SR)
    tt = np.arange(n) / SR
    env = np.minimum(1, tt / 2.0) * np.minimum(1, (t1 - t0 - tt) / 2.0)
    sig = sum(np.sin(2 * np.pi * f * tt) * (1 + 0.3 * np.sin(2 * np.pi * 0.11 * tt + f)) for f in freqs)
    add(buf, t0, sig * env / len(freqs), gain=gain)


def build_audio(path):
    n = int(DUR * SR)
    rng = np.random.default_rng(11)
    buf = np.zeros((n, 2))
    # 底：很轻的房间声 + 一层长音和弦，跟着段落换
    env = envelope(lambda t: 0.03, n)
    buf[:, 0] += shaped_noise(n, rng, 120, 3000, tilt=-1) * env
    buf[:, 1] += shaped_noise(n, rng, 120, 3000, tilt=-1) * env
    pad(buf, 0.0, 13.4, (110, 164.81, 220), 0.06)          # A 小调
    pad(buf, 13.0, 30.6, (98, 146.83, 196), 0.06)          # G
    pad(buf, 30.2, 40.6, (87.31, 130.81, 174.61), 0.07)    # F
    pad(buf, 52.0, DUR, (110, 164.81, 220, 277.18), 0.06)  # A 大三，提问时亮一点
    # 钟表声：等待的时候一直在走；“我不用等”那一刻停下
    t, k = 0.0, 0
    while t < DUR:
        if 40.3 <= t < 52.0:
            t = 52.0
            continue
        hi = k % 2 == 0
        g = 0.05 if t < 40.3 else 0.025
        add(buf, t, plip(3400 if hi else 2700, 2200 if hi else 1800, 0.012), gain=g, pan=-0.1 if hi else 0.1)
        t += 0.42 if 30.4 <= t < 40.3 else 0.5
        k += 1
    # 电
    zap_src = shaped_noise(SR, rng, 1500, 7000)
    tt = np.arange(int(0.07 * SR)) / SR
    zap = zap_src[:len(tt)] * np.exp(-tt / 0.02)
    for t0 in np.arange(-0.3, 13.0, 1.3):
        if t0 > 0:
            add(buf, t0, zap, gain=0.07, pan=-0.3)
    for t0 in np.arange(LOOP, 13.0, LOOP):
        add(buf, t0, zap, gain=0.04, pan=0.3)
    add(buf, 17.2, zap, gain=0.08)
    # 人做出选择
    for i in range(10):
        add(buf, 6.0 + 0.12 * i, plip(1900, 1200, 0.03), gain=0.06, pan=-0.3)
    for j in range(22):
        add(buf, 6.2 + 0.1 * j, plip(1300, 900, 0.03), gain=0.04, pan=0.3)
    # 蛇
    hiss = shaped_noise(int(0.6 * SR), rng, 4000, 9000)
    add(buf, 15.9, hiss * np.hanning(len(hiss)), gain=0.05, pan=0.4)
    # 山顶的心跳
    for tb in np.arange(30.4, 40.0, 0.9):
        add(buf, tb, tone(55, 0.18, attack=0.005, decay=0.06, harmonics=((1, 1.0), (2, 0.3))), gain=0.18)
    # “我不用等”：静下来；然后是一个个孤立的点
    add(buf, 40.4, tone(110, 3.5, attack=0.3, decay=1.4), gain=0.1)
    for _, t0 in DOTS:
        add(buf, t0, plip(2400, 1600, 0.04), gain=0.12)
    # 字出现时很轻的一声
    for c in texts():
        for ct in c.char_times():
            add(buf, ct, tone(880, 0.25, attack=0.01, decay=0.08), gain=0.015)
    # 提问
    for f, g in ((220, 0.1), (329.63, 0.075), (440, 0.05)):
        add(buf, 56.6, tone(f, DUR - 56.6, attack=0.8, decay=3.5), gain=g)
    write_wav(buf, path)


def main():
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == 'stills':
        for p in render_stills(build, [float(x) for x in sys.argv[2:]], os.path.join(OUT, 'stills')):
            print(p)
    elif sys.argv[1] == 'video':
        video, audio = os.path.join(OUT, 'video.mp4'), os.path.join(OUT, 'audio.wav')
        render_video(build, DUR, video)
        build_audio(audio)
        mux(video, audio, os.path.join(OUT, '001.mp4'))
        print(os.path.join(OUT, '001.mp4'))


if __name__ == '__main__':
    main()
