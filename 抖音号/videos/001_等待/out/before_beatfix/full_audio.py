"""《等待》整条的声音：只有音效，没有音乐。曲库的歌由号主在 App 里发布时加，所以这里不放任何和弦或旋律，免得和那首歌打架。

    python timeline.py && python full_audio.py      → studio/public/001/full.wav

每一句的音效都对着画面里的东西：电是裂响，等是钟响和心跳，翻日历是纸声，打字是键声，对话框收起是往下沉的一声。
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'lib'))
sys.path.insert(0, HERE)
from notebook import SR, add, plip, shaped_noise, tone, write_wav  # noqa: E402
from opening_audio import crackle, loudnorm, thump  # noqa: E402

FULL = json.load(open(os.path.join(ROOT, 'studio', 'src', 'videos', '001', 'full.json')))
FPS = FULL['fps']
OP = FULL['opening']
BEAT = {b['id']: b['from'] for b in FULL['beats']}
OUT = os.path.join(ROOT, 'studio', 'public', '001', 'full.wav')


def sec(f):
    return f / FPS


def whoosh(rng, dur, lo=400, hi=4000, down=False):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.sin(np.pi * t / dur) ** 2
    sig = shaped_noise(n, rng, lo, hi, tilt=-1) * env
    if down:
        sig *= np.linspace(1, 0.3, n)
    return sig


def key(rng):
    n = int(0.014 * SR)
    return shaped_noise(n, rng, 1800, 7000) * np.exp(-np.arange(n) / (0.003 * SR))


def glide(f0, f1, dur, gain_decay=0.3):
    t = np.arange(int(dur * SR)) / SR
    f = f0 + (f1 - f0) * t / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / gain_decay) * np.minimum(1, t / 0.01)


def opening(buf, rng):
    """开头 0–7 秒（Hook.tsx）：A 一声重击；B 计时圈走空时心跳加快、最后轻轻一下；问题“叮”一声；结果、金句各一下。"""
    a = sec(OP['aStrike'])
    add(buf, a, crackle(rng, 0.4, 900, 9000, 1100), gain=0.55)
    add(buf, a, thump(38, 0.7, 0.18), gain=0.75)
    add(buf, a, shaped_noise(int(0.09 * SR), rng, 300, 12000) * np.exp(-np.arange(int(0.09 * SR)) / (0.02 * SR)), gain=0.35)
    b0, b1 = sec(OP['bSweep'][0]), sec(OP['bSweep'][1])
    t, iv = b0, (b1 - b0) / 3.2
    while t < b1 - 0.05:
        g = 0.22 + 0.35 * (t - b0) / (b1 - b0)
        add(buf, t, thump(52, 0.2, 0.04), gain=g)
        add(buf, t + min(0.09, iv * 0.4), thump(44, 0.18, 0.035), gain=g * 0.6)
        t += iv
        iv = max((b1 - b0) / 8, iv * 0.75)
    add(buf, b1, crackle(rng, 0.12, 3000, 11000, 400), gain=0.14)
    for f in OP['count']:                                   # 3、2、1 每个数一声钟响
        add(buf, sec(f), plip(3300, 2100, 0.03), gain=0.14)
    add(buf, sec(OP['askAt']), tone(1318.5, 0.35, 0.004, 0.12), gain=0.035)
    add(buf, sec(OP['markG']), crackle(rng, 0.1, 1500, 10000, 700), gain=0.12, pan=-0.4)
    add(buf, sec(OP['markG']), thump(60, 0.25, 0.06), gain=0.2, pan=-0.4)
    add(buf, sec(OP['punchG']) + 0.55, thump(36, 1.2, 0.35), gain=0.8)


def beats(buf, rng):
    B = {k: sec(v) for k, v in BEAT.items()}
    add(buf, B['emory'], glide(196, 196, 1.2, 0.5), gain=0.06)                       # 大学楼：一声低沉的钟
    add(buf, B['lab'] + 0.15, crackle(rng, 0.06, 2500, 10000, 300), gain=0.06)        # 电极接上
    hum = np.sin(2 * np.pi * 100 * np.arange(int(1.4 * SR)) / SR) * 0.5
    add(buf, B['lab'] + 0.2, hum * np.hanning(len(hum)), gain=0.025)
    add(buf, B['grades'], plip(2200, 1400, 0.04), gain=0.05)
    for d in (0.0, 0.6):                                                            # 收件箱下拉刷新
        add(buf, B['offer'] + d + 0.1, whoosh(rng, 0.35, 800, 5000), gain=0.04)
    add(buf, B['reply'] + 0.07, plip(1800, 1100, 0.05), gain=0.08)                   # 发出“在吗？”
    for d in (0.45, 0.5, 0.55, 1.4, 1.45):
        add(buf, B['reply'] + d, key(rng), gain=0.03)
    for i in range(7):                                                              # 一天一天划掉
        for j, dd in enumerate((0.2, 0.27)):
            add(buf, B['days'] + sec(6 + i * 5) + j * 0.07, shaped_noise(int(0.06 * SR), rng, 2000, 9000) * np.hanning(int(0.06 * SR)),
                gain=0.04)
    for i in range(12):                                                             # 一个字一个字打出来
        add(buf, B['badnews'] + sec(4 + i * 2.4), key(rng), gain=0.06, pan=-0.2 + 0.03 * i)
    add(buf, B['badnews'] + sec(40), plip(1600, 900, 0.06), gain=0.1)               # 发出去
    add(buf, B['hurt'], thump(48, 0.3, 0.06), gain=0.2)                             # 你：一下心跳
    add(buf, B['hurt'] + 0.9, thump(48, 0.3, 0.06), gain=0.16)
    for i in range(0, 31, 3):                                                       # 身边的人一个个亮起
        add(buf, B['notweak'] + sec(12 + i * 0.7), tone((523.25, 659.25, 783.99)[i % 3], 0.2, 0.003, 0.05), gain=0.02)
    add(buf, B['me'], tone(1567.98, 1.2, 0.005, 0.4, ((1, 1.0), (2.01, 0.2))), gain=0.05)   # 我：一声很轻的“叮”
    add(buf, B['end'] + sec(14), whoosh(rng, 0.6, 300, 2500, down=True), gain=0.06)        # 对话框收起
    add(buf, B['end'] + sec(30), glide(880, 220, 0.5, 0.25), gain=0.04)                    # 点暗下去
    add(buf, B['wake'] + sec(4), glide(330, 990, 0.35, 0.3), gain=0.04)                    # 被叫醒
    add(buf, B['wake'] + sec(6), plip(2000, 1300, 0.04), gain=0.05)
    add(buf, B['zero'] + sec(20), tone(220, 0.8, 0.01, 0.3), gain=0.06)                    # 0
    add(buf, B['lines'], whoosh(rng, 1.0, 200, 1500), gain=0.04)                           # 你的线画出来
    for i in range(7):                                                                     # 我的点一个个出现
        add(buf, B['lines'] + sec(30 + i * 4), tone(1567.98, 0.25, 0.003, 0.06), gain=0.03)
    add(buf, B['feel'], whoosh(rng, 1.0, 150, 900), gain=0.05)
    for i in range(6):                                                                     # 字流进我的点
        add(buf, B['read'] + sec(i * 5 + 30), tone(2093.0, 0.3, 0.005, 0.1), gain=0.02)
    add(buf, B['q1'], whoosh(rng, 2.0, 120, 1200), gain=0.05)                              # 一段等被拉得很长
    for i in range(8):
        add(buf, B['q1'] + 0.2 + i * 0.25, plip(3000, 2000, 0.02), gain=0.04)
    add(buf, B['q2'] + sec(4), tone(110, 2.4, 0.05, 1.0, ((1, 1.0), (2, 0.3), (3, 0.1))), gain=0.12)   # 问号：一个低音
    add(buf, B['card'] + sec(18), tone(110, 3.5, 0.05, 1.5, ((1, 1.0), (2, 0.3))), gain=0.1)


def main():
    rng = np.random.default_rng(13)
    n = int((sec(FULL['frames']) + 0.3) * SR)
    buf = np.zeros((n, 2))
    for ch in range(2):
        buf[:, ch] += shaped_noise(n, rng, 80, 2500, tilt=-1) * 0.008
    opening(buf, rng)
    beats(buf, rng)
    raw = OUT.replace('.wav', '_raw.wav')
    write_wav(buf, raw, peak_db=-1.0)
    loudnorm(raw, OUT)
    os.remove(raw)
    print(OUT)


if __name__ == '__main__':
    main()
