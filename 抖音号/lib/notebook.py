"""人间旁听生的笔记本画风工具。

所有坐标都按 1080x1920 的基础单位来写，绘制时放大 SS 倍再缩回，用超采样做抗锯齿。
一个场景是一组元素，每个元素有 draw(d, t)；t 是全片时间（秒）。
"""
import math
import os
import subprocess
import wave
from multiprocessing import Pool

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SS = 1080, 1920, 30, 2
SR = 44100


def set_size(w, h):
    """换画幅（比如横屏 1920x1080）。渲染脚本在模块顶层调用，主进程和渲染子进程都会执行到。"""
    global W, H
    W, H = w, h

PAPER = (243, 238, 228)
INK = (35, 50, 74)
RED = (192, 80, 77)
GRAY = (138, 133, 119)
SOIL = (122, 104, 82)
WATER = (205, 218, 228)
RULE = (222, 215, 201)
MARGIN = (228, 176, 160)
RAIN = (150, 156, 168)

RULE_Y0, RULE_STEP = 380, 100
LEFT, RIGHT = 150, 950

SONGTI = '/System/Library/Fonts/Supplemental/Songti.ttc'
HIRA = '/System/Library/Fonts/Hiragino Sans GB.ttc'
_FACES = {
    'black': (SONGTI, 0), 'bold': (SONGTI, 1), 'regular': (SONGTI, 6),
    'sans': (HIRA, 0), 'sansb': (HIRA, 2),
}
_font_cache = {}


def font(kind, size):
    key = (kind, size)
    if key not in _font_cache:
        path, idx = _FACES[kind]
        _font_cache[key] = ImageFont.truetype(path, int(size * SS), index=idx)
    return _font_cache[key]


def P(x, y):
    return (x * SS, y * SS)


_BASE = PAPER


def set_base(color):
    """换底色（深色画风用），mix 的半透明都和它插值。"""
    global _BASE
    _BASE = color


def mix(color, a, base=None):
    """底色上画半透明颜色：直接和底色插值，省掉逐层合成。"""
    a = max(0.0, min(1.0, a))
    return tuple(int(b + (c - b) * a) for b, c in zip(base or _BASE, color))


def rule_y(i):
    return RULE_Y0 + i * RULE_STEP


def clamp01(x):
    return max(0.0, min(1.0, x))


def ease(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def fade(t, t_in, t_out, fin=0.3, fout=0.4):
    if t < t_in or t > t_out:
        return 0.0
    a = 1.0
    if fin:
        a = min(a, (t - t_in) / fin)
    if fout:
        a = min(a, (t_out - t) / fout)
    return clamp01(a)


def keyframes(points):
    """[(t, v), ...] 线性插值成函数。"""
    ts = [p[0] for p in points]
    vs = [p[1] for p in points]
    return lambda t: float(np.interp(t, ts, vs))


# ---------- 线条 ----------

def partial(pts, frac):
    """按长度截取折线的前 frac 部分，用来做「一笔画出来」的动画。"""
    if frac <= 0 or len(pts) < 2:
        return []
    if frac >= 1:
        return list(pts)
    lens = [math.dist(a, b) for a, b in zip(pts[:-1], pts[1:])]
    target = sum(lens) * frac
    out, acc = [pts[0]], 0.0
    for (a, b), L in zip(zip(pts[:-1], pts[1:]), lens):
        if acc + L >= target:
            r = (target - acc) / L if L else 0
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
            break
        out.append(b)
        acc += L
    return out


def polyline(d, pts, color, width, alpha=1.0, frac=1.0):
    pts = partial(pts, frac)
    if len(pts) >= 2 and alpha > 0:
        d.line([P(x, y) for x, y in pts], fill=mix(color, alpha), width=max(1, int(width * SS)), joint='curve')


def circle(d, cx, cy, r, outline=None, fill=None, width=2.5, alpha=1.0):
    if alpha <= 0 or r <= 0:
        return
    d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)],
              outline=mix(outline, alpha) if outline else None,
              fill=mix(fill, alpha) if fill else None,
              width=max(1, int(width * SS)))


def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=48, a0=0.0, a1=2 * math.pi):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for a in np.linspace(a0, a1, n + 1):
        ex, ey = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + ex * c - ey * s, cy + ex * s + ey * c))
    return out


def wavy(xa, xb, y, amp=3.0, period=22.0, seed=0):
    rng = np.random.default_rng(seed)
    n = max(4, int((xb - xa) / 6))
    xs = np.linspace(xa, xb, n)
    jitter = rng.normal(0, 0.6, n)
    return [(x, y + amp * math.sin((x - xa) / period * 2 * math.pi) + j) for x, j in zip(xs, jitter)]


def label(d, t, t_in, t_out, text, pos, color=RED, kind='sans', size=30, anchor='ls',
          leader=None):
    """批注：一行小字，可带一条引线 leader=(起点, 终点)。终点可以是随时间变化的函数。"""
    a = fade(t, t_in, t_out, 0.3, 0.4)
    if a <= 0:
        return
    d.text(P(*pos), text, font=font(kind, size), fill=mix(color, a), anchor=anchor)
    if leader:
        p0, p1 = leader
        if callable(p1):
            p1 = p1(t)
        if p1:
            polyline(d, [p0, p1], color, 2, a, frac=ease((t - t_in) / 0.4))


# ---------- 元素 ----------

class Text:
    """写在横格线上的一行字，逐字出现，像手写。"""

    def __init__(self, text, t, line, t_out, kind='bold', size=64, color=INK, rate=14.0,
                 x=LEFT, align='left', underline=(), dy=-16):
        self.text, self.t, self.t_out = text, t, t_out
        self.kind, self.size, self.color, self.rate = kind, size, color, rate
        self.f = font(kind, size)
        self.offsets = [self.f.getlength(text[:i]) / SS for i in range(len(text) + 1)]
        self.width = self.offsets[-1]
        self.x0 = x if align == 'left' else (x - self.width if align == 'right' else x - self.width / 2)
        self.baseline = rule_y(line) + dy
        self.underline = (underline,) if isinstance(underline, str) else tuple(underline)
        self.done_at = t + len(text) / rate

    def char_times(self):
        return [self.t + i / self.rate for i, ch in enumerate(self.text) if not ch.isspace()]

    def draw(self, d, t):
        a_el = fade(t, self.t, self.t_out, fin=0, fout=0.4)
        if a_el <= 0:
            return
        n = (t - self.t) * self.rate
        for i, ch in enumerate(self.text):
            a = clamp01(n - i) * a_el
            if a <= 0:
                break
            d.text(P(self.x0 + self.offsets[i], self.baseline), ch, font=self.f,
                   fill=mix(self.color, a), anchor='ls')
        for k, word in enumerate(self.underline):
            i = self.text.find(word)
            if i < 0:
                continue
            u0 = self.done_at + 0.15 + 0.35 * k
            frac = ease((t - u0) / 0.45)
            if frac > 0:
                xa = self.x0 + self.offsets[i] + 2
                xb = self.x0 + self.offsets[i + len(word)] - 2
                y = self.baseline + self.size * 0.2
                # 不用 hash()：字符串 hash 每个进程不同，多进程渲染时下划线会抖
                polyline(d, wavy(xa, xb, y, seed=sum(map(ord, word))), RED, 3.5, a_el, frac)


class Fn:
    """把一个 fn(d, t) 包成元素。"""

    def __init__(self, fn):
        self.fn = fn

    def draw(self, d, t):
        self.fn(d, t)


class Rain:
    """落在纸面上的细雨丝，intensity(t) 控制同时可见的比例。"""

    def __init__(self, intensity, n=260, seed=7):
        rng = np.random.default_rng(seed)
        self.intensity = intensity
        self.x0 = rng.uniform(-300, W + 100, n)
        self.y0 = rng.uniform(0, H + 300, n)
        self.v = rng.uniform(1500, 2400, n)
        self.len = rng.uniform(36, 80, n)
        self.a = rng.uniform(0.18, 0.4, n)
        self.th = rng.uniform(0, 1, n)

    def draw(self, d, t):
        k = self.intensity(t)
        if k <= 0:
            return
        span = H + 300
        for i in np.nonzero(self.th < k)[0]:
            y = (self.y0[i] + self.v[i] * t) % span - 150
            x = self.x0[i] + 0.14 * (y + 150)
            L = self.len[i]
            d.line([P(x, y), P(x + 0.14 * L, y + L)], fill=mix(RAIN, self.a[i]), width=int(1.6 * SS))


def make_paper(header_left, header_right=None):
    rng = np.random.default_rng(1)
    w, h = W * SS, H * SS
    small = rng.normal(0, 1, (H // 48, W // 48)).astype(np.float32)
    blot = Image.fromarray(np.uint8(np.clip(small * 30 + 128, 0, 255))).resize((w, h), Image.BICUBIC)
    blot = blot.filter(ImageFilter.GaussianBlur(24 * SS))
    blot = (np.asarray(blot, np.float32) - 128) / 30 * 1.6
    grain = rng.normal(0, 2.0, (h, w)).astype(np.float32)
    base = np.array(PAPER, np.float32)[None, None, :] + (blot + grain)[..., None]
    img = Image.fromarray(np.uint8(np.clip(base, 0, 255)))
    d = ImageDraw.Draw(img)
    i = 0
    while rule_y(i) < H - 120:
        d.line([P(0, rule_y(i)), P(W, rule_y(i))], fill=RULE, width=SS)
        i += 1
    d.line([P(118, 0), P(118, H)], fill=MARGIN, width=int(1.5 * SS))
    d.text(P(LEFT, 268), header_left, font=font('sans', 28), fill=GRAY, anchor='ls')
    if header_right:
        d.text(P(RIGHT - 30, 268), header_right, font=font('sans', 28), fill=GRAY, anchor='rs')
    return img


# ---------- 渲染 ----------

_G = {}


def _init(build):
    _G['scene'] = build()


def _frame(i):
    sc = _G['scene']
    t = i / FPS
    img = sc['paper'].copy()
    d = ImageDraw.Draw(img)
    for el in sc['elements']:
        el.draw(d, t)
    return img.resize((W, H), Image.LANCZOS).tobytes()


def render_stills(build, times, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    _init(build)
    paths = []
    for t in times:
        img = Image.frombytes('RGB', (W, H), _frame(int(round(t * FPS))))
        path = os.path.join(out_dir, f'still_{t:05.1f}.png')
        img.save(path)
        paths.append(path)
    return paths


def render_video(build, duration, out_path, workers=8):
    n = int(round(duration * FPS))
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers, initializer=_init, initargs=(build,)) as pool:
        for k, buf in enumerate(pool.imap(_frame, range(n), chunksize=4)):
            p.stdin.write(buf)
            if k % 300 == 0:
                print(f'frame {k}/{n}', flush=True)
    p.stdin.close()
    p.wait()


def mux(video, audio, out_path):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error',
                    '-i', video, '-i', audio, '-c:v', 'copy',
                    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-movflags', '+faststart', out_path], check=True)


# ---------- 声音 ----------

def shaped_noise(n, rng, lo, hi, tilt=0.0):
    """白噪声在频域里整形：lo/hi 是柔和的高通/低通拐点，tilt<0 往低频倾斜。"""
    spec = np.fft.rfft(rng.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1.0
    g = 1 / (1 + (lo / f) ** 4) / (1 + (f / hi) ** 4) * (f / 1000.0) ** (tilt / 2)
    out = np.fft.irfft(spec * g, n)
    return out / (np.max(np.abs(out)) + 1e-9)


def envelope(fn, n):
    """把 fn(t) 按 100Hz 采样再插值到音频采样率。"""
    ct = np.arange(0, n / SR + 0.02, 0.01)
    cv = np.array([fn(t) for t in ct])
    return np.interp(np.arange(n) / SR, ct, cv)


def add(buf, t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[0] or i < 0:
        return
    sig = sig[: buf.shape[0] - i]
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414


def tone(freq, dur, attack=0.02, decay=None, harmonics=((1, 1.0), (2, 0.25), (3, 0.08))):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = sum(a * np.sin(2 * np.pi * freq * k * t) for k, a in harmonics)
    env = np.minimum(1, t / attack) * (np.exp(-t / decay) if decay else 1)
    env *= np.minimum(1, (dur - t) / 0.05)
    return sig * env


def plip(f0=1400, f1=420, dur=0.09):
    t = np.arange(int(dur * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.018)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.025)


def write_wav(buf, path, peak_db=-3.0):
    buf = buf / (np.max(np.abs(buf)) + 1e-9) * (10 ** (peak_db / 20))
    data = (np.clip(buf, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
