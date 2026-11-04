"""深色画风：黑底、发光的线、居中的大字。

渲染和声音沿用 notebook.py；这里只换底色、配色和文字的摆法。
build() 里先调 use()，让 mix 的半透明和黑底插值（多进程渲染时每个进程都会跑 build）。
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import notebook as nb
from notebook import SS, P, ease, fade, font, mix, polyline, wavy

BG = (15, 15, 18)
INK = (238, 232, 220)
DIM = (126, 122, 116)
RED = (232, 96, 82)
BLUE = (96, 120, 156)

MARGIN_X = 90


def use():
    nb.set_base(BG)


def make_bg(header_left, header_right=None):
    """黑底，加一点暗角和颗粒，免得压缩后出色带。"""
    rng = np.random.default_rng(2)
    W, H = nb.W, nb.H
    w, h = W * SS, H * SS
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w * 0.75)) ** 2 + ((yy - h * 0.45) / (h * 0.75)) ** 2)
    vign = np.clip(1.0 + 0.35 * (0.6 - r), 0.75, 1.15)
    grain = rng.normal(0, 1.6, (h, w)).astype(np.float32)
    base = np.array(BG, np.float32)[None, None, :] * vign[..., None] + grain[..., None]
    img = Image.fromarray(np.uint8(np.clip(base, 0, 255)))
    d = ImageDraw.Draw(img)
    y = 250 if H > W else 80                     # 竖屏避开顶部的状态栏
    d.text(P(MARGIN_X, y), header_left, font=font('sans', 28), fill=DIM, anchor='ls')
    if header_right:
        d.text(P(W - MARGIN_X, y), header_right, font=font('sans', 28), fill=DIM, anchor='rs')
    return img


def glow(d, pts, color, width, alpha=1.0, frac=1.0):
    """发光的线：外面两圈宽而淡，里面一笔实线。"""
    polyline(d, pts, color, width * 4, alpha * 0.10, frac)
    polyline(d, pts, color, width * 2.2, alpha * 0.22, frac)
    polyline(d, pts, color, width, alpha, frac)


def glow_dot(d, cx, cy, r, color, alpha=1.0):
    if alpha <= 0 or r <= 0:
        return
    for k, a in ((2.4, 0.10), (1.6, 0.22), (1.0, 1.0)):
        rr = r * k
        d.ellipse([P(cx - rr, cy - rr), P(cx + rr, cy + rr)], fill=mix(color, alpha * a))


class Caption:
    """一行居中的大字：整行淡入、往上浮一点；underline 里的词下面画红色波浪线。"""

    def __init__(self, text, t, y, t_out, kind='bold', size=72, color=INK, x=None, align='center',
                 underline=(), fin=0.3):
        x = nb.W / 2 if x is None else x
        self.text, self.t, self.y, self.t_out = text, t, y, t_out
        self.kind, self.size, self.color, self.fin = kind, size, color, fin
        self.f = font(kind, size)
        self.width = self.f.getlength(text) / SS
        self.x0 = x - self.width / 2 if align == 'center' else (x - self.width if align == 'right' else x)
        self.underline = (underline,) if isinstance(underline, str) else tuple(underline)

    def char_times(self):
        return [self.t] if self.t >= 0 else []

    def draw(self, d, t):
        a = fade(t, self.t, self.t_out, fin=self.fin if self.t >= 0 else 0, fout=0.35)
        if a <= 0:
            return
        rise = 14 * (1 - ease((t - self.t) / 0.45)) if self.t >= 0 else 0
        y = self.y + rise
        d.text(P(self.x0, y), self.text, font=self.f, fill=mix(self.color, a), anchor='ls')
        for k, word in enumerate(self.underline):
            i = self.text.find(word)
            if i < 0:
                continue
            frac = ease((t - (self.t + 0.5 + 0.3 * k)) / 0.45) if self.t >= 0 else 1.0
            if frac > 0:
                xa = self.x0 + self.f.getlength(self.text[:i]) / SS + 2
                xb = self.x0 + self.f.getlength(self.text[:i + len(word)]) / SS - 2
                pts = wavy(xa, xb, y + self.size * 0.22, amp=3.5, period=24, seed=sum(map(ord, word)))
                polyline(d, pts, RED, 4, a, frac)
