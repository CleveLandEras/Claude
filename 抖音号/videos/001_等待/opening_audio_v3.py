"""（第三版，留作对照）笔记 001《等待》开头样片（第三版）的“乐谱”：心跳模型 + 声音。

    python opening_audio.py
        → studio/src/videos/001/heart.json   每条心跳线每一帧的相位（画面读它画线）
        → studio/public/001/opening.wav      声音（心跳和画面上的跳动严丝合缝）

分镜见 分镜_开头.md，节拍表 studio/src/videos/001/cues.json。
这里的心跳是“想象你自己在选”时的戏剧化表现，不是实验数据。
"""
import json
import math
import os
import re
import subprocess
import sys

import imageio_ffmpeg
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'lib'))
from notebook import SR, add, plip, shaped_noise, tone, write_wav  # noqa: E402

SRC = os.path.join(ROOT, 'studio', 'src', 'videos', '001')
CUES = json.load(open(os.path.join(SRC, 'cues_v3.json')))
FPS, F, PRE = CUES['fps'], CUES['frames'], CUES['pre']
SH = CUES['shots']
ME = CUES['me']
PICKED = CUES['picked']
OUT_WAV = os.path.join(ROOT, 'studio', 'public', '001', 'opening_v3.wav')
OUT_HEART = os.path.join(SRC, 'heart_v3.json')


def sec(f):
    return f / FPS


def pick_frame(j):
    return CUES['pickStart'] + j * CUES['pickStep']


# ---------- 心跳模型 ----------

def bpm_me(f):
    """“你”的心跳：A 那一下猛跳又落回；B 倒数时一路往上爬；之后慢慢平；最后和等的人一起又快起来。"""
    if f < SH['a'] + 6:
        return 64
    if f < SH['b']:
        return 64 + 34 * math.exp(-(f - CUES['aShock']) / 8)
    if f < CUES['bShock']:
        return 64 + 76 * ((f - SH['b']) / (CUES['bShock'] - SH['b'])) ** 1.6
    if f < SH['reveal']:
        return 96 + 44 * math.exp(-(f - CUES['bShock']) / 15)
    if f < SH['pick']:
        return 96 - 8 * min(1, (f - SH['reveal']) / 40)
    return 88 + 40 * min(1, (f - SH['pick']) / 48)


def bpm_other(i, base, f):
    if f < SH['pick']:
        return base + 3 * math.sin(f / 23 + i)
    if i in PICKED:
        s = pick_frame(PICKED.index(i))
        if f < s:
            return base + 12 * (f - SH['pick']) / max(1, s - SH['pick'])
        return 58 + (base + 40 - 58) * math.exp(-(f - s) / 12)
    return base + 45 * min(1, (f - SH['pick']) / 48)


def heart_model():
    rng = np.random.default_rng(3)
    bases = rng.uniform(60, 84, CUES['rows'])
    frames = np.arange(-PRE, F)
    phase = []
    for i in range(CUES['rows']):
        bpm = np.array([bpm_me(f) if i == ME else bpm_other(i, bases[i], f) for f in frames])
        start = 0.37 if i == ME else rng.uniform(0, 1)
        ph = start + np.concatenate([[0], np.cumsum(bpm[:-1] / 60 / FPS)])
        phase.append(ph)
    return phase


def beat_times(ph, f0, f1):
    """相位每过一个整数就是一拍。返回 [f0, f1) 帧之间每一拍的时间（秒）。"""
    out = []
    for k in range(len(ph) - 1):
        f = k - PRE
        if f < f0 or f >= f1:
            continue
        a, b = ph[k], ph[k + 1]
        # QRS 尖峰在一拍里的 0.22 处，心跳声对准它
        n = math.floor(a - 0.22 + 1e-9)
        if math.floor(b - 0.22) > n:
            frac = (n + 1 + 0.22 - a) / (b - a)
            out.append(sec(f + frac))
    return out


# ---------- 声音零件 ----------

def thump(freq, dur, decay):
    t = np.arange(int(dur * SR)) / SR
    f = freq * (1 + 1.2 * np.exp(-t / 0.015))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay) * np.minimum(1, t / 0.002)


def crackle(rng, dur, lo, hi, density):
    n = int(dur * SR)
    imp = (rng.random(n) < density / SR).astype(float) * rng.uniform(0.3, 1.0, n)
    hiss = shaped_noise(n, rng, lo, hi) * 0.3
    t = np.arange(n) / SR
    burst = np.convolve(imp, np.exp(-np.arange(80) / 12), mode='same') + hiss
    return burst * np.exp(-t / (dur * 0.35))


def chord(freqs, dur, attack, release):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) for f in freqs) / len(freqs)
    env = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / release)
    return sig * env


def build(phase):
    rng = np.random.default_rng(5)
    n = int((sec(F) + 0.4) * SR)
    buf = np.zeros((n, 2))
    line = sec(SH['line'])

    # 极轻的房间底噪，全程都在，静的时候也不是数字静音
    room = shaped_noise(n, rng, 80, 2500, tilt=-1) * 0.008
    buf[:, 0] += room
    buf[:, 1] += shaped_noise(n, rng, 80, 2500, tilt=-1) * 0.008

    # 你的心跳：B 倒数时越来越响；往后拉开以后退远一点；定格时停
    for tb in beat_times(phase[ME], -PRE, SH['line']):
        if tb < 0:
            continue
        f = tb * FPS
        if SH['b'] <= f < CUES['bShock']:
            g = 0.32 + 0.38 * (f - SH['b']) / (CUES['bShock'] - SH['b'])
        elif f >= SH['reveal']:
            g = 0.16
        else:
            g = 0.3
        add(buf, tb, thump(52, 0.25, 0.05), gain=g)
        add(buf, tb + 0.11, thump(44, 0.22, 0.045), gain=g * 0.6)
    # 往后拉开以后，别人的心跳也隐约在
    for i in range(CUES['rows']):
        if i == ME:
            continue
        for tb in beat_times(phase[i], SH['reveal'] + 20, SH['line']):
            add(buf, tb, thump(60 + i % 5 * 4, 0.15, 0.03), gain=0.025, pan=-0.8 + 1.6 * i / CUES['rows'])

    # B：低音一路往上爬，越来越紧；电下去的那一刻戛然而止
    t0, t1 = sec(SH['b']), sec(CUES['bShock'])
    m = int((t1 - t0) * SR)
    tt = np.arange(m) / SR
    k = tt / (t1 - t0)
    freq = 55 * 2 ** (k * 0.9)
    drone = (np.sin(2 * np.pi * np.cumsum(freq) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(freq) / SR))
    drone += shaped_noise(m, rng, 200, 1800) * 0.25 * k
    add(buf, t0, drone * (k ** 1.5) * np.minimum(1, (t1 - t0 - tt) / 0.01), gain=0.13)
    # 倒数：每秒一声钟响
    for f in CUES['count']:
        add(buf, sec(f), plip(3300, 2100, 0.03), gain=0.16)
        add(buf, sec(f), thump(140, 0.12, 0.03), gain=0.08)

    # A：马上，重
    a = sec(CUES['aShock'])
    add(buf, a, crackle(rng, 0.4, 900, 9000, 1100), gain=0.55)
    add(buf, a, thump(38, 0.7, 0.18), gain=0.75)
    add(buf, a, shaped_noise(int(0.09 * SR), rng, 300, 12000) * np.exp(-np.arange(int(0.09 * SR)) / (0.02 * SR)),
        gain=0.35)
    # B：等了那么久，只有轻轻“嗤”一下
    add(buf, sec(CUES['bShock']), crackle(rng, 0.09, 3500, 12000, 300), gain=0.1)

    # 往后拉开：一层很轻的和弦进来，定格时收住
    r0 = sec(SH['reveal'])
    add(buf, r0, chord((110, 164.81, 220, 261.63), line - r0 + 0.08, 0.9, 0.08), gain=0.07)
    # 10 个人一个接一个选了 A
    for j in range(len(PICKED)):
        add(buf, sec(pick_frame(j)), crackle(rng, 0.12, 1500, 10000, 700), gain=0.16, pan=-0.6 + 1.2 * j / 9)
        add(buf, sec(pick_frame(j)), thump(70 - j * 2, 0.18, 0.04), gain=0.12)

    # 金句：定格后全静，落下时一声低沉的重击，再留一个长音
    p2 = sec(CUES['punch2'])
    add(buf, p2, thump(36, 1.2, 0.35), gain=0.8)
    add(buf, p2, chord((110, 130.81, 164.81, 246.94), sec(F) + 0.4 - p2, 0.4, 1.0), gain=0.06)
    return buf


def loudnorm(src, dst, target=-14.0):
    """两遍 loudnorm，线性增益，不压动态：静的地方要静，炸的地方要炸。"""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    first = subprocess.run([ff, '-hide_banner', '-i', src, '-af',
                            f'loudnorm=I={target}:TP=-1.5:LRA=20:print_format=json', '-f', 'null', '-'],
                           capture_output=True, text=True).stderr
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', first, re.S).group(0))
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=20:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', src, '-af', af, '-ar', str(SR), dst], check=True)


def main():
    phase = heart_model()
    json.dump({'pre': PRE, 'phase': [[round(float(v), 4) for v in ph] for ph in phase]},
              open(OUT_HEART, 'w'), separators=(',', ':'))
    raw = OUT_WAV.replace('.wav', '_raw.wav')
    write_wav(build(phase), raw, peak_db=-1.0)
    loudnorm(raw, OUT_WAV)
    os.remove(raw)
    print(OUT_HEART)
    print(OUT_WAV)


if __name__ == '__main__':
    main()
