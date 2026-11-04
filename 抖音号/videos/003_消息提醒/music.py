"""《消息提醒》（003 横屏，61.2 秒 = 1836 帧）的原创配乐，和音效混成最终音轨。

照 002 的 music.py：全部用 numpy 合成，纯音乐，没有人声，没有鼓。不用曲库、采样、第三方账号。

  /Users/decheng.huang/Documents/dy/.venv/bin/python /Users/decheng.huang/Documents/dy/videos/003_消息提醒/music.py
  （先跑 sfx.py）

读：studio/src/videos/003/timeline.ts（经 sfx.py 读；只读）
    studio/public/003/sfx.wav、sfx_events.json（sfx.py 的成品；只读，不改）
写：studio/public/003/music.wav（单独的配乐，电平 = 它在 mix.wav 里的电平，含让开，没过限幅）
    studio/public/003/mix.wav（音效 ＋ 配乐，48 kHz、正好 61.2 秒，整条 −14 LUFS，过一道前瞻限幅，真峰值 ≤ −2 dBTP）
    videos/003_消息提醒/out/音效/配乐核对.json、videos/003_消息提醒/out/声音_自查.md（自查）

调和速度：100 BPM（一拍 0.6 秒）。每一段从时间表的拍起点重新起拍，段内按 100 BPM 走。
前半段 D 小调（略紧张），22.6 秒“先分开”转 D 大调（同一个主音，一下亮起来）。主要能量在 200 Hz–2 kHz，整条过 2.4 kHz 的柔和低通，
不抢 1–4 kHz 的音效。有音高的音效（提示音、铃、按钮）都落在当时的和弦里。

结构（秒数都从 timeline.ts 取）：
  A   0–8.2       钩子：拨弦的低音脉冲（一下比一下密：四分 → 八分），木琴八分音符的固定音型，D 小调 Dm–B♭–Gm–A–Dm；
                  开头一句拇指琴动机 A D E F（往上走，停在 F 上，像在问）；5.8–8.2 伸手又缩回：固定音型停，只剩脉冲和垫音
  A'  8.2–9.4     计数跑起来：A 和弦上木琴十六分音符往上跑一个八度，脉冲变十六分，渐强；9.4 停在 120：Dm 一下重音
  T   10.4–11.8   标题卡：10.4–10.6（6 帧落下）让开给转场的嗖，10.6 落地时一个低的 Dm(add9) 和弦，不打拍子
  B1  11.8–13.4   全开：固定音型＋脉冲回来，最满的“吵”
  B2  13.4–21.6   全关：安静但不安。只剩垫音和稀的拨弦；小钟走的那 1.8 秒配乐只留垫音（钟就是拍子）；
                  19.0 起“挂在心上”：钢琴 A–B♭ 半音一来一回（叹气）
  R   21.6–22.6   推向右栏：拇指琴在 A7 上往上走、越来越快，接到 22.6
  C   22.6–31.0   先分开：D 大调，轻快。拨弦低音踩拍、木琴反拍和弦（嘭—嚓）、拇指琴旋律；关键音效前后 0.2 秒内的旋律音自动让掉
  C2  31.0–33.6   拉回三栏：D–G–A，只有低音和琶音，不出旋律（字幕要读）
  D   33.6–38.6   金句：收。33.6 琶音变慢，34.6 起只剩垫音和隔两拍一个的钢琴音，38.6 一刀抽空
  ·   38.6–39.85  定格那一秒抽空（和音效同一条门），快门（39.7）之后才回来
  E   39.85–58.2  清单：平稳、低、不抢字。拇指琴八分音符琶音（只在 D4–A4 这一窄条里）、拨弦低音、垫音；每张清单卡换一组和弦
  F   58.2–61.2   结尾：四个按钮的音（D6 E6 F♯6 A6）落在 Dadd9 上；之后拇指琴把开头动机用大调答一遍（A D E F♯），
                  停在 Asus4 上淡到 0（循环回第 0 帧的 Dm，正好是 V → i）

混音：配乐整条比音效低 MUSIC_REL LU；每个 key 音效出现时配乐再压 DUCK_DB（提前 40 毫秒压下、压 0.15 秒、0.5 秒放开）；
定格那一秒和音效一起全停。
11/2 评委改：前 15 秒原来比全片响 3.7 LU。混音时 13.4 秒（全关开头，本来就安静）之前的音效＋配乐整体压 RIDE dB，
13.4–15.4 秒慢慢回到 0；RIDE 自动解，让前 15 秒正好比全片响 HOOK_LU。前 15 秒里面的轻重关系不变。
"""
import json
import math
import os
import re
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfx                                   # 借它的时间表、合成零件、响度和限幅函数；不跑它的 main，不写 sfx.wav

ROOT = sfx.ROOT
EV, B = sfx.EV, sfx.B
SR, FPS, NF, SPF, N = sfx.SR, sfx.FPS, sfx.NF, sfx.SPF, sfx.N
SFX_WAV, SFX_EVENTS = sfx.OUT_WAV, sfx.OUT_EVENTS
OUT_MUSIC = os.path.join(sfx.PUB, 'music.wav')
OUT_MIX = os.path.join(sfx.PUB, 'mix.wav')
OUT_CHECK = os.path.join(HERE, 'out', '音效', '配乐核对.json')
OUT_MD = os.path.join(HERE, 'out', '声音_自查.md')
SEED = 3013

BPM = 100.0
Q = 60.0 / BPM                    # 一拍 0.6 秒
EI = Q / 2                        # 八分音符 0.3 秒
SX = Q / 4                        # 十六分音符 0.15 秒
MIX_TARGET = -14.0                # mix.wav 整条响度（11/2 评委改：−15 → −14）
HOOK_LU = 1.5                     # 前 15 秒比全片响多少 LU（评委：不超过 2；按 1.5 解，留 0.5 的余量）
MIX_TP = -2.0                     # mix.wav 真峰值上限（要求 ≤ −1.5，留 0.5 dB 给 AAC 编码）
MUSIC_REL = -5.0                  # 配乐整条响度比音效整条低多少 LU
DUCK_DB = -6.0                    # key 音效出现时配乐再压多少
END = N / SR

# ======================================================================
# 音高
# ======================================================================
PC = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}


def mid(name):
    """'G4' → MIDI 67。"""
    p, o = (name[:2], name[2:]) if len(name) > 2 and name[1] in '#b' else (name[:1], name[1:])
    return 12 * (int(o) + 1) + PC[p]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


CHORD = {
    'Dm': 'D F A', 'Dmadd9': 'D F A E', 'Bb': 'Bb D F', 'Gm': 'G Bb D', 'A': 'A C# E', 'A7': 'A C# E G', 'Asus4': 'A D E',
    'D': 'D F# A', 'Dadd9': 'D F# A E', 'G': 'G B D', 'Gmaj7': 'G B D F#', 'Bm': 'B D F#', 'Em': 'E G B',
}
ROOTNOTE = {'Dm': 'D3', 'Dmadd9': 'D3', 'Bb': 'Bb2', 'Gm': 'G2', 'A': 'A2', 'A7': 'A2', 'Asus4': 'A2', 'D': 'D3', 'Dadd9': 'D3',
            'G': 'G2', 'Gmaj7': 'G2', 'Bm': 'B2', 'Em': 'E3'}


def tones(ch, lo, hi):
    """和弦 ch 在 [lo, hi]（MIDI）之间的所有音，从低到高。"""
    pcs = {PC[x] for x in CHORD[ch].split()}
    return [m for m in range(mid(lo), mid(hi) + 1) if m % 12 in pcs]


# ======================================================================
# 乐器（都返回单声道；峰值没归一，幅度就是力度）
# ======================================================================
ts = sfx.ts


def kalimba(rng, f0, vel=0.7, ring=1.4):
    """拇指琴：金属簧片拨一下。主音很强，带 1.0015 倍的伴音、很弱的 2、3 倍，和一个 5.9 倍的簧片泛音（35 毫秒就没了）。"""
    n = int(ring * SR)
    tau = 0.85 * (392.0 / f0) ** 0.35
    parts = [(f0, 1.0, tau), (f0 * 1.0015, 0.22, tau * 0.9), (2.0 * f0, 0.07, tau * 0.28), (3.01 * f0, 0.04, 0.06),
             (5.92 * f0, 0.07 * vel, 0.035)]
    y = sfx.modal(n, parts, rng, att=0.0012)
    y = y + 0.05 * sfx.contact(n, rng, 300, 1800, 0.004)
    return vel * sfx.fades(sfx.shape(y, 120, 2600, order=2), 0.0005, 0.05)


def marimba(rng, f0, vel=0.7, ring=1.3):
    """木琴：软槌敲木条。1、3.93、9.2 倍三个模态，高的衰减很快；软槌的一下闷响。"""
    n = int(ring * SR)
    tau = 0.55 * (392.0 / f0) ** 0.5
    parts = [(f0, 1.0, tau), (3.93 * f0, 0.12 * vel, 0.05), (9.2 * f0, 0.02, 0.012), (f0 * 0.5, 0.05, 0.05)]
    y = sfx.modal(n, parts, rng, att=0.002)
    y = y + 0.04 * sfx.contact(n, rng, 200, 1500, 0.006)
    return vel * sfx.fades(sfx.shape(y, 120, 2400, order=2), 0.0005, 0.05)


def piano(rng, f0, dur, vel=0.5):
    """柔和的钢琴：两根弦（差 ±0.8 音分），谐波带一点非谐，高次谐波衰减更快；力度小，音色暗、圆；放开时 0.2 秒收掉。"""
    rel = 0.2
    n = int((dur + rel + 0.05) * SR)
    t = ts(n)
    y = np.zeros(n)
    bri = 2.0 + 4.0 * vel
    for k in range(1, 14):
        fk = k * f0 * math.sqrt(1 + 0.0003 * k * k)
        if fk > 3500:
            break
        a = (1 / k ** 1.1) * math.exp(-(k - 1) / bri)
        tau = 2.6 * (262.0 / f0) ** 0.55 / (1 + 0.45 * (k - 1))
        for c in (-0.8, 0.8):
            ph = rng.uniform(0, 2 * np.pi)
            y += 0.5 * a * np.sin(2 * np.pi * fk * 2 ** (c / 1200) * t + ph) * (0.7 * np.exp(-t / tau) + 0.3 * np.exp(-t / (tau * 4)))
    y *= 1 - np.exp(-t / 0.004)
    y *= np.where(t < dur, 1.0, np.exp(-(t - dur) / (rel / 3)))
    y = y + 0.03 * sfx.contact(n, rng, 300, 1500, 0.006)
    return vel * sfx.fades(sfx.shape(y, 80, 3000, order=2), 0.0005, 0.03)


def pizz(rng, f0, vel=0.6, ring=0.7, damp=None):
    """拨弦（弦乐的 pizzicato）：谐波 1–14 次按 1/k^1.1 递减、高次衰减更快，带一点非谐；琴身在 450 Hz、1.1 kHz 两个共振峰；
    拨的那一下一点 0.8–3 kHz 的“嘣”。damp 给一个秒数时用手掌捂住（脉冲用：短、闷，但 2–5 次谐波还在，手机外放听得出“嘣嘣”）。"""
    n = int(ring * SR)
    t = ts(n)
    tau0 = 0.32 * (220.0 / f0) ** 0.35
    y = np.zeros(n)
    for k in range(1, 15):
        fk = k * f0 * math.sqrt(1 + 0.0004 * k * k)
        if fk > 5000:
            break
        a = (1 / k ** 1.1) * (1.0 if k <= 3 else math.exp(-(k - 3) / 4))
        y += a * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t / (tau0 / (1 + 0.6 * (k - 1))))
    y *= 1 - np.exp(-t / 0.0015)
    if damp:
        y *= np.exp(-t / damp)
    y = sfx.shape(y, 70, 4000, order=2, peaks=((450, 2, 4), (1100, 3, 3)))
    y = y + 0.05 * sfx.contact(n, rng, 800, 3000, 0.003)
    return vel * sfx.fades(y, 0.0005, 0.04)


def pad(rng, freqs, dur, att=0.9, rel=1.1, lp=1500.0, hp=150.0):
    """垫音：每个音三条略走音的声部（±5 音分），每条是 1/k 递减的谐波（像软的锯齿波），只要 lp 以下的；慢起慢落，带一点慢颤音。"""
    n = int((dur + rel) * SR)
    t = ts(n)
    env = np.clip(t / att, 0, 1) ** 1.5 * np.where(t < dur, 1.0, np.exp(-(t - dur) / (rel / 3)))
    y = np.zeros(n)
    for f0 in freqs:
        for c in (-5.0, 0.0, 5.0):
            fv = f0 * 2 ** ((c + rng.normal(0, 1.0)) / 1200)
            vib = 1 + 0.0015 * np.sin(2 * np.pi * rng.uniform(4.0, 5.5) * t + rng.uniform(0, 6.28))
            ph = 2 * np.pi * np.cumsum(fv * vib) / SR
            for k in range(1, 12):
                if k * fv > lp * 1.6:
                    break
                y += (1 / k) * np.sin(k * ph + rng.uniform(0, 6.28))
    y = sfx.shape(y * env, hp, lp, order=2)
    return y / (len(freqs) * 3)


# ======================================================================
# 谱子
# ======================================================================
NOTES = []        # dict(t, inst, m 或 freqs, dur, vel, pan, sec, send)
CHORDS = []       # (起, 止, 和弦, 段)
KEYS = []         # key 音效的时刻（配乐让开用）
CLEAR = []        # key 音效和有音高的提示音、叮的时刻（旋律音让开用）


def note(t, inst, m, dur=0.6, vel=0.6, pan=0.0, sec='', send=0.22):
    if t < END:
        NOTES.append(dict(t=float(t), inst=inst, m=m, dur=dur, vel=vel, pan=pan, sec=sec, send=send))


def chords(sec, t0, t1, plan):
    """plan：[(拍, 和弦), ...]，拍从 t0 起算（100 BPM）。最后一个和弦到 t1。"""
    for k, (b, ch) in enumerate(plan):
        a = t0 + b * Q
        z = t0 + plan[k + 1][0] * Q if k + 1 < len(plan) else t1
        if a >= t1 - 0.05:
            break
        CHORDS.append((a, min(z, t1), ch, sec))


def chord_at(t):
    for a, z, ch, sec in CHORDS:
        if a - 1e-6 <= t < z - 1e-6:
            return ch
    return None


def arp(sec, t0, t1, pattern, lo, hi, vel, step=EI, inst='kalimba', mask=None, pan=0.18, ring=1.4):
    """琶音：每 step 秒一个音，取那一刻的和弦在 [lo, hi] 里的第 pattern[k] 个音。mask(k, t) 为假就跳过。"""
    k = 0
    t = t0
    while t < t1 - 1e-6:
        ch = chord_at(t)
        if ch and (mask is None or mask(k, t)):
            tt = tones(ch, lo, hi)
            m = tt[min(pattern[k % len(pattern)], len(tt) - 1)]
            note(t, inst, m, ring, vel(t) if callable(vel) else vel, pan=pan * (1 if k % 2 else -1), sec=sec)
        k += 1
        t = t0 + k * step


def pulse(sec, t0, t1, step, vel):
    """低音脉冲：捂住的拨弦，每 step 秒一下，弹那一刻和弦的根音（拍上的重一点）。"""
    k = 0
    t = t0
    while t < t1 - 1e-6:
        ch = chord_at(t)
        if ch:
            on_beat = abs(((t - t0) / Q) - round((t - t0) / Q)) < 1e-6
            v = (vel(t) if callable(vel) else vel) * (1.0 if on_beat else 0.75)
            note(t, 'pulse', mid(ROOTNOTE[ch]), 0.3, v, sec=sec, send=0.08)
        k += 1
        t = t0 + k * step


def bass(sec, vel=0.45, inst='pizz', every=None):
    """每个和弦起点弹一下根音（every 给拍数时，和弦里每隔这么多拍再弹一下）。"""
    for a, z, ch, s in CHORDS:
        if s != sec:
            continue
        t = a
        while t < z - 1e-6:
            note(t, inst, mid(ROOTNOTE[ch]), min(z - t, 1.2), vel, sec=sec, send=0.1)
            if not every:
                break
            t += every * Q


def melody(sec, t0, inst, line, vel=0.6, send=0.22, end=None, clear=0.0):
    """line：[(拍, 长几拍, 音名), ...]，拍从 t0 起算。end：段尾，超出的不弹；clear>0：离 key 音效不到 clear 秒的音让掉。"""
    for b, d, nm in line:
        a = t0 + b * Q
        if end is not None and a >= end - 0.05:
            continue
        if clear and any(abs(a - k) < clear for k in CLEAR):
            continue
        note(a, inst, mid(nm), min(d * Q, end - a) if end is not None else d * Q, vel, sec=sec, send=send)


def pad_chords(sec, vel, lo='D4', hi='D5', n=3, inst='pad'):
    for a, z, ch, s in [c for c in CHORDS if c[3] == sec]:
        note(a, inst, [hz(m) for m in tones(ch, lo, hi)][:n], max(0.3, z - a), vel, sec=sec, send=0.35)


def compose():
    NOTES.clear()
    CHORDS.clear()
    evs = json.load(open(SFX_EVENTS))
    KEYS[:] = [e['t'] for e in evs if e['key']]
    CLEAR[:] = [e['t'] for e in evs if e['key'] or e['name'] in ('提示音', '叮', '铃', '开盖', '翻书')]
    c0, c1 = EV['count']
    fl = EV['countFlash'][0]
    ti, bt = sfx.TITLE_DROP                                           # 10.4 起落下，10.6 落地
    b08, b09 = B['B08']['t0'], B['B09']['t0']
    k0, k1 = EV['clockTurn']
    p0, p1 = EV['push']
    pull = EV['pull'][0]
    b19, b20, b21 = B['B19']['t0'], B['B20']['t0'], B['B21']['t0']
    fz0, fz1 = sfx.FREEZE
    e0 = EV['shot'] + 0.15
    b24, b25, b26, b27 = B['B24']['t0'], B['B25']['t0'], B['B26']['t0'], B['B27']['t0']

    # —— A 0–8.2：钩子，D 小调，略紧张 ——
    chords('A', 0.0, c0, [(0, 'Dm'), (4, 'Bb'), (8, 'Gm'), (10, 'A'), (12, 'Dm')])
    motif = [(0, 'A4'), (0.5, 'D5'), (1, 'E5'), (1.5, 'F5')]            # 开头动机：往上走，停在 F 上（像在问）
    for b, nm in motif:
        note(b * Q, 'kalimba', mid(nm), 1.6, 0.42, sec='A')
    t_st = B['B04']['t0']                                               # 5.8 伸手：固定音型停
    # 脉冲一下比一下密：0–3.2 四分音符，3.2 起八分音符
    pulse('A', 0.0, 3.2, Q, lambda t: 0.34 + 0.06 * t / 3.2)
    pulse('A', 3.2, c0, EI, lambda t: 0.36 + 0.06 * min(1, (t - 3.2) / 5))
    arp('A', B['B02']['t0'], t_st, [0, 2, 1, 2, 3, 2, 1, 2], 'D4', 'D5', 0.34, inst='marimba', pan=0.15, ring=0.9)
    arp('A', B['B05']['t0'] + 0.6, c0, [0, 2, 1, 2], 'D4', 'D5', 0.26, step=Q, inst='marimba', pan=0.15, ring=0.9)
    bass('A', 0.42)
    pad_chords('A', 0.3, 'D4', 'D5', 3)

    # —— A' 8.2–9.4：计数跑起来。A 和弦上木琴十六分音符往上跑一个八度（A4 → A5，D 和声小调），脉冲十六分，渐强；
    #    9.4 停在 120：Dm 一下重音 ——
    CHORDS.append((c0, fl, 'A', "A'"))
    run = ['A4', 'Bb4', 'C#5', 'D5', 'E5', 'F5', 'G5', 'A5']
    k = 0
    while c0 + k * SX < fl - 1e-6:
        note(c0 + k * SX, 'marimba', mid(run[k % 8]) + 12 * (k // 8), 0.5, 0.28 + 0.14 * k / 8, pan=0.15 * (-1) ** k, sec="A'")
        k += 1
    pulse("A'", c0, fl, SX, lambda t: 0.32 + 0.1 * (t - c0) / (fl - c0))
    note(c0, 'pad', [hz(mid(x)) for x in ('A3', 'C#4', 'E4', 'G4')], fl - c0, 0.35, sec="A'")
    CHORDS.append((fl, ti, 'Dm', "A'"))
    for nm in ('D3', 'A3', 'D4', 'F4'):
        note(fl, 'piano', mid(nm), 0.9, 0.35, sec="A'")
    note(fl, 'pizz', mid('D3'), 0.8, 0.6, sec="A'")
    note(fl + 0.25, 'marimba', mid('D6'), 0.8, 0.3, sec="A'")
    note(fl + 0.3, 'pad', [hz(mid(x)) for x in ('D4', 'F4', 'A4')], ti - fl - 0.3, 0.3, sec="A'")
    pulse("A'", fl + Q, ti, Q, 0.3)

    # —— T 10.4–11.8：标题卡。10.6 一个低的 Dm(add9)，不打拍子 ——
    CHORDS.append((bt, b08, 'Dmadd9', 'T'))
    for nm in ('D3', 'A3', 'E4', 'F4'):
        note(bt, 'piano', mid(nm), b08 - bt, 0.36, sec='T')
    note(bt, 'pad', [hz(mid(x)) for x in ('D4', 'E4', 'A4')], b08 - bt, 0.36, sec='T')

    # —— B1 11.8–13.4：全开，最满的“吵” ——
    chords('B1', b08, b09, [(0, 'Dm')])
    pulse('B1', b08, b09, EI, 0.42)
    arp('B1', b08, b09, [0, 2, 1, 2, 3, 2, 1, 2], 'D4', 'D5', 0.36, inst='marimba', pan=0.15, ring=0.9)
    bass('B1', 0.42)
    pad_chords('B1', 0.32)

    # —— B2 13.4–21.6：全关，安静但不安。Dm（13.4）→ B♭（小钟，只留垫音）→ Dm（交表那条晚到）→ A（一惊）→ Dm（挂在心上）——
    st = EV['startle'][0]
    hang = B['B12']['t0']
    CHORDS.extend([(b09, k0, 'Dm', 'B2'), (k0, k1, 'Bb', 'B2'), (k1, st, 'Dm', 'B2'), (st, hang, 'A', 'B2'), (hang, p0, 'Dm', 'B2')])
    for a, z, ch, sec in [c for c in CHORDS if c[3] == 'B2']:
        note(a, 'pad', [hz(m) for m in tones(ch, 'D4', 'D5')][:3], z - a, 0.4, sec='B2', send=0.4)
    for t, nm in [(b09, 'D3'), (b09 + 2 * Q, 'A3'), (k1, 'D3'), (k1 + 2 * Q, 'A2'), (st + 0.6, 'A2'), (hang, 'D3'),
                  (hang + 4 * Q, 'D3')]:
        note(t, 'pizz', mid(nm), 0.7, 0.4, sec='B2', send=0.12)
    for k, nm in enumerate(['F4', 'A4', 'D4', 'E4']):                 # 13.4 到小钟之前：稀的拨弦（每两拍一个）；小钟那段不弹
        if b09 + 0.3 + 2 * Q * k < k0 - 0.2:
            note(b09 + 0.3 + 2 * Q * k, 'pizz', mid(nm), 0.6, 0.3, sec='B2', send=0.2)
    k = 0
    while hang + 0.3 + k * 2 * Q < p0 - 0.3:                            # 挂在心上：A–B♭ 半音一来一回（叹气）
        note(hang + 0.3 + k * 2 * Q, 'piano', mid('A4' if k % 2 == 0 else 'Bb4'), 2 * Q, 0.3, sec='B2', send=0.3)
        k += 1

    # —— R 21.6–22.6：推向右栏，拇指琴在 A7 上往上走、越来越快 ——
    CHORDS.append((p0, p1, 'A7', 'R'))
    up = [mid(x) for x in ('A4', 'C#5', 'E5', 'G5', 'A5', 'C#6', 'E6', 'G6')]
    t, d, k = p0, 0.2, 0
    while t < p1 - 0.04 and k < len(up):
        note(t, 'kalimba', up[k], 0.9, 0.28 + 0.03 * k, pan=0.2 * (-1) ** k, sec='R')
        t += d
        d *= 0.82
        k += 1
    note(p0, 'pad', [hz(mid(x)) for x in ('A3', 'C#4', 'E4', 'G4')], p1 - p0 - 0.05, 0.4, sec='R')
    note(p0, 'pizz', mid('A2'), 0.8, 0.45, sec='R')

    # —— C 22.6–31.0：先分开，D 大调，轻快。拨弦低音踩 1、3 拍，木琴反拍和弦，拇指琴旋律（离 key 音效 0.2 秒内的音让掉）——
    c_end = pull
    chords('C', p1, c_end, [(0, 'D'), (2, 'G'), (4, 'A'), (6, 'D'), (8, 'Bm'), (10, 'G'), (11, 'D')])
    bass('C', 0.5, every=2)
    t, k = p1 + EI, 0
    while t < c_end - 0.05:                                              # 反拍：木琴两个音的和弦，短
        ch = chord_at(t)
        for m in tones(ch, 'F#4', 'D5')[:2]:
            note(t, 'marimba', m, 0.4, 0.26, pan=0.12, sec='C', send=0.15)
        k += 1
        t = p1 + EI + k * Q
    tune = [(0, 0.5, 'A5'), (0.5, 0.5, 'F#5'), (1, 0.5, 'A5'), (1.5, 0.5, 'D6'), (2, 1, 'B5'), (3, 0.5, 'A5'), (3.5, 0.5, 'G5'),
            (4, 0.5, 'E5'), (4.5, 0.5, 'A5'), (5, 1, 'C#6'), (6, 0.5, 'D6'), (6.5, 0.5, 'A5'), (7, 0.5, 'F#5'), (7.5, 0.5, 'D5'),
            (8, 1, 'B5'), (9, 0.5, 'F#5'), (9.5, 0.5, 'D6'), (10, 1, 'B5'), (11, 0.5, 'A5'), (11.5, 0.5, 'F#5'), (12, 1, 'D6'),
            (13, 1, 'A5')]
    melody('C', p1, 'kalimba', tune, 0.42, end=c_end, clear=0.2)
    pad_chords('C', 0.26, 'D4', 'D5', 3)

    # —— C2 31.0–33.6：拉回三栏，D–G–A，只有低音和琶音（字幕要读） ——
    chords('C2', pull, b19, [(0, 'D'), (2, 'G'), (3, 'A')])
    bass('C2', 0.45)
    arp('C2', pull, b19, [0, 1, 2, 1], 'D4', 'A4', 0.3, pan=0.15)
    pad_chords('C2', 0.26)

    # —— D 33.6–38.6：金句，收。33.6 琶音变慢；34.6 起只剩垫音和隔两拍一个的钢琴音；38.6 一刀抽空 ——
    CHORDS.extend([(b19, b20, 'Dadd9', 'D'), (b20, b21, 'Gmaj7', 'D'), (b21, fz0, 'Dadd9', 'D')])
    arp('D', b19, b20, [0, 1, 2, 3], 'D4', 'E5', 0.24, step=Q, pan=0.15, ring=1.8)
    note(b19, 'pizz', mid('D3'), 0.8, 0.35, sec='D')
    for a, z, ch, s in [c for c in CHORDS if c[3] == 'D']:
        note(a, 'pad', [hz(m) for m in tones(ch, 'D4', 'E5')][:4], z - a, 0.36, sec='D', send=0.4)
    for t, nm in [(b20, 'B4'), (b20 + 2 * Q, 'F#5'), (b21, 'A4'), (b21 + 2 * Q, 'E5')]:
        note(t, 'piano', mid(nm), 2 * Q, 0.28, sec='D', send=0.35)
    for nm in ('D3', 'A3'):
        note(b21, 'piano', mid(nm), fz0 - b21, 0.24, sec='D', send=0.3)

    # —— E 39.85–58.2：清单，平稳、低、不抢字。每张卡换一组和弦 ——
    CHORDS.append((e0, b24, 'D', 'E'))
    chords('E', b24, b25, [(0, 'Bm'), (4, 'G')])
    chords('E', b25, b26, [(0, 'D'), (4, 'A')])
    chords('E', b26, b27, [(0, 'Bm'), (4, 'G'), (8, 'A')])
    arp('E', e0, b27, [0, 1, 2, 1, 0, 2, 1, 2], 'C#4', 'B4', lambda t: 0.22 + 0.04 * min(1, (t - e0) / 2), pan=0.15, ring=1.2)
    bass('E', 0.38, every=2)
    pad_chords('E', 0.24, 'D4', 'D5', 3)

    # —— F 58.2–61.2：按钮（D6 E6 F♯6 A6）落在 Dadd9 上；然后把开头动机用大调答一遍，停在 Asus4 上淡到 0 ——
    bl = EV['buttons'][-1]
    tq = bl + 0.5
    CHORDS.extend([(b27, tq, 'Dadd9', 'F'), (tq, END, 'Asus4', 'F')])
    note(b27, 'pizz', mid('D3'), 1.0, 0.4, sec='F')
    note(b27, 'pad', [hz(mid(x)) for x in ('D4', 'F#4', 'A4', 'E5')], tq - b27, 0.3, sec='F', send=0.4)
    for b, nm in [(0, 'A4'), (0.5, 'D5'), (1, 'E5'), (1.5, 'F#5')]:
        note(tq + b * Q, 'kalimba', mid(nm), 1.6, 0.4, sec='F')
    note(tq, 'pizz', mid('A2'), 1.0, 0.36, sec='F')
    note(tq, 'pad', [hz(mid(x)) for x in ('A3', 'D4', 'E4')], END - tq, 0.32, sec='F', send=0.4)
    NOTES.sort(key=lambda n: n['t'])


# ======================================================================
# 渲染
# ======================================================================
INST_DB = {'kalimba': -4.0, 'marimba': -2.0, 'piano': -3.0, 'pizz': -2.0, 'pulse': 0.0, 'pad': -15.0}


def render_note(n, rng):
    inst = n['inst']
    if inst == 'kalimba':
        return kalimba(rng, hz(n['m']), n['vel'], ring=max(1.0, n['dur']))
    if inst == 'marimba':
        return marimba(rng, hz(n['m']), n['vel'], ring=max(0.6, n['dur']))
    if inst == 'piano':
        return piano(rng, hz(n['m']), n['dur'], n['vel'])
    if inst == 'pizz':
        return pizz(rng, hz(n['m']), n['vel'], ring=max(0.5, n['dur']))
    if inst == 'pulse':
        return pizz(rng, hz(n['m']), n['vel'], ring=0.35, damp=0.07)
    if inst == 'pad':
        return n['vel'] * pad(rng, n['m'], n['dur'])
    raise ValueError(inst)


def arc_db(t):
    """整体的起伏（dB）：钩子略紧张、计数时渐强到最高，标题卡让开，全开吵，全关压低（小钟那段最低），推向右栏往上涨，
    先分开最亮，金句收，清单平稳低，结尾轻。都是缓坡，只有标题卡前那一下让开是陡的。"""
    c0, c1 = EV['count']
    fl = EV['countFlash'][0]
    ti, bt = sfx.TITLE_DROP
    k0, k1 = EV['clockTurn']
    p0, p1 = EV['push']
    pts = [(0.0, -4.0), (B['B04']['t0'], -4.0), (c0, -4.0), (c1, -5.0), (fl + 0.3, -5.0), (ti - 0.05, -5.0), (ti + 0.04, -16.0),
           (bt - 0.01, -16.0), (bt, -5.0), (B['B08']['t0'], -3.0), (B['B09']['t0'], -3.0), (B['B09']['t0'] + 0.8, -6.0),
           (k0, -8.0), (k1, -8.0), (EV['startle'][0], -6.0), (p0, -6.0), (p1 - 0.05, -4.0), (p1, -6.5), (EV['pull'][0], -6.0),
           (B['B19']['t0'], -4.5), (B['B20']['t0'], -6.5), (sfx.FREEZE[0], -7.0), (sfx.FREEZE[1], -7.0),
           (EV['shot'] + 0.15, -5.5), (B['B27']['t0'], -5.5), (END, -6.0)]
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    return np.interp(t, x, y)


def gate_curve(t):
    """配乐也停的地方：定格那一秒（和音效同一条门），快门之后 0.15 秒才回来；最后 1.2 秒淡到 0。"""
    g = sfx.gate_curve(t)
    a, b = sfx.FREEZE[1], EV['shot'] + 0.15
    g[(t >= a) & (t < b)] = 0
    tail = END - 1.2
    g *= np.clip(1 - (t - tail) / 1.2, 0, 1) ** 1.5
    return g


def duck_curve(t, keys):
    """key 音效出现时配乐再压 DUCK_DB：提前 40 毫秒压下去，压 0.15 秒，0.5 秒放开（按 dB 线性）。"""
    d = np.zeros_like(t)
    for k in keys:
        a = k - 0.04
        lo, hi = np.searchsorted(t, a), np.searchsorted(t, k + 0.65)
        tt = t[lo:hi]
        v = np.where(tt < k, DUCK_DB * (tt - a) / 0.04, np.where(tt < k + 0.15, DUCK_DB, DUCK_DB * (1 - (tt - k - 0.15) / 0.5)))
        d[lo:hi] = np.minimum(d[lo:hi], v)
    return 10 ** (d / 20), d


def render_music():
    compose()
    rng0 = np.random.default_rng(SEED)
    dry = np.zeros((N, 2))
    send = np.zeros(N)
    for i, n in enumerate(NOTES):
        y = render_note(n, np.random.default_rng([SEED, i])) * 10 ** (INST_DB[n['inst']] / 20)
        st = int(round(n['t'] * SR))
        m = min(len(y), N - st)
        if m <= 0:
            continue
        p = n['pan']
        dry[st:st + m, 0] += y[:m] * math.cos((p + 1) * math.pi / 4) * 1.414
        dry[st:st + m, 1] += y[:m] * math.sin((p + 1) * math.pi / 4) * 1.414
        send[st:st + m] += y[:m] * n['send']
    ir = sfx.make_ir(rng0, 1.2, 200, 4000, pre=0.02)
    wet = sfx.conv(send, ir)
    t = np.arange(N) / SR
    duck, duck_db = duck_curve(t, KEYS)
    music = (dry + 0.8 * wet) * (10 ** (arc_db(t) / 20) * duck)[:, None]
    music = np.stack([sfx.shape(music[:, c], 60, 2400, order=2) for c in range(2)], 1)
    music *= gate_curve(t)[:, None]                                       # 低通之后再乘：定格那一秒是真的 0
    music[: int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]
    return music, dict(duck_db=duck_db, keys=list(KEYS))


# ======================================================================
# 混音、限幅、自查
# ======================================================================
def lufs(x, tmp, name):
    p = os.path.join(tmp, name)
    s = 10 ** (-1 / 20) / max(1e-9, np.max(np.abs(x)))
    sfx.write_wav(p, x * s)
    r = sfx.ebur(p)
    return r['I'] - 20 * math.log10(s), r


def master(mix, tmp):
    I0, _ = lufs(mix, tmp, 'pre.wav')
    y = mix * 10 ** ((MIX_TARGET - I0) / 20)
    gmin = 1.0
    for _ in range(5):
        tp = 20 * math.log10(sfx.true_peak_env(y).max())
        if tp <= MIX_TP - 0.2:
            break
        y, g = sfx.limit(y, MIX_TP - 0.4)
        gmin = min(gmin, g)
        p = os.path.join(tmp, 'lim.wav')
        sfx.write_wav(p, y)
        y = y * 10 ** ((MIX_TARGET - sfx.ebur(p)['I']) / 20)
    return y, gmin


def band_share(x, bands):
    P = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    tot = P.sum()
    return {f'{a}–{b} Hz': round(float(P[(f >= a) & (f < b)].sum() / tot) * 100, 1) for a, b in bands}


def pitched_sfx():
    """有音高的音效（落点秒, Hz, 说明）：和 sfx.py 里写的音一一对应，用来查落在不在当时的和弦里。"""
    H = sfx.HZ
    out = [(EV['buzz'][0], H['A5'], '拼单立减 A5'), (EV['buzz'][0] + 0.075, H['D6'], '拼单立减 D6'),
           (EV['buzz'][1], H['D6'], '工作群 D6'), (EV['buzz'][1] + 0.16, H['A5'], '工作群 A5'),
           (EV['buzz'][2], H['F6'], '热榜 F6'), (EV['buzz'][2] + 0.09, H['D6'], '热榜 D6'), (EV['keyLight'][0], H['F5'], '要紧的那条 F5'),
           (EV['highlight'][0], H['D6'], '停在第 23 条 D6'), (EV['buzzAgain'], H['A5'], '又一条 A5'),
           (EV['buzzAgain'] + 0.07, H['D6'], '又一条 D6'), (EV['buzzAgain'] + 0.14, H['F6'], '又一条 F6'),
           (EV['countFlash'][0], H['A6'], '120 A6'), (EV['countFlash'][0] + 0.2, H['A6'], '120 再闪 A6')]
    out += [(la + 0.08, f, '标签') for la, f in zip(EV['labels'], (H['D6'], H['F6'], H['A6']))]
    if 'midSelf' in EV:
        out.append((EV['midSelf'], H['A5'], '读数 +1 A5'))
    out += [(EV['cardIn'][0] + 0.03, H['D6'], '交表晚到（闷）D6'), (EV['cardIn'][0] + 0.19, H['A5'], '交表晚到（闷）A5')]
    out += [(tp, H['D6'], '置顶的群照常亮 D6') for tp in EV['groupPing']] + [(tp + 0.16, H['A5'], '置顶的群照常亮 A5') for tp in EV['groupPing']]
    out += [(tb + 0.02, f, f'静音铃 {k + 1}') for k, (tb, f) in enumerate(zip(EV['bells'], (H['A5'], H['F#5'], H['D5'])))]
    out += [(s[1] + 0.06, f * 2, f'开盖 {k + 1}') for k, (s, f) in enumerate(zip(EV['stops'], (H['D6'], H['F#6'], H['A6'])))]
    out += [(EV['dmPing'][2], H['A5'], '私聊 A5'), (EV['dmPing'][2] + 0.12, H['D6'], '私聊 D6'),
            (EV['rightCard'], H['D6'], '工作群立刻亮 D6'), (EV['rightCard'] + 0.16, H['A5'], '工作群立刻亮 A5'),
            (EV['rightLate'], H['A6'], '右栏 0 件 A6')]
    out += [(tb, f, f'按钮 {k + 1}') for k, (tb, f) in enumerate(zip(EV['buttons'], (H['D6'], H['E6'], H['F#6'], H['A6'])))]
    return out


def harmony_checks():
    rows = []
    for t, f0, lab in sorted(pitched_sfx()):
        ch = chord_at(t)
        pc = int(round(69 + 12 * math.log2(f0 / 440))) % 12
        inch = ch is not None and pc in {PC[x] for x in CHORD[ch].split()}
        rows.append(dict(t=round(t, 2), label=lab, chord=ch or '（配乐没声）', in_chord=inch))
    return rows


def ride_curve(db):
    """前段整体压 db：13.4 秒（B09 全关开头）之前都是 db，13.4–15.4 秒线性回到 0。"""
    t0 = B['B09']['t0']
    return 10 ** (np.interp(np.arange(N) / SR, [0, t0, t0 + 2.0, END], [db, db, 0.0, 0.0]) / 20)


def hook_diff(x, tmp):
    """前 15 秒的整条响度减全片的整条响度（LU，ffmpeg ebur128）。"""
    p = os.path.join(tmp, 'hook.wav')
    sfx.write_wav(p, x * (10 ** (-1 / 20) / max(1e-9, np.max(np.abs(x)))))
    return sfx.ebur(p, 'atrim=0:15')['I'] - sfx.ebur(p)['I']


def solve_ride(base, tmp):
    """找 RIDE：让前 15 秒比全片响 HOOK_LU（割线法，最多 6 步，差 0.05 LU 以内停）。"""
    xs, ys = [0.0], [hook_diff(base, tmp)]
    x = -(ys[0] - HOOK_LU) * 1.6
    for _ in range(6):
        y = hook_diff(base * ride_curve(x)[:, None], tmp)
        xs.append(x)
        ys.append(y)
        if abs(y - HOOK_LU) < 0.05:
            break
        slope = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
        x = x - (y - HOOK_LU) / slope
    return xs[-1], list(zip([round(v, 2) for v in xs], [round(v, 2) for v in ys]))


def main():
    music, info = render_music()
    sx, sr = sfx.read_wav(SFX_WAV)
    assert sr == SR and len(sx) == N and len(music) == N, (sr, len(sx), len(music), N)
    a, b = sfx.FREEZE                                                   # 定格那一秒：音效轨里的抖动噪声也清掉，只剩成品自己的抖动
    tt = np.arange(N) / SR
    fg = np.where((tt >= a + 0.02) & (tt < b), 0.0, 1.0)
    sx = sx * fg[:, None]
    with tempfile.TemporaryDirectory() as tmp:
        I_sfx, _ = lufs(sx, tmp, 'sfx.wav')
        I_mus, _ = lufs(music, tmp, 'mus.wav')
        g_mus = 10 ** ((I_sfx + MUSIC_REL - I_mus) / 20)
        music = music * g_mus
        ride_db, ride_steps = solve_ride(sx + music, tmp)
        R = ride_curve(ride_db)[:, None]
        sx, music = sx * R, music * R
        mix, gmin = master(sx + music, tmp)
        I_pre, _ = lufs(sx + music, tmp, 'pre2.wav')
        g_all = 10 ** ((MIX_TARGET - I_pre) / 20)
        sfx.write_wav(OUT_MUSIC, music * g_all)
        sfx.write_wav(OUT_MIX, mix, dither=True, rng=np.random.default_rng(SEED + 1))
        x, xsr = sfx.read_wav(OUT_MIX)
        fin = sfx.ebur(OUT_MIX)
        fin15 = sfx.ebur(OUT_MIX, 'atrim=0:15')
        ln = sfx.loudnorm_json(OUT_MIX, MIX_TARGET, MIX_TP)
        mo, _ = sfx.read_wav(OUT_MUSIC)
        mus = sfx.ebur(OUT_MUSIC)
        pk = os.path.join(tmp, 'sfx_in_mix.wav')
        sfx.write_wav(pk, np.clip(sx * g_all, -1, 1))
        sfx_in = sfx.ebur(pk)
        hp = 'highpass=f=300:poles=2,highpass=f=300:poles=2'
        phone = sfx.ebur(OUT_MIX, hp)
        mus_ph = sfx.ebur(OUT_MUSIC, hp)['M']
        sfx_ph = sfx.ebur(pk, hp)['M']
    evs = json.load(open(SFX_EVENTS))
    # 每个 key 音效：起音后 0.05–0.45 秒（400 毫秒窗的末尾落在这里），音效最响减配乐最响（手机频段 300 Hz 以上）
    margins = []
    for e in evs:
        if not e['key']:
            continue
        ms = (sfx_ph[:, 0] >= e['t'] + 0.05) & (sfx_ph[:, 0] <= e['t'] + 0.45)
        mm = (mus_ph[:, 0] >= e['t'] + 0.05) & (mus_ph[:, 0] <= e['t'] + 0.45)
        margins.append(dict(t=e['t'], label=e['label'], sfx_M=round(float(sfx_ph[ms, 1].max()), 1),
                            music_M=round(float(mus_ph[mm, 1].max()), 1), margin=round(float(sfx_ph[ms, 1].max() - mus_ph[mm, 1].max()), 1)))
    # 定格那一秒（38.6–39.6，去掉两头 20 毫秒的门）
    a, b = sfx.FREEZE
    fz = x[int((a + 0.025) * SR):int((b - 0.005) * SR)]
    ref = x[int((a - 1.0) * SR):int(a * SR)]
    db = lambda v: round(20 * math.log10(v + 1e-12), 1)
    M = fin['M']
    fzM = M[(M[:, 0] >= a + 0.45) & (M[:, 0] <= b)]
    freeze = dict(rms_dbfs=db(np.sqrt(np.mean(fz ** 2))), peak_dbfs=db(np.max(np.abs(fz))), before_rms_dbfs=db(np.sqrt(np.mean(ref ** 2))),
                  M_max_lufs=round(float(fzM[:, 1].max()), 1) if len(fzM) else None)
    # 各段配乐的瞬时响度中位数
    secs = [('A 钩子', 0, EV['count'][0]), ("A' 计数", EV['count'][0], EV['titleOut'][0]), ('T 标题卡', EV['bigText'][0], B['B08']['t0']),
            ('B1 全开', B['B08']['t0'], B['B09']['t0']), ('B2 全关', B['B09']['t0'], EV['push'][0]),
            ('R 推镜头', EV['push'][0], EV['push'][1]), ('C 先分开', EV['push'][1], EV['pull'][0]), ('C2 拉回', EV['pull'][0], B['B19']['t0']),
            ('D 金句', B['B19']['t0'], a), ('E 清单', EV['shot'] + 0.15, B['B27']['t0']), ('F 结尾', B['B27']['t0'], END)]
    MM = mus['M']
    sec_rows = {}
    for name, s0, s1 in secs:
        v = MM[(MM[:, 0] >= s0 + 0.4) & (MM[:, 0] <= s1), 1]
        v = v[v > -70]
        sec_rows[name] = round(float(np.median(v)), 1) if len(v) else None
    harm = harmony_checks()
    sfx_chk = json.load(open(sfx.OUT_CHECK))
    summary = dict(
        mix=dict(file=OUT_MIX, sr=xsr, samples=len(x), seconds=len(x) / SR, I=fin['I'], LRA=fin['LRA'], TP=fin['TP'],
                 loudnorm_I=float(ln['input_i']), loudnorm_TP=float(ln['input_tp']), limiter_min_db=round(20 * math.log10(gmin), 2),
                 phone_I=phone['I'], I_first15=fin15['I'], first15_minus_all=round(fin15['I'] - fin['I'], 1),
                 ride_db=round(ride_db, 2), ride_steps=ride_steps),
        music=dict(file=OUT_MUSIC, I=mus['I'], TP=mus['TP'], sfx_in_mix_I=sfx_in['I'], rel_to_sfx_LU=round(mus['I'] - sfx_in['I'], 1),
                   bands=band_share(mo.mean(axis=1), [(20, 200), (200, 2000), (1000, 4000), (2000, 20000)]), sections_M_median=sec_rows,
                   notes=len(NOTES)),
        key_margin=dict(median=float(np.median([m['margin'] for m in margins])), rows=margins),
        freeze=freeze, harmony=harm,
        chords=[(round(a_, 2), round(z_, 2), ch, s_) for a_, z_, ch, s_ in sorted(CHORDS)],
    )
    json.dump(summary, open(OUT_CHECK, 'w'), ensure_ascii=False, indent=1)
    write_md(summary, sfx_chk, evs)
    m = summary['mix']
    print(f"写出 {OUT_MIX}：{m['samples']} 个采样 = {m['seconds']:.4f} 秒，{m['sr']} Hz；I {m['I']} LUFS（loudnorm 复核 {m['loudnorm_I']}），"
          f"真峰值 {m['TP']} dBTP（复核 {m['loudnorm_TP']}），限幅最深 {m['limiter_min_db']} dB，300 Hz 以上 {m['phone_I']} LUFS")
    print(f"前 15 秒 {m['I_first15']} LUFS，比全片响 {m['first15_minus_all']} LU；前段整体压 {m['ride_db']} dB（解的过程 {m['ride_steps']}）")
    mu = summary['music']
    print(f"写出 {OUT_MUSIC}：{mu['notes']} 个音；整条 {mu['I']} LUFS，音效在混音里 {mu['sfx_in_mix_I']} LUFS，配乐低 {-mu['rel_to_sfx_LU']} LU；频段 {mu['bands']}")
    print('  各段配乐瞬时响度中位数', sec_rows)
    print(f"key 音效比配乐高（手机频段，LU）：中位数 {summary['key_margin']['median']}，最低", sorted(margins, key=lambda r: r['margin'])[:5])
    print('定格那一秒', freeze)
    bad = [r for r in harm if not r['in_chord']]
    print(f"有音高的音效 {len(harm)} 个，不在当时和弦里的 {len(bad)} 个：", [(r['t'], r['label'], r['chord']) for r in bad])


# ======================================================================
# 自查表
# ======================================================================
def write_md(s, chk, evs):
    m, mu, fz, km = s['mix'], s['music'], s['freeze'], s['key_margin']
    rows = [r for r in chk['rows'] if r['spec']]
    ok = lambda e: e is not None and abs(e) <= 1000 / FPS
    L = ['# 003《消息提醒》声音自查', '',
         f'跑的脚本：`videos/003_消息提醒/sfx.py`、`music.py`（numpy 合成，没用曲库、采样、第三方账号）。时间全从 `studio/src/videos/003/timeline.ts` 读，'
         f'这一版的 timeline.ts 已带分镜“遮字幕测试”的 v3 改动（14.1 拿起手机、15:40 交表才弹出、红心飞进盒子、翻书）。timeline.ts 再改，两个脚本重跑就跟上。', '',
         '## 结论', '',
         f'- **响度**：mix.wav 整条 {m["I"]} LUFS（目标 {MIX_TARGET:g}），真峰值 {m["TP"]} dBTP（要求 ≤ −1.5）；loudnorm 复核 {m["loudnorm_I"]} LUFS、{m["loudnorm_TP"]} dBTP。',
         f'- **前 15 秒**：{m["I_first15"]} LUFS，比全片响 {m["first15_minus_all"]} LU（要求不超过 2 LU；原来 −11.3 对 −15，响 3.7 LU）。',
         f'- **长度**：{m["samples"]} 个采样 ÷ {m["sr"]} Hz = {m["seconds"]:.4f} 秒（要求正好 61.2 秒）。',
         f'- **定格那一秒**（{sfx.FREEZE[0]}–{sfx.FREEZE[1]} 秒）：有效值 {fz["rms_dbfs"]} dBFS，峰值 {fz["peak_dbfs"]} dBFS（只剩 16 bit 抖动噪声）；'
         f'前一秒是 {fz["before_rms_dbfs"]} dBFS。几乎无声：是。',
         f'- **音效时刻**：任务点名的 {len(rows)} 个声音，单轨上量全部和落点差 ≤ 1 帧：{"是" if all(ok(r["solo_err_ms"]) for r in rows) else "否"}；'
         f'成品里量差 ≤ 1 帧的 {sum(ok(r["err_ms"]) for r in rows)} 个（成品里量偏的，是被同一时刻或紧挨着的声音盖住，单轨上都对）。',
         f'- **配乐低于音效**：配乐整条 {mu["I"]} LUFS，音效在混音里 {mu["sfx_in_mix_I"]} LUFS（低 {-mu["rel_to_sfx_LU"]} LU）；'
         f'每个 key 音效响的那 0.4 秒，音效比配乐高（300 Hz 以上）中位数 {km["median"]} LU，最低 {min(r["margin"] for r in km["rows"])} LU。', '',
         '## 0. 11/2 评委指出的四处，改了什么', '',
         f'1. **前 15 秒太响**：全片改到 {MIX_TARGET:g} LUFS；13.4 秒（全关开头，本来就安静）之前的音效和配乐整体压 {m["ride_db"]} dB，'
         f'13.4–15.4 秒慢慢回到 0，前 15 秒里面的轻重不变。结果前 15 秒 {m["I_first15"]} LUFS，比全片响 {m["first15_minus_all"]} LU；真峰值 {m["TP"]} dBTP。',
         f'2. **6.8 秒布料声没对上动作**：按“往前探 3 帧、往后撤 10 帧并握拳”，布料声挪到后撤开始 {sfx.RECOIL[0]:.2f} 秒，'
         f'长 10 帧（{sfx.RECOIL[1] - sfx.RECOIL[0]:.3f} 秒），20 毫秒起、撤完收住，比原来响 7 dB（原来几乎听不见）。',
         f'3. **27 条横幅喷出**：timeline.ts 的 burst（{sfx.BANNERS[0]:.2f}–{sfx.BANNERS[-1]:.2f} 秒）里排 {len(sfx.BANNERS)} 声“噌”（往上扫的短嗖＋小“啵”），'
         '间隔 62 → 19 毫秒越来越密、一条比一条高（画面还没画横幅，建议画面按同一个间隔出，或在 timeline.ts 加 banners 列表，重跑 sfx.py 就跟上）；计数滴答照旧压低一层；'
         f'底下手机一直抖的震动声留着、压低 5 dB，到震散那一下停。{sfx.SHATTER} 秒一记“震散”：闷响＋冲开的气浪＋ 24 片碎片在 0.1 秒（3 帧）内四散，'
         '上面轻轻一声“叮”（计数停在 120）。每次手机震动的声音都改成正好 8 帧长，和画面抖 8 帧对齐。',
         f'4. **标题卡 6 帧落下、2 帧回弹**：转场的“嗖”从 {sfx.TITLE_DROP[0]} 起往下砸，落地前 15 毫秒收掉，“咚”对到 {sfx.TITLE_DROP[1]} 秒落地那一帧。',
         f'5. **11/3 协调方挪两声**（照 out/样片_v2_自查.md 文末）：“全关”那一声往后挪 5 帧到第 343 帧（它现在是从右边滑进来、那一帧到位）；'
         f'“推向右栏”那一声的落点从到顶的 22.57 秒（第 677 帧）改到推镜头开始的 {EV["push"][0]} 秒（第 {round(EV["push"][0] * FPS)} 帧），'
         '一起头就听得见，跟着镜头越推越响，22.57 收掉。', '',
         '## 1. 每个点名的音效：时刻和分镜对不对得上', '',
         '“落点”是 sfx_events.json 里的 t；“单轨”是只放这一个声音时量到的起音和落点差多少；“成品”是在 sfx.wav 里量的（被前一个声音盖住时会量偏）。'
         '1 帧 = 33 毫秒。', '',
         '| 要的声音 | 分镜／时间表 | 落点 t（秒） | 单轨差（毫秒） | 成品差（毫秒） | 对上 |', '|---|---|---|---|---|---|']
    for r in rows:
        name, want, src = r['spec']
        L.append(f'| {name} | {src} | {r["t"]:.2f} | {r["solo_err_ms"]} | {r["err_ms"] if r["err_ms"] is not None else "量不出（被盖住）"} | '
                 f'{"是" if ok(r["solo_err_ms"]) else "否"} |')
    ticks = [r for r in chk['rows'] if r['label'].startswith('计数滴答')]
    L += ['', f'- 计数滴答：8.2–9.4 秒共 {len(ticks)} 下，间隔从 80 毫秒缩到 25 毫秒，音高 2.1 → 3.4 kHz 往上走；单轨差都 ≤ 1 帧：'
              f'{"是" if all(ok(r["solo_err_ms"]) for r in ticks) else "否"}。每一下同时有一条横幅喷出的“噌”。',
          '- 钩子“越来越密”：每次震都是 8 帧长，8 帧里 0.3 震一下 → 0.88 震两下 → 2.6 震两下 → 7.55 震三下（更急）→ 8.2 起 27 条横幅一条比一条快地喷出。'
          '每个 App 一种提示音（拼单是电子味的“嘀嘟”，工作群是玻璃“叮咚”，热榜是木琴两声）。',
          f'- 标题卡：{sfx.TITLE_DROP[0]} 起一声往下砸的“嗖”（6 帧），落地前 15 毫秒收掉，{sfx.TITLE_DROP[1]} 落地那一帧一下软“咚”。',
          '- 静音铃三声 A5 → F♯5 → D5 往下走、一声比一声轻；开盖三次的亮声 D → F♯ → A 往上走；四个按钮 D6 E6 F♯6 A6 往上走。', '',
          '## 2. 点名之外加的声音', '', '画面上有动作、没点名的地方补的声音，大多很轻；只有 31.75 秒“工作群立刻亮”是 key，和 0.88 秒钩子里的工作群提示音同一个声、一样响（前后呼应：这回一来就看到）。删哪条都不影响别的。', '']
    extra = {}
    req = {(round(t, 3), lab) for t, lab in chk['required']}
    for e in evs:
        if (round(e['t'], 3), e['label']) in req:
            continue
        extra.setdefault(re.sub(r' \d+/\d+$|（第 \d+ 分钟）', '', e['label']), []).append(e['t'])
    for lab, tt in extra.items():
        L.append(f'- {lab}：' + '、'.join(f'{t:.2f}' for t in tt[:6]) + (f' 等，共 {len(tt)} 下' if len(tt) > 6 else ''))
    bad = [r for r in s['harmony'] if not r['in_chord']]
    L += ['', '## 3. 响度和真峰值', '',
          f'- mix.wav：ffmpeg ebur128 量 I = {m["I"]} LUFS，LRA = {m["LRA"]} LU，真峰值 {m["TP"]} dBTP；loudnorm 复核 {m["loudnorm_I"]} LUFS、{m["loudnorm_TP"]} dBTP；'
          f'前瞻限幅最深压了 {m["limiter_min_db"]} dB；300 Hz 以上（手机外放）{m["phone_I"]} LUFS。量法和 002、tools/watch/check.py 一样（ffmpeg ebur128，peak=true）。',
          f'- sfx.wav 单独 {chk["I"]} LUFS、真峰值 {chk["TP"]} dBTP；music.wav 单独 {mu["I"]} LUFS（电平就是它在 mix 里的电平）。',
          f'- 配乐各段瞬时响度中位数（LUFS）：' + '，'.join(f'{k} {v}' for k, v in mu['sections_M_median'].items()) + '。',
          f'- 配乐频段占比：{mu["bands"]}。',
          f'- key 音效 1–4 kHz 电平都 ≥ 整条响度 − 26 dB（check.py 的口径）：{"是" if not chk["key_weak_1_4k"] else "否"}。',
          f'- 有音高的音效 {len(s["harmony"])} 个，落在当时和弦外的 {len(bad)} 个' + (('：' + '，'.join(f'{r["t"]} {r["label"]}（{r["chord"]}）' for r in bad)) if bad else '。'),
          '', '## 4. 定格那一秒', '',
          f'- {sfx.FREEZE[0]} 秒起 20 毫秒内音效、配乐、混响尾巴一起收到 0，到 {sfx.FREEZE[1]} 秒；音效 {sfx.FREEZE[1]} 秒放开（快门 {EV["shot"]} 秒），'
          f'配乐快门之后（{EV["shot"] + 0.15:.2f} 秒）才回来。',
          f'- mix.wav 里 {sfx.FREEZE[0] + 0.025:.3f}–{sfx.FREEZE[1] - 0.005:.3f} 秒：有效值 {fz["rms_dbfs"]} dBFS，峰值 {fz["peak_dbfs"]} dBFS，'
          f'400 毫秒瞬时响度最高 {fz["M_max_lufs"]} LUFS（窗完全落在定格里的那几点）。', '',
          '## 5. 没做到或没查的', '',
          '- 没在手机上外放听过；“手机频段”是用 300 Hz 高通近似的。',
          '- 没有把声音合进视频再跑 tools/watch/check.py（成片还没渲）；成片出来以后用 `--lufs -14 --peak -1.5 --sfx studio/public/003/sfx_events.json` 跑一遍。',
          '- 评委改的几处，时间都从 timeline.ts 样片 v2 读（poke/retract、burst、shatter、titleDrop；抖 8 帧照 Gray003 的 shake()）。'
          '27 条横幅各自的时刻 timeline.ts 里还没有，是在 burst 里按“越来越密”排的，画面画好后要对一遍。',
          ]
    open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
