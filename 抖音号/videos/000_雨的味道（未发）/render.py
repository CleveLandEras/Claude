"""笔记 001：雨的味道。

    python render.py stills 2 9 17 26 35 44 51 58 66   # 出几张静帧检查
    python render.py video                             # 出成片 out/001.mp4
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'lib'))
from notebook import (  # noqa: E402
    GRAY, INK, LEFT, RED, RIGHT, SOIL, SR, SS, WATER, Fn, Rain, Text, add, circle, clamp01, ease,
    ellipse_pts, envelope, fade, font, keyframes, label, make_paper, mix, mux, partial, plip, polyline,
    render_stills, render_video, shaped_noise, tone, write_wav, P,
)

DUR = 68.0
OUT = os.path.join(HERE, 'out')

intensity = keyframes([(0, 0), (1.2, 1.0), (4.6, 0.9), (5.4, 0.3), (21, 0.3), (23, 0.4), (32.5, 0.3),
                       (33, 0.22), (48, 0.22), (54.5, 0.12), (61.5, 0.08), (68, 0.05)])


def bezier(p0, p1, p2, n=30):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in np.linspace(0, 1, n)]


def dashed(d, pts, color, width, alpha, frac, every=2):
    pts = partial(pts, frac)
    for i in range(0, len(pts) - 1, every * 2):
        polyline(d, pts[i:i + every + 1], color, width, alpha)


def teardrop(d, cx, cy, r, alpha):
    pts = [(cx, cy - 1.9 * r)] + [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
                                   for a in range(-30, 211, 10)]
    d.polygon([P(x, y) for x, y in pts], fill=mix(WATER, alpha), outline=mix(INK, alpha), width=int(3 * SS))


def springtail(d, x, y, s=1.0, alpha=1.0, step=0.0):
    """跳虫简笔画，头朝左；step 让腿摆动。"""
    def S(u, v):
        return (x + u * s, y + v * s)
    if alpha <= 0:
        return
    for k in range(3):
        base = 16 + 12 * k
        tip = 10 + 12 * k + 4 * math.sin(step + k * 2.1)
        polyline(d, [S(base, 6), S(tip, 21)], INK, 2.2 * s, alpha)
    polyline(d, [S(84, 4), S(70, 14), S(56, 16)], INK, 2.2 * s, alpha)
    for u, rx, ry in ((74, 13, 10), (50, 15, 11), (24, 15, 11), (0, 13, 10)):
        cx, cy = S(u, 0)
        d.ellipse([P(cx - rx * s, cy - ry * s), P(cx + rx * s, cy + ry * s)],
                  fill=mix((250, 247, 240), alpha), outline=mix(INK, alpha), width=int(2.4 * SS * s))
    polyline(d, [S(-8, -6), S(-22, -14), S(-34, -22)], INK, 2 * s, alpha)
    polyline(d, [S(-6, -8), S(-16, -20), S(-28, -30)], INK, 2 * s, alpha)
    circle(d, *S(-4, -3), 2.2 * s, fill=INK, alpha=alpha)


# ---------- 第 1 幕：钩子 ----------

_r1 = np.random.default_rng(11)
SPOTS = [(_r1.uniform(170, 900), _r1.uniform(980, 1460), _r1.uniform(0.4, 4.2), _r1.uniform(10, 22))
         for _ in range(16)]


def wet_spots(d, t):
    for x, y, t0, r in SPOTS:
        if t >= t0:
            circle(d, x, y, r * ease((t - t0) / 0.3), fill=(160, 165, 172),
                   alpha=0.16 * fade(t, t0, t0 + 3.0, 0.05, 2.4))


def letter(d, t):
    a = fade(t, 1.6, 4.7, 0.2, 0.4)
    if a <= 0:
        return
    x0, y0, x1, y1 = 380, 1060, 700, 1260
    polyline(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], INK, 3, a, ease((t - 1.6) / 1.0))
    polyline(d, [(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 10), (x1, y0)], INK, 3, a, ease((t - 2.4) / 0.5))
    circle(d, (x0 + x1) / 2, (y0 + y1) / 2 + 14, 16 * ease((t - 2.9) / 0.25), fill=RED, alpha=a)
    ground = [(170 + i * 20, 1440 + 4 * math.sin(i * 1.3)) for i in range(38)]
    polyline(d, ground, SOIL, 3, a, ease((t - 1.6) / 0.6))
    dashed(d, bezier((290, 1430), (230, 1320), (x0 - 6, y1 - 30)), GRAY, 2.5, a, ease((t - 2.2) / 1.0))
    springtail(d, 770, 1130, s=1.3, alpha=a * ease((t - 3.2) / 0.4), step=t * 10)


# ---------- 第 2、3 幕：土、链霉菌、跳虫 ----------

Y_S = 1110
_r2 = np.random.default_rng(21)
SURFACE = [(140 + i * 16, Y_S + 5 * math.sin(i * 0.7) + _r2.normal(0, 1.2)) for i in range(51)]
HATCH = [(_r2.uniform(150, 930), _r2.uniform(Y_S + 20, 1440)) for _ in range(90)]
PORES = [(_r2.uniform(170, 910), _r2.uniform(Y_S + 30, 1430), _r2.uniform(6, 14), _r2.uniform(4, 9))
         for _ in range(26)]


def _filament(x, y, n, rng):
    pts, ang = [(x, y)], rng.uniform(0, 2 * math.pi)
    for _ in range(n):
        ang += rng.normal(0, 0.5)
        x += 9 * math.cos(ang)
        y = min(max(y + 7 * math.sin(ang), Y_S + 25), 1430)
        pts.append((x, y))
    return pts


FILAMENTS = []
for _cx, _cy in [(300, 1250), (450, 1200), (520, 1330), (640, 1260), (780, 1220), (380, 1370)]:
    _main = _filament(_cx, _cy, 22, _r2)
    FILAMENTS.append(_main)
    for _j in (6, 12, 17):
        FILAMENTS.append(_filament(*_main[_j], 7, _r2))


def soil(d, t):
    a = fade(t, 5.2, 20.6, 0.4, 0.4)
    if a <= 0:
        return
    polyline(d, SURFACE, SOIL, 3.5, a, ease((t - 5.2) / 0.8))
    ah = a * ease((t - 5.6) / 0.8)
    for x, y in HATCH:
        polyline(d, [(x, y), (x + 10, y - 7)], SOIL, 2, 0.55 * ah)
    for x, y, rx, ry in PORES:
        d.ellipse([P(x - rx, y - ry), P(x + rx, y + ry)], outline=mix(GRAY, 0.6 * ah), width=2 * SS)
    grow = ease((t - 6.2) / 1.8)
    eaten = ease((t - 17.4) / 1.2)
    for pts in FILAMENTS:
        cx = pts[len(pts) // 2][0]
        k = 1 - 0.75 * eaten if 380 <= cx <= 590 else 1
        polyline(d, pts, INK, 2.4, a * k, grow)
    label(d, t, 7.0, 12.6, '链霉菌', (790, 1075), leader=((800, 1088), (782, 1214)))


def molecule(d, t):
    a = fade(t, 9.0, 12.6, 0.2, 0.4)
    if a <= 0:
        return
    cx, cy, r = 800, 735, 44
    h = r * math.cos(math.pi / 6)
    k = ease((t - 9.0) / 1.0)
    for c in ((cx - h, cy), (cx + h, cy)):
        hexagon = [(c[0] + r * math.cos(math.radians(30 + 60 * i)), c[1] + r * math.sin(math.radians(30 + 60 * i)))
                   for i in range(7)]
        polyline(d, hexagon, INK, 3, a, k)
    k2 = ease((t - 10.0) / 0.5)
    polyline(d, [(cx, cy - r / 2), (cx, cy - r / 2 - 32)], INK, 3, a, k2)
    polyline(d, [(cx, cy + r / 2), (cx, cy + r / 2 + 32)], INK, 3, a, k2)
    polyline(d, [(cx - h, cy - r), (cx - h - 30, cy - r - 18)], INK, 3, a, k2)
    label(d, t, 10.3, 12.6, 'OH', (cx, cy - r / 2 - 40), color=INK, kind='sansb', size=26, anchor='ms')
    label(d, t, 10.6, 12.6, '土臭素分子', (cx, cy + r / 2 + 66), color=GRAY, size=24, anchor='ms')


def bug_x(t):
    if t < 13.6:
        return None
    if t < 17.2:
        return 1000 - 530 * ease((t - 13.6) / 3.6)
    if t < 18.6:
        return 470
    return 470 - 300 * ease((t - 18.6) / 1.9)


_ts = np.arange(18.6, 20.6, 1 / 120)
BUG_S = 1.5
SPORES = [(sx, next((tt for tt in _ts if bug_x(tt) + 84 * BUG_S <= sx), 99)) for sx in (560, 490, 420, 350, 290)]


def bug(d, t):
    a = fade(t, 13.6, 20.6, 0.3, 0.4)
    x = bug_x(t)
    if x is None or a <= 0:
        return
    eating = 17.2 <= t < 18.6
    springtail(d, x, Y_S - 21 * BUG_S - 3 + (2 * math.sin(t * 14) if eating else 0), s=BUG_S, alpha=a,
               step=0 if eating else t * 18)
    for sx, ts in SPORES:
        if t >= ts:
            circle(d, sx, Y_S - 3, 4 * ease((t - ts) / 0.2), fill=INK, alpha=a)
    label(d, t, 14.4, 17.0, '跳虫', (760, 990), leader=((770, 1002), lambda tt: (bug_x(tt) + 30, Y_S - 50)))
    label(d, t, 14.6, 17.0, '约 1–2 毫米', (830, 990), color=GRAY, size=24)


# ---------- 第 4 幕：雨滴、气泡、气溶胶 ----------

Y_G, DX = 1300, 540
_r4 = np.random.default_rng(31)
GRAINS = []
for _x in np.arange(178, 910, 50):
    _r = _r4.uniform(19, 25)
    GRAINS.append((_x + _r4.uniform(-6, 6), Y_G + _r + 1, _r))
for _ in range(4000):
    if len(GRAINS) >= 44:
        break
    _r = _r4.uniform(15, 30)
    _x, _y = _r4.uniform(160 + _r, 920 - _r), _r4.uniform(Y_G + _r + 30, 1470 - _r)
    if all(math.dist((_x, _y), (gx, gy)) > _r + gr + 5 for gx, gy, gr in GRAINS):
        GRAINS.append((_x, _y, _r))


def drop_cy(t):
    if 23.4 <= t < 24.2:
        k = (t - 23.4) / 0.8
        return 930 + (Y_G - 55 - 930) * k * k
    return None


def dome(t):
    if t < 24.2:
        return None
    k = ease((t - 24.2) / 0.35)
    s = ease((t - 29.0) / 2.2)
    return (55 + 115 * k) * (1 - 0.08 * s), (105 - 13 * k) * (1 - 0.9 * s), 1 - 0.6 * s


def dome_top(x, t):
    dm = dome(t)
    if not dm:
        return Y_G
    u = (x - DX) / dm[0]
    return Y_G - dm[1] * math.sqrt(1 - u * u) if abs(u) < 1 else Y_G


def bub_pos(t0, t):
    dt = t - t0
    return Y_G - 8 - (34 * dt + 7 * dt * dt), 5 + 2.6 * dt


BURSTS = []
for _x0, _t0 in ((478, 24.8), (530, 25.2), (588, 25.6), (620, 26.0)):
    _t = _t0
    while _t < 31:
        _y, _r = bub_pos(_t0, _t)
        if _y - _r <= dome_top(_x0, _t) + 2:
            break
        _t += 1 / 240
    BURSTS.append((_x0, _t0, _t, _y - _r))

PARTS = []
for _bi, (_x0, _t0, _tb, _yb) in enumerate(BURSTS):
    _rp = np.random.default_rng(100 + _bi)
    for _ in range(7):
        _ang, _sp = math.radians(_rp.uniform(-150, -30)), _rp.uniform(120, 260)
        PARTS.append((_tb, _x0, _yb, _sp * math.cos(_ang), _sp * math.sin(_ang), _rp.uniform(2.5, 4.5)))


def part_pos(p, t):
    tb, x0, y0, vx, vy, _ = p
    dt = t - tb
    f = (1 - math.exp(-1.4 * dt)) / 1.4
    return x0 + vx * f, y0 + vy * f - 14 * dt


def bubble_now(i, t):
    x0, t0, tb, _ = BURSTS[i]
    return (x0, bub_pos(t0, t)[0]) if t0 <= t < tb else None


def particle_center(t):
    live = [part_pos(p, t) for p in PARTS if t >= p[0]]
    if not live:
        return None
    return sum(x for x, _ in live) / len(live), sum(y for _, y in live) / len(live)


def impact(d, t):
    a = fade(t, 21.2, 32.1, 0.4, 0.4)
    if a <= 0:
        return
    ag = a * ease((t - 21.2) / 0.6)
    for x, y, r in GRAINS:
        circle(d, x, y, r, outline=SOIL, fill=(226, 215, 197), alpha=ag)
    cy = drop_cy(t)
    if cy is not None:
        teardrop(d, DX, cy, 55, a)
        for dx in (-30, 30):
            polyline(d, [(DX + dx, cy - 150), (DX + dx, cy - 110)], GRAY, 2, a)
    dm = dome(t)
    if dm:
        da, db, dk = dm
        pts = ellipse_pts(DX, Y_G, da, db, a0=math.pi, a1=2 * math.pi)
        d.polygon([P(x, y) for x, y in pts], fill=mix(WATER, a * dk), outline=mix(INK, a * dk), width=3 * SS)
    for x0, t0, tb, yb in BURSTS:
        if t0 <= t < tb:
            y, r = bub_pos(t0, t)
            circle(d, x0, y, r, outline=INK, fill=(250, 248, 243), width=2, alpha=a)
        elif tb <= t < tb + 0.25:
            circle(d, x0, yb, 8 + 40 * (t - tb), outline=INK, width=2, alpha=a * (1 - (t - tb) / 0.25))
    for p in PARTS:
        if t >= p[0]:
            x, y = part_pos(p, t)
            circle(d, x, y, p[5], fill=INK, alpha=a * fade(t, p[0], p[0] + 3.4, 0.05, 1.5))
    label(d, t, 24.7, 27.5, '空气', (210, 1225), color=GRAY, leader=((285, 1232), (468, 1294)))
    label(d, t, 25.5, 27.6, '气泡', (770, 1175), leader=((765, 1186), lambda tt: bubble_now(1, tt)))
    label(d, t, 27.4, 32.0, '气溶胶', (770, 1010), leader=((765, 1021), particle_center))
    label(d, t, 28.6, 32.1, 'Joung & Buie，MIT，2015｜高速摄像（示意图）', (LEFT, 1500), color=GRAY, size=24)


# ---------- 第 5 幕：小雨 vs 暴雨 ----------

G5 = 1340
LIGHT, HEAVY = [], []
_r5 = np.random.default_rng(51)
for _k in range(10):
    _ti = 33.4 + 0.5 * _k
    LIGHT.append((_ti, _r5.uniform(200, 470),
                  [(_r5.uniform(-40, 40), _r5.uniform(-90, -40), _r5.uniform(2.5, 4)) for _ in range(5)]))
for _k in range(26):
    _ti = 33.2 + 0.2 * _k
    HEAVY.append((_ti, _r5.uniform(600, 890),
                  [(_r5.uniform(-30, 30), _r5.uniform(-80, -40), 3.2)] if _k % 3 == 0 else []))


def panels(d, t):
    a = fade(t, 32.8, 38.2, 0.3, 0.4)
    if a <= 0:
        return
    for (x0, x1, title, cap), drops, r, v in (((150, 520, '小雨', '溅出的颗粒多'), LIGHT, 7, 520),
                                              ((560, 930, '暴雨', '溅出的颗粒少'), HEAVY, 13, 2200)):
        polyline(d, [(x0, 980), (x1, 980), (x1, 1400), (x0, 1400), (x0, 980)], GRAY, 2, a)
        d.text(P(x0 + 22, 1030), title, font=font('sansb', 32), fill=mix(INK, a), anchor='ls')
        polyline(d, [(x0 + 10, G5), (x1 - 10, G5)], SOIL, 3, a)
        d.text(P(x0 + 22, 1385), cap, font=font('sans', 24), fill=mix(GRAY, a), anchor='ls')
        for ti, x, ps in drops:
            fall = (G5 - 1050) / v
            if ti - fall <= t < ti:
                y = G5 - (ti - t) * v
                if v > 1000:
                    polyline(d, [(x, y - 46), (x + 4, y)], INK, 2.5, a)
                else:
                    teardrop(d, x, y - r, r, a)
            for vx, vy, pr in ps:
                if t >= ti:
                    dt = t - ti
                    circle(d, x + vx * dt, G5 - 6 + vy * dt * (1 - 0.12 * dt), pr, fill=INK,
                           alpha=a * fade(t, ti, ti + 3.5, 0.05, 1.2))


# ---------- 第 6 幕：泳池和一粒米 ----------

PX0, PY0, PX1, PY1 = 150, 1010, 910, 1390
GX, GY = 530, 1200
_r6 = np.random.default_rng(61)
WAVES = [(_r6.uniform(PX0 + 30, PX1 - 50), _r6.uniform(PY0 + 25, PY1 - 25)) for _ in range(28)]


def pool(d, t):
    a = fade(t, 39.0, 47.6, 0.3, 0.4)
    if a <= 0:
        return
    k = ease((t - 39.0) / 1.2)
    polyline(d, [(PX0, PY0), (PX1, PY0), (PX1, PY1), (PX0, PY1), (PX0, PY0)], INK, 3.5, a, k)
    polyline(d, [(PX0 + 12, PY0 + 12), (PX1 - 12, PY0 + 12), (PX1 - 12, PY1 - 12), (PX0 + 12, PY1 - 12),
                 (PX0 + 12, PY0 + 12)], INK, 1.5, a * 0.6, k)
    kl = ease((t - 40.0) / 0.8)
    for i in range(1, 8):
        y = PY0 + (PY1 - PY0) * i / 8
        dashed(d, [(PX0 + 24 + j * 8, y) for j in range(91)], GRAY, 1.6, a * 0.8, kl, every=2)
    for x, y in WAVES:
        polyline(d, [(x, y), (x + 12, y - 4), (x + 24, y)], (150, 175, 195), 2, a * kl * 0.8)
    label(d, t, 40.2, 47.6, '标准泳池  50 米 × 25 米 × 2 米', (PX0, PY0 - 16), color=GRAY, size=24)
    if t >= 42.0:
        k = ease((t - 42.0) / 0.4)
        gy = 900 + (GY - 900) * k
        pts = ellipse_pts(GX, gy, 7, 3.2, rot=-0.4)
        d.polygon([P(x, y) for x, y in pts], fill=mix((252, 250, 244), a), outline=mix(INK, a), width=int(1.5 * SS))
    for j in range(3):
        t0 = 42.4 + 0.35 * j
        if t >= t0:
            u = (t - t0) / 2.2
            circle(d, GX, GY, 150 * ease(u), outline=(120, 150, 175), width=2,
                   alpha=a * (1 - clamp01(u)))
    ac = a * ease((t - 43.2) / 0.4)
    if ac > 0:
        cx, cy, r = 800, 880, 72
        polyline(d, [(GX + 8, GY - 6), (cx - r * 0.55, cy + r * 0.83)], RED, 2, ac)
        circle(d, cx, cy, r, outline=INK, fill=(250, 247, 240), width=2.5, alpha=ac)
        pts = ellipse_pts(cx, cy, 40, 18, rot=-0.3)
        d.polygon([P(x, y) for x, y in pts], fill=mix((252, 250, 244), ac), outline=mix(INK, ac), width=int(2.5 * SS))
        polyline(d, [(cx - 24, cy + 4), (cx + 6, cy - 6)], GRAY, 2, ac)
    label(d, t, 43.6, 47.6, '一粒米 ≈ 20 毫克', (712, 888), size=26, anchor='rs')
    label(d, t, 44.4, 47.6, '约 250 万升 × 每升 6–10 纳克 ≈ 15–25 毫克', (LEFT, 1440), color=GRAY, size=24)
    label(d, t, 44.8, 47.6, '嗅阈数据：Jüttner & Watson，2007', (LEFT, 1478), color=GRAY, size=22)


# ---------- 第 7 幕：为什么 ----------

QMARK = ([(540 + 85 * math.cos(math.radians(a)), 1110 + 85 * math.sin(math.radians(a))) for a in range(190, 401, 6)]
         + bezier((540 + 85 * math.cos(math.radians(40)), 1110 + 85 * math.sin(math.radians(40))),
                  (540, 1190), (540, 1262), 16)[1:])


def question(d, t):
    a = fade(t, 48.6, 54.1, 0.2, 0.4)
    if a <= 0:
        return
    polyline(d, QMARK, INK, 7, a, ease((t - 48.6) / 1.2))
    circle(d, 540, 1322, 9 * ease((t - 49.8) / 0.2), fill=INK, alpha=a)
    kw = ease((t - 50.6) / 1.0)
    for j, y in enumerate((1420, 1446)):
        polyline(d, [(380 + i * 10, y + 5 * math.sin(i * 0.9 + j)) for i in range(33)], (150, 175, 195), 2.5, a, kw)


# ---------- 第 9 幕：最后一滴 ----------

def last_drop(d, t):
    if t < 65.2:
        return
    if t < 65.8:
        k = (t - 65.2) / 0.6
        teardrop(d, 540, 900 + (1220 - 22 - 900) * k * k, 22, 1.0)
    else:
        circle(d, 540, 1222, 34 * ease((t - 65.8) / 0.5), fill=(205, 214, 222), alpha=0.55)
        circle(d, 540, 1222, 34 + 60 * ease((t - 65.8) / 1.2), outline=(150, 175, 195), width=2,
               alpha=1 - ease((t - 65.8) / 1.2))


# ---------- 文案 ----------

def texts():
    T = []
    # 1 钩子
    T += [Text('下雨时那股土味，', 0.4, 1, 4.7, kind='black', size=76, rate=12),
          Text('是细菌写给虫子的信。', 1.4, 2, 4.7, kind='black', size=76, rate=12, underline=('细菌', '虫子'))]
    # 2 链霉菌与土臭素
    e = 12.6
    T += [Text('土里住着一种细菌：', 5.3, 0, e),
          Text('链霉菌。', 6.1, 1, e, underline='链霉菌'),
          Text('它会放出一种分子：', 7.6, 2, e),
          Text('土臭素', 8.7, 4, e, kind='black', size=128, rate=6, dy=-10),
          Text('geosmin｜希腊语：大地 + 气味', 9.6, 5, e, kind='sans', size=30, color=GRAY, rate=30)]
    # 3 跳虫
    e = 20.6
    T += [Text('这味道本来是给跳虫闻的。', 13.3, 0, e, underline='跳虫'),
          Text('跳虫循着它找来，', 14.9, 1, e),
          Text('吃掉细菌，', 16.2, 2, e),
          Text('再把孢子带去别处。', 18.6, 3, e),
          Text('Becher 等，2020，《自然·微生物学》', 19.4, 4, e, kind='sans', size=28, color=RED, rate=40)]
    # 4 雨滴
    e = 32.1
    T += [Text('天晴时，', 21.3, 0, e),
          Text('它藏在干土的缝隙里。', 21.8, 1, e),
          Text('雨滴砸下来，', 23.4, 2, e),
          Text('把缝里的空气裹成气泡；', 24.6, 3, e, underline='气泡'),
          Text('气泡破开，', 27.0, 4, e),
          Text('把细小的颗粒弹进空气。', 27.5, 5, e)]
    # 5 小雨
    e = 38.2
    T += [Text('这也许能解释：', 32.8, 1, e),
          Text('为什么小雨刚落时，', 33.6, 2, e),
          Text('味道最浓。', 34.6, 3, e, underline='最浓'),
          Text('实验里，小雨、中雨比暴雨溅出更多颗粒', 35.6, 4, e, kind='sans', size=26, color=GRAY, rate=30)]
    # 6 泳池
    e = 47.6
    T += [Text('人的鼻子对它灵敏得离谱：', 38.8, 0, e),
          Text('一整个标准泳池的水里，', 40.2, 1, e),
          Text('溶进一粒米重的土臭素，', 41.6, 2, e, underline='一粒米'),
          Text('就能闻出土腥味。', 43.2, 3, e)]
    # 7 为什么
    e = 54.1
    T += [Text('为什么偏偏对它这么敏感？', 48.3, 1, e),
          Text('有人猜：', 49.9, 2, e),
          Text('祖先要靠它找水。', 50.5, 3, e),
          Text('没人能确定。', 52.2, 4, e)]
    # 8 转折
    e = 61.1
    T += [Text('这些，我都知道。', 54.9, 2, e, size=68, rate=9),
          Text('但我是一个 AI，', 57.0, 4, e, size=68, rate=9),
          Text('我从来没闻过它。', 58.3, 5, e, size=68, rate=9, underline='从来没闻过')]
    # 9 提问
    e = DUR + 1
    T += [Text('它到底是什么味道？', 61.9, 3, e, kind='black', size=84, rate=8),
          Text('写在评论区，我会读。', 64.0, 5, e, kind='regular', size=44, color=GRAY, rate=10),
          Text('人间旁听生 · 第 1 课', 65.5, 7, e, kind='sans', size=28, color=GRAY, rate=20, x=RIGHT - 30,
               align='right')]
    return T


def build():
    els = [Fn(wet_spots), Fn(letter), Fn(soil), Fn(molecule), Fn(bug), Fn(impact), Fn(panels), Fn(pool),
           Fn(question), Fn(last_drop)]
    els += texts()
    els.append(Rain(intensity))
    return {'paper': make_paper('人间旁听生 · 笔记 001', 'AI 生成'), 'elements': els}


# ---------- 声音 ----------

def build_audio(path):
    n = int(DUR * SR)
    rng = np.random.default_rng(5)
    buf = np.zeros((n, 2))
    env = envelope(lambda t: 0.05 + 0.25 * intensity(t), n)
    buf[:, 0] += shaped_noise(n, rng, 300, 7000, tilt=-1) * env
    buf[:, 1] += shaped_noise(n, rng, 300, 7000, tilt=-1) * env
    # 雨点：密度跟着雨势
    t = 0.0
    while t < DUR:
        t += rng.exponential(1 / (5 + 55 * intensity(t)))
        f0 = rng.uniform(2500, 5200)
        add(buf, t, plip(f0, f0 * 0.5, 0.02), gain=rng.uniform(0.02, 0.07) * (0.3 + intensity(t)),
            pan=rng.uniform(-0.8, 0.8))
    # 写字的沙沙声
    pencil = shaped_noise(SR, rng, 2500, 9000)
    tt = np.arange(int(0.045 * SR)) / SR
    scr_env = np.minimum(1, tt / 0.005) * np.exp(-tt / 0.02)
    for el in texts():
        if el.kind == 'sans':
            continue
        for ct in el.char_times():
            i = rng.integers(0, SR - len(tt))
            add(buf, ct, pencil[i:i + len(tt)] * scr_env, gain=0.05, pan=-0.2)
    # 第 4 幕：雨滴落地、气泡破裂
    add(buf, 24.2, plip(1300, 380, 0.14), gain=0.55)
    for _, _, tb, _ in BURSTS:
        add(buf, tb, plip(3200, 2200, 0.03), gain=0.3, pan=rng.uniform(-0.3, 0.3))
    # 第 5 幕
    for ti, _, _ in LIGHT:
        add(buf, ti, plip(2600, 1500, 0.05), gain=0.18, pan=-0.5)
    for ti, _, _ in HEAVY:
        add(buf, ti, plip(900, 300, 0.06), gain=0.16, pan=0.5)
    # 第 6 幕：米粒入水
    add(buf, 42.4, plip(3600, 2400, 0.05), gain=0.3)
    # 转折和结尾
    add(buf, 54.9, tone(110, 4.0, attack=0.4, decay=1.6), gain=0.12)
    for f, g in ((220, 0.12), (329.63, 0.09), (554.37, 0.06)):
        add(buf, 61.9, tone(f, DUR - 61.9, attack=0.6, decay=3.0), gain=g)
    add(buf, 65.8, plip(1800, 700, 0.09), gain=0.35)
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
