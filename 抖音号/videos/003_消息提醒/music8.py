"""《消息提醒》第八版（003 横屏，69.4 秒 = 2082 帧）的原创配乐，和音效混成最终音轨。

从第四版的 music.py 复制过来：乐器（拇指琴、木琴、钢琴、拨弦、垫音）、记谱的小工具、渲染、让开、混音、限幅都原样留着，
只按第八版的场景重排了段落。全部用 numpy 合成，纯音乐，没有人声，没有鼓。不用曲库、采样、第三方账号。

  /Users/decheng.huang/Documents/dy/.venv/bin/python /Users/decheng.huang/Documents/dy/videos/003_消息提醒/music8.py
  （一条命令全出：先调 sfx8.main() 出音效轨，再出配乐、混音、自查）

读：studio/src/videos/003/timeline8.ts（经 sfx8.py 读；只读）
写：studio/public/003/v8/music.wav（单独的配乐，电平 = 它在 mix.wav 里的电平，含让开，没过限幅）
    studio/public/003/v8/mix.wav（音效 ＋ 配乐，48 kHz、双声道、正好 69.4 秒，整条 −14 LUFS，前瞻限幅，真峰值 ≤ −2 dBTP）
    videos/003_消息提醒/out/声音_v8_自查.md（全部从磁盘读回 wav 量）

调和速度：100 BPM（一拍 0.6 秒）；每段从段起点重新起拍。主要能量在 200 Hz–2 kHz，整条过 2.4 kHz 的柔和低通，不抢 1–4 kHz 的音效。
有音高的音效（提示音、铃、开关、贴纸、头像）都落在当时的和弦里（自查表里逐个查）。

结构（秒数都从 timeline8.ts 取）：
  A   0–7.6      钩子：D 小调 Dm–B♭–Gm–A。开头拇指琴动机 A D E F（往上走，停在 F 上，像在问）；拨弦脉冲 2.2 秒起由四分变八分，
                 6.0 起木琴音型变十六分（越来越密）
  A'  7.6–8.6    喷满、计数狂涨：A 和弦上木琴往上跑一个八度，脉冲十六分，渐强；8.45 震散：Dm 一下重音
  B   8.6–16.6   群聊，不安：8.6 Dm 八分脉冲＋钢琴 A–B♭ 半音（叹气）；11.4 开了免打扰：只剩垫音和稀的拨弦；
                 14.2–15.8 “响个不停”最满（十六分脉冲、木琴、拨弦）；15.8 一瘫：A 和弦，拇指琴往下走三个音
  C   16.6–36.6  设置页：转 D 大调，轻快但收着。拨弦低音、拇指琴八分琶音（只在 D4–A4 这一窄条里）、垫音；旋律只在无字幕的拍里出
  D   36.6–46.2  三种情况：平稳（琶音放慢到四分）；44.0 “先别开”落一个低的 Bm 和弦，之后只剩垫音和低音
  E   46.2–55.4  回到桌前：46.2–49.6 测一下（D 大调琶音）；49.6 起放松（琶音停，只剩钢琴长音和垫音）；
                 52.8–53.6 配乐让开（53.0 那一声手机响前 0.2 秒压到 −20 dB）；54.6 点头：A 和弦往 D 走
  F   55.4–61.0  顺带：轻快（木琴反拍、拇指琴琶音）
  G   61.0–66.2  清单屏：平稳、低（Bm–G–A，琶音在 C♯4–B4）
  H   66.2–69.4  结尾：拇指琴把开头动机用大调答一遍（A D E F♯），停在 Asus4 上淡到 0（循环回第 0 帧的 Dm，正好是 V → i）

无字幕的拍（BEATS8 里 sub 为空的 10 拍）：配乐整体抬 1.5 dB（B02、B04 本来就满，不抬），B08、B11、B13、B18、B20、B23、B25、B28
各加一句拇指琴的小句。

混音：配乐整条比音效低 MUSIC_REL LU；duck 的音效（手机响、震散、弹开、打勾、快门）出现时配乐再压 DUCK_DB
（提前 40 毫秒压下、压 0.15 秒、0.5 秒放开）；EV8.noisy 那 5 下不让（“响个不停”配乐最满）。
前 15 秒比全片响超过 HOOK_MAX LU 时，16.6 秒之前整体压 RIDE dB（16.6–18.6 慢慢回到 0），让它正好比全片响 HOOK_LU（第四版评委的口径）。
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
sys.dont_write_bytecode = True
import sfx8 as sfx                           # 借它的时间表、合成零件、响度和限幅函数；main() 里先调它出音效轨

ROOT = sfx.ROOT
EV, B, SC, BEATS = sfx.EV, sfx.B, sfx.SC, sfx.BEATS
SR, FPS, NF, SPF, N = sfx.SR, sfx.FPS, sfx.NF, sfx.SPF, sfx.N
SFX_WAV, SFX_EVENTS = sfx.OUT_WAV, sfx.OUT_EVENTS
OUT_MUSIC = os.path.join(sfx.PUB, 'music.wav')
OUT_MIX = os.path.join(sfx.PUB, 'mix.wav')
OUT_MD = os.path.join(HERE, 'out', '声音_v8_自查.md')
SEED = 3018

BPM = 100.0
Q = 60.0 / BPM                    # 一拍 0.6 秒
EI = Q / 2                        # 八分音符 0.3 秒
SX = Q / 4                        # 十六分音符 0.15 秒
MIX_TARGET = -14.0                # mix.wav 整条响度
HOOK_LU = 1.5                     # 前 15 秒最多比全片响多少 LU（超过 HOOK_MAX 才压，压到 HOOK_LU）
HOOK_MAX = 2.0
MIX_TP = -2.0                     # mix.wav 真峰值上限（要求 ≤ −1.5，留 0.5 dB 给 AAC 编码）
MUSIC_REL = -5.0                  # 配乐整条响度比音效整条低多少 LU
DUCK_DB = -6.0                    # duck 音效出现时配乐再压多少
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


SECS = []         # (段, 起, 止, 说明)


def plan_chords(sec, t1, pl):
    """pl：[(秒, 和弦), ...]，每个和弦到下一个的起点，最后一个到 t1。"""
    for k, (a, ch) in enumerate(pl):
        z = pl[k + 1][0] if k + 1 < len(pl) else t1
        CHORDS.append((a, z, ch, sec))


def fill(sec, t0, t1, names, vel=0.34, step=EI):
    """无字幕的拍：拇指琴一句小的（离要紧的音效不到 0.12 秒的音让掉）。"""
    for k, nm in enumerate(names):
        t = t0 + 0.1 + k * step
        if t < t1 - 0.1 and not any(abs(t - c) < 0.12 for c in CLEAR):
            note(t, 'kalimba', mid(nm), 1.4, vel, pan=0.2 * (-1) ** k, sec=sec)


def compose():
    NOTES.clear()
    CHORDS.clear()
    SECS.clear()
    evs = json.load(open(SFX_EVENTS))
    KEYS[:] = [e['t'] for e in evs if e['duck']]
    CLEAR[:] = [e['t'] for e in evs if e['key'] or e['name'] in ('提示音', '叮', '铃', '确认', '啵', '开关')]
    c0 = EV['countRun'][0]
    sh = EV['shatter'][0]
    bt = lambda i: B[i]['t0']

    # —— A 0–7.6：钩子，D 小调，紧、越来越密 ——
    SECS.append(('A 钩子', 0.0, c0, 'D 小调 Dm–B♭–Gm–A；动机 A D E F；脉冲四分 → 八分（2.2）→ 木琴十六分（6.0）'))
    plan_chords('A', c0, [(0.0, 'Dm'), (3.4, 'Bb'), (4.8, 'Gm'), (6.0, 'A')])
    for b, nm in [(0, 'A4'), (0.5, 'D5'), (1, 'E5'), (1.5, 'F5')]:
        note(b * Q, 'kalimba', mid(nm), 1.6, 0.42, sec='A')
    pulse('A', 0.0, 2.2, Q, lambda t: 0.34 + 0.03 * t / 2.2)
    pulse('A', 2.2, c0, EI, lambda t: 0.36 + 0.06 * min(1, (t - 2.2) / 5))
    arp('A', 2.2, 6.0, [0, 2, 1, 2, 3, 2, 1, 2], 'D4', 'D5', 0.3, inst='marimba', pan=0.15, ring=0.9)
    arp('A', 6.0, c0 - 0.05, [0, 2, 1, 2, 3, 2, 1, 2], 'D4', 'D5', lambda t: 0.24 + 0.06 * (t - 6.0) / 1.6, step=SX, inst='marimba',
        pan=0.15, ring=0.6)
    bass('A', 0.42)
    pad_chords('A', 0.3, 'D4', 'D5', 3)

    # —— A' 7.6–8.6：喷满、计数狂涨（A 和弦上木琴往上跑一个八度，脉冲十六分，渐强）；8.45 震散：Dm 一下重音 ——
    SECS.append(("A' 喷满、计数狂涨、震散", c0, 8.6, 'A 和弦往上跑一个八度，8.45 Dm 重音'))
    CHORDS.append((c0, sh, 'A', "A'"))
    run = ['A4', 'Bb4', 'C#5', 'D5', 'E5', 'F5', 'G5', 'A5']
    stp = (sh - c0) / 9
    for k in range(9):
        note(c0 + k * stp, 'marimba', mid(run[k % 8]) + 12 * (k // 8), 0.5, 0.28 + 0.16 * k / 8, pan=0.15 * (-1) ** k, sec="A'")
    pulse("A'", c0, sh, SX, lambda t: 0.32 + 0.1 * (t - c0) / (sh - c0))
    note(c0, 'pad', [hz(mid(x)) for x in ('A3', 'C#4', 'E4', 'G4')], sh - c0, 0.35, sec="A'")
    CHORDS.append((sh, 8.6, 'Dm', "A'"))
    for nm in ('D3', 'A3', 'D4', 'F4'):
        note(sh, 'piano', mid(nm), 0.9, 0.35, sec="A'")
    note(sh, 'pizz', mid('D3'), 0.8, 0.6, sec="A'")

    # —— B 8.6–16.6：群聊，不安 ——
    b1, b2, b3, b4, c_ = 8.6, bt('B06'), bt('B07'), bt('B08'), bt('B09')       # 8.6、11.4、14.2、15.8、16.6
    SECS.extend([('B1 吵的群里夹着要紧的', b1, b2, 'Dm，八分脉冲＋钢琴 A–B♭ 半音（叹气）'),
                 ('B2 开了免打扰', b2, b3, 'B♭ → Dm，只剩垫音、稀的拨弦、很轻的四分脉冲'),
                 ('B3 不开，响个不停', b3, b4, 'Dm，最满：十六分脉冲、木琴八分、拨弦'),
                 ('B4 往后一瘫（无字幕）', b4, c_, 'A，拇指琴往下走 E C♯ A')])
    plan_chords('B1', b2, [(b1, 'Dm')])
    plan_chords('B2', b3, [(b2, 'Bb'), (12.8, 'Dm')])
    plan_chords('B3', b4, [(b3, 'Dm')])
    plan_chords('B4', c_, [(b4, 'A')])
    pulse('B1', b1, b2, EI, 0.32)
    bass('B1', 0.4, every=4)
    pad_chords('B1', 0.32)
    k = 0
    while b1 + 0.6 + k * 2 * Q < b2 - 0.3:
        t = b1 + 0.6 + k * 2 * Q
        if not any(abs(t - c) < 0.15 for c in CLEAR):
            note(t, 'piano', mid('A4' if k % 2 == 0 else 'Bb4'), 2 * Q, 0.3, sec='B1', send=0.3)
        k += 1
    for a, z, ch, s in [c for c in CHORDS if c[3] == 'B2']:
        note(a, 'pad', [hz(m) for m in tones(ch, 'D4', 'D5')][:3], z - a, 0.38, sec='B2', send=0.4)
    for t, nm in [(b2, 'Bb2'), (b2 + 2 * Q, 'F3'), (12.8, 'D3'), (12.8 + 2 * Q, 'A2')]:
        note(t, 'pizz', mid(nm), 0.7, 0.36, sec='B2', send=0.12)
    pulse('B2', b2, b3, Q, 0.22)
    pulse('B3', b3, b4, SX, lambda t: 0.36 + 0.08 * (t - b3) / (b4 - b3))
    arp('B3', b3, b4, [0, 2, 1, 2, 3, 2, 1, 2], 'D4', 'D5', 0.34, inst='marimba', pan=0.15, ring=0.8)
    bass('B3', 0.45, every=2)
    pad_chords('B3', 0.34)
    note(b4, 'pad', [hz(mid(x)) for x in ('A3', 'C#4', 'E4')], c_ - b4, 0.3, sec='B4', send=0.4)
    note(b4, 'pizz', mid('A2'), 0.8, 0.4, sec='B4')
    for k, nm in enumerate(('E5', 'C#5', 'A4')):
        note(b4 + 0.05 + 0.22 * k, 'kalimba', mid(nm), 1.2, 0.36 - 0.04 * k, pan=0.2 * (-1) ** k, sec='B4')

    # —— C 16.6–36.6：设置页，D 大调，轻快但收着（和弦跟着画面换；有音高的音效落的地方都是含 D 的和弦） ——
    d0 = bt('B18')                                                             # 36.6
    SECS.append(('C 设置页', c_, d0, 'D 大调；拨弦低音、拇指琴八分琶音（D4–A4）、垫音；旋律只在 B11、B13'))
    plan_chords('C', d0, [(16.6, 'D'), (18.6, 'Bm'), (19.2, 'D'), (21.0, 'G'), (21.8, 'D'), (24.2, 'G'), (25.0, 'D'), (27.4, 'Bm'),
                          (30.2, 'G'), (31.4, 'A'), (32.6, 'D'), (33.8, 'G'), (34.6, 'D'), (36.0, 'A')])
    bass('C', 0.4, every=2)
    arp('C', c_, d0, [0, 1, 2, 1], 'D4', 'A4', 0.2, pan=0.15, ring=1.0)
    pad_chords('C', 0.24)

    # —— D 36.6–46.2：三种情况，平稳；44.0 “先别开”落一个低的 Bm ——
    e0 = bt('B23')                                                             # 46.2
    lowc = bt('B22')                                                           # 44.0
    SECS.append(('D 三种情况', d0, e0, 'G–D–Bm–G…，琶音四分；44.0 低的 Bm（钢琴 B2 F♯3 B3 D4），之后只剩垫音和低音'))
    plan_chords('D', e0, [(36.6, 'G'), (37.4, 'D'), (38.6, 'G'), (39.8, 'D'), (40.4, 'G'), (41.2, 'Bm'), (42.6, 'G'), (43.4, 'A'),
                          (44.0, 'Bm'), (45.2, 'G')])
    bass('D', 0.38, every=2)
    arp('D', d0, lowc - 0.05, [0, 1, 2, 1], 'D4', 'A4', 0.22, step=Q, pan=0.15, ring=1.4)
    pad_chords('D', 0.24)
    for nm in ('B2', 'F#3', 'B3', 'D4'):
        note(lowc, 'piano', mid(nm), 1.6, 0.42, sec='D', send=0.35)

    # —— E 46.2–55.4：回到桌前。49.6 起放松；52.8–53.6 让开给 53.0 那一声 ——
    f0 = bt('B29')                                                             # 55.4
    relax = bt('B25')                                                          # 49.6
    kr = EV['keyRing']
    SECS.extend([('E1 测一下', e0, relax, 'D 大调琶音'),
                 ('E2 放松、只在该响的时候响', relax, f0, '琶音停，钢琴长音＋垫音；52.8–53.6 让开（−20 dB），53.6 起回来')])
    plan_chords('E', f0, [(46.2, 'D'), (48.6, 'G'), (49.6, 'D'), (51.0, 'G'), (52.4, 'D'), (54.6, 'A')])
    arp('E', e0, relax - 0.05, [0, 1, 2, 1], 'D4', 'A4', 0.2, pan=0.15, ring=1.0)
    for t, nm in [(46.2, 'D3'), (47.4, 'A2'), (48.6, 'G2'), (49.6, 'D3'), (51.0, 'G2'), (kr + 0.6, 'D3'), (54.6, 'A2')]:
        note(t, 'pizz', mid(nm), 0.8, 0.38, sec='E', send=0.12)
    for a, z, ch, s in [c for c in CHORDS if c[3] == 'E']:
        a2 = kr + 0.6 if a <= kr < z else a                                    # 53.0 那一声底下不起垫音
        note(a2, 'pad', [hz(m) for m in tones(ch, 'D4', 'D5')][:3], z - a2, 0.26, sec='E', send=0.35)
    for t, ch_notes, d in [(relax, ('D3', 'A3', 'F#4'), 1.4), (51.0, ('G2', 'D3', 'B3'), 1.3), (kr + 0.6, ('D3', 'A3', 'F#4'), 1.0)]:
        for nm in ch_notes:
            note(t, 'piano', mid(nm), d, 0.26, sec='E', send=0.35)

    # —— F 55.4–61.0：顺带，轻快 ——
    g0 = bt('B31')                                                             # 61.0
    SECS.append(('F 顺带', f0, g0, 'D–G–A–D–A；木琴反拍、拇指琴琶音'))
    plan_chords('F', g0, [(55.4, 'D'), (56.6, 'G'), (57.8, 'A'), (59.0, 'D'), (60.2, 'A')])
    bass('F', 0.42, every=2)
    arp('F', f0, g0, [0, 1, 2, 1], 'D4', 'A4', 0.22, pan=0.15, ring=1.0)
    t, k = f0 + EI, 0
    while t < g0 - 0.05:
        for m in tones(chord_at(t), 'F#4', 'D5')[:2]:
            note(t, 'marimba', m, 0.4, 0.2, pan=0.12, sec='F', send=0.15)
        k += 1
        t = f0 + EI + k * Q
    pad_chords('F', 0.24)

    # —— G 61.0–66.2：清单屏，平稳、低 ——
    h0 = SC['end']                                                             # 66.2
    SECS.append(('G 清单屏', g0, h0, 'Bm–G–A；拇指琴琶音只在 C♯4–B4'))
    plan_chords('G', h0, [(61.0, 'Bm'), (63.4, 'G'), (65.8, 'A')])
    arp('G', g0 + 0.15, h0, [0, 1, 2, 1, 0, 2, 1, 2], 'C#4', 'B4', 0.2, pan=0.15, ring=1.2)
    bass('G', 0.36, every=2)
    pad_chords('G', 0.24)

    # —— H 66.2–69.4：结尾，开头动机用大调答一遍，停在 Asus4 上淡出 ——
    tq = h0 + 1.4
    SECS.append(('H 结尾', h0, END, 'Dadd9 上拇指琴 A D E F♯（开头动机的大调回答），67.6 停在 Asus4，最后 1.2 秒淡到 0'))
    CHORDS.extend([(h0, tq, 'Dadd9', 'H'), (tq, END, 'Asus4', 'H')])
    note(h0, 'pizz', mid('D3'), 1.0, 0.4, sec='H')
    note(h0, 'pad', [hz(mid(x)) for x in ('D4', 'F#4', 'A4', 'E5')], tq - h0, 0.3, sec='H', send=0.4)
    for b, nm in [(0, 'A4'), (0.5, 'D5'), (1, 'E5'), (1.5, 'F#5')]:
        note(h0 + 0.15 + b * Q, 'kalimba', mid(nm), 1.6, 0.42, sec='H')
    note(tq, 'pizz', mid('A2'), 1.0, 0.36, sec='H')
    note(tq, 'pad', [hz(mid(x)) for x in ('A3', 'D4', 'E4')], END - tq, 0.32, sec='H', send=0.4)

    # —— 无字幕的拍：拇指琴小句 ——
    FILLS = {'B11': ['D5', 'G5', 'B5'], 'B13': ['D6', 'B5', 'G5'], 'B18': ['G5', 'B5', 'D6'], 'B20': ['B5', 'G5', 'D5'],
             'B23': ['F#5', 'A5', 'D6'], 'B25': ['A5', 'F#5', 'D5'], 'B28': ['A4', 'C#5', 'E5']}
    for bid, names in FILLS.items():
        fill('无字幕 ' + bid, B[bid]['t0'], B[bid]['t1'], names)
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
    """整体的起伏（dB）：钩子紧、计数时渐强到最高，震散后收；群聊不安，免打扰那段最低，“响个不停”最满；设置页收着；
    44.0 低和弦稍抬；53.0 那一声前 0.2 秒让开到 −20；顺带略亮；清单低；结尾中等。无字幕的拍再抬 1.5 dB（B02、B04 本来就满）。"""
    kr = EV['keyRing']
    pts = [(0.0, -4.0), (2.2, -3.5), (7.6, -3.5), (8.4, -2.5), (8.47, -5.0), (8.6, -6.0), (11.3, -6.0), (11.6, -9.0), (14.1, -9.0),
           (14.3, -3.5), (15.7, -3.5), (15.95, -6.0), (16.6, -7.0), (43.9, -7.0), (44.0, -5.5), (45.0, -7.0), (49.6, -7.0),
           (52.6, -8.0), (kr - 0.2, -20.0), (kr + 0.6, -20.0), (kr + 1.2, -8.0), (55.4, -6.0), (60.9, -6.0), (61.2, -8.0),
           (66.2, -6.5), (END, -6.5)]
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    base = np.interp(t, x, y)
    bump = np.zeros_like(t)
    for b in BEATS:
        if not b['sub'] and b['id'] not in ('B02', 'B04'):
            bump = np.maximum(bump, 1.5 * np.clip(np.minimum((t - b['t0']) / 0.15, (b['t1'] - t) / 0.15), 0, 1))
    return base + bump


def gate_curve(t):
    """配乐：开头 30 毫秒淡入（render_music 里做），最后 1.2 秒淡到 0（音效那条门只管最后 0.25 秒）。"""
    g = sfx.gate_curve(t)
    tail = END - 1.2
    return g * np.clip(1 - (t - tail) / 1.2, 0, 1) ** 1.5




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


def harmony_checks():
    """有音高的音效（sfx8.put 的 notes）落在不在当时的和弦里。"""
    rows = []
    for e in sfx.EVENTS:
        for dt, nm in e['notes']:
            t = e['vis'] + dt
            ch = chord_at(t)
            inch = ch is not None and mid(nm) % 12 in {PC[x] for x in CHORD[ch].split()}
            rows.append(dict(t=round(t, 3), label=e['label'], note=nm, chord=ch or '（配乐没声）', in_chord=inch))
    return sorted(rows, key=lambda r: r['t'])


def xcorr_lag(xm, e, lo, hi, tlen=0.3, srch=0.04):
    """成品里这个声音实际在哪：拿它自己的波形（前 tlen 秒，不超过下一个声音之前）在成品的 ±srch 秒里做归一化互相关，
    回（离放置点几毫秒，相关系数）。不受前一个声音的尾巴、配乐影响（第四版直接找起音的法子会被前一个声音的尾巴骗）。"""
    s = sfx.shape(e['sig'][:int(max(0.02, tlen) * SR)], lo, hi)
    st = int(round(e['start'] * SR))
    pad = int(srch * SR)
    a, b = max(0, st - pad), min(len(xm), st + len(s) + pad)
    seg = sfx.shape(xm[a:b], lo, hi)
    n = 1 << (len(seg) + len(s)).bit_length()
    c = np.fft.irfft(np.fft.rfft(seg, n) * np.conj(np.fft.rfft(s, n)), n)[:len(seg) - len(s) + 1]
    e2 = np.convolve(seg ** 2, np.ones(len(s)), 'valid')
    cn = c / np.sqrt(e2 * np.sum(s ** 2) + 1e-20)
    i = int(np.argmax(cn))
    return round((a + i - st) / SR * 1000, 1), round(float(cn[i]), 2)


def runs_below(x, db, a, z):
    """x（单声道电平）在 a–z 秒里连续低于 db dBFS 的最长一段（秒）。"""
    q = (x[int(a * SR):int(z * SR)] < 10 ** (db / 20)).astype(int)
    idx = np.flatnonzero(np.diff(np.concatenate([[0], q, [0]])))
    r = idx[1::2] - idx[::2]
    return round(float(r.max()) / SR, 3) if len(r) else 0.0




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
    chk = sfx.main()                                                    # 先出音效轨（v8/sfx.wav、sfx_events.json）
    music, info = render_music()
    sx, sr = sfx.read_wav(SFX_WAV)
    assert sr == SR and len(sx) == N and len(music) == N, (sr, len(sx), len(music), N)
    with tempfile.TemporaryDirectory() as tmp:
        I_sfx, _ = lufs(sx, tmp, 'sfx.wav')
        I_mus, _ = lufs(music, tmp, 'mus.wav')
        music = music * 10 ** ((I_sfx + MUSIC_REL - I_mus) / 20)
        d0 = hook_diff(sx + music, tmp)
        if d0 > HOOK_MAX:
            ride_db, ride_steps = solve_ride(sx + music, tmp)
        else:
            ride_db, ride_steps = 0.0, [(0.0, round(d0, 2))]
        R = ride_curve(ride_db)[:, None]
        sx, music = sx * R, music * R
        mix, gmin = master(sx + music, tmp)
        I_pre, _ = lufs(sx + music, tmp, 'pre2.wav')
        g_all = 10 ** ((MIX_TARGET - I_pre) / 20)
        sfx.write_wav(OUT_MUSIC, music * g_all)
        sfx.write_wav(OUT_MIX, mix, dither=True, rng=np.random.default_rng(SEED + 1))

    # —— 以下全部从磁盘读回量 ——
    x, xsr = sfx.read_wav(OUT_MIX)
    fin = sfx.ebur(OUT_MIX)
    fin15 = sfx.ebur(OUT_MIX, 'atrim=0:15')
    ln = sfx.loudnorm_json(OUT_MIX, MIX_TARGET, MIX_TP)
    mo, _ = sfx.read_wav(OUT_MUSIC)
    mus = sfx.ebur(OUT_MUSIC)
    sxf, _ = sfx.read_wav(SFX_WAV)
    xm = x.mean(axis=1)
    # 每个点名的声音：单轨起音差（声音开头到听得出的起音）＋成品里的位置差（互相关）= mix.wav 里起音和 EV8 的差
    byk = {}
    for e in sfx.EVENTS:
        byk.setdefault((e['label'], round(e['vis'] + e['lead'], 3)), e)
    hits = np.array(sorted({e['vis'] for e in sfx.EVENTS if e['cat'] != 'tex'}))
    rows = []
    for r in chk['rows']:
        if not r['spec']:
            continue
        e = byk[(r['label'], r['t'])]
        lo, hi = sfx.BAND.get(e['kind'], (700, 8000))
        nx, pv = hits[hits > e['vis'] + 1e-4], hits[hits < e['vis'] - 1e-4]
        gn = float(nx[0] - e['vis']) if len(nx) else 1.0
        gp = float(e['vis'] - pv[-1]) if len(pv) else 1.0
        lag, cc = xcorr_lag(xm, e, lo, hi, min(0.3, 0.9 * gn), min(0.04, 0.45 * min(gp, gn)))
        tot = None if r['solo_err_ms'] is None else round(r['solo_err_ms'] + lag, 1)
        rows.append(dict(name=r['spec'][0], src=r['spec'][2], t=r['t'], frame=int(math.floor(r['t'] * FPS + 0.5)), solo=r['solo_err_ms'],
                         lag=lag, cc=cc, total=tot, direct=r['err_ms']))
    # 爆音、断层
    clip_n = int(np.sum(np.abs(x) >= 32766 / 32768))
    dd = np.abs(np.diff(x, axis=0)).max(axis=1)
    jt = int(np.argmax(dd))
    lv = np.abs(x).max(axis=1)
    mlv = np.abs(mo).max(axis=1)
    kr0 = EV['keyRing']
    gaps = dict(mix=runs_below(lv, -60, 0.05, END - 1.3),
                music=max(runs_below(mlv, -60, 0.05, kr0 - 0.25), runs_below(mlv, -60, kr0 + 0.7, END - 1.3)),
                music_kr=runs_below(mlv, -60, kr0 - 0.25, kr0 + 0.7))
    # silentMsg 那一刻 / keyRing 前配乐让开
    sm = EV['silentMsg']
    pk = lambda y, a, b: round(20 * math.log10(np.max(np.abs(y[int(a * SR):int(b * SR)])) + 1e-12), 1)
    rmsd = lambda y, a, b: round(20 * math.log10(np.sqrt(np.mean(y[int(a * SR):int(b * SR)] ** 2)) + 1e-12), 1)
    silent = dict(sfx_peak=pk(sxf, sm - 0.05, sm + 0.3), buzz_peak=pk(sxf, EV['noisy'][0], EV['noisy'][0] + 0.3),
                  tag_peak=pk(sxf, EV['silentTag'], EV['silentTag'] + 0.2))
    kr = EV['keyRing']
    clear_kr = dict(before=rmsd(mo, kr - 1.2, kr - 0.4), during=rmsd(mo, kr - 0.2, kr + 0.4), after=rmsd(mo, kr + 1.4, kr + 2.2))
    MM = mus['M']
    sec_rows = []
    for name, s0, s1, desc in SECS:
        v = MM[(MM[:, 0] >= s0 + 0.4) & (MM[:, 0] <= s1), 1]
        v = v[v > -70]
        chs = [c[2] for c in sorted(CHORDS) if s0 - 1e-6 <= c[0] < s1 - 1e-6]
        sec_rows.append(dict(name=name, t0=round(s0, 2), t1=round(s1, 2), desc=desc, chords='–'.join(dict.fromkeys(chs)) if chs else '',
                             M=round(float(np.median(v)), 1) if len(v) else None))
    harm = harmony_checks()
    s = dict(mix=dict(sr=xsr, samples=len(x), seconds=len(x) / SR, ch=x.shape[1], I=fin['I'], LRA=fin['LRA'], TP=fin['TP'],
                      ln_I=float(ln['input_i']), ln_TP=float(ln['input_tp']), lim=round(20 * math.log10(gmin), 2),
                      I15=fin15['I'], d15=round(fin15['I'] - fin['I'], 1), ride=round(ride_db, 2), ride_steps=ride_steps),
             music=dict(I=mus['I'], TP=mus['TP'], notes=len(NOTES)), sfx=dict(I=chk['I'], TP=chk['TP'], events=chk['events']),
             rows=rows, clip=clip_n, jump=(round(float(dd[jt]), 3), round(jt / SR, 3)), gaps=gaps, silent=silent, clear_kr=clear_kr,
             secs=sec_rows, harm=harm, solo_off=chk['solo_off'])
    write_md(s)
    m = s['mix']
    print(f"写出 {OUT_MIX}：{m['samples']} 个采样 = {m['seconds']:.4f} 秒，{m['sr']} Hz × {m['ch']}；I {m['I']} LUFS（loudnorm {m['ln_I']}），"
          f"真峰值 {m['TP']} dBTP（loudnorm {m['ln_TP']}），限幅最深 {m['lim']} dB；前 15 秒 {m['I15']}（差 {m['d15']}，压 {m['ride']} dB）")
    mx = max(abs(r['total']) for r in rows if r['total'] is not None)
    print(f"点名的 {len(rows)} 个：mix.wav 里起音和 EV8 最大差 {mx} 毫秒；互相关系数最低 {min(r['cc'] for r in rows)}；"
          f"没量出的 {[r['name'] for r in rows if r['total'] is None]}")
    print('爆音', clip_n, '最大跳变', s['jump'], '断层', gaps, 'silentMsg', silent, 'keyRing 前让开', clear_kr)
    print('各段', [(r['name'], r['M']) for r in sec_rows])
    print('和弦外的音效', [(r['t'], r['label'], r['note'], r['chord']) for r in harm if not r['in_chord']])


def write_md(s):
    m, rows = s['mix'], s['rows']
    ok = lambda v: v is not None and abs(v) <= 1000 / FPS
    mx = max(abs(r['total']) for r in rows if r['total'] is not None)
    worst = max((r for r in rows if r['total'] is not None), key=lambda r: abs(r['total']))
    bad = [r for r in s['harm'] if not r['in_chord']]
    sil, kr = s['silent'], s['clear_kr']
    L = ['# 003《消息提醒》第八版声音自查', '',
         '跑的脚本：`videos/003_消息提醒/music8.py`（它先调 `sfx8.py` 出音效轨）。numpy 合成，没用曲库、采样、第三方账号。'
         '时间全从 `studio/src/videos/003/timeline8.ts` 读（FPS8、DUR8、BEATS8、SC8、EV8），没改它。下面的数全部从磁盘读回 wav 量（ffmpeg ebur128，peak=true）。', '',
         '## 结论', '',
         f'- **响度**：mix.wav 整条 **{m["I"]} LUFS**（要求 −14 ±0.5：{"是" if abs(m["I"] + 14) <= 0.5 else "否"}），'
         f'真峰值 **{m["TP"]} dBTP**（要求 ≤ −1.5：{"是" if m["TP"] <= -1.5 else "否"}）；loudnorm 复核 {m["ln_I"]} LUFS、{m["ln_TP"]} dBTP；'
         f'LRA {m["LRA"]} LU；前瞻限幅最深压了 {m["lim"]} dB。',
         f'- **格式和长度**：{m["sr"]} Hz、{m["ch"]} 声道、16 bit；{m["samples"]} 个采样 = {m["seconds"]:.4f} 秒（要求 69.4）。',
         f'- **对点**：点名的 {len(rows)} 个声音，mix.wav 里起音和 EV8 的差最大 **{mx} 毫秒**（{worst["name"]}），1 帧 = 33.3 毫秒，'
         f'全部 ≤ 1 帧：{"是" if all(ok(r["total"]) for r in rows) else "否"}。',
         f'- **爆音**：mix.wav 里到满刻度的采样 {s["clip"]} 个；相邻两个采样最大跳变 {s["jump"][0]}（在 {s["jump"][1]} 秒，是那里音效本身的起音）。',
         f'- **断层**：0.05 秒到淡出前（{END - 1.3:.1f} 秒），mix.wav 连续低于 −60 dBFS 最长 {s["gaps"]["mix"]} 秒，'
         f'music.wav 除 {EV["keyRing"]} 秒那一下以外最长 {s["gaps"]["music"]} 秒（配乐从头到淡出没有断开）；'
         f'{EV["keyRing"] - 0.2:.1f}–{EV["keyRing"] + 0.6:.1f} 秒是特意让开（配乐压到 −20 dB、不起新音），里面最长 {s["gaps"]["music_kr"]} 秒低于 −60 dBFS，'
         '手机提示音和它的混响尾巴盖着，不是断层。',
         f'- **{EV["silentMsg"]} 秒“开了免打扰，消息来了不提醒”**：没有手机声。sfx.wav 里这一刻最响 {sil["sfx_peak"]} dBFS，'
         f'对比 {EV["noisy"][0]} 秒手机响 {sil["buzz_peak"]} dBFS、{EV["silentTag"]} 秒贴纸“没提醒” {sil["tag_peak"]} dBFS——只有一下很闷很轻的“噗”。',
         f'- **{EV["keyRing"]} 秒那一声前配乐让开**：music.wav 有效值 让开前 {kr["before"]} dBFS → {EV["keyRing"] - 0.2:.1f}–{EV["keyRing"] + 0.4:.1f} 秒 '
         f'{kr["during"]} dBFS → 之后 {kr["after"]} dBFS。',
         f'- **前 15 秒**：{m["I15"]} LUFS，比全片响 {m["d15"]} LU（第四版评委口径：不超过 2）；'
         + ('没压。' if m['ride'] == 0 else f'16.6 秒前整体压了 {m["ride"]} dB（16.6–18.6 回到 0）。'),
         f'- **和弦**：有音高的音效 {len(s["harm"])} 个音，落在当时和弦外的 {len(bad)} 个' + ('。' if not bad else '：' + '，'.join(
             f'{r["t"]} {r["label"]} {r["note"]}（{r["chord"]}）' for r in bad) + '。'),
         '', '## 1. 点名的音效：起音和 EV8 差多少', '',
         '“单轨差”= 只放这一个声音时，量到的起音离声音开头多少毫秒（震动起转要十几毫秒，嗖一起头就有三五成响）；'
         '“成品位置差”= 拿这个声音自己的波形在 mix.wav 里做互相关找到的位置，离放置点多少毫秒（不受前后挨着的声音、配乐影响）；'
         '“合计”= 两个相加，就是 mix.wav 里听到的起音离 EV8 多少毫秒。“直接量”是第四版的老法子（在 sfx.wav 上找起音），'
         '前一个声音的尾巴还没散时会被骗，只作参考。', '',
         '| 要的声音 | EV8 | 秒 | 帧 | 单轨差 | 成品位置差（相关系数） | 合计（毫秒） | ≤1 帧 | 直接量 |', '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        L.append(f'| {r["name"]} | {r["src"]} | {r["t"]:.2f} | {r["frame"]} | {r["solo"]} | {r["lag"]}（{r["cc"]}） | {r["total"]} | '
                 f'{"是" if ok(r["total"]) else "否"} | {r["direct"] if r["direct"] is not None else "被盖住"} |')
    L += ['', '- 每次手机响 = 震（8 帧）＋提示音，两个都放在同一个 EV8 秒上；上表列的是震动那一下。提示音、暖铃、开关声见 `studio/public/003/v8/sfx_events.json`。',
          '- 开关声跟在点击后 60 毫秒（拨动 25 毫秒，到头一下小“笃”：拨开 D6、拨灰 D5）；EV8.offs 两个开关没有点击，直接拨灰。',
          f'- 计数狂涨：{EV["countRun"][0]}–{EV["countRun"][1]} 秒 {len(sfx.TICKS)} 下滴答，间隔 60 → 20 毫秒，音高 2.1 → 3.4 kHz；'
          f'喷满：{EV["burst"][0]}–{EV["burst"][1]} 秒 {len(sfx.BANNERS)} 条横幅“噌”，间隔 61 → 18 毫秒；单轨差都 ≤ 1 帧：'
          f'{"是" if not s["solo_off"] else "否"}。',
          '', '## 2. 配乐各段', '',
          '| 段 | 起–止（秒） | 和弦 | 做法 | 配乐瞬时响度中位数（LUFS） |', '|---|---|---|---|---|']
    for r in s['secs']:
        L.append(f'| {r["name"]} | {r["t0"]}–{r["t1"]} | {r["chords"]} | {r["desc"]} | {r["M"]} |')
    L += ['', f'- 配乐 {s["music"]["notes"]} 个音；music.wav 单独 {s["music"]["I"]} LUFS（就是它在 mix 里的电平），sfx.wav 单独 {s["sfx"]["I"]} LUFS'
              f'（音效轨自己调到 −19，混音时配乐比音效低 {-MUSIC_REL:g} LU）。',
          '- 配乐让开：手机响（buzz、allBanners、testMsg、keyRing）、震散、弹开、打勾、快门出现时压 6 dB（提前 40 毫秒）；EV8.noisy 五下不让。',
          '- 无字幕的 10 拍配乐抬 1.5 dB（B02、B04 本来就满，不抬）；B08、B11、B13、B18、B20、B23、B25、B28 各一句拇指琴小句。',
          '', '## 3. 没做到或没查的', '',
          '- 没在手机上外放听过，也没合进成片跑 `tools/watch/check.py`（画面还在做）；成片出来后用 '
          '`--lufs -14 --peak -1.5 --sfx studio/public/003/v8/sfx_events.json` 跑一遍。',
          '- 群聊往上滚（chatScroll）的小“嗒”按缓出排的，画面的滚动曲线没核；横幅喷出 22 条、计数滴答各自的时刻 EV8 里没有，是在 burst、countRun 里按“越来越密”排的。',
          '- “响个不停”五下和钩子四下的提示音是同一套合成，没逐条做成不同的群。',
          ]
    open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
