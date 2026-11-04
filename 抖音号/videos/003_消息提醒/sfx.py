"""《消息提醒》（003 横屏，61.2 秒 = 1836 帧）的音效轨。

照 002 的 sfx.py：每个声音用 numpy 合成（实物怎么发声就怎么合成：敲击 = 几个按指数衰减的振动模态 + 一下接触噪声；
嗖 = 扫频的带通噪声；手机震 = 马达 + 机壳磕桌面），按时间表的秒数放上去，整条量响度再统一调。不用曲库、采样、第三方账号。

  /Users/decheng.huang/Documents/dy/.venv/bin/python /Users/decheng.huang/Documents/dy/videos/003_消息提醒/sfx.py

读：studio/src/videos/003/timeline.ts（BEATS 每拍起止、EV 每个动作的秒数；Gray003.tsx 也只读它；这里只读，不改）
写：studio/public/003/sfx.wav（48 kHz、16 bit、双声道；关键音效左右一样，放正中；整条 −19 LUFS，真峰值 ≤ −1.5 dBTP）
    studio/public/003/sfx_events.json（每个音效：t 起音秒、frame 帧、name 名字、beat 拍、key、label 说明）
    videos/003_消息提醒/out/音效/落点核对.json（从磁盘读回 sfx.wav，逐个找起音，和画面事件对时间差；music.py 拿它写自查）

和 002 不同：
  - 没有环境底噪（这条没有“世界冷暖”那层），音效之间留给配乐；
  - 38.6–39.6 定格：音效和混响尾巴全部抽空（GATE），39.7 快门从静里出来；
  - 时间全从 timeline.ts 的 EV 取（秒）。分镜“遮字幕测试”那 6 条（小钟 14:40→15:40、红心飞进盒子、翻书）画面改了 EV 以后重跑就跟上。

有音高的声音都在配乐的调里：前半段 D 小调（D F A、B♭），22.6 起 D 大调（D F♯ A、G、Bm）。
"""
import json
import math
import os
import re
import subprocess
import tempfile
import wave
import zlib

import imageio_ffmpeg
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
TL_PATH = os.path.join(ROOT, 'studio', 'src', 'videos', '003', 'timeline.ts')
PUB = os.path.join(ROOT, 'studio', 'public', '003')
OUT_WAV = os.path.join(PUB, 'sfx.wav')
OUT_EVENTS = os.path.join(PUB, 'sfx_events.json')
OUT_DIR = os.path.join(HERE, 'out', '音效')
OUT_CHECK = os.path.join(OUT_DIR, '落点核对.json')
FF = imageio_ffmpeg.get_ffmpeg_exe()


def load_tl():
    """读 timeline.ts：FPS、DUR、BEATS（id、t0、t1）、EV（JS 对象，去掉注释、给键加引号后按 JSON 读）。"""
    s = open(TL_PATH, encoding='utf-8').read()
    fps = float(re.search(r'export const FPS = ([\d.]+)', s).group(1))
    dur = float(re.search(r'export const DUR = ([\d.]+)', s).group(1))
    beats = [dict(id=a, t0=float(b), t1=float(c)) for a, b, c in re.findall(r"\{id: '(\w+)', t0: ([\d.]+), t1: ([\d.]+)", s)]
    body = s[s.index('export const EV = {') + len('export const EV = '):]
    body = body[:body.index('\n};') + 2]
    body = re.sub(r'//[^\n]*', '', body)
    body = re.sub(r'(\w+)\s*:', r'"\1":', body)
    body = re.sub(r',(\s*[}\]])', r'\1', body)
    read = json.loads(re.search(r'export const READ = (\[\[.*?\]\]);', s).group(1))
    hn = re.search(r'const HEART_N = (\d+);', open(os.path.join(os.path.dirname(TL_PATH), 'Gray003.tsx'), encoding='utf-8').read())
    hf = re.search(r'const HEART_FLY = ([\d.]+);', open(os.path.join(os.path.dirname(TL_PATH), 'Gray003.tsx'), encoding='utf-8').read())
    return dict(fps=fps, dur=dur, beats=beats, ev=json.loads(body), read=read,
                heart_n=int(hn.group(1)) if hn else 12, heart_fly=float(hf.group(1)) if hf else 0.32)


TLD = load_tl()
SR = 48000
FPS = int(TLD['fps'])
NF = int(round(TLD['dur'] * FPS))      # 1836 帧
SPF = SR // FPS                         # 每帧 1600 个采样
N = NF * SPF                            # 2 937 600 个采样 = 61.2 秒
BEATS = TLD['beats']
B = {b['id']: b for b in BEATS}
EV = TLD['ev']
READ = TLD['read']                      # 三栏读数 [被打断, 晚看到]
TARGET = -19.0                         # sfx.wav 单独的整条响度（mix.wav 由 music.py 另调到 −15）
TP_CEIL = -1.5
SEED = 3003
FREEZE = EV['freeze']                   # 38.6–39.6 定格，声音抽空

# 11/2 评委改的几处画面（timeline.ts 样片 v2 已加 poke/retract、burst、shatter、titleDrop；没有时用括号里的默认值）
SHAKE = EV.get('shakeFrames', 8) / FPS                  # 每次手机震，画面抖 8 帧（Gray003 的 shake()），震动声也是 8 帧长
RECOIL = EV['retract'] if 'poke' in EV else EV.get('recoil', [6.9, 6.9 + 10 / FPS])   # 手往前探 3 帧后往后撤 10 帧并握拳
BANNER_N = 27


def _banner_times():
    """27 条横幅喷出的时刻：EV.banners 有就用；没有就在 EV.burst（8.2–9.15）里排开，越来越密：
    相邻两条的间隔每条乘同一个比，最后一个间隔是第一个的 0.3 倍（第一个约 62 毫秒，最后一个约 19 毫秒）。"""
    if 'banners' in EV:
        return [float(x) for x in EV['banners']]
    b0, b1 = EV.get('burst', [EV['count'][0], EV['count'][1] - 0.25])
    r = 0.3 ** (1 / (BANNER_N - 2))
    gaps = [r ** k for k in range(BANNER_N - 1)]
    sc = (b1 - b0) / sum(gaps)
    out = [b0]
    for g in gaps:
        out.append(out[-1] + g * sc)
    return out


def _count_ticks():
    """计数滴答（4→120，8.2–9.4）：间隔 80 毫秒起、每下乘 0.95、最短 25 毫秒。"""
    c0, c1 = EV['count']
    out, t, d = [], c0, 0.08
    while t < c1 - 0.005:
        out.append(t)
        t += d
        d = max(0.025, d * 0.95)
    return out


BANNERS = _banner_times()
TICKS = _count_ticks()
_sh = EV.get('shatter', EV['countFlash'][0])
SHATTER = float(_sh[0] if isinstance(_sh, list) else _sh)   # 9.4 计数停在 120，3 帧内横幅全部震散
TITLE_DROP = (EV['titleDrop'][:2] if 'titleDrop' in EV else [EV['titleOut'][0], EV['bigText'][0]])   # 10.4 起 6 帧落下，10.6 落地（再 2 帧回弹）

# 音名 → Hz（只用到这些）
HZ = {'D5': 587.33, 'E5': 659.26, 'F5': 698.46, 'F#5': 739.99, 'A5': 880.0, 'Bb5': 932.33, 'D6': 1174.66, 'E6': 1318.51,
      'F6': 1396.91, 'F#6': 1479.98, 'A6': 1760.0, 'D7': 2349.32, 'F#7': 2959.96, 'A7': 3520.0}


def beat_at(t):
    for b in BEATS:
        if b['t0'] <= t < b['t1']:
            return b['id']
    return BEATS[-1]['id']


def ease(x):
    """和 Gray003.tsx 的 ease 一样（三次缓入缓出）。"""
    x = np.clip(x, 0, 1)
    return np.where(x < 0.5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)


def ease_inv(v):
    """ease 的反函数：画面走到 v（0–1）那一刻的进度。"""
    xs = np.linspace(0, 1, 4001)
    return float(np.interp(v, ease(xs), xs))


# ======================================================================
# 声音的零件（和 002 sfx.py 同一套）
# ======================================================================
def ts(n):
    return np.arange(n) / SR


def shape(x, lo=None, hi=None, order=2, tilt=0.0, peaks=()):
    """频域里整形（零相位）：lo/hi 是柔和的高通/低通拐点，tilt<0 往低频倾斜，peaks=(中心, Q, dB) 加共振峰。"""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1.0
    g = np.ones_like(f)
    if lo:
        g /= np.sqrt(1 + (lo / f) ** (2 * order))
    if hi:
        g /= np.sqrt(1 + (f / hi) ** (2 * order))
    if tilt:
        g *= (f / 1000.0) ** (tilt / 2)
    for fc, q, db in peaks:
        g *= 1 + (10 ** (db / 20) - 1) * np.exp(-0.5 * ((f - fc) / (fc / q)) ** 2)
    g[0] = 0.0
    return np.fft.irfft(X * g, n)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))) + 1e-12)


def noise(n, rng, lo=None, hi=None, order=2, tilt=0.0, peaks=()):
    y = shape(rng.standard_normal(max(n, 64)), lo, hi, order, tilt, peaks)[:n]
    return y / rms(y)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-12)


def fades(x, fi=0.0004, fo=0.008):
    a, b = int(fi * SR), int(fo * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b and b < len(x):
        x[-b:] *= np.linspace(1, 0, b)
    return x


def jit(rng, cents):
    return 2 ** (rng.normal(0, cents) / 1200)


def var(rng, p):
    return 1 + rng.uniform(-p, p)


def modal(n, parts, rng, att=0.0006):
    """几个按指数衰减的振动模态（频率, 幅度, 衰减时间）。"""
    t = ts(n)
    y = np.zeros(n)
    for f, a, tau in parts:
        if f <= 20 or f >= 0.45 * SR or a == 0:
            continue
        y += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / tau)
    return y * (1 - np.exp(-t / att))


def contact(n, rng, lo, hi, tau, att=0.00015):
    """碰上去那一下的接触噪声。"""
    m = min(n, int(max(0.06, 12 * tau) * SR))
    t = ts(m)
    y = np.zeros(n)
    y[:m] = noise(m, rng, lo, hi) * np.exp(-t / tau) * (1 - np.exp(-t / att))
    return y


def tv_noise(n, rng, fc, bw, nfft=1024, hop=128):
    """时变带通噪声：fc（Hz）、bw（倍频程）都可以逐样本变。"""
    fc = np.broadcast_to(np.asarray(fc, float), (n,))
    bw = np.broadcast_to(np.asarray(bw, float), (n,))
    pad = nfft
    x = rng.standard_normal(n + 2 * pad)
    win = np.hanning(nfft + 1)[:-1]
    starts = np.arange(0, n + pad, hop)
    fr = np.lib.stride_tricks.sliding_window_view(x, nfft)[starts] * win
    S = np.fft.rfft(fr, axis=1)
    fq = np.fft.rfftfreq(nfft, 1 / SR)
    fq[0] = 1.0
    ci = np.clip(starts + nfft // 2 - pad, 0, n - 1)
    sig = np.maximum(bw[ci], 0.04) / 2.355
    G = np.exp(-0.5 * (np.log2(fq[None, :] / fc[ci][:, None]) / sig[:, None]) ** 2)
    Y = np.fft.irfft(S * G, nfft, axis=1) * win
    out = np.zeros(len(x) + nfft)
    for i, s in enumerate(starts):
        out[s:s + nfft] += Y[i]
    y = out[pad:pad + n]
    return y / rms(y)


def _mixin(y, s, i=0, g=1.0):
    m = min(len(s), len(y) - i)
    if m > 0:
        y[i:i + m] += g * s[:m]
    return y


# ======================================================================
# 各种声音（都返回单声道、峰值 1）
# ======================================================================
def g_vibrate(rng, pulses, motor=172.0):
    """手机震：马达 172 Hz 上下（每一下起转时低一点，50 毫秒转稳），马达音饱和出 3、5、7 次谐波；
    机壳每转一圈磕一下桌面（1–4.8 kHz 的碎响，跟马达同相位）——手机外放放不出 172 Hz，靠这层碎响听见“嗡嗡”。
    pulses：[(起, 长), ...]（秒，从声音开头算）。"""
    end = max(a + d for a, d in pulses) + 0.06
    n = int(end * SR)
    t = ts(n)
    env = np.zeros(n)
    since = np.full(n, 10.0)
    for a, d in sorted(pulses):
        env = np.maximum(env, np.clip((t - a) / 0.018, 0, 1) * np.clip((a + d - t) / 0.035, 0, 1))
        m = t >= a
        since[m] = t[m] - a
    f = motor * jit(rng, 25) * (0.82 + 0.18 * np.clip(since / 0.05, 0, 1))
    f = f * (1 + 0.008 * norm(shape(rng.standard_normal(n), 2, 15)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.tanh(2.2 * np.sin(ph)) / np.tanh(2.2)
    knock = np.maximum(0.0, np.sin(ph + 0.6)) ** 12
    rattle = noise(n, rng, 1000, 4800, tilt=-0.3) * knock
    y = 0.6 * norm(shape(body, 130, 2200)) + 0.75 * norm(rattle)
    y = np.tanh(2.5 * norm(y)) / np.tanh(2.5)                   # 碎响很尖，压一下峰值（响度不变，限幅少压）
    return norm(fades(y * env, 0.001, 0.01))


def _tone(rng, f0, n, timbre, tau):
    """提示音里的一个音。glass：小玻璃铃（谐和的 2、3 倍 + 一点 4.16 倍的金属味）；square：电子味的方波（奇次谐波，6 kHz 以上不要）；
    wood：木琴（1、3.93 倍，软）。"""
    t = ts(n)
    if timbre == 'glass':
        parts = [(f0, 1.0, tau), (f0 + rng.uniform(0.8, 2.0), 0.25, tau * 0.9), (2.0 * f0, 0.22, tau * 0.35),
                 (3.0 * f0, 0.06, tau * 0.2), (4.16 * f0, 0.05, 0.03)]
        return norm(modal(n, parts, rng, att=0.0008)) + 0.08 * norm(contact(n, rng, 3000, 10000, 0.001))
    if timbre == 'square':
        ph = 2 * np.pi * f0 * t + rng.uniform(0, 6.28)
        y = (np.sin(ph) + 0.3 * np.sin(3 * ph) + 0.12 * np.sin(5 * ph)) * np.exp(-t / tau) * (1 - np.exp(-t / 0.002))
        return norm(shape(y, None, 6000))
    parts = [(f0, 1.0, tau), (f0 * 1.0015, 0.2, tau * 0.9), (3.93 * f0, 0.14, 0.03)]
    return norm(modal(n, parts, rng, att=0.0015)) + 0.05 * norm(contact(n, rng, 1500, 6000, 0.002))


def g_chime(rng, notes, gap=0.1, timbre='glass', tau=0.3, vels=None):
    """原创的通知提示音：两三个音的小铃，按 gap 秒一个接一个。不是任何 App 的提示音，音都在配乐的调里。"""
    vels = vels or [1.0] * len(notes)
    n = int((gap * (len(notes) - 1) + 6 * tau + 0.1) * SR)
    y = np.zeros(n)
    for k, (f0, v) in enumerate(zip(notes, vels)):
        i = int(k * gap * SR)
        _mixin(y, v * _tone(rng, f0 * jit(rng, 3), n - i, timbre, tau), i)
    return norm(fades(y, 0.0003, 0.02))


def g_tick(rng, f0=2300.0, fine=True):
    """计数的“嗒”：小木块，模态 1、1.52、2.31 倍，十几毫秒就没了。"""
    n = int(0.07 * SR)
    f0 *= jit(rng, 30)
    k = 0.6 if fine else 1.0
    y = norm(modal(n, [(f0, 1, 0.010 * k), (1.52 * f0, 0.45, 0.007 * k), (2.31 * f0, 0.25, 0.004 * k)], rng, att=0.0003))
    y = y + 0.55 * norm(contact(n, rng, 1500, 8000, 0.0012))
    if not fine:
        y = y + 0.2 * norm(modal(n, [(420 * jit(rng, 50), 1, 0.006)], rng))
    return norm(fades(y))


def g_ding(rng, f0=1568.0, bright=1.0, decay=1.0):
    """“叮”：小金属条（钟琴）的几个模态 2.756、5.404、8.933 倍，主音旁边带一个差 1–2 Hz 的伴音。"""
    f0 *= jit(rng, 6)
    dk = decay * var(rng, 0.08)
    n = int(min(1.4, 0.9 * dk + 0.3) * SR)
    parts = [(f0, 1.0, 0.42 * dk), (f0 + rng.uniform(0.7, 2.2), 0.2, 0.38 * dk), (2.756 * f0, 0.34 * bright, 0.10 * dk),
             (5.404 * f0, 0.14 * bright, 0.032 * dk), (8.933 * f0, 0.05 * bright, 0.011 * dk)]
    y = norm(modal(n, parts, rng)) + 0.22 * bright * norm(contact(n, rng, 2500, 10000, 0.0015))
    return norm(fades(y))


def g_warm(rng, f0=880.0):
    """暖的一声：软槌敲铃，泛音近于谐和，再叠一层慢起的同音，听着发暖。"""
    n = int(1.8 * SR)
    t = ts(n)
    f0 *= jit(rng, 4)
    parts = [(f0, 1.0, 0.65), (f0 * 1.0015, 0.25, 0.6), (2.0 * f0 * 1.003, 0.3, 0.26), (3.01 * f0, 0.14, 0.12),
             (4.18 * f0, 0.06, 0.05), (f0 / 2, 0.12, 0.5)]
    y = norm(modal(n, parts, rng, att=0.001))
    bloom = modal(n, [(f0, 1, 0.5), (2 * f0, 0.4, 0.3), (3 * f0, 0.15, 0.2)], rng) * (1 - np.exp(-t / 0.06))
    y = y + 0.35 * norm(bloom) + 0.14 * norm(contact(n, rng, 500, 3500, 0.003))
    return norm(fades(y))


def g_glint(rng, f0=4200.0, tau=0.022):
    """一颗很小的玻璃亮声。"""
    n = int(max(0.09, 5 * tau) * SR)
    f0 *= jit(rng, 10)
    y = modal(n, [(f0, 1, tau), (2.76 * f0, 0.25, tau * 0.3), (1.0021 * f0, 0.3, tau)], rng, att=0.0003)
    return norm(fades(y))


def g_whoosh(rng, dur=0.24, f0=3200.0, f1=900.0, bw=1.3, tp=0.12, tail=0.05, floor=0.36, flutter=0.12):
    """嗖：带通噪声从 f0 扫到 f1。一起音就到峰值的 floor，tp 秒到峰值，之后按 tail 衰减；带一点气流的抖动。"""
    dur *= var(rng, 0.06)
    n = int(dur * SR)
    t = ts(n)
    fc = f0 * jit(rng, 40) * (f1 / f0) ** np.clip(t / dur, 0, 1)
    y = tv_noise(n, rng, fc, bw)
    e = np.where(t < tp, floor + (1 - floor) * (t / tp) ** 2, np.exp(-(t - tp) / tail))
    e *= np.clip(t / 0.003, 0, 1)
    am = 1 + flutter * norm(shape(rng.standard_normal(n), 8, 40))
    return norm(fades(y * e * am, 0, 0.01))


def g_swell(rng, span, f0=700.0, f1=3800.0, tail=0.05, bw0=1.8, bw1=0.9, floor=0.08):
    """往里收的“嗖——”：带通噪声从 f0 往 f1 走、通带收窄，越来越响，正好在 span 秒到顶，之后 tail 秒收掉（转场、推镜头用）。
    floor：一起头就有多响（峰值的几成）；推镜头用 0.35，动作一开始就听得见。"""
    n = int((span + 6 * tail) * SR)
    t = ts(n)
    u = np.clip(t / span, 0, 1)
    y = tv_noise(n, rng, f0 * (f1 / f0) ** u, bw0 + (bw1 - bw0) * u)
    e = np.where(t < span, floor + (1 - floor) * u ** 2.2, np.exp(-(t - span) / tail)) * np.clip(t / 0.01, 0, 1)
    am = 1 + 0.1 * norm(shape(rng.standard_normal(n), 8, 40))
    return norm(fades(y * e * am, 0, 0.01))


def g_knock(rng, f0=1450.0, tau=0.055):
    """指节敲木头：f0、1.58、2.31 倍，再加一个 0.55 倍的“木头身子”和一下 1–4.5 kHz 的接触噪声。"""
    n = int(0.3 * SR)
    f0 *= jit(rng, 20)
    y = norm(modal(n, [(f0, 1, tau), (1.58 * f0, 0.55, 0.6 * tau), (2.31 * f0, 0.3, 0.35 * tau), (0.55 * f0, 0.45, 0.75 * tau)],
                   rng, att=0.00025))
    y = y + 0.7 * norm(contact(n, rng, 1000, 4500, 0.003))
    return norm(fades(y))


def g_click(rng, f0=2000.0, tau=0.045, n_s=0.12):
    """清脆的一下“咔”：硬东西碰木头。f0、1.47 倍、0.62 倍三个模态 + 1.5–7 kHz 的接触噪声。"""
    n = int(n_s * SR)
    f0 *= jit(rng, 25)
    y = norm(modal(n, [(f0, 1, tau), (1.47 * f0, 0.5, 0.6 * tau), (0.62 * f0, 0.55, 0.8 * tau)], rng, att=0.0002))
    y = y + 0.6 * norm(contact(n, rng, 1500, 7000, 0.0015))
    return norm(fades(y, 0.0002, 0.005))


def g_clock(rng, tock=False):
    """小钟的“嘀”“嗒”：擒纵机构的金属小撞击。嘀高（3.6 kHz 一带）、嗒低一点（2.5 kHz 一带），十几毫秒，带一点壳子的余响。"""
    n = int(0.12 * SR)
    f0 = (2500.0 if tock else 3600.0) * jit(rng, 15)
    y = norm(modal(n, [(f0, 1, 0.012), (1.53 * f0, 0.5, 0.007), (0.71 * f0, 0.4, 0.02)], rng, att=0.0002))
    y = y + 0.5 * norm(contact(n, rng, 2000, 9000, 0.0008))
    return norm(fades(y, 0.0002, 0.005))


def g_bubble(rng, f0=1000.0, dur=0.06):
    """“啵”：小气泡，一个往上滑的短音。"""
    n = int(dur * SR)
    t = ts(n)
    f = f0 * jit(rng, 40) * (1 + 0.6 * t / dur)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (dur * 0.22)) * (1 - np.exp(-t / 0.0015))
    y = norm(y) + 0.15 * norm(contact(n, rng, 1500, 6000, 0.001))
    return norm(fades(y))


def g_pop(rng, f0):
    """按钮弹出来的“啵”：音高 25 毫秒内从 0.72 f0 滑到 f0（像软木塞拔出），60 毫秒衰减，带一点 2 倍泛音和接触声。音高听得出。"""
    n = int(0.3 * SR)
    t = ts(n)
    f = f0 * jit(rng, 4) * (0.72 + 0.28 * (1 - np.exp(-t / 0.009)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) * np.exp(-t / 0.075) + 0.3 * np.sin(2 * ph + 0.7) * np.exp(-t / 0.03)) * (1 - np.exp(-t / 0.0008))
    y = norm(y) + 0.22 * norm(contact(n, rng, 1500, 7000, 0.0012))
    return norm(fades(y))


def g_rustle(rng, dur=0.35, attack=None):
    """布料：800–6500 Hz 的噪声乘上细碎的颗粒。探身、缩回用。attack 给秒数时快起（动作一开始就有声），之后按 cos 收到 dur 正好没了。"""
    n = int(dur * SR)
    t = ts(n)
    base = noise(n, rng, 800, 6500, tilt=-0.3)
    imp = (rng.random(n) < 140 / SR) * rng.uniform(0.2, 1, n)
    gr = np.convolve(imp, np.exp(-np.arange(int(0.006 * SR)) / (0.0015 * SR)))[:n]
    if attack:
        e = np.clip(t / attack, 0, 1) * np.cos(0.5 * np.pi * np.clip((t - attack) / (dur - attack), 0, 1)) ** 1.2
    else:
        e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return norm(fades(base * (0.35 + gr / (gr.max() + 1e-9)) * e))


def g_banner(rng, u):
    """一条横幅从手机里喷出来：一下往上扫的短“噌”（1.6 → 4.5 kHz，70 毫秒，起得快），尾上一下小“啵”；u（0–1）是第几条，越往后越高、越短。"""
    dur = 0.075 - 0.025 * u
    n = int((dur + 0.06) * SR)
    t = ts(n)
    f0 = 1600 * 1.25 ** u
    y = tv_noise(n, rng, f0 * (2.8 ** np.clip(t / dur, 0, 1)), 1.0)
    e = np.clip(t / 0.003, 0, 1) * np.where(t < dur * 0.4, 1.0, np.exp(-(t - dur * 0.4) / (dur * 0.35)))
    y = norm(y * e)
    _mixin(y, g_bubble(rng, 950 * 1.6 ** u, 0.04), int(dur * 0.5 * SR), 0.45)
    return norm(fades(y, 0.0003, 0.01))


def g_shatter(rng):
    """横幅全部震散（3 帧内）：一下闷响（g_pu，叠指节敲击，手机外放靠它）＋一口冲开的宽带气浪（1–8 kHz，1 毫秒起、60 毫秒散）
    ＋ 24 片碎片四散（0–100 毫秒里一片片的纸声，越来越轻）＋几颗飞出去的小亮声＋往下沉的余风（3 kHz → 900 Hz，0.3 秒）。"""
    n = int(0.7 * SR)
    t = ts(n)
    y = np.zeros(n)
    _mixin(y, g_pu(rng, 1.2, low=0.8, knock=1.4, sat=2.0, kf=1300, kt=0.06), 0, 1.0)
    burst = noise(n, rng, 1000, 8000, tilt=-0.3) * np.clip(t / 0.001, 0, 1) * np.exp(-t / 0.06)
    y += 0.7 * norm(burst)
    for k in range(24):
        o = 0.1 * (k / 24) ** 0.8 + rng.uniform(0, 0.008)
        _mixin(y, g_flick(rng), int(o * SR), 0.5 * (1 - 0.6 * k / 24) * rng.uniform(0.6, 1.0))
    for k in range(4):
        _mixin(y, g_glint(rng, rng.uniform(3000, 5200), tau=0.03), int(rng.uniform(0.03, 0.2) * SR), 0.12)
    wind = tv_noise(n, rng, 3000 * (900 / 3000) ** np.clip(t / 0.3, 0, 1), 1.4) * np.clip(t / 0.01, 0, 1) * np.exp(-t / 0.12)
    y += 0.3 * norm(wind)
    y = np.tanh(1.5 * norm(y)) / np.tanh(1.5)
    return norm(fades(y))


def g_pu(rng, size=1.0, low=0.9, knock=0.0, sat=1.5, kf=1500.0, kt=0.065):
    """闷“噗”：一个从 270 Hz 掉到 100 Hz 的闷响 + 一口气 + 一点 1–2 kHz 的接触声；knock>0 再叠一层指节敲木头（手机外放靠它）。"""
    n = int(0.3 * SR)
    t = ts(n)
    fb = (100 + 170 * np.exp(-t / 0.014)) * jit(rng, 30) / size ** 0.25
    body = np.sin(2 * np.pi * np.cumsum(fb) / SR) * np.exp(-t / (0.045 * size)) * (1 - np.exp(-t / 0.0012))
    puff = noise(n, rng, 200, 1500, tilt=-0.5) * np.exp(-t / (0.022 * size)) * (1 - np.exp(-t / 0.0015))
    y = low * norm(body) + 0.6 * norm(puff) + 0.3 * norm(contact(n, rng, 900, 2400, 0.003))
    if knock:
        _mixin(y, g_knock(rng, kf, kt), int(0.006 * SR), knock)
    y = np.tanh(sat * y) / np.tanh(sat)
    return norm(fades(y))


def g_impact(rng):
    """标题卡落下的那一下：软的“咚”。73 Hz 的闷响（D2，起音高一点往下沉）饱和一下；440–880 Hz 的箱板；
    叠一下 1.1 kHz 的指节敲木头（手机外放靠它）；再一层 2–8 kHz 的空气声慢慢散掉（像灰尘扬起来）。"""
    n = int(1.2 * SR)
    t = ts(n)
    ph = 2 * np.pi * np.cumsum(73.4 * (1 + 0.3 * np.exp(-t / 0.03))) / SR
    body = (np.sin(ph) * np.exp(-t / 0.28) + 0.4 * np.sin(2.02 * ph + 1) * np.exp(-t / 0.1)) * (1 - np.exp(-t / 0.002))
    body = np.tanh(2.2 * body) / np.tanh(2.2)
    box = modal(n, [(440, 1, 0.09), (587, 0.6, 0.07), (880, 0.35, 0.05)], rng, att=0.001)
    air = noise(n, rng, 2000, 8000, tilt=-0.4) * np.exp(-t / 0.35) * np.clip(t / 0.03, 0, 1)
    y = 0.7 * norm(body) + 0.9 * norm(box) + 0.22 * norm(air)
    _mixin(y, g_knock(rng, 1100, 0.07), int(0.004 * SR), 1.4)
    y = np.tanh(1.5 * norm(y)) / np.tanh(1.5)
    return norm(fades(y))


def g_tok(rng, f0):
    """标签落下的“笃”：有音高的小木块（f0、1.58、2.9 倍），40 毫秒就没了。"""
    n = int(0.2 * SR)
    f0 *= jit(rng, 5)
    y = norm(modal(n, [(f0, 1, 0.045), (1.58 * f0, 0.3, 0.018), (2.9 * f0, 0.12, 0.008)], rng, att=0.0004))
    y = y + 0.4 * norm(contact(n, rng, 1500, 7000, 0.0012))
    return norm(fades(y))


def g_mute_bell(rng, f0):
    """静音铃：一个小铃被手捂住——主音 0.11 秒就没了、没有亮泛音，带一下隔着手的“笃”（0.31 f0 的闷响 + 1.5 kHz 的短敲击）。"""
    n = int(0.8 * SR)
    f0 *= jit(rng, 4)
    y = norm(modal(n, [(f0, 1.0, 0.11), (f0 + 1.5, 0.3, 0.1), (2.70 * f0, 0.15, 0.03)], rng))
    y = y + 0.45 * norm(modal(n, [(f0 * 0.31, 1, 0.035), (f0 * 0.62, 0.4, 0.02)], rng))
    _mixin(y, g_knock(rng, 1500, 0.035), 0, 0.8)
    return norm(fades(shape(y, 150, 5000)))


def g_startle(rng):
    """一惊：一下尖的往上蹿的“咻↑”（700 → 2600 Hz，70 毫秒滑上去，之后带 16 Hz 的哆嗦），起头一下指节敲（1.7 kHz），
    底下一口很短的倒吸气（0.11 秒）。"""
    n = int(0.5 * SR)
    t = ts(n)
    u = np.clip(t / 0.07, 0, 1)
    f = 700 * (2600 / 700) ** (u ** 0.7)
    f = f * (1 + 0.025 * np.sin(2 * np.pi * 16 * t) * np.clip((t - 0.07) / 0.03, 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.25 * np.sin(2 * ph + 1)) * np.where(t < 0.07, 1, np.exp(-(t - 0.07) / 0.1)) * (1 - np.exp(-t / 0.002))
    gasp = tv_noise(n, rng, 1400 * (1 + 0.5 * u), 1.5) * np.clip(t / 0.05, 0, 1) ** 1.5 * np.clip((0.11 - t) / 0.015, 0, 1)
    y = 0.8 * norm(tone) + 0.35 * norm(gasp)
    _mixin(y, g_knock(rng, 1700, 0.04), 0, 0.9)
    return norm(fades(y))


def g_flick(rng):
    """一张小卡片飞出去：很短的一下纸声（1.8–7.5 kHz，6 毫秒）。"""
    n = int(0.04 * SR)
    t = ts(n)
    y = noise(n, rng, 1800, 7500, tilt=-0.2) * np.exp(-t / 0.006) * (1 - np.exp(-t / 0.0006))
    return norm(fades(y, 0, 0.004))


def g_riffle(rng, offs):
    """发牌：一串小卡片飞出去的纸声（offs 是每张的起点，秒），底下一层往上扫的轻风。"""
    n = int((max(offs) + 0.45) * SR)
    y = np.zeros(n)
    for o in offs:
        _mixin(y, g_flick(rng) * rng.uniform(0.6, 1.0), int(o * SR))
    w = g_whoosh(rng, dur=max(offs) + 0.3, f0=1200, f1=3500, tp=max(offs) * 0.6 + 0.05, tail=0.08, floor=0.3)
    _mixin(y, 0.5 * w, 0)
    return norm(y)


def g_poof(rng):
    """轻柔的“噗”：一口软的气（250–2600 Hz，8 毫秒起、70 毫秒散）+ 一下很轻的低响（160 Hz 往下掉）+ 一层 2.5–9 kHz 的“嘶”慢慢散掉，
    像吹灭一个小东西。没有敲击，不硬。"""
    n = int(0.5 * SR)
    t = ts(n)
    puff = noise(n, rng, 250, 2600, tilt=-0.6) * np.clip(t / 0.008, 0, 1) * np.exp(-t / 0.07)
    body = np.sin(2 * np.pi * np.cumsum(160 * (1 + 0.6 * np.exp(-t / 0.01))) / SR) * np.exp(-t / 0.05) * (1 - np.exp(-t / 0.002))
    air = noise(n, rng, 2500, 9000) * np.exp(-t / 0.14) * np.clip(t / 0.02, 0, 1)
    y = norm(puff) + 0.15 * norm(body) + 0.3 * norm(air)
    y = shape(y, 200, None)                                      # 低响只留一点：手机放不出，只会顶峰值
    y = np.tanh(2.0 * norm(y)) / np.tanh(2.0)                   # 压一下峰值（软，不硬）
    return norm(fades(y))


def g_pin(rng):
    """置顶的图钉按下去：轻的“咔”（3.2 kHz 的硬塑料 + 接触声），28 毫秒后第二颗图钉轻一点（两张卡同时钉上，听着还是一下“咔”），
    底下一点点 900 Hz 的“扎进软木”。"""
    n = int(0.18 * SR)
    y = np.zeros(n)
    _mixin(y, g_click(rng, 3200, 0.018), 0, 1.0)
    _mixin(y, g_click(rng, 2750, 0.02), int(0.028 * SR), 0.6)
    _mixin(y, norm(modal(int(0.06 * SR), [(900 * jit(rng, 20), 1, 0.012)], rng)), int(0.004 * SR), 0.35)
    y = np.tanh(2.0 * norm(y)) / np.tanh(2.0)
    return norm(fades(y))


def g_lid(rng, sparkle):
    """小木盒开盖：合页两下小“咔”（1.5 kHz、1.1 kHz，18 毫秒）+ 空心的“啵”（520 Hz 的盒子 + 1.18 kHz）+ 三颗小亮声往上冒
    （sparkle 那个音的高八度，攒着的红心飞出来，一颗比一颗轻）。"""
    n = int(1.0 * SR)
    y = np.zeros(n)
    _mixin(y, g_click(rng, 1500, 0.012, 0.08), 0, 0.8)
    _mixin(y, g_click(rng, 1100, 0.015, 0.08), int(0.018 * SR), 0.6)
    pok = norm(modal(int(0.3 * SR), [(520 * jit(rng, 15), 1, 0.05), (1180 * jit(rng, 15), 0.45, 0.02)], rng, att=0.0008))
    _mixin(y, pok, int(0.012 * SR), 0.9)
    for k, d in enumerate((0.06, 0.13, 0.21)):
        _mixin(y, g_glint(rng, sparkle * 2, tau=0.09), int(d * SR), 0.32 - 0.06 * k)
    return norm(fades(y))


def g_page(rng, dur=0.42, flap=0.6):
    """翻书页：纸面滑过的嘶声（1–6 kHz，先涨后落）带纸的细碎颗粒，翻到底一下软的“啪”（纸拍下去：400–900 Hz 的闷声 + 2–6 kHz 的气）。"""
    n = int((dur + 0.15) * SR)
    t = ts(n)
    u = np.clip(t / dur, 0, 1)
    y = tv_noise(n, rng, 1800 * (3200 / 1800) ** np.sin(np.pi * u), 1.6)
    imp = (rng.random(n) < 220 / SR) * rng.uniform(0.2, 1, n)
    gr = np.convolve(imp, np.exp(-np.arange(int(0.004 * SR)) / (0.001 * SR)))[:n]
    e = np.sin(np.pi * u) ** 1.2 * (t < dur)
    y = norm(y * e * (0.5 + gr / (gr.max() + 1e-9)))
    m = int(0.15 * SR)
    tt = ts(m)
    fl = (noise(m, rng, 2000, 6000) * 0.5 + noise(m, rng, 350, 900)) * np.exp(-tt / 0.025) * (1 - np.exp(-tt / 0.002))
    _mixin(y, flap * norm(fl), int((dur - 0.03) * SR))
    return norm(fades(y, 0.005, 0.01))


def g_shutter(rng):
    """截图的快门“咔嚓”：先一下高的“咔”（4.2 kHz + 2–10 kHz 的接触声，快门打开），中间 50 毫秒机构滑动的嘶声，
    65 毫秒后一下低一点、厚一点的“嚓”（2.6 kHz + 1.3 kHz，快门合上），带一点弹簧的余响。"""
    n = int(0.35 * SR)
    t = ts(n)
    y = np.zeros(n)
    _mixin(y, g_click(rng, 4200, 0.012, 0.1), 0, 1.0)
    _mixin(y, norm(contact(int(0.05 * SR), rng, 2000, 10000, 0.002)), 0, 0.6)
    mech = noise(n, rng, 1500, 6000) * np.clip((t - 0.005) / 0.01, 0, 1) * np.clip((0.06 - t) / 0.01, 0, 1)
    y += 0.18 * norm(mech)
    i = int(0.065 * SR)
    _mixin(y, g_click(rng, 2600, 0.02, 0.12), i, 0.95)
    _mixin(y, norm(modal(int(0.15 * SR), [(1300 * jit(rng, 15), 1, 0.025), (5300, 0.25, 0.04)], rng)), i, 0.45)
    y = np.tanh(1.8 * norm(y)) / np.tanh(1.8)
    return norm(fades(y))


# ======================================================================
# 排事件
# ======================================================================
EVENTS = []


def put(kind, vis, sound, gain, cat='mid', lead=0.0, anchor=0.0, label='', send=None, pan=0.0, key=False, spec=None, check=True, req=False):
    """vis：画面事件的秒；lead：音效比画面早多少秒（负数）；anchor：声音里“落点”离声音开头多少秒（先起后落的嗖用）。
    放置位置 = vis + lead − anchor；事件表里的 t = vis + lead（落点）。cat：key / mid / tick（计数）/ tex（细碎的一层）。
    spec：这是任务点名要的哪一个声音（自查表用），写的是分镜里的说法；req：它是点名的那个声音的一部分（同一下的提示音、后面的滴答等）。"""
    EVENTS.append(dict(kind=kind, vis=float(vis), lead=lead, anchor=anchor, sound=sound, gain=gain, cat=cat, label=label or kind,
                       send=send, pan=pan, key=key or cat == 'key', spec=spec, check=check and cat != 'tex', req=req or spec is not None))


def roll_ticks(kind, ab, total, step, gain, label):
    """三栏读数从 0 滚到 total（Gray003：round(total × ease(进度))）：每跨过 step 一下很轻的“嗒”，中间密、两头疏，跟数字一起走。"""
    for v in np.arange(step, total + 1e-9, step):
        x = ease_inv(v / total)
        put(kind, ab[0] + x * (ab[1] - ab[0]), lambda r, v=v: g_tick(r, 2600 + 6 * v), gain, cat='tex', label=label)


def plan():
    EVENTS.clear()
    rng = np.random.default_rng(SEED)
    hz = HZ

    # —— B01–B02 钩子：手机一条条来（0.3、0.88、2.6 秒，7.55 秒又一下）。11/2 评委改：每次震，画面抖 8 帧（SHAKE），震动声也正好 8 帧长；
    #    8 帧里震得一次比一次急：一下 → 两下 → 两下 → 三下。每个 App 一种提示音（拼单是电子味的“嘀嘟”，工作群是玻璃“叮咚”，热榜是木琴两声）——
    b0, b1, b2 = EV['buzz']
    sk = SHAKE
    put('震动', b0, lambda r: g_vibrate(r, [(0, sk)]), -8, 'key', label='手机震一下（拼单立减，计数 1；8 帧）',
        spec=('手机震动＋通知提示音 第 1 下', 0.3, '分镜 0–1.8 拍：0.3 秒手机亮、震一下，计数跳成 1；画面抖 8 帧'))
    put('提示音', b0, lambda r: g_chime(r, [hz['A5'], hz['D6']], 0.075, 'square', 0.12, [0.8, 1.0]), -8, 'key',
        label='提示音：拼单立减', send={'hall': 0.12}, req=True)
    put('震动', b1, lambda r: g_vibrate(r, [(0, 0.11), (0.15, sk - 0.15)]), -5, 'key', label='手机震两下（工作群（37），计数 2；8 帧）',
        spec=('手机震动＋通知提示音 第 2 下', 0.88, '时间表 buzz[1]：工作群（37）（v2 提前到第 1 秒）；画面抖 8 帧'))
    put('提示音', b1, lambda r: g_chime(r, [hz['D6'], hz['A5']], 0.16, 'glass', 0.32, [1.0, 0.8]), -9, 'key',
        label='提示音：工作群（叮咚）', send={'hall': 0.15}, req=True)
    put('震动', b2, lambda r: g_vibrate(r, [(0, 0.1), (0.14, sk - 0.14)]), -6, 'key', label='手机震两下（热榜第一，计数 3；8 帧）',
        spec=('手机震动＋通知提示音 第 3 下', 2.6, '分镜 1.8–3.2 拍：又震两下，计数 1→3；画面抖 8 帧'))
    put('提示音', b2, lambda r: g_chime(r, [hz['F6'], hz['D6']], 0.09, 'wood', 0.16), -10, 'key', label='提示音：热榜第一',
        send={'hall': 0.12}, req=True)
    put('嗖', EV['preview'][0], lambda r: g_whoosh(r, dur=0.2, f0=1800, f1=3200, tp=0.05, tail=0.04, floor=0.3), -24, 'tex',
        label='横幅展开，露出“明早 8 点前交表”')

    # —— B03 要紧的那条亮起（暖黄）：一声暖的“叮”；打开群往上滚：轻的划动声；停在第 23 条：一下轻“嗒” ——
    put('叮', EV['keyLight'][0], lambda r: g_warm(r, hz['F5']), -10, 'mid', label='要紧的那条亮起（暖叮 F5）', send={'hall': 0.18})
    sc0, sc1 = EV['scroll']
    put('嗖', sc0, lambda r: g_whoosh(r, dur=sc1 - sc0 + 0.05, f0=2600, f1=1500, tp=0.12, tail=0.2, floor=0.4), -25, 'tex',
        label='群消息往上滚')
    for k in range(9):                  # 滚过去的一条条消息：细碎的小“嗒”。画面是 easeOut 滚动，滚过第 k 条的时刻 = easeOut 的反函数
        x = 1 - (1 - (k + 0.5) / 9) ** (1 / 3)
        put('滴答', sc0 + (sc1 - sc0) * x, lambda r: g_tick(r, 3000), -30, 'tex', label='滚过的消息')
    put('嗒', EV['highlight'][0], lambda r: g_tok(r, hz['D6']), -18, 'mid', label='停在第 23 条，其余变灰')

    # —— B04–B05 探身去关、停住；11/2 评委改：手先往前探 3 帧、再往后撤 10 帧并握拳，布料声对到后撤开始（RECOIL[0]），
    #    长度正好 10 帧，起得快（20 毫秒），撤完收住。7.55 秒手机又亮一下：8 帧里震三下（更急）＋提示音 ——
    put('嗖', EV['sheetIn'][0], lambda r: g_whoosh(r, dur=0.22, f0=1400, f1=2800, tp=0.08, tail=0.05, floor=0.25), -25, 'tex',
        label='“关闭通知”页滑上来')
    put('布料', EV['reach'][0], lambda r: g_rustle(r, 0.4), -27, 'tex', label='探身')
    rc0, rc1 = RECOIL
    put('布料', rc0, lambda r: g_rustle(r, rc1 - rc0, attack=0.02), -21, 'mid', label='手往后撤、握拳（10 帧）',
        spec=('手往后撤的布料声（10 帧）', round(rc0, 2), '评委改：手先往前探 3 帧、再往后撤 10 帧并握拳，布料声对到后撤开始（约 6.9 秒）'))
    ba = EV['buzzAgain']
    put('震动', ba, lambda r: g_vibrate(r, [(0, 0.07), (0.1, 0.07), (0.2, sk - 0.2)]), -4, 'key', label='手机又震（8 帧里三下，计数 4）',
        spec=('手机震动＋通知提示音 第 4 下', 7.55, '分镜 7.2–8.2 拍：手机又亮一下（v2：7.55 秒，计数加到 4）；画面抖 8 帧'))
    put('提示音', ba, lambda r: g_chime(r, [hz['A5'], hz['D6'], hz['F6']], 0.07, 'square', 0.1), -9, 'key', label='提示音：又一条推送',
        send={'hall': 0.12}, req=True)

    # —— B06 计数 4→120（8.2–9.4）。11/2 评委改：27 条横幅从手机里喷出、铺满画面（BANNERS，越来越密：间隔 80 → 25 毫秒），
    #    每条一声“噌”（往上扫的短嗖＋一下小“啵”，一条比一条高），底下一层越来越快的计数“嗒”；
    #    9.4 计数停在 120，3 帧内横幅全部震散：一记“震散”（闷响＋冲开的气浪＋碎片四散），上面轻轻一声“叮”（A6，计数停住）；
    #    计数狂涨时手机一直抖（Gray003 shake()），所以底下一层一直震，到震散那一下停 ——
    c0, c1 = EV['count']
    put('震动', c0, lambda r: g_vibrate(r, [(0.0, SHATTER - c0)], motor=180), -11, 'mid', label='计数狂涨，手机一直抖（到震散为止）', req=True)
    for k, t in enumerate(BANNERS):
        u = k / max(1, len(BANNERS) - 1)
        put('喷出', t, lambda r, u=u: g_banner(r, u), -14 + 2 * u, 'mid', label=f'横幅喷出 {k + 1}/{len(BANNERS)}', req=True,
            spec=(f'横幅从手机喷出（{len(BANNERS)} 条，越来越密）', t,
                  f'评委改：{BANNERS[0]:.2f}–{BANNERS[-1]:.2f} 秒 {len(BANNERS)} 条横幅喷出铺满画面；间隔 62 → 19 毫秒，音高往上走') if k == 0 else None)
    for k, t in enumerate(TICKS):
        u = (t - c0) / (c1 - c0)
        put('滴答', t, lambda r, u=u: g_tick(r, 2100 + 1300 * u), -14 + 2 * u, 'tick', label=f'计数滴答 {k + 1}/{len(TICKS)}', req=True,
            spec=('计数跳动的滴答（越来越快）', c0, f'分镜 8.2–9.4：从 4 跑到 120，共 {len(TICKS)} 下，间隔 80→25 毫秒') if k == 0 else None)
    put('震散', SHATTER, lambda r: g_shatter(r), -5, 'key', label='120：横幅全部震散（3 帧）', send={'hall': 0.15},
        spec=('9.4 秒横幅震散', SHATTER, '评委改：第 9.4 秒计数停在 120，3 帧内横幅全部震散'))
    f0_, f1_ = EV['countFlash']
    put('叮', f0_, lambda r: g_ding(r, hz['A6'], bright=1.0), -17, 'mid', label='120 停住、闪一下', send={'hall': 0.2}, req=True)
    put('叮', f0_ + 0.2, lambda r: g_ding(r, hz['A6'], bright=0.8, decay=0.8), -22, 'mid', label='120 再闪一下', send={'hall': 0.2}, req=True)

    # —— B07 标题卡“同一天，三种设法”。11/2 评委改：6 帧落下（TITLE_DROP）、2 帧回弹；落下时一声往下砸的“嗖”，
    #    在落地前 15 毫秒收掉，落地那一帧（10.6）一下软“咚”，起音干净；10.8 三个你滑开：一声轻嗖；三个标签落下：三声“笃”（D6 F6 A6） ——
    td0, land = TITLE_DROP
    sp = land - 0.015 - td0                                  # 落下的嗖：从 10.4 涨到落地前 15 毫秒（默认参数绑住，免得后面改名的变量串进来）
    put('嗖', land - 0.015, lambda r, sp=sp: g_swell(r, sp, 900, 3600, tail=0.006), -10, 'mid', anchor=sp,
        label='转场：标题卡落下（6 帧）', check=False, req=True)
    put('咚', land, lambda r: g_impact(r), -2, 'key', label='转场：标题卡“同一天，三种设法”落地', send={'hall': 0.18},
        spec=('标题卡“同一天，三种设法”的转场声（对到落地）', land, '评委改：10.4 起 6 帧落下、2 帧回弹，转场声对到 10.6 落地那一下'))
    put('嗖', EV['split'][0], lambda r: g_whoosh(r, dur=0.42, f0=1100, f1=2600, tp=0.18, tail=0.08, floor=0.2), -21, 'tex',
        label='你分成三个滑开')
    for k, la in enumerate(EV['labels']):
        # 11/3 协调方：“全关”现在是 11.2 秒从右边滑进来、第 343 帧到位（不是落下），这一声往后挪 5 帧，落在到位那一帧
        tl = (round((la + 0.08) * FPS) + 5) / FPS if k == 1 else la + 0.08
        put('笃', tl, lambda r, k=k: g_tok(r, (hz['D6'], hz['F6'], hz['A6'])[k]), -12, 'mid',
            label=('标签落下：全开', '标签滑到位：全关', '标签落下：先分开')[k])

    # —— B08 全开：左栏手机不停亮（每次亮一下一声很轻的“嘀”）；读数滚到 120：很轻的“嗒”跟着数字走 ——
    t0, t1 = EV['leftFlash'], B['B08']['t1']
    k = math.ceil(t0 * 2.6)
    blips = [hz['D6'], hz['A5'], hz['F6'], hz['A5']]
    while k / 2.6 < t1 - 0.1:
        put('嘀', k / 2.6 + 0.04, lambda r, f=blips[k % 4]: g_chime(r, [f], 0, 'square', 0.06), -21, 'mid', label='全开：手机又亮',
            send={'room': 0.1})
        k += 1
    roll_ticks('滴答', EV['leftRoll'], READ[0][0], 8, -27, f'左栏读数滚到 {READ[0][0]}')
    roll_ticks('滴答', EV['midRoll'], READ[1][0] - 1, 3, -27, f'中栏读数滚到 {READ[1][0] - 1}')

    # —— B09 v3：全关的你自己拿起手机看一眼（14.1），读数 +1（14.55），又放下（15.55 落桌） ——
    if 'pickUp' in EV:
        put('布料', EV['pickUp'][0], lambda r: g_rustle(r, 0.3), -27, 'tex', label='自己拿起手机')
        put('嗒', EV['pickUp'][0] + 0.12, lambda r: g_click(r, 1900, 0.02), -13, 'mid', label='手机离开桌面')
        put('嗒', EV['midSelf'], lambda r: g_tok(r, hz['A5']), -17, 'mid', label=f'中栏读数 +1（{READ[1][0] - 1}→{READ[1][0]}，自己拿起来的）')
        put('嗒', EV['putDown'][1] - 0.04, lambda r: g_pu(r, 0.6, low=0.5, knock=0.8, sat=1.4, kf=1700, kt=0.03), -13, 'mid',
            label='手机放回桌上')

    # —— B10 全关：小钟走一圈（一小时）：12 下“嘀嗒”加走完一下（每下 5 分钟，跟着指针的缓入缓出，中间密两头疏）；
    #    v3：走到 15:40 交表那条才弹出来（灰）：工作群提示音的闷版本（隔着关掉的通知，又晚又闷），和 31.75 秒“立刻亮”那声对照 ——
    k0, k1 = EV['clockTurn']
    for k in range(12):
        tk = k0 + ease_inv(k / 12) * (k1 - k0) if k else k0
        put('嘀嗒', tk, lambda r, k=k: g_clock(r, tock=bool(k % 2)), -8 if k else -6, 'mid' if k else 'key',
            label=f'小钟走（第 {k * 5} 分钟）', req=True,
            spec=('全关段：小钟走动（12 下＋走完一下）', k0, '分镜 15.0–18.0 拍：小钟走一圈（1 小时）；时间表 clockTurn 15.4–17.2') if k == 0 else None)
    put('嘀嗒', k1, lambda r: g_clock(r), -6, 'mid', label='小钟走完一小时（15:40）', req=True)
    put('提示音', EV['cardIn'][0] + 0.03,
        lambda r: norm(shape(g_chime(r, [hz['D6'], hz['A5']], 0.16, 'glass', 0.2, [1.0, 0.7]), 200, 1500, order=2)), -14, 'mid',
        label='交表那条到 15:40 才弹出来（闷的工作群提示音）')

    # —— B11 中栏的你一惊（18.0）：“咻↑”＋敲；手机翻过来（18.6 落下）：轻“嗒” ——
    put('惊', EV['startle'][0], lambda r: g_startle(r), -6, 'key', label='中栏的你一惊',
        spec=('全关段：“一惊”的一下', 18.0, '分镜 18.0–19.0 拍：中栏的“你”一惊，手机翻过来'))
    put('嗒', EV['flip'][1] - 0.04, lambda r: g_click(r, 2300, 0.03), -12, 'mid', label='手机翻过来')
    # —— B12 那条卡片砸到头上（19.4）：沉的一下 ——
    put('咚', EV['cardDrop'][1], lambda r: g_pu(r, 1.3, low=0.9, knock=0.9, sat=1.8, kf=1150, kt=0.06), -9, 'mid',
        label='“交表”卡片压到头上')
    put('嗒', EV['flipBack'][1] - 0.03, lambda r: g_click(r, 2000, 0.025), -22, 'tex', label='手机又扣回去')

    # —— B13 镜头推向右栏：推镜头一开始（21.6，第 648 帧）就起一声“嗖”（一起头就有峰值的三成多，听得见），跟着镜头越推越响，
    #    推到位前 30 毫秒（22.57）一刀收掉，配乐在 22.6 转大调。11/3 协调方：事件表的落点写起头（原来写的是到顶的 22.57） ——
    p0, p1 = EV['push']
    put('嗖', p0, lambda r, sp=p1 - 0.03 - p0: g_swell(r, sp, 700, 3000, tail=0.03, bw0=2.0, bw1=1.0, floor=0.35), -15, 'mid',
        label='推向右栏（先分开，从推镜头开始）')

    # —— B14 先分开：发牌（12 张小卡片 22 毫秒一张飞进四个标签）；四个标签弹出：四声小“啵”；
    #    广告推送放大 → 变灰 → 缩小消失：消失那一下轻柔的“噗” ——
    d0 = EV['deal'][0]
    put('刷', d0, lambda r: g_riffle(r, [0.022 * k for k in range(12)]), -13, 'mid', label='消息分成四类（发牌）')
    for i in range(4):
        put('啵', EV['chipsIn'][0] + 0.06 * i + 0.03, lambda r, i=i: g_bubble(r, 900 + 160 * i), -16, 'mid', label='分类标签弹出')
    put('嗖', EV['adOpen'][0], lambda r: g_whoosh(r, dur=0.3, f0=1200, f1=2500, tp=0.12, tail=0.06, floor=0.2), -26, 'tex',
        label='广告推送放大到中间')
    g0, g1 = EV['adGone']
    put('嗖', g0, lambda r: g_whoosh(r, dur=g1 - g0, f0=2600, f1=900, tp=(g1 - g0) * 0.6, tail=0.05, floor=0.15), -27, 'tex',
        label='广告推送缩小')
    put('噗', g1 - 0.12, lambda r: g_poof(r), -4.5, 'key', label='广告推送消失（轻噗）',
        spec=('先分开段：广告推送消失（轻柔的“噗”）', 24.0, '分镜 22.6–24.6 拍：“广告推送”那堆变灰、缩小、消失；时间表 adGone 23.9–24.4'))

    # —— B15 群：放大到中间；工作群、老师群升到最上：轻的往上“嗖”；图钉按下：轻“咔”；照常亮：两声轻的工作群提示音 ——
    put('嗖', EV['groupOpen'][0], lambda r: g_whoosh(r, dur=0.3, f0=1200, f1=2500, tp=0.12, tail=0.06, floor=0.2), -26, 'tex',
        label='群放大到中间')
    r0, r1 = EV['rise']
    put('嗖', r0, lambda r: g_whoosh(r, dur=r1 - r0, f0=1000, f1=2800, tp=(r1 - r0) * 0.55, tail=0.08, floor=0.2), -22, 'tex',
        label='工作群、老师群升到最上')
    pa, pb = EV['pins']
    put('咔', pa + 0.37 * (pb - pa), lambda r: g_pin(r), -5.5, 'key', label='置顶：图钉按下',
        spec=('先分开段：置顶（轻“咔”）', 25.6, '分镜 24.6–27.0 拍：两张卡升到最上，加图钉；时间表 pins 25.6–25.95（图钉 25.73 落到底）'))
    for k, tp in enumerate(EV['groupPing']):
        put('提示音', tp, lambda r: g_chime(r, [hz['D6'], hz['A5']], 0.16, 'glass', 0.28, [1.0, 0.8]), -17 - 2 * k, 'mid',
            label='置顶的群照常亮', send={'hall': 0.15})

    # —— B16 别的群挂静音铃：三声被捂住的铃（A5 → F♯5 → D5，往下走，一声比一声轻） ——
    for k, tb in enumerate(EV['bells']):
        put('闷铃', tb + 0.02, lambda r, k=k: g_mute_bell(r, (hz['A5'], hz['F#5'], hz['D5'])[k]), -5 - 1.5 * k, 'key',
            label=f'静音铃 {k + 1}',
            spec=(f'先分开段：静音铃（闷一下）第 {k + 1} 个', tb, '分镜 27.0–28.6 拍：其余群卡片挂上静音铃；时间表 bells 27.1、27.3、27.5'))

    # —— B17 点赞：放大、收进小盒子（一阵轻的“嗖”）；时间轴 9、15、21 点各开一次盖：合页“咔”＋空心“啵”＋三颗往上冒的亮声
    #    （D、F♯、A，一次比一次高）；最后私聊照常亮：一声私聊提示音 ——
    put('嗖', EV['likeOpen'][0], lambda r: g_whoosh(r, dur=0.3, f0=1200, f1=2500, tp=0.12, tail=0.06, floor=0.2), -26, 'tex',
        label='点赞放大到中间')
    bi0, bi1 = EV['boxIn']
    put('嗒', bi0 + 0.37 * (bi1 - bi0), lambda r: g_tok(r, hz['D5']), -20, 'mid', label='小盒子出来')
    if 'hearts' in EV:                                         # v3：红心一个个飞进盒子：每颗进去一声很轻的“噗”
        h0, h1 = EV['hearts']
        hn, hf = TLD['heart_n'], TLD['heart_fly']
        for k in range(hn):
            put('啵', h0 + k * (h1 - h0) / (hn - 1) + hf, lambda r: g_bubble(r, 1500, 0.04), -29, 'tex', label='红心飞进盒子')
    for k, (s0, s1, s2) in enumerate(EV['stops']):
        put('开盖', s1, lambda r, k=k: g_lid(r, (hz['D6'], hz['F#6'], hz['A6'])[k]), -5.5, 'key',
            label=f'盒子开盖（{(9, 15, 21)[k]} 点）', send={'hall': 0.12},
            spec=(f'先分开段：盒子开盖 第 {k + 1} 次（{(9, 15, 21)[k]} 点）', s1,
                  '分镜 28.6–31.0 拍：时间轴 9、15、21 点各开一次盒子；时间表 stops[i][1]'))
    put('提示音', EV['dmPing'][2], lambda r: g_chime(r, [hz['A5'], hz['D6']], 0.12, 'wood', 0.22), -15, 'mid',
        label='私聊照常亮', send={'hall': 0.12})

    # —— B18 拉回三栏；工作群“明早 8 点前交表”立刻亮：和 0.88 秒同一个工作群提示音（这次一来就看到）；读数滚到 67 ——
    q0, q1 = EV['pull']
    put('嗖', q0, lambda r: g_whoosh(r, dur=q1 - q0, f0=2800, f1=1000, tp=0.2, tail=0.15, floor=0.3), -23, 'tex', label='拉回三栏')
    put('提示音', EV['rightCard'], lambda r: g_chime(r, [hz['D6'], hz['A5']], 0.16, 'glass', 0.32, [1.0, 0.8]), -8, 'key',
        label='工作群“明早 8 点前交表”立刻亮', send={'hall': 0.15})
    roll_ticks('滴答', EV['rightRoll'], 67, 5, -27, '右栏读数滚到 67')
    put('叮', EV['rightLate'], lambda r: g_ding(r, hz['A6'], bright=0.6, decay=0.7), -19, 'mid', label='右栏“晚看到 0 件”')

    # —— B19–B21 卡片收进手机（轻嗖）；v3：右边的你拿起书（33.7）、翻开（34.1）；37.0 翻一页：纸声，不加铃（金句这里配乐在收） ——
    put('嗖', EV['cardIntoPhone'][0], lambda r: g_whoosh(r, dur=0.3, f0=2400, f1=1200, tp=0.2, tail=0.04, floor=0.2), -26, 'tex',
        label='卡片收进手机')
    if 'bookTake' in EV:
        put('布料', EV['bookTake'][0], lambda r: g_rustle(r, 0.35), -26, 'tex', label='拿起桌上的书')
        o0, o1 = EV['bookOpen']
        put('翻书', o1, lambda r: g_page(r, 0.25, 0.8), -15, 'mid', anchor=0.22, label='把书翻开')
        put('翻书', EV['glowPulse'] + 0.42, lambda r: g_page(r, 0.42, 0.6), -13, 'mid', anchor=0.39, label='翻一页（是分出来的）')
    else:
        put('叮', EV['glowPulse'], lambda r: g_warm(r, hz['F#5']), -11, 'mid', label='“空”亮一下（暖铃 F♯5）', send={'hall': 0.2})

    # —— B22 定住（38.6–39.6）：音效全停（见 gate_curve）；B23 39.7 截图：快门“咔嚓”从静里出来 ——
    put('快门', EV['shot'], lambda r: g_shutter(r), -3.5, 'key', label='截图快门', send={'room': 0.12},
        spec=('清单开始：截图快门声', 39.7, '分镜 39.6 起清单屏 1；时间表 shot 39.7（画面闪白）'))

    # —— B24–B26 清单翻页（42.2、47.2、52.2 卡片从右边滑进来）：很轻的一下“唰” ——
    for b in ('B24', 'B25', 'B26'):
        put('嗖', B[b]['t0'], lambda r: g_whoosh(r, dur=0.3, f0=2400, f1=1300, tp=0.08, tail=0.06, floor=0.25), -25, 'tex',
            label='清单翻页：' + {'B24': '微信群', 'B25': 'iPhone', 'B26': '安卓'}[b])

    # —— B27 四个按钮一个个弹出：四声“啵”（D6 E6 F♯6 A6，往上走） ——
    for k, tb in enumerate(EV['buttons']):
        put('啵', tb, lambda r, k=k: g_pop(r, (hz['D6'], hz['E6'], hz['F#6'], hz['A6'])[k]), -7, 'key',
            label='按钮弹出：' + ('工作群', '家长群', '班级群', '亲戚群')[k],
            spec=(f'结尾：按钮弹出 第 {k + 1} 个', (58.4, 58.6, 58.8, 59.0)[k], '分镜 58.2–61.2 拍：四个按钮一个一个弹出来，间隔 0.2 秒'))


# ======================================================================
# 混音
# ======================================================================
def make_ir(rng, rt60, lo, hi, dur=None, pre=0.008):
    n = int((dur or rt60 * 1.1) * SR)
    t = ts(n)
    ir = np.zeros((n, 2))
    for ch in range(2):
        z = rng.standard_normal(n)
        low = shape(z, None, 1500)
        high = z - low
        y = low * np.exp(-6.9 * t / rt60) + high * np.exp(-6.9 * t / (rt60 * 0.45))
        y = shape(y, lo, hi)
        y[: int(pre * SR)] = 0
        ir[:, ch] = y / np.sqrt(np.sum(y ** 2))
    return ir


def conv(x, ir):
    n = len(x) + len(ir) - 1
    m = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, m)
    out = np.zeros((len(x), 2))
    for ch in range(2):
        out[:, ch] = np.fft.irfft(X * np.fft.rfft(ir[:, ch], m), m)[: len(x)]
    return out


def gate_curve(t=None):
    """定格那一秒声音抽空：38.6 起 20 毫秒收到 0，到 39.6 一直是 0（混响尾巴一起收），39.6 起 10 毫秒放开（快门在 39.7）。
    最后 0.25 秒淡到 0（接回第 0 帧不爆）。music.py 也用它。"""
    if t is None:
        t = np.arange(N) / SR
    a, b = FREEZE
    g = np.ones_like(t)
    m = (t >= a) & (t < a + 0.02)
    g[m] = 1 - (t[m] - a) / 0.02
    g[(t >= a + 0.02) & (t < b)] = 0
    m = (t >= b) & (t < b + 0.01)
    g[m] = (t[m] - b) / 0.01
    end = N / SR
    g *= np.clip((end - t) / 0.25, 0, 1)
    return g


def duck_curve(x, depth_db=6.0):
    """关键音效响的时候，计数和细碎层让开：10 毫秒一块取峰值，立即压下、0.25 秒放开。"""
    blk = SR // 100
    nb = len(x) // blk + 1
    pk = np.array([np.abs(x[i * blk:(i + 1) * blk]).max() if i * blk < len(x) else 0 for i in range(nb)])
    ref = np.percentile(pk[pk > 0], 99) if np.any(pk > 0) else 1
    env = np.zeros(nb)
    r = math.exp(-0.01 / 0.25)
    for i in range(nb):
        env[i] = max(pk[i], env[i - 1] * r if i else 0)
    g = 10 ** (-depth_db * np.clip(env / (0.5 * ref), 0, 1) / 20)
    return np.interp(np.arange(len(x)), np.arange(nb) * blk + blk / 2, g)


def render():
    plan()
    rng = np.random.default_rng(SEED)
    bus = {k: np.zeros(N) for k in ('key', 'mid', 'tick', 'tex')}
    texs = np.zeros((N, 2))
    sends = {k: np.zeros(N) for k in ('room', 'hall')}
    occ = {}
    for e in EVENTS:
        # 种子 = 种类 + 画面秒数 + 同一时刻同一种类的第几个：加删别的声音不影响它
        key = (e['kind'], round(e['vis'], 3))
        e['seed'] = [SEED, zlib.crc32(f"{e['kind']}{e['vis']:.3f}".encode()), occ.get(key, 0)]
        occ[key] = occ.get(key, 0) + 1
        sig = e['sound'](np.random.default_rng(e['seed'])) * 10 ** (e['gain'] / 20)
        st = int(round((e['vis'] + e['lead'] - e['anchor']) * SR))
        e['start'] = st / SR
        e['sig'] = sig
        if st >= N:
            continue
        if st < 0:
            sig, st = sig[-st:], 0
        sig = sig[: N - st]
        m = len(sig)
        if e['cat'] == 'tex' and e['pan']:
            p = e['pan']
            texs[st:st + m, 0] += sig * math.cos((p + 1) * math.pi / 4) * 1.414
            texs[st:st + m, 1] += sig * math.sin((p + 1) * math.pi / 4) * 1.414
        else:
            bus[e['cat']][st:st + m] += sig
        snd = e['send'] if e['send'] is not None else ({'room': 0.08} if e['cat'] in ('key', 'mid') else {})
        for k, v in snd.items():
            sends[k][st:st + m] += sig * v
    irs = {'room': make_ir(rng, 0.35, 200, 5000), 'hall': make_ir(rng, 0.9, 300, 7000, pre=0.015)}
    wet = sum(conv(sends[k], irs[k]) for k in irs)
    gate = gate_curve()
    duck = duck_curve(bus['key'] + bus['mid'])
    mono = lambda x: np.stack([x, x], axis=1)
    stems = {
        'key': mono(bus['key']),
        'mid': mono(bus['mid']),
        'tick': mono(bus['tick'] * duck),
        'tex': (mono(bus['tex']) + texs) * duck[:, None],
        'wet': wet,
    }
    mix = sum(stems.values())
    mix = np.stack([shape(mix[:, ch], 35, None, order=2) for ch in range(2)], axis=1)
    mix *= gate[:, None]                                    # 高通之后再乘：定格那一秒是真的 0
    mix[: int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]
    return mix, stems


# ======================================================================
# 响度
# ======================================================================
def write_wav(path, x, dither=False, rng=None):
    x = np.clip(x, -1, 1)
    q = x * 32767
    if dither:
        q = q + (rng.random(q.shape) - rng.random(q.shape))
    data = np.clip(np.round(q), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def read_wav(path):
    with wave.open(path) as w:
        ch, sr, n = w.getnchannels(), w.getframerate(), w.getnframes()
        x = np.frombuffer(w.readframes(n), '<i2').reshape(-1, ch) / 32768.0
    return x, sr


def ebur(path, pre=''):
    """ffmpeg ebur128：整条响度 I、响度范围 LRA、真峰值，和每 0.1 秒的瞬时响度 M（400 毫秒窗）。"""
    af = (pre + ',' if pre else '') + 'ebur128=peak=true:framelog=info'
    err = subprocess.run([FF, '-hide_banner', '-nostats', '-i', path, '-af', af, '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    M = [(float(a), -120.0 if ('inf' in b or 'nan' in b) else float(b)) for a, b in re.findall(r't:\s*([\d.]+)\s+TARGET:\S+\s+LUFS\s+M:\s*(\S+)', err)]
    summ = err[err.rfind('Summary:'):]
    I = float(re.search(r'I:\s*(-?[\d.]+) LUFS', summ).group(1))
    LRA = float(re.search(r'LRA:\s*(-?[\d.]+) LU', summ).group(1))
    tp = re.search(r'True peak:\s*Peak:\s*(-?[\d.]+|-inf)', summ)
    TP = float(tp.group(1)) if tp and 'inf' not in tp.group(1) else -120.0
    return dict(I=I, LRA=LRA, TP=TP, M=np.array(M))


def loudnorm_json(path, target=None, tp=None):
    err = subprocess.run([FF, '-hide_banner', '-nostats', '-i', path, '-af',
                          f'loudnorm=I={target or TARGET}:TP={tp or TP_CEIL}:LRA=20:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', err, re.S).group(0))


def true_peak_env(x, os_=4):
    """4 倍过采样后的峰值（每个原始采样取它附近 4 个过采样点的最大值，两个声道取大的）。"""
    n = len(x)
    out = np.zeros(n)
    for ch in range(x.shape[1]):
        X = np.fft.rfft(x[:, ch])
        Y = np.zeros(n * os_ // 2 + 1, complex)
        Y[: len(X)] = X
        y = np.abs(np.fft.irfft(Y, n * os_) * os_)[: n * os_].reshape(n, os_).max(axis=1)
        out = np.maximum(out, y)
    return out


def limit(x, ceil_db):
    """前瞻限幅：按过采样峰值算每 1 毫秒要压多少，往前看 3 毫秒、放开 60 毫秒。只碰超过上限的那几下。"""
    ceil = 10 ** (ceil_db / 20)
    pkv = true_peak_env(x)
    req = np.minimum(1.0, ceil / np.maximum(pkv, 1e-9))
    blk = SR // 1000
    nb = len(x) // blk + 1
    rb = np.array([req[i * blk:(i + 1) * blk].min() if i * blk < len(x) else 1.0 for i in range(nb)])
    la = np.array([rb[i:i + 4].min() for i in range(nb)])
    g = np.ones(nb)
    rel = 1 - math.exp(-1 / 60)
    for i in range(nb):
        prev = g[i - 1] if i else 1.0
        g[i] = min(la[i], prev + (1 - prev) * rel)
    gs = np.interp(np.arange(len(x)), np.arange(nb) * blk, g)
    return x * gs[:, None], float(gs.min())


def master(mix, tmp, target=TARGET, tp_ceil=TP_CEIL):
    p = os.path.join(tmp, 'pre.wav')
    s0 = 10 ** (-1 / 20) / np.max(np.abs(mix))
    write_wav(p, mix * s0)
    I0 = ebur(p)['I'] - 20 * math.log10(s0)
    y = mix * 10 ** ((target - I0) / 20)
    gmin = 1.0
    for _ in range(5):
        tp = 20 * math.log10(true_peak_env(y).max())
        if tp <= tp_ceil - 0.25:
            break
        y, g = limit(y, tp_ceil - 0.4)
        gmin = min(gmin, g)
        write_wav(p, y)
        y = y * 10 ** ((target - ebur(p)['I']) / 20)
    return y, gmin


# ======================================================================
# 自查：从磁盘读回 sfx.wav，逐个找起音
# ======================================================================
BAND = {'震动': (900, 5000), '咚': (700, 3000), '噗': (300, 3000), '布料': (800, 6000)}


def detect(x, t, lo=700, hi=8000, back=0.05, ahead=0.06):
    """在 t 前后找起音：带通后 2 毫秒有效值（每 1 毫秒一点）；“涨” = 这一点比前 8 毫秒里最低的高多少 dB。
    t−back 到 t+ahead 里第一个涨了 6 dB 以上、而且离这一段最高点不到 18 dB 的点就是起音（前后挨得近的声音，back/ahead 收窄到
    间隔的 45%，免得量到邻居）。回 (起音秒, 涨了多少 dB)。"""
    a = max(0, int((t - 0.2) * SR))
    b = min(len(x), int((t + 0.2) * SR))
    seg = shape(x[a:b], lo, hi)
    w, hop = int(0.002 * SR), int(0.001 * SR)
    e = np.sqrt(np.convolve(seg ** 2, np.ones(w) / w, 'same'))[::hop]
    db = 20 * np.log10(e + 1e-9)
    tt = a / SR + np.arange(len(db)) * hop / SR
    lb = 8
    mn = np.array([db[max(0, i - lb):i].min() if i else db[0] for i in range(len(db))])
    rise = db - mn
    win = (tt >= t - back) & (tt <= t + ahead)
    peak = float(db[win].max())
    idx = np.where(win & (rise >= 6) & (db >= peak - 18))[0]
    if not len(idx):
        return None, round(float(rise[win].max()), 1)
    i = idx[0]
    return float(tt[i]), round(float(rise[i:i + 15].max()), 1)


NAME = {'嘀': '提示音', '笃': '嗒', '闷铃': '铃', '开盖': '开盖', '嘀嗒': '嘀嗒', '惊': '惊', '刷': '嗖', '布料': '布料'}


def write_events():
    rows = []
    for e in EVENTS:
        t = e['vis'] + e['lead']
        fr = int(math.floor(t * FPS + 0.5))
        rows.append(dict(t=round(t, 3), frame=fr, name=NAME.get(e['kind'], e['kind']), beat=beat_at(t), key=bool(e['key']),
                         label=e['label']))
    rows.sort(key=lambda r: r['t'])
    json.dump(rows, open(OUT_EVENTS, 'w'), ensure_ascii=False, indent=1)
    return rows


def check(x, I):
    """每个要查的声音：成品 sfx.wav 里量到的起音和事件表的落点差多少（毫秒、帧）；key 点 1–4 kHz 电平（check.py 口径）。"""
    mono = x.mean(axis=1)
    rows = []
    hits = sorted({round(e['vis'] + e['lead'], 4) for e in EVENTS if e['cat'] != 'tex'})
    for e in EVENTS:
        if not e['check']:
            continue
        t = e['vis'] + e['lead']
        k = hits.index(round(t, 4))
        gp = t - hits[k - 1] if k else 1.0
        gn = hits[k + 1] - t if k + 1 < len(hits) else 1.0
        lo, hi = BAND.get(e['kind'], (700, 8000))
        on, rise = detect(mono, t, lo, hi, back=min(0.05, 0.45 * gp), ahead=min(0.06, 0.45 * gn))
        # 单轨上量：只有这一个声音，放在它自己的位置上（看合成和放置有没有错；成品里被前一个声音盖住的，看这一列）
        pad = int(0.2 * SR)
        solo = np.concatenate([np.zeros(pad), e['sig'], np.zeros(pad)])
        ts_ = pad / SR + e['anchor']
        s_on, _ = detect(solo, ts_, lo, hi, back=0.03 if e['anchor'] else 0.05, ahead=0.06)
        solo_err = None if s_on is None else round((s_on - ts_) * 1000, 1)
        seg = mono[max(0, int((t - 2 / FPS) * SR)):int((t + 3 / FPS) * SR)]
        n = 2048
        seg = np.pad(seg, (0, max(0, n - len(seg))))
        fr = np.lib.stride_tricks.sliding_window_view(seg, n)[::n // 2]
        wn = np.hanning(n)
        P = (np.abs(np.fft.rfft(fr * wn, axis=1)) ** 2).mean(axis=0) * 2 / (n * np.sum(wn ** 2))
        f = np.fft.rfftfreq(n, 1 / SR)
        band = 10 * math.log10(P[(f >= 1000) & (f < 4000)].sum() + 1e-20)
        rows.append(dict(t=round(t, 3), kind=e['kind'], label=e['label'], key=bool(e['key']), spec=e['spec'],
                         onset=None if on is None else round(on, 3), err_ms=None if on is None else round((on - t) * 1000, 1),
                         solo_err_ms=solo_err, rise_db=rise, band_1_4k_db=round(band, 1)))
    return rows


def main():
    os.makedirs(PUB, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    mix, stems = render()
    ev_rows = write_events()
    with tempfile.TemporaryDirectory() as tmp:
        y, gmin = master(mix, tmp)
        write_wav(OUT_WAV, y, dither=True, rng=np.random.default_rng(SEED + 1))
    x, sr = read_wav(OUT_WAV)
    r = ebur(OUT_WAV)
    rows = check(x, r['I'])
    a, b = FREEZE
    fz = x[int((a + 0.025) * SR):int((b - 0.005) * SR)]
    fz_db = 20 * math.log10(np.sqrt(np.mean(fz ** 2)) + 1e-12)
    bad = [q for q in rows if q['err_ms'] is None or abs(q['err_ms']) > 1000 / FPS]
    bad_solo = [q for q in rows if q['solo_err_ms'] is None or abs(q['solo_err_ms']) > 1000 / FPS]
    weak = [q for q in rows if q['key'] and q['band_1_4k_db'] < r['I'] - 26]
    out = dict(file=OUT_WAV, samples=len(x), seconds=len(x) / SR, sr=sr, I=r['I'], LRA=r['LRA'], TP=r['TP'],
               limiter_min_db=round(20 * math.log10(gmin), 2), freeze_rms_dbfs=round(fz_db, 1), events=len(EVENTS), solo_off=bad_solo,
               required=[[round(e['vis'] + e['lead'], 3), e['label']] for e in EVENTS if e['req']],
               key=sum(q['key'] for q in ev_rows), checked=len(rows), off_by_more_than_1_frame=bad, key_weak_1_4k=weak, rows=rows)
    json.dump(out, open(OUT_CHECK, 'w'), ensure_ascii=False, indent=1)
    print(f"写出 {OUT_EVENTS}：{len(ev_rows)} 个落点，key {out['key']} 个")
    print(f"写出 {OUT_WAV}：{len(x)} 个采样 = {len(x) / SR:.3f} 秒，I {r['I']} LUFS，LRA {r['LRA']}，真峰值 {r['TP']} dBTP，"
          f"限幅最深 {out['limiter_min_db']} dB；定格那一秒有效值 {fz_db:.1f} dBFS")
    print(f"起音核对 {len(rows)} 个；单轨上量差超过 1 帧的 {len(bad_solo)} 个：", [(q['t'], q['label'], q['solo_err_ms']) for q in bad_solo])
    print(f"  成品里量差超过 1 帧的 {len(bad)} 个（被前后的声音盖住）：", [(q['t'], q['label'], q['err_ms'], q['solo_err_ms']) for q in bad])
    print(f"key 点 1–4 kHz 低于 I−26 的 {len(weak)} 个：", [(q['t'], q['label'], q['band_1_4k_db']) for q in weak])
    for q in rows:
        if q['spec']:
            print(f"  {q['spec'][0]:28s} 落点 {q['t']:6.2f}  量到 {q['onset']}  差 {q['err_ms']} 毫秒  高出底 {q['rise_db']} dB  1–4k {q['band_1_4k_db']}")


if __name__ == '__main__':
    main()
