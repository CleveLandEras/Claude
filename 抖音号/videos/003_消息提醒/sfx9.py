"""《消息提醒》第九版（003 横屏，长度 = timeline9.ts 的 DUR9）的音效轨。

从第八版的 sfx8.py 复制过来：合成零件、混响、响度、限幅、起音检测都原样留着，只改了读哪张时间表，按 EV9 重排了事件，
新加三个零件（翻牌 g_flip、盖章 g_stamp、手机黑掉 g_off）。每个声音用 numpy 合成，按时间表的秒数放上去，整条量响度再统一调。
不用曲库、采样、第三方账号。

  /Users/decheng.huang/Documents/dy/.venv/bin/python -I /Users/decheng.huang/Documents/dy/videos/003_消息提醒/sfx9.py
  （只出音效轨；要配乐和混音跑 music9.py，它会先调这里的 main）

读：studio/src/videos/003/timeline9.ts（FPS9、DUR9、BEATS9、SC9、EV9；只读，不改）
写：studio/public/003/v9/sfx.wav（48 kHz、16 bit、双声道；整条 −19 LUFS，真峰值 ≤ −1.5 dBTP）
    studio/public/003/v9/sfx_events.json（每个音效：t 起音秒、frame 帧、name、beat 拍、key、duck 配乐让不让、label 说明）
（只为试跑：环境变量 SOUND9_TL 换一张时间表、SOUND9_OUT 换输出文件夹；平时不用设。）

秒数一律从 EV9、SC9 读，脚本里不写死。时间表改了只要重跑 music9.py。
实验那段（SC9.fitz；EV9 的 fitzIn、pile、batches、calm、labels、selfTag、dark、anxious、label3、fitzOut）缺哪个键就跳过哪个声音。

和第八版不同：
  - EV9.stamp 红章“过了”：低、闷的一下（g_stamp），表示“晚了”，配乐让开；
  - EV9.nextDay 大字钟翻牌（g_flip）；EV9.chips 三张小卡钉住（g_pin ＋ 有音高的小“笃”）；EV9.cardIn 小卡进来；EV9.preOut 页面滑走；
    EV9.doneTag、tagNo、cut、howTag、tag3 贴纸都是“啵”；EV9.bell2 静音铃（大调里用 F♯5）；
  - EV9.silentMsg 照第八版：没有手机声，只一下很轻的闷“噗”（−30 dB）；EV9.quiet 那段（群里刷屏、手机不响）一个手机声都没有。

有音高的声音都在配乐的调里：SC9.desk2 开头以前 D 小调（D F A、B♭、Gm），以后 D 大调（D F♯ A，G、Bm）。music9.py 逐个查和弦，
查到不在和弦里的，把那一格和弦换成主和弦（小调 Dm、大调 D）。
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
TL_PATH = os.environ.get('SOUND9_TL') or os.path.join(ROOT, 'studio', 'src', 'videos', '003', 'timeline9.ts')
PUB = os.environ.get('SOUND9_OUT') or os.path.join(ROOT, 'studio', 'public', '003', 'v9')
OUT_WAV = os.path.join(PUB, 'sfx.wav')
OUT_EVENTS = os.path.join(PUB, 'sfx_events.json')
FF = imageio_ffmpeg.get_ffmpeg_exe()


def load_tl():
    """读 timeline9.ts：FPS9、DUR9、BEATS9（id、t0、t1、有没有字幕、part）、SC9、EV9（JS 对象，去掉注释、给键加引号后按 JSON 读）。"""
    s = open(TL_PATH, encoding='utf-8').read()
    fps = float(re.search(r'export const FPS9 = ([\d.]+)', s).group(1))
    dur = float(re.search(r'export const DUR9 = ([\d.]+)', s).group(1))
    beats = [dict(id=a, t0=float(b), t1=float(c), sub=d.strip() != '[]', part=p)
             for a, b, c, d, p in re.findall(r"\{id: '(\w+)', t0: ([\d.]+), t1: ([\d.]+), sub: (\[.*?\])(?:, part: '(\w+)')?\}", s)]

    def obj(name):
        body = s[s.index(f'export const {name} = {{') + len(f'export const {name} = '):]
        body = body[:body.index('\n};') + 2]
        body = re.sub(r'//[^\n]*', '', body)
        body = re.sub(r'(\w+)\s*:', r'"\1":', body)
        body = re.sub(r',(\s*[}\]])', r'\1', body)
        return json.loads(body)

    return dict(fps=fps, dur=dur, beats=beats, ev=obj('EV9'), sc=obj('SC9'))


TLD = load_tl()
SR = 48000
FPS = int(TLD['fps'])
NF = int(round(TLD['dur'] * FPS))      # 帧数（DUR9 × FPS9）
SPF = SR // FPS                         # 每帧 1600 个采样
N = NF * SPF                            # 采样数，正好 DUR9 秒
BEATS = TLD['beats']
B = {b['id']: b for b in BEATS}
EV = TLD['ev']
SC = TLD['sc']
TARGET = -19.0                          # sfx.wav 单独的整条响度（mix.wav 由 music9.py 另调到 −14）
TP_CEIL = -1.5
SEED = 3009
SHAKE = 8 / FPS                         # 手机响一下，画面抖 8 帧，震动声也是 8 帧长（照第四版）

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
# 第八版新加的零件
# ======================================================================
HZ.update({'G5': 783.99, 'B5': 987.77, 'C#6': 1108.73, 'G6': 1567.98})


def g_tap(rng, f0=2600.0):
    """手指点屏幕：很短的一下“嗒”（玻璃面上的指尖：2.6 kHz 一带的小模态 8 毫秒＋1.5–8 kHz 的接触声 1 毫秒），底下一点 300 Hz 的指肚闷声。"""
    n = int(0.06 * SR)
    f0 *= jit(rng, 30)
    y = norm(modal(n, [(f0, 1, 0.008), (1.6 * f0, 0.4, 0.004)], rng, att=0.0002))
    y = y + 0.8 * norm(contact(n, rng, 1500, 8000, 0.001))
    y = y + 0.25 * norm(modal(n, [(300 * jit(rng, 30), 1, 0.006)], rng))
    return norm(fades(y, 0.0002, 0.005))


def g_switch(rng, on=True):
    """开关拨动：小圆钮滑过去（25 毫秒的摩擦声，拨开往上扫、拨灰往下扫）＋到头一下有音高的小“笃”（拨开 D6，拨灰 D5）。"""
    n = int(0.25 * SR)
    t = ts(n)
    sl = 0.025
    u = np.clip(t / sl, 0, 1)
    fc = 1800 * 2 ** u if on else 3600 * 0.5 ** u
    slide = tv_noise(n, rng, fc, 1.2) * np.clip(t / 0.003, 0, 1) * np.clip((sl - t) / 0.006, 0, 1)
    y = 0.35 * norm(slide)
    _mixin(y, g_tok(rng, HZ['D6'] if on else HZ['D5']), int(sl * SR), 1.0)
    return norm(fades(y, 0.0003, 0.01))


def g_lock(rng, f0=2200.0):
    """上锁的“咔”：锁舌先一下高的“咔”（f0），20 毫秒后一下低一点、厚一点的“嗒”（0.62 f0，扣上），带一点金属小亮声。"""
    n = int(0.2 * SR)
    y = np.zeros(n)
    _mixin(y, g_click(rng, f0, 0.012, 0.1), 0, 0.8)
    _mixin(y, g_click(rng, f0 * 0.62, 0.025, 0.12), int(0.02 * SR), 1.0)
    _mixin(y, g_glint(rng, f0 * 2.1, 0.02), int(0.02 * SR), 0.15)
    y = np.tanh(1.6 * norm(y)) / np.tanh(1.6)
    return norm(fades(y))


def g_bounce(rng):
    """第 5 个头像被弹出去：一下“嘣”——弹簧似的音高先往上蹿（350 → 900 Hz，50 毫秒）再带 22 Hz 的颤、散掉，
    起头一下指节敲（g_knock），尾上一点往外飞的嗖。"""
    n = int(0.5 * SR)
    t = ts(n)
    u = np.clip(t / 0.05, 0, 1)
    f = 350 * (900 / 350) ** (u ** 0.6) * (1 + 0.06 * np.sin(2 * np.pi * 22 * t) * np.exp(-t / 0.15))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.3 * np.sin(2 * ph + 0.5)) * np.exp(-t / 0.09) * (1 - np.exp(-t / 0.002))
    y = norm(tone)
    _mixin(y, g_knock(rng, 1300, 0.04), 0, 0.8)
    _mixin(y, g_whoosh(rng, dur=0.22, f0=1500, f1=3800, tp=0.06, tail=0.05, floor=0.3), int(0.03 * SR), 0.35)
    y = np.tanh(1.5 * norm(y)) / np.tanh(1.5)
    return norm(fades(y))


def g_unrung(rng):
    """开了免打扰，消息进来不提醒：隔着衣袋似的一下很闷的“噗”（700 Hz 的小气泡低通到 900 Hz），几乎听不出——“本来该响，没响”。"""
    y = np.concatenate([g_bubble(rng, 700, 0.08), np.zeros(int(0.05 * SR))])
    return norm(fades(shape(y, 150, 900, order=2)))


# ======================================================================
# 第九版新加的零件
# ======================================================================
HZ.update({'C6': 1046.50})


def g_flip(rng, span):
    """翻牌（大字钟翻到“第二天 9:00”）：松开那一下小“嗒”（2.4 kHz），翻过去带起的一口风（1.5 → 3.2 kHz，越来越响），
    中间三片小牌子轻轻擦过，span 秒时牌子落下：一下厚一点的“啪嗒”（1.3 kHz 的塑料 + 600 Hz 的壳子）。"""
    n = int((span + 0.25) * SR)
    y = np.zeros(n)
    _mixin(y, g_click(rng, 2400, 0.012, 0.08), 0, 0.75)
    _mixin(y, g_swell(rng, span, f0=1500, f1=3200, tail=0.03, floor=0.3), 0, 0.3)
    for k, u in enumerate((0.3, 0.55, 0.75)):
        _mixin(y, g_click(rng, 3000 + 300 * k, 0.006, 0.05), int(u * span * SR), 0.25)
    _mixin(y, g_click(rng, 1300, 0.03, 0.15), int(span * SR), 1.0)
    _mixin(y, norm(modal(int(0.15 * SR), [(600 * jit(rng, 15), 1, 0.03), (940, 0.4, 0.02)], rng)), int(span * SR), 0.5)
    y = np.tanh(1.6 * norm(y)) / np.tanh(1.6)
    return norm(fades(y))


def g_stamp(rng):
    """盖章“过了”：低、闷的一下“咚”——橡皮章拍在纸上、压到桌面。130 → 70 Hz 往下掉的闷响（饱和一下），一下 300–1800 Hz 的纸面
    “啪”（12 毫秒），叠一下 650 Hz 的指节敲木头（手机外放靠它）；整体 2.8 kHz 低通，没有亮声。"""
    n = int(0.5 * SR)
    t = ts(n)
    fb = (70 + 60 * np.exp(-t / 0.02)) * jit(rng, 20)
    body = np.sin(2 * np.pi * np.cumsum(fb) / SR) * np.exp(-t / 0.09) * (1 - np.exp(-t / 0.0015))
    body = np.tanh(2.0 * body) / np.tanh(2.0)
    slap = noise(n, rng, 300, 1800, tilt=-0.4) * np.exp(-t / 0.012) * (1 - np.exp(-t / 0.0004))
    y = 0.8 * norm(body) + 0.7 * norm(slap)
    _mixin(y, g_knock(rng, 650, 0.06), int(0.002 * SR), 1.0)
    y = shape(y, 40, 2800, order=2)
    y = np.tanh(1.6 * norm(y)) / np.tanh(1.6)
    return norm(fades(y))


def g_off(rng):
    """手机黑掉：电源键一下小“咔”（3 kHz），屏幕熄掉的一声往下沉的“嘟↓”（560 → 150 Hz，0.16 秒，2 kHz 低通），尾上一点静电“嘶”散掉。"""
    n = int(0.45 * SR)
    t = ts(n)
    y = np.zeros(n)
    _mixin(y, g_click(rng, 3000, 0.01, 0.08), 0, 0.7)
    u = np.clip(t / 0.16, 0, 1)
    ph = 2 * np.pi * np.cumsum(560 * (150 / 560) ** (u ** 0.7)) / SR
    tone = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.exp(-t / 0.12) * (1 - np.exp(-t / 0.003))
    y += norm(shape(tone, 100, 2000))
    y += 0.12 * norm(noise(n, rng, 3000, 9000) * np.exp(-t / 0.08) * np.clip(t / 0.005, 0, 1))
    return norm(fades(y))


def _geom(a, b, n, last_ratio):
    """在 a–b 里排 n 个点，越来越密：相邻间隔每次乘同一个比，最后一个间隔是第一个的 last_ratio 倍。"""
    r = last_ratio ** (1 / (n - 2))
    gaps = [r ** k for k in range(n - 1)]
    sc = (b - a) / sum(gaps)
    out = [a]
    for g in gaps:
        out.append(out[-1] + g * sc)
    return out


def _run_ticks(a, b, d0=0.06, k=0.92, dmin=0.02):
    """计数狂涨的滴答：间隔 d0 起、每下乘 k、最短 dmin（一下比一下密）。"""
    out, t, d = [], a, d0
    while t < b - 0.005:
        out.append(t)
        t += d
        d = max(dmin, d * k)
    return out


BANNER_N = 22
BANNERS = _geom(EV['burst'][0], EV['burst'][1], BANNER_N, 0.3)    # EV9.burst 里，间隔越来越密
TICKS = _run_ticks(*EV['countRun'])                                # EV9.countRun 里，间隔 60 → 20 毫秒


# ======================================================================
# 排事件
# ======================================================================
EVENTS = []


def put(kind, vis, sound, gain, cat='mid', lead=0.0, anchor=0.0, label='', send=None, pan=0.0, key=False, spec=None, check=True,
        req=False, duck=None, notes=()):
    """同 sfx.py 的 put。另加：duck（配乐要不要为它让开，默认 = key）；notes（有音高的声音：[(离落点几秒, 音名), ...]，配乐查和弦用）。
    spec = (要的声音, EV9 的秒, 出处)。"""
    k = key or cat == 'key'
    EVENTS.append(dict(kind=kind, vis=float(vis), lead=lead, anchor=anchor, sound=sound, gain=gain, cat=cat, label=label or kind,
                       send=send, pan=pan, key=k, spec=spec, check=check and cat != 'tex', req=req or spec is not None,
                       duck=k if duck is None else duck, notes=list(notes)))


FITZ_KEYS = ('fitzIn', 'pile', 'batches', 'calm', 'labels', 'selfTag', 'dark', 'anxious', 'label3', 'fitzOut')


def has(*ks):
    return all(k in EV for k in ks)


def plan():
    """按 EV9 排。秒数全从 EV、SC 取；实验那段的键缺了就跳过。"""
    EVENTS.clear()
    H = HZ
    sk = SHAKE
    W = lambda d=0.3, a=1300, b=2700, tp=0.08: (lambda r: g_whoosh(r, dur=d, f0=a, f1=b, tp=tp, tail=0.05, floor=0.5))

    def ring(t, label, chime, notes, vg=-8, cg=-9, pulses=None, spec=None, duck=True, warm=None):
        """手机响一下 = 震（默认 8 帧）＋提示音；warm 给音名时底下再垫一声暖铃。"""
        p = pulses or [(0, sk)]
        put('震动', t, lambda r, p=p: g_vibrate(r, p), vg, 'key', label=label + '：震', spec=spec, duck=duck)
        put('提示音', t, chime, cg, 'key', label=label + '：提示音', send={'hall': 0.12}, req=True, duck=duck, notes=notes)
        if warm:
            put('叮', t, lambda r, f=H[warm]: g_warm(r, f), cg - 5, 'mid', label=label + '：暖铃垫底', send={'hall': 0.2}, req=True,
                check=False, duck=duck, notes=[(0, warm)])

    def whoosh(t, label, gain=-25, spec=None, check=True, **kw):
        put('嗖', t, W(**kw), gain, 'mid', label=label, duck=False, check=check, spec=(spec, t, label) if spec else None)

    def tap(t, label, spec, sw=None):
        put('点击', t, lambda r: g_tap(r), -14, 'mid', label=label + '：点', duck=False, spec=(spec, t, label))
        if sw is not None:
            put('开关', t + 0.06, lambda r, on=sw: g_switch(r, on), -15, 'mid', label=label + ('：开关拨开（绿）' if sw else '：开关拨灰'),
                duck=False, req=True, notes=[(0.025, 'D6' if sw else 'D5')])

    def pop(t, label, spec, f='D6', gain=-13):
        put('啵', t, lambda r, f=H[f]: g_pop(r, f), gain, 'mid', label=label, duck=False, spec=(spec, t, label), notes=[(0, f)])

    def tok(t, label, spec=None, f='D6', gain=-17):
        put('嗒', t, lambda r, f=H[f]: g_tok(r, f), gain, 'mid', label=label, duck=False, spec=(spec, t, label) if spec else None,
            notes=[(0, f)])

    # —— 钩子：四个 App 依次响（EV9.buzz，照第八版），中间贴纸“怎么查，看简介”一下“啵” ——
    apps = [('限时秒杀', lambda r: g_chime(r, [H['A5'], H['D6']], 0.075, 'square', 0.12, [0.8, 1.0]), [(0, 'A5'), (0.075, 'D6')],
             [(0, sk)]),
            ('热点新闻', lambda r: g_chime(r, [H['F6'], H['D6']], 0.09, 'wood', 0.16), [(0, 'F6'), (0.09, 'D6')],
             [(0, 0.11), (0.15, sk - 0.15)]),
            ('工作群', lambda r: g_chime(r, [H['D6'], H['A5']], 0.16, 'glass', 0.3, [1.0, 0.8]), [(0, 'D6'), (0.16, 'A5')],
             [(0, 0.1), (0.14, sk - 0.14)]),
            ('家长群', lambda r: g_chime(r, [H['A5'], H['D6'], H['F6']], 0.07, 'glass', 0.18), [(0, 'A5'), (0.07, 'D6'), (0.14, 'F6')],
             [(0, 0.07), (0.1, 0.07), (0.2, sk - 0.2)])]
    for k, (t, (name, ch, nt, pl)) in enumerate(zip(EV['buzz'], apps)):
        ring(t, f'手机响 {k + 1}/4（{name}，计数 {k + 1}）', ch, nt, vg=-8 + k, cg=-9, pulses=pl,
             spec=(f'手机响 buzz 第 {k + 1} 下（{name}）', t, f'EV9.buzz[{k}]'))
    if has('howTag'):
        pop(EV['howTag'], '贴纸“怎么查，看简介”弹出', '贴纸 howTag', gain=-14)

    # —— 喷满、计数狂涨、震散（照第八版）；推镜头底下一层往里收的“嗖——”，正好在 camPush 结束时到顶 ——
    c0, c1 = EV['countRun']
    sh = EV['shatter'][0]
    put('震动', c0, lambda r: g_vibrate(r, [(0.0, sh - c0)], motor=180), -12, 'mid', label='计数狂涨，手机一直抖（到震散为止）',
        req=True, check=False)
    for k, t in enumerate(BANNERS):
        u = k / (len(BANNERS) - 1)
        put('喷出', t, lambda r, u=u: g_banner(r, u), -15 + 2 * u, 'mid', label=f'横幅喷出 {k + 1}/{len(BANNERS)}', req=True,
            spec=(f'喷满 burst（{len(BANNERS)} 条横幅的第 1 条）', t, 'EV9.burst[0]') if k == 0 else None)
    for k, t in enumerate(TICKS):
        u = (t - c0) / (c1 - c0)
        put('滴答', t, lambda r, u=u: g_tick(r, 2100 + 1300 * u), -15 + 3 * u, 'tick', label=f'计数滴答 {k + 1}/{len(TICKS)}', req=True,
            spec=(f'计数狂涨 countRun（{len(TICKS)} 下的第 1 下）', t, 'EV9.countRun[0]') if k == 0 else None)
    if has('camPush'):
        p0, p1 = EV['camPush']
        put('嗖', p0, lambda r, s_=p1 - p0: g_swell(r, s_, f0=700, f1=3800, tail=0.05, floor=0.35), -24, 'tex', label='镜头推近')
    put('碎响', sh, lambda r: g_shatter(r), -5, 'key', label='震散（3 帧内）', send={'hall': 0.15}, spec=('震散 shatter', sh, 'EV9.shatter[0]'))

    # —— 群聊：放大进来、往上滚、两条要紧的亮暖黄（暖铃 F5、A5） ——
    whoosh(EV['chatIn'][0], '群聊放大进来', spec='嗖：群聊进 chatIn', a=1200, b=2600, tp=0.1)
    s0, s1 = EV['chatScroll']
    put('嗖', s0, lambda r: g_whoosh(r, dur=s1 - s0 + 0.05, f0=2600, f1=1500, tp=0.12, tail=0.2, floor=0.4), -29, 'tex', label='群消息往上滚')
    for k in range(8):
        x = 1 - (1 - (k + 0.5) / 8) ** (1 / 3)
        put('滴答', s0 + (s1 - s0) * x, lambda r: g_tick(r, 3000), -32, 'tex', label='滚过的消息')
    put('叮', EV['keyA'], lambda r: g_warm(r, H['F5']), -12, 'mid', label='“@所有人 周五开家长会”亮暖黄', send={'hall': 0.18},
        notes=[(0, 'F5')])
    put('叮', EV['keyB'], lambda r: g_warm(r, H['A5']), -13, 'mid', label='“王老师：明天带水彩笔”亮暖黄', send={'hall': 0.18},
        notes=[(0, 'A5')])

    # —— ① 不关：贴纸“啵”；五条一条条弹，每条都震＋提示音（配乐不让，最满）；往后一瘫：布料 ——
    pop(EV['tagNo'], '贴纸“① 不关”弹出', '贴纸 tagNo', gain=-14)
    for k, t in enumerate(EV['noisy']):
        ring(t, f'不关：又一条（{k + 1}/5）', lambda r: g_chime(r, [H['D6'], H['A5']], 0.11, 'glass', 0.18, [1.0, 0.75]),
             [(0, 'D6'), (0.11, 'A5')], vg=-8 + 0.5 * k, cg=-11 + 0.5 * k, pulses=[(0, 0.2)], duck=False,
             spec=(f'手机响 noisy 第 {k + 1} 下', t, f'EV9.noisy[{k}]'))
    sl0, sl1 = EV['slump']
    put('布料', sl0, lambda r: g_rustle(r, sl1 - sl0 + 0.1, attack=0.03), -20, 'mid', label='你往后一瘫', duck=False, check=False)

    # —— ② 全关：切（刷屏那几条撤掉，很轻的嗖）＋贴纸换“② 全关”（啵）；挂静音铃（捂住的铃 F5）；
    #    silentMsg 王老师那条：故意没有手机声，只一下很闷很轻的“噗”；贴纸“没提醒”；第二天：大字钟翻牌；拿起手机；红章“过了”：低、闷 ——
    cut = EV['cut']
    put('嗖', cut, W(d=0.18, a=2600, b=1400, tp=0.03), -29, 'tex', label='刷屏的几条撤掉')
    pop(cut, '贴纸换成“② 全关”', '贴纸 cut', gain=-14)
    put('铃', EV['bellOn'], lambda r: g_mute_bell(r, H['F5']), -10, 'mid', label='群名旁挂上静音铃', notes=[(0, 'F5')],
        spec=('静音铃 bellOn', EV['bellOn'], 'EV9.bellOn'))
    put('没响', EV['silentMsg'], lambda r: g_unrung(r), -30, 'mid', label='王老师：明早8点前交表（不带 @）：故意没有手机声，只一下很闷很轻的“噗”',
        duck=False, spec=('silentMsg：故意没有手机声（只一下很轻的闷“噗”）', EV['silentMsg'], 'EV9.silentMsg'))
    pop(EV['silentTag'], '贴纸“没提醒”弹出', '贴纸“没提醒” silentTag', gain=-14)
    n0, n1 = EV['nextDay']
    put('翻牌', n0, lambda r, s_=n1 - n0: g_flip(r, s_), -11, 'mid', label='大字钟翻成“第二天 9:00”', duck=False,
        spec=('翻牌 nextDay', n0, 'EV9.nextDay[0]'))
    put('布料', EV['pickUp'], lambda r: g_rustle(r, 0.35, attack=0.03), -23, 'mid', label='拿起手机看', duck=False, check=False)
    put('盖章', EV['stamp'], lambda r: g_stamp(r), -7, 'key', label='红章“过了”盖下来（低、闷：晚了）', send={'room': 0.15}, duck=True,
        spec=('盖章 stamp（低、闷）', EV['stamp'], 'EV9.stamp'))

    # —— 实验（时间表里有才排；最终版已删） ——
    if has('fitzIn'):
        whoosh(EV['fitzIn'][0], '实验页进来', spec='嗖：实验页进 fitzIn', d=0.34, a=1200, b=2600, tp=0.1)
    if has('pile'):
        for k, t in enumerate(EV['pile']):
            tok(t, f'通知攒进格子 {k + 1}/{len(EV["pile"])}', spec=f'攒通知 pile[{k}]', f=('A5', 'D6', 'F6', 'A6')[k % 4], gain=-22)
    if has('batches'):
        for k, t in enumerate(EV['batches']):
            put('嗖', t, W(d=0.25, a=2600, b=900, tp=0.05), -22, 'mid', label=f'到点一次推下来 {k + 1}/{len(EV["batches"])}', duck=False,
                spec=(f'一次推下来 batches[{k}]', t, f'EV9.batches[{k}]'))
            put('提示音', t + 0.12, lambda r: g_chime(r, [H['D6'], H['F6']], 0.08, 'glass', 0.2, [0.9, 1.0]), -15 + k, 'mid',
                label=f'推下来那一批：提示音（跟屏幕闪）{k + 1}', send={'hall': 0.12}, req=True, duck=True, notes=[(0, 'D6'), (0.08, 'F6')])
    if has('calm'):
        put('噗', EV['calm'], lambda r: g_poof(r), -27, 'mid', label='人松下来（呼一口气）', duck=False, check=False)
    if has('labels'):
        for k, t in enumerate(EV['labels']):
            pop(t, ('“更专注”', '“压力更小”')[k % 2] + ' 弹出', f'字 labels[{k}]', f=('A5', 'C6')[k % 2], gain=-15)
    if has('selfTag'):
        pop(EV['selfTag'], '贴纸“自评”弹出', '贴纸 selfTag', f='F6', gain=-15)
    if has('dark'):
        put('黑屏', EV['dark'], lambda r: g_off(r), -13, 'mid', label='手机黑掉：一条不收', duck=False, spec=('黑屏 dark', EV['dark'], 'EV9.dark'))
    if has('anxious'):
        for k, d in enumerate((0, 0.85, 1.7)):
            put('布料', EV['anxious'] + d, lambda r: g_rustle(r, 0.3, attack=0.03), -27, 'tex', label=f'探头看手机 {k + 1}')
    if has('label3'):
        pop(EV['label3'], '“更焦虑”弹出', '字 label3', f='Bb5', gain=-14)
    if has('fitzOut'):
        whoosh(EV['fitzOut'][0], '实验页退出', gain=-28, check=False, d=0.3, a=2700, b=1300)

    # —— ③ 留人：贴纸“啵”；静音铃（大调里是 F♯5）；三张小卡飞到手机旁钉住（图钉“咔”＋小“笃” D6、F♯6、A6）；
    #    回到锁屏；quiet 那段群里还在进，一个手机声都没有；keyRing 王老师那条：全片最“对”的一声（照第八版：震轻、提示音 A5–D6 长、暖铃 F♯5） ——
    pop(EV['tag3'], '贴纸“③ 留人”弹出', '贴纸 tag3', gain=-14)
    put('铃', EV['bell2'], lambda r: g_mute_bell(r, H['F#5']), -11, 'mid', label='群名旁又挂上静音铃', notes=[(0, 'F#5')],
        spec=('静音铃 bell2', EV['bell2'], 'EV9.bell2'))
    for k, t in enumerate(EV['chips']):
        nm = ('“王老师”', '“领导”', '“@所有人”')[k % 3]
        put('嗖', t, lambda r: g_flick(r), -26, 'tex', label=nm + ' 小卡飞来')
        put('钉住', t, lambda r: g_pin(r), -15, 'mid', label=nm + ' 小卡钉住', duck=False, spec=(f'小卡钉住 chips[{k}]', t, f'EV9.chips[{k}]'))
        tok(t, nm + ' 小卡（音高）', f=('D6', 'F#6', 'A6')[k % 3], gain=-23)
    put('布料', EV['lockIn'], lambda r: g_rustle(r, 0.35), -28, 'tex', label='手机回到锁屏（人坐回去）')
    kr = EV['keyRing']
    ring(kr, '王老师：明早 8 点前交表（该响的时候响）', lambda r: g_chime(r, [H['A5'], H['D6']], 0.17, 'glass', 0.45, [0.85, 1.0]),
         [(0, 'A5'), (0.17, 'D6')], vg=-10, cg=-7, warm='F#5', spec=('手机响 keyRing（全片最“对”的一声）', kr, 'EV9.keyRing'))
    put('布料', EV['nod'][0], lambda r: g_rustle(r, 0.35), -27, 'tex', label='点头')

    # —— 设置页：先亮“设好的样子”（贴纸啵），那页滑走后从头教 ——
    whoosh(EV['setIn'][0], '群聊设置页进来（设好的样子）', spec='嗖：设置页进 setIn', d=0.34, a=1200, b=2600, tp=0.1)
    pop(EV['doneTag'], '贴纸“设好的样子”弹出', '贴纸 doneTag')
    whoosh(EV['preOut'][0], '设好的那页滑走', spec='嗖：设好的那页滑走 preOut', d=0.3, a=2700, b=1300, tp=0.06)
    tap(EV['tapMute'], '点“消息免打扰”', '点击 tapMute（后跟开关拨开）', sw=True)
    put('嗖', EV['rowsOut'][0], W(d=0.3, a=1500, b=2600), -29, 'tex', label='滑出两行')
    put('亮', EV['hl1'], lambda r: g_glint(r, 3600, 0.03), -27, 'tex', label='黄框到第一行')
    tap(EV['tapFold'], '点“折叠该聊天”', '点击 tapFold（后跟开关拨灰）', sw=False)
    pop(EV['foldTag'], '贴纸弹出（折叠关着）', '贴纸 foldTag')
    put('亮', EV['hl2'], lambda r: g_glint(r, 3600, 0.03), -27, 'tex', label='黄框移到第二行')
    tap(EV['tapRow2'], '点第二行', '点击 tapRow2')
    whoosh(EV['subIn'][0], '“以下消息仍通知”页盖进来', spec='嗖：子页进 subIn', d=0.34, a=1300, b=2700)
    for k, t in enumerate(EV['sw']):
        put('亮', t, lambda r, k=k: g_glint(r, 3400 + 300 * k, 0.025), -28, 'tex', label='开关亮框')
    tap(EV['tapAll'], '点“@所有人”', '点击 tapAll（后跟开关拨开）', sw=True)
    put('嗖', EV['cardIn'], W(d=0.22, a=1300, b=2600, tp=0.05), -26, 'mid', label='右边小卡进来（“关注的群成员”）', duck=False,
        spec=('嗖：小卡进来 cardIn', EV['cardIn'], 'EV9.cardIn'))
    put('嗖', EV['cardIn'], lambda r: g_flick(r), -27, 'tex', label='小卡的纸声')
    tap(EV['tapAdd'], '点“添加成员 ＋”', '点击 tapAdd')
    for k, t in enumerate(EV['adds']):
        tok(t, ('“王老师”', '“领导”')[k % 2] + ' 头像落位', spec=f'头像落位 adds[{k}]')
    for k, t in enumerate(EV['adds2']):
        tok(t, ('“王老师”', '“领导”')[k % 2] + ' 头像落位（小卡里）', spec=f'头像落位 adds2[{k}]', gain=-19)
    for k, t in enumerate(EV['allBanners']):
        ring(t, ('@所有人 横幅（吵的）', '@所有人 横幅（要紧的）')[k % 2],
             lambda r: g_chime(r, [H['D6'], H['A5']], 0.16, 'glass', 0.3, [1.0, 0.8]), [(0, 'D6'), (0.16, 'A5')],
             vg=-8, cg=-9 + k, warm='F#5' if k else None, spec=(f'手机响 allBanners 第 {k + 1} 下', t, f'EV9.allBanners[{k}]'))
    whoosh(EV['subOut'][0], '子页退回设置页', spec='嗖：子页出 subOut', d=0.3, a=2700, b=1300)
    put('嗖', EV['morph2'][0], W(d=0.25, a=1800, b=3000), -30, 'tex', label='第二行变成虚线“？”')
    put('嗖', EV['slotsIn'][0], W(d=0.25, a=1500, b=2800), -30, 'tex', label='4 个空位出来')
    for k, t in enumerate(EV['five'][:4]):
        tok(t, f'头像 {k + 1}/5 挤进空位', spec=f'头像落位 five[{k}]', gain=-17 + 0.7 * k)
    put('弹开', EV['bounce'], lambda r: g_bounce(r), -9, 'key', label='第 5 个头像被弹出去', duck=True,
        spec=('第 5 个被弹出 bounce', EV['bounce'], 'EV9.bounce'))
    tap(EV['tapMuteOff'], '免打扰拨回', '点击 tapMuteOff（后跟开关拨灰）', sw=False)
    pop(EV['noTag'], '贴纸“开了的，关掉”弹出', '贴纸 noTag')
    whoosh(EV['setOut'][0], '设置页退出', spec='嗖：设置页出 setOut', d=0.34, a=2700, b=1200)

    # —— 测一下（照第八版） ——
    ring(EV['testMsg'], '小李 @你 测试一下', lambda r: g_chime(r, [H['D6'], H['A5']], 0.16, 'glass', 0.3, [1.0, 0.8]), [(0, 'D6'), (0.16, 'A5')],
         vg=-8, cg=-9, spec=('手机响 testMsg', EV['testMsg'], 'EV9.testMsg'))
    put('确认', EV['testOk'], lambda r: g_chime(r, [H['D6'], H['F#6'], H['A6']], 0.06, 'glass', 0.2, [0.7, 0.85, 1.0]), -12, 'mid',
        label='测试通过：打勾（上行确认音 D6–F♯6–A6）', send={'hall': 0.15}, duck=True,
        spec=('打勾 testOk（上行确认音）', EV['testOk'], 'EV9.testOk'), notes=[(0, 'D6'), (0.06, 'F#6'), (0.12, 'A6')])
    pop(EV['testTag'], '贴纸“步骤看简介”弹出', '贴纸 testTag')

    # —— 清单：压暗（很轻往下的嗖）、清单屏进来、截图快门；结尾页进来 ——
    if has('dim'):
        put('嗖', EV['dim'][0], W(d=0.35, a=2200, b=800, tp=0.1), -31, 'tex', label='画面压暗')
    whoosh(EV['listIn'][0], '清单屏进来', spec='嗖：清单屏进 listIn', d=0.3, a=1300, b=2700, gain=-27)
    put('快门', EV['shot'], lambda r: g_shutter(r), -4, 'key', label='截图快门', send={'room': 0.12}, spec=('截图快门 shot', EV['shot'], 'EV9.shot'))
    whoosh(EV['endIn'][0], '结尾页进来', spec='嗖：结尾页进 endIn', d=0.34, a=1300, b=2600)


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
    """没有定格：只在最后 0.25 秒淡到 0（接回第 0 帧不爆）。music9.py 也用它。"""
    if t is None:
        t = np.arange(N) / SR
    return np.clip((N / SR - t) / 0.25, 0, 1)




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


BAND.update({'点击': (1200, 8000), '开关': (1000, 8000), '没响': (150, 1200), '弹开': (300, 5000),
             '盖章': (300, 4000), '黑屏': (300, 5000), '钉住': (1200, 8000), '翻牌': (1000, 8000)})
NAME = {'笃': '嗒', '刷': '嗖'}


def write_events():
    rows = []
    for e in EVENTS:
        t = e['vis'] + e['lead']
        fr = int(math.floor(t * FPS + 0.5))
        rows.append(dict(t=round(t, 3), frame=fr, name=NAME.get(e['kind'], e['kind']), beat=beat_at(t), key=bool(e['key']),
                         duck=bool(e['duck']), label=e['label']))
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
    """出 sfx.wav、sfx_events.json；从磁盘读回 sfx.wav 逐个找起音。回核对结果（music9.py 拿它写自查，不另存文件）。"""
    os.makedirs(PUB, exist_ok=True)
    mix, stems = render()
    ev_rows = write_events()
    with tempfile.TemporaryDirectory() as tmp:
        y, gmin = master(mix, tmp)
        write_wav(OUT_WAV, y, dither=True, rng=np.random.default_rng(SEED + 1))
    x, sr = read_wav(OUT_WAV)
    r = ebur(OUT_WAV)
    rows = check(x, r['I'])
    bad = [q for q in rows if q['err_ms'] is None or abs(q['err_ms']) > 1000 / FPS]
    bad_solo = [q for q in rows if q['solo_err_ms'] is None or abs(q['solo_err_ms']) > 1000 / FPS]
    out = dict(file=OUT_WAV, samples=len(x), seconds=len(x) / SR, sr=sr, I=r['I'], LRA=r['LRA'], TP=r['TP'],
               limiter_min_db=round(20 * math.log10(gmin), 2), events=len(EVENTS), key=sum(q['key'] for q in ev_rows),
               checked=len(rows), off_by_more_than_1_frame=bad, solo_off=bad_solo, rows=rows,
               required=[[round(e['vis'] + e['lead'], 3), e['label']] for e in EVENTS if e['req']])
    print(f"写出 {OUT_EVENTS}：{len(ev_rows)} 个落点，key {out['key']} 个")
    print(f"写出 {OUT_WAV}：{len(x)} 个采样 = {len(x) / SR:.4f} 秒，I {r['I']} LUFS，真峰值 {r['TP']} dBTP，限幅最深 {out['limiter_min_db']} dB")
    print(f"起音核对 {len(rows)} 个；单轨上差超过 1 帧 {len(bad_solo)} 个：", [(q['t'], q['label'], q['solo_err_ms']) for q in bad_solo])
    print(f"  sfx.wav 里差超过 1 帧 {len(bad)} 个：", [(q['t'], q['label'], q['err_ms'], q['solo_err_ms']) for q in bad])
    return out


if __name__ == '__main__':
    main()
