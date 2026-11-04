"""笔记 001《等待》开头样片（第四版）的声音。

    python opening_audio.py      → studio/public/001/opening.wav

分镜见 分镜_开头.md，节拍表 studio/src/videos/001/cues.json（画面和声音共用）。
声音也对着字走：电 = 裂响；等 = 钟响和越来越快的心跳；人出现 = 轻轻一声“叮”；金句前全静。
第三版（心跳线）的声音脚本留在 opening_audio_v3.py。
"""
import json
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

CUES = json.load(open(os.path.join(ROOT, 'studio', 'src', 'videos', '001', 'cues_v4.json')))
FPS, F = CUES['fps'], CUES['frames']
SH = CUES['shots']
OUT = os.path.join(ROOT, 'studio', 'public', '001', 'opening.wav')


def sec(f):
    return f / FPS


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
    return sig * np.minimum(1, t / attack) * np.minimum(1, (dur - t) / release)


def build():
    rng = np.random.default_rng(9)
    n = int((sec(F) + 0.4) * SR)
    buf = np.zeros((n, 2))
    for ch in range(2):
        buf[:, ch] += shaped_noise(n, rng, 80, 2500, tilt=-1) * 0.008

    # 第 1 场：很轻的底音，让人安静读完
    add(buf, 0, chord((110, 164.81, 220), sec(SH['a']) + 0.3, 0.05, 0.3), gain=0.05)

    # 第 2 场 A：马上，重
    a = sec(CUES['aStrike'])
    add(buf, a, crackle(rng, 0.4, 900, 9000, 1100), gain=0.55)
    add(buf, a, thump(38, 0.7, 0.18), gain=0.75)
    burst = shaped_noise(int(0.09 * SR), rng, 300, 12000) * np.exp(-np.arange(int(0.09 * SR)) / (0.02 * SR))
    add(buf, a, burst, gain=0.35)

    # 第 3 场 B：每秒一声钟响；心跳越来越快越响；低音往上爬；最后只“嗤”一下
    b0, b1 = sec(SH['b']), sec(CUES['bStrike'])
    for f in CUES['count']:
        add(buf, sec(f), plip(3300, 2100, 0.03), gain=0.16)
        add(buf, sec(f), thump(140, 0.12, 0.03), gain=0.08)
    t, interval = b0 + 0.15, 0.85
    while t < b1 - 0.1:
        k = (t - b0) / (b1 - b0)
        g = 0.2 + 0.4 * k
        add(buf, t, thump(52, 0.25, 0.05), gain=g)
        add(buf, t + 0.11, thump(44, 0.22, 0.045), gain=g * 0.6)
        t += interval
        interval = max(0.36, interval * 0.88)
    m = int((b1 - b0) * SR)
    tt = np.arange(m) / SR
    k = tt / (b1 - b0)
    freq = 55 * 2 ** (k * 0.9)
    drone = np.sin(2 * np.pi * np.cumsum(freq) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(freq) / SR)
    drone += shaped_noise(m, rng, 200, 1800) * 0.25 * k
    add(buf, b0, drone * k ** 1.5 * np.minimum(1, (b1 - b0 - tt) / 0.01), gain=0.13)
    add(buf, b1, crackle(rng, 0.09, 3500, 12000, 300), gain=0.1)

    # 第 5、6 场：一层很轻的和弦；人一个个出现；10 个人到 A 时各一声小电响
    e0, l0 = sec(SH['exp']), sec(SH['line'])
    add(buf, e0, chord((110, 164.81, 220, 261.63), l0 - e0 + 0.08, 0.8, 0.08), gain=0.07)
    pe = CUES['people']
    scale = (659.25, 783.99, 880.0, 987.77, 1174.66)
    for i in range(0, pe['n'], 2):
        add(buf, sec(pe['start'] + i * pe['step']), tone(scale[(i // 2) % 5], 0.2, 0.003, 0.05), gain=0.025,
            pan=-0.5 + i / pe['n'])
    ma, mb = CUES['moveA'], CUES['moveB']
    for j in range(len(CUES['picked'])):
        t = sec(ma['start'] + j * ma['step'] + CUES['travel'])
        add(buf, t, crackle(rng, 0.1, 1500, 10000, 700), gain=0.13, pan=-0.5)
        add(buf, t, thump(70 - j * 2, 0.16, 0.04), gain=0.1, pan=-0.5)
    for j in range(0, 22, 2):
        add(buf, sec(mb['start'] + j * mb['step'] + CUES['travel']), plip(1500, 900, 0.03), gain=0.03, pan=0.5)

    # 第 7 场：定住，全静；金句落下时一声低沉的重击，再留一个长音
    p2 = sec(CUES['punch2'])
    add(buf, p2, thump(36, 1.2, 0.35), gain=0.8)
    add(buf, p2, chord((110, 130.81, 164.81, 246.94), sec(F) + 0.4 - p2, 0.4, 1.0), gain=0.06)
    return buf


def loudnorm(src, dst, target=-14.0):
    """两遍 loudnorm，线性增益，不压动态。"""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    first = subprocess.run([ff, '-hide_banner', '-i', src, '-af',
                            f'loudnorm=I={target}:TP=-1.5:LRA=20:print_format=json', '-f', 'null', '-'],
                           capture_output=True, text=True).stderr
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', first, re.S).group(0))
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=20:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', src, '-af', af, '-ar', str(SR), dst], check=True)


def main():
    raw = OUT.replace('.wav', '_raw.wav')
    write_wav(build(), raw, peak_db=-1.0)
    loudnorm(raw, OUT)
    os.remove(raw)
    print(OUT)


if __name__ == '__main__':
    main()
