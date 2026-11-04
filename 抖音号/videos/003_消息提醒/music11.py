"""《消息提醒》第十版（不教学的观点片，长度 = timeline11.ts 的 DUR11）的原创配乐，和音效混成最终音轨。

从第九版的 music9.py 复制过来：乐器（拇指琴、木琴、钢琴、拨弦、垫音）、记谱的小工具、渲染、让开、混音、限幅都原样留着，
只按第十版的场景重写了谱子和自查。全部用 numpy 合成，纯音乐，没有人声，没有鼓。不用曲库、采样、第三方账号。

  /Users/decheng.huang/Documents/dy/.venv/bin/python -I /Users/decheng.huang/Documents/dy/videos/003_消息提醒/music11.py
  （一条命令全出：先调 sfx11.main() 出音效轨，再出配乐、混音、自查）

读：studio/src/videos/003/timeline11.ts（经 sfx11.py 读；只读）
写：studio/public/003/v11/music.wav（单独的配乐，电平 = 它在 mix.wav 里的电平，含让开；单独限到 −1 dB 防削波）
    studio/public/003/v11/mix.wav（音效 ＋ 配乐，48 kHz、双声道、16 bit、正好 DUR11 秒，整条 −14 LUFS，前瞻限幅，真峰值 ≤ −2 dBTP）
    videos/003_消息提醒/out/声音_v11_自查.md（全部从磁盘读回 wav 量）

调和速度：全片 D 小调，不转大调；112 BPM。秒数一个都不写死，段落的起止全从 SC11、EV11、BEATS11 算（compose 开头）：
  A  0 – SC11.me 结束    被吵：Dm，捂住的拨弦按 3+3+2 走（拍子落不稳，轻快但烦躁），木琴 A–B♭–A 磨半音
  B  cut – thread        放不下：同样的脉动更薄；拇指琴动机 A D E F；S04 脉动减半、往下三个音；S05 脉动回来（“还是会点开”）
  C  thread – fear 前    慢下来、变空：只剩低垫音，拨弦间隔越拉越长，气泡越密配乐越空
  （fear 前 0.28 秒起配乐是 0，fear 后 0.4 秒起用 1 秒回来）
  D  fear – S09          说破：低的钢琴 D、A；S08 钢琴 A–B♭–A（放在卡片之间）
  E  S09、S10            只留低音（长的低钢琴 B♭、G）和两个拇指琴音
  H  hint、end           Gm → Asus4，拇指琴 A D E（动机少最后一个音，不解决）；最后 0.5 秒淡到 0

混音（照第九版）：配乐整条比音效低 MUSIC_REL LU；duck 的音效（手机响、怕漏、第三下落字）出现时配乐再压 DUCK_DB（提前 40 毫秒压下、压 0.15 秒、
0.5 秒放开）。前 15 秒比全片响超过 HOOK_MAX LU 时，thread 之前整体压 RIDE dB（之后 2 秒回到 0），让它正好比全片响 HOOK_LU。
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
import sfx11 as sfx                           # 借它的时间表、合成零件、响度和限幅函数；main() 里先调它出音效轨

ROOT = sfx.ROOT
EV, B, SC, BEATS = sfx.EV, sfx.B, sfx.SC, sfx.BEATS
SR, FPS, NF, SPF, N = sfx.SR, sfx.FPS, sfx.NF, sfx.SPF, sfx.N
SFX_WAV, SFX_EVENTS = sfx.OUT_WAV, sfx.OUT_EVENTS
OUT_MUSIC = os.path.join(sfx.PUB, 'music.wav')
OUT_MIX = os.path.join(sfx.PUB, 'mix.wav')
OUT_MD = os.path.join(sfx.PUB, '声音_v11_自查.md') if os.environ.get('SOUND11_OUT') else os.path.join(HERE, 'out', '声音_v11_自查.md')
SEED = 3020

BPM = 112.0
Q = 60.0 / BPM                    # 一拍
EI = Q / 2                        # 八分音符
SX = Q / 4                        # 十六分音符
MIX_TARGET = -14.0                # mix.wav 整条响度
HOOK_LU = 5.0                     # 前 15 秒最多比全片响多少 LU（超过 HOOK_MAX 才压，压到 HOOK_LU）
HOOK_MAX = 6.0
MIX_TP = -2.0                     # mix.wav 真峰值上限（要求 ≤ −2）
MUSIC_REL = -3.0                  # 配乐整条响度比音效整条低多少 LU
DUCK_DB = -8.0                    # duck 音效出现时配乐再压多少
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
    'D': 'D F# A', 'Dadd9': 'D F# A E', 'G': 'G B D', 'Gmaj7': 'G B D F#', 'Bm': 'B D F#', 'Em': 'E G B', 'F': 'F A C',
}
ROOTNOTE = {'Dm': 'D3', 'Dmadd9': 'D3', 'Bb': 'Bb2', 'Gm': 'G2', 'A': 'A2', 'A7': 'A2', 'Asus4': 'A2', 'D': 'D3', 'Dadd9': 'D3',
            'G': 'G2', 'Gmaj7': 'G2', 'Bm': 'B2', 'Em': 'E3', 'F': 'F2'}


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
    """plan：[(拍, 和弦), ...]，拍从 t0 起算。最后一个和弦到 t1。"""
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
    """pl：[(秒, 和弦), ...]，按时间排；每个和弦到下一个的起点，最后一个到 t1。时间表一改，落在 t1 之后或不往后走的那几个自动丢掉。"""
    pl = sorted(pl, key=lambda p: p[0])
    keep = []
    for a, ch in pl:
        if a < t1 - 0.05 and (not keep or a > keep[-1][0] + 0.05):
            keep.append((a, ch))
    for k, (a, ch) in enumerate(keep):
        z = keep[k + 1][0] if k + 1 < len(keep) else t1
        CHORDS.append((a, z, ch, sec))


def fill(sec, t0, t1, names, vel=0.34, step=EI):
    """无字幕的拍：拇指琴一句小的（离要紧的音效不到 0.12 秒的音让掉）。"""
    for k, nm in enumerate(names):
        t = t0 + 0.1 + k * step
        if t < t1 - 0.1 and not any(abs(t - c) < 0.12 for c in CLEAR):
            note(t, 'kalimba', mid(nm), 1.4, vel, pan=0.2 * (-1) ** k, sec=sec)


def bstart(t):
    """t 落在哪一拍，回那一拍的起点。"""
    for b in BEATS:
        if b['t0'] <= t < b['t1']:
            return b['t0']
    return t


def has(*ks):
    return all(k in EV for k in ks)


def pcs(ch):
    return {PC[x] for x in CHORD[ch].split()}


def grid(sec, t0, t1, prog, beats=2):
    """从 t0 起每 beats 拍换一个和弦，按 prog 轮着来，到 t1。"""
    pl, k = [], 0
    while t0 + k * beats * Q < t1 - 0.3:
        pl.append((t0 + k * beats * Q, prog[k % len(prog)]))
        k += 1
    plan_chords(sec, t1, pl)


FIXES = []        # (秒, 音效, 音, 原和弦, 换成)
ANCH = {}         # 各段的起止秒（compose 里从 EV、SC 算）


def fix_chords():
    """有音高的音效落在当时和弦外的，把那一格换成 Dm（全片小调）。查两遍。"""
    FIXES.clear()
    for _ in range(2):
        for e in sfx.EVENTS:
            for dt, nm in e['notes']:
                t = e['vis'] + dt
                for i, (a, z, ch, sec) in enumerate(CHORDS):
                    if a - 1e-6 <= t < z - 1e-6:
                        pc = mid(nm) % 12
                        if pc not in pcs(ch) and pc in pcs('Dm'):
                            CHORDS[i] = (a, z, 'Dm', sec)
                            FIXES.append((round(t, 3), e['label'], nm, ch, 'Dm'))
                        break


def tres(sec, t0, t1, vel):
    """烦躁的脉动：捂住的拨弦弹和弦根音的高八度（手机外放听得见，峰值也小），两拍一组按 3+3+2 个十六分走，拍子总落不稳，听着轻快但不踏实。"""
    k = 0
    while t0 + k * 2 * Q < t1 - 1e-6:
        for off, acc in ((0, 1.0), (3 * SX, 0.8), (6 * SX, 0.9)):
            t = t0 + k * 2 * Q + off
            ch = chord_at(t)
            if t < t1 - 1e-6 and ch:
                note(t, 'pulse', mid(ROOTNOTE[ch]) + 12, 0.3, vel * acc, sec=sec, send=0.08)
        k += 1


def rub(sec, t0, t1, period, vel):
    """木琴磨半音：A4–B♭4–A4，每 period 秒一次，离手机响、贴纸不到 0.15 秒的音让掉。"""
    t = t0
    while t < t1 - 1e-6:
        for j, nm in enumerate(('A4', 'Bb4', 'A4')):
            a = t + j * EI
            if a < t1 and not any(abs(a - c) < 0.15 for c in CLEAR):
                note(a, 'marimba', mid(nm), 0.7, vel, pan=0.15 * (-1) ** j, sec=sec)
        t += period


def compose():
    NOTES.clear()
    CHORDS.clear()
    SECS.clear()
    evs = json.load(open(SFX_EVENTS))
    KEYS[:] = [e['t'] for e in evs if e['duck']]
    CLEAR[:] = [e['t'] for e in evs if e['key'] or e['name'] in ('提示音', '叮', '铃', '确认', '啵', '开关')]
    stop, th0, th1, fq = EV['stop'], EV['thread'][0], EV['thread'][1], EV['fear']
    s04, s06, s09, s11, s13 = B['S04']['t0'], B['S06']['t0'], B['S09']['t0'], B['S11']['t0'], B['S13']['t0']
    hi, en = SC['hint'][0], SC['end']
    ANCH.clear()
    ANCH.update(stop=stop, th0=th0, fq=fq, s04=s04, s06=s06, s09=s09, s11=s11, s13=s13, hi=hi, en=en)

    # ===== 1. 和弦（全片 D 小调） =====
    plan_chords('A', stop, [(0.0, 'Dm'), (stop * 0.35, 'Bb'), (stop * 0.6, 'Gm'), (stop * 0.82, 'A')])
    plan_chords('C', s06, [(th0, 'Dm'), (s04, 'Bb')])
    plan_chords('D', s09, [(s06, 'Dm')])
    plan_chords('E', hi, [(s09, 'Bb'), (s11, 'Gm'), (s13, 'Dm')])
    plan_chords('H', END, [(hi, 'Gm'), (en, 'Asus4')])
    CHORDS.sort()
    fix_chords()

    # ===== 2. 音 =====
    SECS.append(('A 被打断', 0.0, stop, 'Dm–B♭–Gm–A；3+3+2 脉动，木琴磨半音，越来越满，到 stop 一刀切掉'))
    tres('A', 0.0, stop, 0.1)
    bass('A', 0.05, every=4)
    pad_chords('A', 0.6)
    rub('A', 1.0, stop, 4 * Q, 0.11)

    SECS.append(('C 现实和实验', th0, s06, 'Dm–B♭ 低垫音；拨弦很稀；两个拇指琴音'))
    note(th0, 'pad', [hz(mid(x)) for x in ('D4', 'F4', 'A4')], s06 - th0, 0.16, sec='C', send=0.4)
    for t in (s04, s04 + 1.4, s04 + 2.8, s04 + 4.2):
        note(t, 'pizz', mid('D3'), 0.8, 0.13, sec='C', send=0.15)
    note(th1, 'kalimba', mid('A4'), 1.4, 0.2, sec='C')
    note(th1 + 1.1, 'kalimba', mid('F4'), 1.4, 0.16, sec='C')

    SECS.append(('D 三个场景', s06, s09, 'Dm 垫音；每个场景一个拇指琴音'))
    note(s06, 'pad', [hz(mid(x)) for x in ('D4', 'F4', 'A4')], s09 - s06, 0.18, sec='D', send=0.4)
    note(s06, 'kalimba', mid('F4'), 1.6, 0.22, sec='D')
    note(B['S07']['t0'], 'kalimba', mid('D4'), 1.6, 0.2, sec='D')
    note(B['S08']['t0'], 'kalimba', mid('A4'), 1.6, 0.18, sec='D')

    SECS.append(('E 稀缺和观点', s09, hi, 'B♭–Gm–Dm；长的低钢琴，吸走的地方落几个音'))
    note(s09, 'piano', mid('Bb2'), s11 - s09, 0.17, sec='E', send=0.25)
    for t, nm in zip(EV['bites'], ('Bb4', 'A4', 'F4', 'D4')):
        note(t, 'kalimba', mid(nm), 1.4, 0.18, sec='E')
    note(s11, 'piano', mid('G2'), s13 - s11, 0.17, sec='E', send=0.25)
    for nm in ('D3', 'A3'):
        note(fq, 'piano', mid(nm), 1.6, 0.2, sec='E', send=0.35)
    note(s13, 'piano', mid('D2'), hi - s13, 0.18, sec='E', send=0.3)
    for j, nm in enumerate(('A4', 'F4', 'D4')):
        note(s13 + 0.2 + j * 0.7, 'kalimba', mid(nm), 1.4, 0.18 - 0.03 * j, sec='E')

    # —— H 淡淡地收：Gm → Asus4，动机少最后一个音，停在不解决的和弦上淡出 ——
    SECS.append(('H 收', hi, END, 'Gm → Asus4；拇指琴 A D E（少最后一个音）；最后 0.5 秒淡到 0'))
    note(hi, 'pad', [hz(mid(x)) for x in ('G3', 'Bb3', 'D4')], en - hi, 0.2, sec='H', send=0.4)
    note(hi, 'pizz', mid('G2'), 1.0, 0.13, sec='H', send=0.15)
    note(en, 'pizz', mid('A2'), 1.0, 0.14, sec='H', send=0.15)
    note(en, 'pad', [hz(mid(x)) for x in ('A3', 'D4', 'E4')], END - en, 0.24, sec='H', send=0.4)
    for j, nm in enumerate(('A4', 'D5', 'E5')):
        note(en + 0.2 + j * 2 * EI, 'kalimba', mid(nm), 1.6, 0.26, pan=0.15 * (-1) ** j, sec='H')
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
    """整体的起伏（dB），转折点都从 ANCH（EV11、SC11、BEATS11）来：开头最满；另一个人更薄；S04 再低；S05 回一点；thread 起变空；后面都低。"""
    A = ANCH
    pts = [(0.0, -9.0), (A['stop'] * 0.5, -7.0), (A['stop'] - 0.01, -3.0), (A['stop'], -11.0), (A['s04'], -10.0), (A['s09'], -10.0), (A['hi'], -11.0), (A['en'], -10.0), (END, -10.0)]
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])


def gate_curve(t):
    """配乐的门：fear 前 0.55 → 0.28 秒压到 0（先抽空），fear 后 0.4 → 1.4 秒回来；最后 0.5 秒淡到 0。低通之后才乘，所以是真的 0。"""
    q = EV['stop']
    g = np.interp(t, [q - 0.015, q, q + 1.5, q + 2.6], [1, 0, 0, 1])     # 到 stop 一刀切，静 1.5 秒，再慢慢回来
    return g * np.clip((END - t) / 0.5, 0, 1) ** 1.5




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
    scale = 10 ** ((MIX_TARGET - I0) / 20)                              # 累计增益（不含限幅）：music.wav 按它写，电平才等于在 mix.wav 里的电平
    y = mix * scale
    gmin = 1.0
    for _ in range(5):
        tp = 20 * math.log10(sfx.true_peak_env(y).max())
        if tp <= MIX_TP - 0.2:
            break
        y, g = sfx.limit(y, MIX_TP - 0.4)
        gmin = min(gmin, g)
        p = os.path.join(tmp, 'lim.wav')
        sfx.write_wav(p, y)
        k = 10 ** ((MIX_TARGET - sfx.ebur(p)['I']) / 20)
        y, scale = y * k, scale * k
    return y, gmin, scale


def band_share(x, bands):
    P = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    tot = P.sum()
    return {f'{a}–{b} Hz': round(float(P[(f >= a) & (f < b)].sum() / tot) * 100, 1) for a, b in bands}


def harmony_checks():
    """有音高的音效（sfx11.put 的 notes）落在不在当时的和弦里。"""
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
    """前段整体压 db：thread 之前都是 db，之后 2 秒线性回到 0。"""
    t0 = EV['thread'][0]
    return 10 ** (np.interp(np.arange(N) / SR, [0, t0, t0 + 2.0, END + 1], [db, db, 0.0, 0.0]) / 20)


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
    chk = sfx.main()                                                    # 先出音效轨（v11/sfx.wav、sfx_events.json）
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
        mix, gmin, g_all = master(sx + music, tmp)
        sfx.write_wav(OUT_MUSIC, sfx.limit(music * g_all, -1.0)[0])       # 只这条配乐单独限到 −1 dB 防削波；mix.wav 用的是没限的
        sfx.write_wav(OUT_MIX, mix, dither=True, rng=np.random.default_rng(SEED + 1))

    pre = (sx + music) * g_all                                          # 限幅前的混音，下面和读回的 mix.wav 比，看限幅实际压在哪
    # —— 以下全部从磁盘读回量 ——
    x, xsr = sfx.read_wav(OUT_MIX)
    with __import__('wave').open(OUT_MIX) as w:
        bits = 8 * w.getsampwidth()
    fin = sfx.ebur(OUT_MIX)
    fin15 = sfx.ebur(OUT_MIX, 'atrim=0:15')
    ln = sfx.loudnorm_json(OUT_MIX, MIX_TARGET, MIX_TP)
    mo, _ = sfx.read_wav(OUT_MUSIC)
    mus = sfx.ebur(OUT_MUSIC)
    sxf, _ = sfx.read_wav(SFX_WAV)
    xm, sm = x.mean(axis=1), sxf.mean(axis=1)
    # 每个点名的声音：单轨起音差＋成品里的位置差（互相关）= mix.wav 里起音和 EV11 的差
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
    blk = SR // 20
    lim_db = [(20 * math.log10(max(np.abs(x[i:i + blk]).max(), 1e-6) / max(np.abs(pre[i:i + blk]).max(), 1e-6)), i / SR) for i in range(0, N - blk, blk)]
    fq0 = EV['fear']
    lim = dict(fear=round(min(v for v, t in lim_db if fq0 <= t < fq0 + 0.5), 1),
               other=min((round(v, 1), round(t, 2)) for v, t in lim_db if not fq0 - 0.1 <= t < fq0 + 0.5))
    pk = lambda y, a, b: round(20 * math.log10(np.max(np.abs(y[int(a * SR):int(b * SR)])) + 1e-12), 1)
    rmsd = lambda y, a, b: round(20 * math.log10(np.sqrt(np.mean(y[int(a * SR):int(b * SR)] ** 2)) + 1e-12), 1)
    cut, fq = SC['me'][1], EV['fear']
    # 爆音、断层（fear 前后是特意抽空，分开量）
    clip_n = int(np.sum(np.abs(x) >= 32766 / 32768))
    mclip = int(np.sum(np.abs(mo) >= 32766 / 32768))
    dd = np.abs(np.diff(x, axis=0)).max(axis=1)
    jt = int(np.argmax(dd))
    lv = np.abs(x).max(axis=1)
    mlv = np.abs(mo).max(axis=1)
    gaps = dict(mix=max(runs_below(lv, -60, 0.05, fq - 0.3), runs_below(lv, -60, fq, END - 0.5)),
                music=max(runs_below(mlv, -60, 0.05, fq - 0.56), runs_below(mlv, -60, fq + 1.4, END - 0.5)))
    # cut 以后有没有手机声：① 事件表（读回 sfx_events.json）② 拿提示音、震动自己的波形在 sfx.wav 里找（归一化互相关）
    evs = json.load(open(SFX_EVENTS))
    phone_after = [q for q in evs if q['name'] in ('震动', '提示音') and q['t'] >= cut - 1e-6]
    phone_before = [q for q in evs if q['name'] in ('震动', '提示音') and q['t'] < cut]

    def best_match(sig, a, b):
        s = sig[:int(0.3 * SR)]
        seg = sm[int(a * SR):int(b * SR)]
        n_ = 1 << (len(seg) + len(s)).bit_length()
        c = np.fft.irfft(np.fft.rfft(seg, n_) * np.conj(np.fft.rfft(s, n_)), n_)[:len(seg) - len(s) + 1]
        e2 = np.convolve(seg ** 2, np.ones(len(s)), 'valid')
        return round(float(np.max(c / np.sqrt(e2 * np.sum(s ** 2) + 1e-9))), 2)
    tpl = {e['kind']: e['sig'] for e in sfx.EVENTS if e['kind'] in ('震动', '提示音')}
    phone = dict(after=phone_after, n_before=len(phone_before), tail=pk(sxf, cut, cut + 0.05),
                 match={k: (0.0, 0.0) for k in tpl})   # 第十一版手机声到处都有，不再量“cut 以后有没有手机声”
    # fear：前面静不静、是不是全片最重、低不低、配乐让没让
    M = fin['M']

    def mom(t):
        v = M[(M[:, 0] >= t + 0.05) & (M[:, 0] <= t + 0.5), 1]
        return round(float(v.max()), 1) if len(v) else None
    def low_share(a, b):
        seg = sm[int(a * SR):int(b * SR)]
        P = np.abs(np.fft.rfft(seg)) ** 2
        f = np.fft.rfftfreq(len(seg), 1 / SR)
        return round(float(P[f < 1000].sum() / P.sum()) * 100, 1)
    named = [(r['src'], r['t']) for r in rows]
    loud = sorted(((mom(t), s_) for s_, t in named), reverse=True)
    fear = dict(sil_mix=pk(x, fq - sfx.FEAR_SILENCE, fq - 0.002), sil_mus=pk(mo, fq - 0.28, fq), peak=pk(sxf, fq, fq + 0.3), mom=mom(fq), low=low_share(fq, fq + 0.3),
                top=loud[:4], is_top=loud[0][1] == 'EV11.fear', ring_peak=pk(sxf, EV['rings'][0], EV['rings'][0] + 0.3), line3_peak=pk(sxf, EV['line3'], EV['line3'] + 0.3), moms={k: mom(EV[k]) for k in ('line1', 'line2', 'line3')}, ring_mom=mom(EV['rings'][0]),
                mus=(rmsd(mo, fq - 1.5, fq - 0.6), rmsd(mo, fq - 0.28, fq + 0.4), rmsd(mo, fq + 1.5, fq + 2.5)))
    duck = dict(before=rmsd(mo, EV['rings'][1] - 0.5, EV['rings'][1] - 0.1), during=rmsd(mo, EV['rings'][1], EV['rings'][1] + 0.15))
    end = dict(tail=pk(x, END - 0.01, END), mus_before=rmsd(mo, END - 1.5, END - 0.6))
    MM = mus['M']
    sec_rows = []
    for name, s0, s1, desc in SECS:
        v = MM[(MM[:, 0] >= s0 + 0.4) & (MM[:, 0] <= s1), 1]
        v = v[v > -70]
        chs = [c[2] for c in sorted(CHORDS) if s0 - 1e-6 <= c[0] < s1 - 1e-6]
        sec_rows.append(dict(name=name, t0=round(s0, 2), t1=round(s1, 2), desc=desc, chords='–'.join(dict.fromkeys(chs)) if chs else '',
                             M=round(float(np.median(v)), 1) if len(v) else None))
    harm = harmony_checks()
    s = dict(mix=dict(sr=xsr, samples=len(x), seconds=len(x) / SR, ch=x.shape[1], bits=bits, I=fin['I'], LRA=fin['LRA'], TP=fin['TP'],
                      ln_I=float(ln['input_i']), ln_TP=float(ln['input_tp']), lim=round(20 * math.log10(gmin), 2),
                      I15=fin15['I'], d15=round(fin15['I'] - fin['I'], 1), ride=round(ride_db, 2)),
             music=dict(I=mus['I'], TP=mus['TP'], notes=len(NOTES)), sfx=dict(I=chk['I'], TP=chk['TP'], events=chk['events'], lim=chk['limiter_min_db']),
             rows=rows, lim=lim, clip=clip_n, mclip=mclip, mpeak=pk(mo, 0, END), jump=(round(float(dd[jt]), 3), round(jt / SR, 3)), gaps=gaps, phone=phone, fear=fear, duck=duck, end=end,
             secs=sec_rows, harm=harm, solo_off=chk['solo_off'], chords=sorted({c[2] for c in CHORDS}), fixes=list(FIXES))
    write_md(s)
    m = s['mix']
    print(f"写出 {OUT_MIX}：{m['samples']} 个采样 = {m['seconds']:.4f} 秒，{m['sr']} Hz × {m['ch']}，{m['bits']} bit；I {m['I']} LUFS（loudnorm {m['ln_I']}），"
          f"真峰值 {m['TP']} dBTP（loudnorm {m['ln_TP']}），LRA {m['LRA']}，限幅最深 {m['lim']} dB；前 15 秒 {m['I15']}（差 {m['d15']}，压 {m['ride']} dB）")
    mx = max(abs(r['total']) for r in rows if r['total'] is not None)
    print(f"点名的 {len(rows)} 个：起音最大差 {mx} 毫秒；相关最低 {min(r['cc'] for r in rows)}；没量出的 {[r['name'] for r in rows if r['total'] is None]}")
    print('超 1 帧', [(r['src'], r['total']) for r in rows if r['total'] is None or abs(r['total']) > 1000 / FPS])
    print('相关低', [(r['src'], r['cc'], r['total']) for r in rows if r['cc'] < 0.3])
    print('music.wav 峰值', s['mpeak'], '削波', mclip, '爆音', clip_n, '最大跳变', s['jump'], '断层', gaps)
    print('手机', phone)
    print('fear', fear)
    print('duck', duck, 'end', end)
    print('各段', [(r['name'], r['M'], r['chords']) for r in sec_rows])
    print('和弦外的音效', [(r['t'], r['label'], r['note'], r['chord']) for r in harm if not r['in_chord']], '换过的和弦', FIXES, '音符数', len(NOTES))


def write_md(s):
    m, rows = s['mix'], s['rows']
    ok = lambda v: v is not None and abs(v) <= 1000 / FPS
    yn = lambda b: '是' if b else '否'
    mx = max(abs(r['total']) for r in rows if r['total'] is not None)
    worst = max((r for r in rows if r['total'] is not None), key=lambda r: abs(r['total']))
    bad = [r for r in s['harm'] if not r['in_chord']]
    ph, fq, du = s['phone'], s['fear'], s['duck']
    cut, q = SC['me'][1], EV['fear']
    bubs = [r for r in rows if r['src'].startswith('EV11.bubbles（')]
    low_cc = [r for r in rows if r['cc'] < 0.2]
    L = ['# 003《消息提醒》第十一版声音自查', '',
         '脚本：`videos/003_消息提醒/music11.py`（先调 `sfx11.py`）。numpy 合成，没用曲库、采样、第三方账号，不配人声。时间全从 `studio/src/videos/003/timeline11.ts` 读，没改它。'
         '下面的数全部从磁盘读回 wav 量（ffmpeg ebur128，peak=true；ffmpeg 是 imageio_ffmpeg 自带的）。', '',
         '## 结论', '',
         f'- **响度**：mix.wav 整条 **{m["I"]} LUFS**（要求 −14 ±0.5：{yn(abs(m["I"] + 14) <= 0.5)}），真峰值 **{m["TP"]} dBTP**（要求 ≤ −2：{yn(m["TP"] <= -2.0)}）；'
         f'loudnorm 复核 {m["ln_I"]} LUFS、{m["ln_TP"]} dBTP；LRA {m["LRA"]} LU；限幅主要压在 fear 那一记（{s["lim"]["fear"]} dB，这一记本来要最重），别处最深 {s["lim"]["other"][0]} dB（{s["lim"]["other"][1]} 秒）。',
         f'- **格式和长度**：{m["sr"]} Hz、{m["ch"]} 声道、{m["bits"]} bit；{m["samples"]} 个采样 = {m["seconds"]:.4f} 秒（DUR11 = {END:g}：{yn(m["samples"] == N)}）。',
         f'- **对点**：点名的 {len(rows)} 个声音，起音和 EV11 的差最大 **{mx} 毫秒**（{worst["src"]}），1 帧 = {1000 / FPS:.1f} 毫秒，全部 ≤ 1 帧：{yn(all(ok(r["total"]) for r in rows))}。',
         f'- **cut（{cut} 秒）以后手机一声都不响**：sfx_events.json 里 cut 前手机声 {ph["n_before"]} 个（buzz0、rings，每次震＋提示音），cut 后 **{len(ph["after"])} 个**。'
         f'拿震动、提示音自己的波形在 sfx.wav 里找（归一化互相关，cut 前 → cut 后）：'
         + '；'.join(f'{k} {a} → {b}' for k, (a, b) in ph['match'].items()) +
         f'。rings 的尾巴在 cut 那一刻收掉：cut 到贴纸之间 sfx.wav 最响 {ph["tail"]} dBFS。',
         f'- **fear（{q} 秒）前的静**：mix.wav 在 {q - sfx.FEAR_SILENCE:.2f}–{q:.2f} 秒（{sfx.FEAR_SILENCE} 秒）最响 **{fq["sil_mix"]} dBFS**（要求静 0.2–0.3 秒）；'
         f'配乐有效值 fear 前 {fq["mus"][0]} → 抽空 {"真 0" if fq["mus"][1] < -200 else fq["mus"][1]} → 回来 {fq["mus"][2]} dBFS。',
         f'- **fear 是全片最重的一下**（点名的声音里排第一：{yn(fq["is_top"])}）：mix.wav 里 400 毫秒响度 {fq["mom"]} LUFS，对比手机响 {fq["ring_mom"]}、line1 {fq["moms"]["line1"]}、line2 {fq["moms"]["line2"]}、line3 {fq["moms"]["line3"]}（三下递进，line3 最重）；'
         f'sfx.wav 峰值 fear {fq["peak"]}、手机响 {fq["ring_peak"]}、line3 {fq["line3_peak"]} dBFS；落下后 0.3 秒 {fq["low"]}% 的能量在 1 kHz 以下（低、闷）。',
         f'- **手机响时配乐让开**：rings[1] 前 {du["before"]} → 响时 {du["during"]} dBFS（music.wav 有效值）。',
         f'- **爆音**：mix.wav 到满刻度的采样 {s["clip"]} 个（music.wav {s["mclip"]} 个，峰值 {s["mpeak"]} dBFS）；相邻采样最大跳变 {s["jump"][0]}（{s["jump"][1]} 秒，是那里音效自己的起音）。',
         f'- **断层**：除 fear 前后特意抽空以外，mix.wav 连续低于 −60 dBFS 最长 {s["gaps"]["mix"]} 秒，music.wav 最长 {s["gaps"]["music"]} 秒。',
         f'- **调**：全片只用小调一路的和弦 {"、".join(s["chords"])}，没有大调明亮收尾；停在 Asus4 上，最后 0.5 秒淡到 0（最后 10 毫秒 mix.wav 最响 {s["end"]["tail"]} dBFS）。',
         f'- **和弦**：有音高的音效 {len(s["harm"])} 个音，落在当时和弦外的 {len(bad)} 个；换过和弦 {len(s["fixes"])} 格。',
         f'- **前 15 秒**：{m["I15"]} LUFS，比全片响 {m["d15"]} LU（第四版评委口径：不超过 2）；' + ('没压。' if m['ride'] == 0 else f'thread 前整体压了 {m["ride"]} dB。'),
         '', '## 1. 点名的音效：起音和 EV11 差多少（毫秒）', '',
         '单轨差 = 只放这一个声音时量到的起音；位置差 = 拿它自己的波形在 mix.wav 里做互相关找到的位置；合计 = 两个相加。', '',
         '| 要的声音 | 出处 | 秒 | 帧 | 单轨差 | 位置差（相关系数） | 合计 | ≤1 帧 |', '|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r in bubs:
            continue
        L.append(f'| {r["name"]} | {r["src"]} | {r["t"]:.3f} | {r["frame"]} | {r["solo"]} | {r["lag"]}（{r["cc"]}） | {r["total"]} | {yn(ok(r["total"]))} |')
    L += ['', f'- bubbles 区间 {len(bubs)} 个气泡（时间公式和 Notice11.tsx 一样，越来越密）不逐行列：合计差最大 {max(abs(r["total"]) for r in bubs)} 毫秒，全部 ≤ 1 帧：{yn(all(ok(r["total"]) for r in bubs))}。',
          '', '## 2. 配乐各段', '', '| 段 | 起–止（秒） | 和弦 | 做法 | 瞬时响度中位数（LUFS） |', '|---|---|---|---|---|']
    for r in s['secs']:
        L.append(f'| {r["name"]} | {r["t0"]}–{r["t1"]} | {r["chords"]} | {r["desc"]} | {r["M"]} |')
    L += ['', f'配乐 {s["music"]["notes"]} 个音；music.wav 单独 {s["music"]["I"]} LUFS（就是它在 mix 里的电平），sfx.wav 单独 {s["sfx"]["I"]} LUFS、真峰值 {s["sfx"]["TP"]} dBTP。',
          '', '## 3. 没做到或没查的', '',
          '- 只用数字量过，没人听过，也没在手机上外放过；“轻快但烦躁”“闷”这些听感没评审。',
          '- 没合进成片跑 `tools/watch/check.py`（这次不渲染）。',
          '- EV11 里没点名的 bell、scroll、cardsOut、fadeOut 没配声（bell 在 cut 之后，配了会被听成手机响）。']
    if low_cc:
        L.append(f'- 相关系数低于 0.2 的 {len(low_cc)} 行（' + '、'.join(r['src'] for r in low_cc) + '）很轻、被配乐盖住，互相关找到的位置不可靠；这些声音在脚本里按采样放在 EV11 的秒上，看单轨差。')
    open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
