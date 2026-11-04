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
EX = FULL['exp']
GR = FULL.get('grid', {})
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


# ---- 手机外放也听得见的几种声音（10/28 七维度评审：重电的能量在 40 Hz，手机外放听不见，倒数滴答反而比重电响） ----
def body_hit(f0=220, f1=90, dur=0.08):
    """闷击：220→90 Hz 下扫，手机喇叭放得出来。"""
    t = np.arange(int(dur * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / (dur * 0.35))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (dur * 0.45)) * np.minimum(1, t / 0.002)


def snap(rng, dur=0.03, fc=2500):
    """爆裂：白噪声收窄到 fc 附近（Q 约 0.7）。"""
    n = int(dur * SR)
    return shaped_noise(n, rng, fc / 1.7, fc * 1.7) * np.exp(-np.arange(n) / (dur * 0.3 * SR))


def heart(f0=80, dur=0.16):
    """心跳：80 Hz 带 160、240 Hz 谐波，再加一点 2 kHz 的拍击感，手机上听得见。"""
    t = np.arange(int(dur * SR)) / SR
    sig = np.sin(2 * np.pi * f0 * t) + 0.6 * np.sin(2 * np.pi * 2 * f0 * t) + 0.35 * np.sin(2 * np.pi * 3 * f0 * t)
    click = 0.35 * np.sin(2 * np.pi * 2000 * t) * np.exp(-t / 0.004) + 0.3 * np.sin(2 * np.pi * 1000 * t) * np.exp(-t / 0.012)
    return (sig * np.exp(-t / (dur * 0.3)) + click) * np.minimum(1, t / 0.004)


def growl(f0=55, dur=1.2, drive=3.0):
    """低鸣：55 Hz 过一道 tanh 饱和，带出 110/165/220 Hz，手机上也有存在感。"""
    t = np.arange(int(dur * SR)) / SR
    sig = np.tanh(drive * np.sin(2 * np.pi * f0 * t)) / np.tanh(drive)
    tail = np.clip((dur - t) / 0.4, 0, 1)                      # 最后 0.4 秒淡出，不硬切
    return sig * np.minimum(1, t / 0.02) * np.exp(-t / (dur * 0.5)) * tail


def ring(freq=1200, dur=0.9):
    """冷色的一声，带一点简单的混响尾巴。"""
    base = tone(freq, 0.35, 0.003, 0.08, ((1, 1.0), (2.01, 0.15)))
    out = np.zeros(int(dur * SR))
    for k, (d, g) in enumerate(((0, 1.0), (0.061, 0.45), (0.113, 0.3), (0.171, 0.2), (0.233, 0.12))):
        i = int(d * SR)
        out[i:i + len(base)] += base[: len(out) - i] * g
    return out


def opening(buf, rng, look=False):
    """开头 0–12 秒：A 早点、重；B 晚点、轻（倒数 3、2、1）；问题；结果；金句。
    A 的声音放左边，B 的放右边，滴答跟着钟走。A 在手机外放上要比 B 响 10 dB 以上。"""
    a = sec(OP['aStrike'])
    # 劈下之前：低嗡加一层 3–6 kHz 的电流滋滋声，慢慢升起来；电流每跑到手腕就噼啪一下（声音先于画面）
    n = int(a * SR)
    t = np.arange(n) / SR
    buzz = (np.sin(2 * np.pi * 100 * t) + 0.4 * np.sin(2 * np.pi * 200 * t)) * (t / a) ** 2
    add(buf, 0.0, buzz, gain=0.05, pan=-0.5)
    sizzle = shaped_noise(n, rng, 3000, 6000) * (0.55 + 0.45 * np.sin(2 * np.pi * 100 * t)) * (0.25 + 0.75 * (t / a) ** 1.5)
    add(buf, 0.0, sizzle, gain=0.07, pan=-0.5)
    for i, fr in enumerate(OP['charge']):
        add(buf, sec(fr), snap(rng, 0.02, 3500), gain=0.06 + 0.1 * i / len(OP['charge']), pan=-0.5)
    # A：重。闷击 + 三下爆裂 + 嘶嘶尾音 + 噼啪，合在一起过一道 tanh 饱和：峰值不变，手机上听着更“厚”；40 Hz 那层降 6 dB
    ev = np.zeros(int(0.45 * SR))
    def put(sig, d, g):
        i = int(d * SR)
        ev[i:i + len(sig)] += sig[: len(ev) - i] * g
    put(body_hit(220, 90, 0.12), 0.0, 0.9)
    for d in (0.0, 0.045, 0.095):
        put(snap(rng, 0.05, 2500), d, 1.0)
    put(shaped_noise(int(0.25 * SR), rng, 6000, 10000) * np.exp(-np.arange(int(0.25 * SR)) / (0.08 * SR)), 0.02, 0.2)
    put(crackle(rng, 0.4, 900, 9000, 1100), 0.0, 0.6)
    ev = np.tanh(3.0 * ev) / np.tanh(3.0)
    add(buf, a, ev, gain=0.75, pan=-0.5)
    add(buf, a, thump(38, 0.7, 0.18), gain=0.25)
    # B：倒数时心跳越来越快（手机听得见的 80 Hz 加谐波）；3、2、1 每个数一声轻“嗒”；走到头只一下轻爆裂
    b0, b1 = sec(OP['bSweep'][0]), sec(OP['bSweep'][1])
    for i, f in enumerate(OP['count']):                      # 每跳一下：“嗒”（钟）—“咚”（心跳），一下比一下重
        add(buf, sec(f), plip(3200, 2200, 0.02), gain=0.06, pan=0.6)
        add(buf, sec(f) + 0.12, heart(80), gain=0.09 + 0.05 * i, pan=0.5)
        add(buf, sec(f) + 0.24, heart(70, 0.14), gain=(0.09 + 0.05 * i) * 0.55, pan=0.5)
    add(buf, b1, snap(rng, 0.03, 2500), gain=0.45, pan=0.5)
    add(buf, b1, body_hit(180, 110, 0.05), gain=0.12, pan=0.5)
    add(buf, sec(OP['askAt']), tone(1318.5, 0.35, 0.004, 0.12), gain=0.035)
    if look:
        # 观感样片：拉远成 32 间房，灯一盏盏亮（细小的咔嗒）；“9”出来时 9 间房一起冷光一闪；推回来一声风
        g0 = sec(OP['p2Start'] + GR['out'] - OP['p2Offset'])
        for i in range(32):
            add(buf, g0 + 0.25 + i * 0.012, plip(2600, 1900, 0.012), gain=0.018, pan=-0.7 + 1.4 * (i % 8) / 7)
        n9 = sec(OP['p2Start'] + GR['nine'] - OP['p2Offset'])
        for j in range(9):
            add(buf, n9 + 0.067 + j * 0.08, plip(2500 * 2 ** (j / 12), 1800 * 2 ** (j / 12), 0.03), gain=0.07, pan=-0.6 + 1.2 * j / 8)
            add(buf, n9 + 0.067 + j * 0.08, snap(rng, 0.015, 2500 * 2 ** (j / 12)), gain=0.12, pan=-0.6 + 1.2 * j / 8)
        add(buf, sec(OP['p2Start'] + GR['back'] - OP['p2Offset']), shaped_noise(int(0.4 * SR), rng, 300, 2500) * np.hanning(int(0.4 * SR)), gain=0.05)
    else:
        mk = sec(OP['markG']) + 0.1                           # 红框真正看得见是在点亮后约 3 帧
        add(buf, mk, crackle(rng, 0.1, 1500, 10000, 700), gain=0.12, pan=-0.4)
        add(buf, mk, heart(90, 0.2), gain=0.15, pan=-0.4)
    # 金句：55 Hz 饱和低鸣代替 36 Hz 纯正弦；“宁可更疼”出来时一声冷色的叮
    hit = sec(OP['punchG'] + 22)
    add(buf, hit, growl(55, 1.2), gain=0.08)
    add(buf, hit, np.tanh(3 * (snap(rng, 0.08, 2200) + 0.6 * body_hit(260, 120, 0.08))), gain=0.18, pan=-0.3)
    add(buf, hit, ring(1200), gain=0.06)


def beats(buf, rng):
    B = {k: sec(v) for k, v in BEAT.items()}
    # 实验那一镜（一个连续镜头）：大学楼一声低沉的钟 → 推进楼门 → 电极接通一下电 → 推进仪器屏幕
    add(buf, B['exp'], glide(196, 196, 1.2, 0.5), gain=0.06)
    add(buf, B['exp'], tone(1174.7, 1.2, 0.005, 0.4, ((1, 1.0), (2.01, 0.3))), gain=0.02)
    add(buf, B['exp'] + sec(EX['enter']), whoosh(rng, 0.45, 300, 2500), gain=0.11)
    add(buf, B['exp'] + sec(EX['on']), crackle(rng, 0.12, 2500, 11000, 400), gain=0.12, pan=-0.3)
    add(buf, B['exp'] + sec(EX['on']), thump(60, 0.2, 0.05), gain=0.12)
    hv = shaped_noise(int(0.35 * SR), rng, 2500, 4000)
    add(buf, B['exp'] + sec(EX['on']), hv * np.exp(-np.arange(len(hv)) / (0.12 * SR)), gain=0.05)
    hum = np.sin(2 * np.pi * 100 * np.arange(int(0.9 * SR)) / SR) * 0.5
    add(buf, B['exp'] + sec(EX['on']), hum * np.hanning(len(hum)), gain=0.025)
    p0, p1 = sec(EX['push'][0]), sec(EX['push'][1])
    add(buf, B['exp'] + p0, whoosh(rng, p1 - p0 + 0.1, 400, 5000), gain=0.14)
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


def highpass(buf, fc=20.0):
    """20 Hz 高通（顺便去掉直流偏移）。"""
    out = np.empty_like(buf)
    f = np.fft.rfftfreq(buf.shape[0], 1 / SR)
    g = 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4)
    for ch in range(buf.shape[1]):
        out[:, ch] = np.fft.irfft(np.fft.rfft(buf[:, ch]) * g, buf.shape[0])
    return out


def render(path, look, trunc=False):
    rng = np.random.default_rng(13)
    n = int((sec(FULL['frames']) + 0.3) * SR)
    # 观感样片只有开头 12.2 秒：只留这一段，按这一段归一化响度
    buf = np.zeros((n, 2))
    for ch in range(2):
        buf[:, ch] += shaped_noise(n, rng, 80, 2500, tilt=-1) * 0.008
    t = np.arange(n) / SR
    hum = np.sin(2 * np.pi * 120 * t) + 0.5 * np.sin(2 * np.pi * 240 * t) + 0.3 * np.sin(2 * np.pi * 360 * t)
    for ch in range(2):
        buf[:, ch] += hum * 0.004
    opening(buf, rng, look)
    beats(buf, rng)
    buf = highpass(buf)
    # 软限幅：只压超过 -6 dBFS 的峰（主要是 A 那一下），其余不动，整体响度才抬得起来
    pk = np.max(np.abs(buf)) + 1e-9
    x = buf / pk
    T = 0.5
    over = np.abs(x) > T
    x[over] = np.sign(x[over]) * (T + (1 - T) * np.tanh((np.abs(x[over]) - T) / (1 - T)))
    buf = x
    if trunc:
        buf = buf[: int((sec(OP['p2End']) + 0.3) * SR)]
    raw = path.replace('.wav', '_raw.wav')
    write_wav(buf, raw, peak_db=-1.0)
    loudnorm(raw, path, target=-16.0)
    os.remove(raw)
    print(path)


def main():
    render(OUT, look=False)                                              # 旧版整条（Full.tsx）
    render(OUT.replace('full.wav', 'look.wav'), look=True, trunc=True)   # 观感样片（开头 12.2 秒）
    render(OUT.replace('full.wav', 'final.wav'), look=True)              # 终版整条（FinalFilm.tsx）


if __name__ == '__main__':
    main()
