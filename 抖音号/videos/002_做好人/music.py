"""《被坑多了，你会变狠吗？》（002 横屏，第五版，59.65 秒 = 1790 帧）的原创配乐，和音效混成最终音轨。

为什么自己做：抖音网页“添加音乐”只改作品底部显示的歌名，不改作品声音；项目规矩不开第三方账号、不下载别人的歌，
所以和 sfx.py 一样全部用 numpy 合成。纯音乐，没有人声，没有鼓。

  /Users/decheng.huang/Documents/dy/.venv/bin/python /Users/decheng.huang/Documents/dy/videos/002_做好人/music.py

读：studio/src/videos/002/timeline.json（每拍起止、事件；只读）
    studio/public/002/sfx.wav、sfx_events.json（sfx.py 的成品；只读，不改）
写：studio/public/002/music.wav（单独的配乐，电平 = 它在 mix.wav 里的电平，含让开，没过限幅）
    studio/public/002/mix.wav（音效 × MIX_SFX_GAIN ＋ 配乐，整条 −15 LUFS，过一道前瞻限幅，真峰值 ≤ −2 dBTP）
    videos/002_做好人/out/音效/配乐核对.json（自查结果）

调和速度：G 大调（和“你只有一遍”的暖音、四盏灯同调），100 BPM。每一段从时间表的拍起点重新起拍（段和段之间本来就有停顿），
段内按 100 BPM 的八分音符走。主要能量在 200 Hz–2 kHz：最低的低音在 130 Hz 上下、很轻，整条过 2.4 kHz 的柔和低通，
不抢 1–4 kHz 的关键音效。

结构（秒数都从 timeline.json 取，括号里是第五版的值）：
  A   S01–S03（0–6.4）     拇指琴轻起；S02 起八分音符琶音，轻快、好奇。开头动机 G B D E D（往上看一眼 E，像在问）
  ？  S04（6.4）            停在 D9sus4（D A C E G）上，没解决，响到倒带
  R   S05（7.8–8.4）       让开：7.8 收掉；8.1–8.4 一下倒放的 G 和弦吸进主旋律
  B   S06–S09（8.4–14.7）  主旋律（木琴），G – Em – C – D
  B'  S10–S13（14.7–22.8） 变狠：同一条旋律借小调（Cm 的 E♭），Em – Cm – Em – Cm
  C   S14–S17（22.8–30.9） 世界冷了：没有琶音、没有低音，只剩每两拍一声冷的玻璃音和很薄的垫音；S15 全停时配乐也停
  D   S18–S23（30.9–45.2） 一点点回暖：琶音从四分音符慢慢回到八分音符，回到大调；S19 定住时停一下，S20 只留一个和弦；
                           S21（38.2–40.6）“没完没了”：一来一回的两音，和乒乓同一个格（每 0.4 秒一下 = 100 BPM 的四分三连音）；
                           40.6 起柔和的钢琴接旋律
  E   S24–S25             最暖最满但仍轻：琶音＋钢琴旋律＋钢琴和弦＋垫音；四盏灯（lamps）响时旋律让开，只留和弦
  U   S26（第七版三改）    “原谅的世界里，好欺负的人多了”：安稳里透出一点不安，别太暗；大调，每拍一个往下走的拇指琴，最后半拍 C 变 Cm
  F   S26b（第七版三改）   “狠人又过得好了，大家又学狠”：转暗、变稀，和回暖反差。没有琶音、没有旋律，只剩每拍一下的低音和暗的垫音，
                           Em → Cm → A♭（比 G 高半音）；第七版重排后它在 S25 前面，S25 一进来往下落半音回到 G
  W   S25（第七版重排）    四个你＋带走句：回暖，软的 G 和弦，四盏灯往上走完后拇指琴把开头动机答一遍；S27–S27h 不出字，和音效的暖音一起收薄
  G   S28–S29              回到开头的动机，两个选项亮起那 0.6 秒让开；停在 D9sus4 上，最后一秒淡到 0，接回第 0 帧的 G 正好解决
  （第七版起各段的秒数都跟时间表走，上面括号里的是第五版的值。）

混音：配乐比音效低一大截（整条比音效低 MUSIC_REL LU）；每个 key 音效出现时配乐再压 DUCK_DB（提前 40 毫秒压下、
压 0.15 秒、0.5 秒放开）；音效全停的地方（S15 粉线起到定住结束、S19 定住）配乐也停。
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfx                                   # 只借它的合成零件、响度和限幅函数；不跑它的 main，不写 sfx.wav

ROOT = sfx.ROOT
TL = sfx.TL
B = sfx.B
E = sfx.E
SR, FPS, NF, SPF = sfx.SR, sfx.FPS, sfx.NF, sfx.SPF
N = NF * SPF
SFX_WAV = sfx.OUT_WAV
SFX_EVENTS = sfx.OUT_EVENTS
OUT_MUSIC = os.path.join(ROOT, 'studio', 'public', '002', 'music.wav')
OUT_MIX = os.path.join(ROOT, 'studio', 'public', '002', 'mix.wav')
OUT_CHECK = os.path.join(HERE, 'out', '音效', '配乐核对.json')
SEED = 3002

BPM = 100.0
Q = 60.0 / BPM                    # 一拍 0.6 秒
EI = Q / 2                        # 八分音符 0.3 秒
MIX_TARGET = -15.0                # mix.wav 整条响度
MIX_TP = -2.0                     # mix.wav 真峰值上限（留 0.5 dB 给 AAC 编码）
MUSIC_REL = -11.0                 # 配乐整条响度比音效整条低多少 LU
DUCK_DB = -6.0                    # key 音效出现时配乐再压多少（第七版从 −5 加到 −6，要求的 3–6 dB 的上限）

t_ = lambda bid: B[bid]['t0']
s_ = lambda bid, k, i=0: (lambda v: (v[i] if isinstance(v, list) else v) / FPS)(E(bid, k))

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
    'G': 'G B D', 'Em': 'E G B', 'C': 'C E G', 'D': 'D F# A', 'Cm': 'C Eb G', 'Am9': 'A C E B',
    'Emadd9': 'E G B F#', 'Cmaj7': 'C E G B', 'D9sus4': 'D G A C E', 'Cadd9': 'C E G D', 'Ab': 'Ab C Eb',
}
ROOTNOTE = {'G': 'G3', 'Em': 'E3', 'C': 'C3', 'D': 'D3', 'Cm': 'C3', 'Am9': 'A3', 'Emadd9': 'E3', 'Cmaj7': 'C3',
            'D9sus4': 'D3', 'Cadd9': 'C3'}


def tones(ch, lo, hi):
    """和弦 ch 在 [lo, hi]（MIDI）之间的所有音，从低到高。"""
    pcs = {PC[x] for x in CHORD[ch].split()}
    return [m for m in range(mid(lo), mid(hi) + 1) if m % 12 in pcs]


# ======================================================================
# 乐器（都返回单声道；峰值没归一，幅度就是力度）
# ======================================================================
ts = sfx.ts


def kalimba(rng, f0, vel=0.7, ring=1.4):
    """拇指琴：金属簧片拨一下。主音很强，带 1.0015 倍的伴音（一点拍频）、很弱的 2 倍、3 倍，和一个 5.9 倍的簧片泛音（35 毫秒就没了）；
    拨的那一下是一口低通过的软噪声。越低的音衰减越长。"""
    n = int(ring * SR)
    tau = 0.85 * (392.0 / f0) ** 0.35
    parts = [(f0, 1.0, tau), (f0 * 1.0015, 0.22, tau * 0.9), (2.0 * f0, 0.07, tau * 0.28), (3.01 * f0, 0.04, 0.06),
             (5.92 * f0, 0.07 * vel, 0.035)]
    y = sfx.modal(n, parts, rng, att=0.0012)
    y = y + 0.05 * sfx.contact(n, rng, 300, 1800, 0.004)
    return vel * sfx.fades(sfx.shape(y, 120, 2600, order=2), 0.0005, 0.05)


def marimba(rng, f0, vel=0.7):
    """木琴：软槌敲木条。1、3.93、9.2 倍三个模态（调过音的木条），高的衰减很快；软槌的一下闷响。"""
    n = int(1.3 * SR)
    tau = 0.55 * (392.0 / f0) ** 0.5
    parts = [(f0, 1.0, tau), (3.93 * f0, 0.12 * vel, 0.05), (9.2 * f0, 0.02, 0.012), (f0 * 0.5, 0.05, 0.05)]
    y = sfx.modal(n, parts, rng, att=0.002)
    y = y + 0.04 * sfx.contact(n, rng, 200, 1500, 0.006)
    return vel * sfx.fades(sfx.shape(y, 120, 2400, order=2), 0.0005, 0.05)


def piano(rng, f0, dur, vel=0.5):
    """柔和的钢琴：两根弦（差 ±0.8 音分），谐波带一点非谐（B = 0.0003），高次谐波衰减更快；力度小，所以高谐波少（音色暗、圆）；
    放开时 0.2 秒收掉（制音器）。最高到 3.5 kHz 的谐波。"""
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


def chime(rng, f0, vel=0.5):
    """冷的玻璃音（世界冷了那一段）：几乎只有主音，30 毫秒慢起（没有敲击感），衰减长，带一点 2.76 倍的冷泛音。"""
    n = int(2.4 * SR)
    t = ts(n)
    y = (np.sin(2 * np.pi * f0 * t + rng.uniform(0, 6.28)) * np.exp(-t / 1.1)
         + 0.25 * np.sin(2 * np.pi * f0 * 1.0021 * t) * np.exp(-t / 0.9)
         + 0.06 * np.sin(2 * np.pi * 2.756 * f0 * t) * np.exp(-t / 0.25))
    y *= np.clip(t / 0.03, 0, 1)
    return vel * sfx.fades(sfx.shape(y, 250, 2400, order=2), 0.0, 0.1)


# ======================================================================
# 谱子
# ======================================================================
NOTES = []        # dict(t, inst, m 或 freqs, dur, vel, pan, sec, send)
CHORDS = []       # (起, 止, 和弦, 段)


def note(t, inst, m, dur=0.6, vel=0.6, pan=0.0, sec='', send=0.22):
    NOTES.append(dict(t=float(t), inst=inst, m=m, dur=dur, vel=vel, pan=pan, sec=sec, send=send))


def chords(sec, t0, t1, plan):
    """plan：[(拍, 和弦), ...]，拍从 t0 起算（100 BPM）。最后一个和弦到 t1。"""
    for k, (b, ch) in enumerate(plan):
        a = t0 + b * Q
        z = t0 + plan[k + 1][0] * Q if k + 1 < len(plan) else t1
        if a >= t1 - 0.05:              # 段变短了：起点在段尾之后的和弦不要
            break
        CHORDS.append((a, min(z, t1), ch, sec))


def chord_at(t):
    for a, z, ch, sec in CHORDS:
        if a - 1e-6 <= t < z - 1e-6:
            return ch
    return None


def arp(sec, t0, t1, pattern, lo, hi, vel, step=EI, mask=None, pan=0.18, ring=1.4):
    """琶音：每 step 秒一个音，取那一刻的和弦在 [lo, hi] 里的第 pattern[k] 个音。mask(k, t) 为假就跳过（用来变稀）。"""
    k = 0
    t = t0
    while t < t1 - 1e-6:
        ch = chord_at(t)
        if ch and (mask is None or mask(k, t)):
            ts_ = tones(ch, lo, hi)
            m = ts_[min(pattern[k % len(pattern)], len(ts_) - 1)]
            note(t, 'kalimba', m, ring, vel(t) if callable(vel) else vel, pan=pan * (1 if k % 2 else -1), sec=sec)
        k += 1
        t = t0 + k * step


def bass(sec, vel=0.35, skip=()):
    for a, z, ch, s in CHORDS:
        if s == sec and a not in skip:
            note(a, 'piano', mid(ROOTNOTE[ch]), min(z - a, 2.4), vel, sec=sec)


def melody(sec, t0, inst, line, vel=0.6, send=0.22, end=None):
    """line：[(拍, 长几拍, 音名), ...]，拍从 t0 起算。end：这一段到哪为止，起点在它之后的音不弹、长的截短（拍变短时旋律不拖进下一段）。"""
    for b, d, nm in line:
        a = t0 + b * Q
        if end is not None and a >= end - 0.05:
            continue
        note(a, inst, mid(nm), min(d * Q, end - a) if end is not None else d * Q, vel, sec=sec, send=send)


def compose():
    NOTES.clear()
    CHORDS.clear()
    t04, t05, t06, t10, t14, t18 = t_('S04'), t_('S05'), t_('S06'), t_('S10'), t_('S14'), t_('S18')
    t19f0, t19f1 = s_('S19', 'freeze', 0), s_('S19', 'freeze', 1)
    t20, t21, t22, t24, t26, t27, t28 = t_('S20'), t_('S21'), t_('S22'), t_('S24'), t_('S26'), t_('S27'), t_('S28')
    s15a, s15b = s_('S15', 'lines', 0), s_('S15', 'freeze', 1)

    # —— A 0–6.4：轻起；S02 起八分音符琶音，轻快、好奇 ——
    chords('A', 0.0, t04, [(0, 'G'), (4, 'C'), (6, 'Em'), (8, 'C'), (10, 'G')])
    motif = [(0, 'G4'), (0.5, 'B4'), (1, 'D5'), (1.5, 'E5'), (2, 'D5'), (3, 'B4')]     # 开头动机：往上看一眼 E 再落回来
    for b, nm in motif:
        note(b * Q, 'kalimba', mid(nm), 1.4, 0.45, sec='A')
    t02 = t_('S02')
    arp('A', t02, t04, [0, 2, 1, 3, 2, 1, 3, 2], 'G4', 'G5', lambda t: 0.36 + 0.12 * min(1, (t - t02) / 2.0))
    bass('A', 0.28, skip=(0.0,))
    melody('A', t_('S03') - 0.2, 'marimba', [(0, 0.5, 'E5'), (0.5, 0.5, 'D5'), (1, 1, 'B4')], 0.42)    # 3.6 再问一次
    # —— ？ 6.4：停在 D9sus4，没解决，响到倒带 ——
    CHORDS.append((t04, t05, 'D9sus4', '？'))
    for nm in ('D3', 'A3', 'C4', 'E4', 'G4'):
        note(t04, 'piano', mid(nm), t05 - t04, 0.42, sec='？')
    note(t04, 'pad', [hz(mid(x)) for x in ('D4', 'A4', 'C5', 'E5')], t05 - t04, 0.5, sec='？')
    note(t04 + 0.02, 'kalimba', mid('A5'), 1.4, 0.3, sec='？')
    # —— R 7.8–8.4：让开；8.1 起一下倒放的 G 和弦吸进主旋律 ——
    note(s_('S05', 'rewind', 1), 'rev', [mid(x) for x in ('G4', 'B4', 'D5')], t06 - s_('S05', 'rewind', 1), 0.45, sec='R')

    # —— B 8.4–14.7：主旋律（木琴） G – Em – C – D ——
    chords('B', t06, t10, [(0, 'G'), (4, 'Em'), (6, 'C'), (8, 'D')])
    arp('B', t06, t10, [0, 1, 2, 3, 2, 1, 2, 1], 'G4', 'D5', 0.42)
    bass('B', 0.33)
    theme = [(0, 1, 'D5'), (1, 0.5, 'B4'), (1.5, 0.5, 'D5'), (2, 2, 'G5'), (4, 1, 'E5'), (5, 0.5, 'D5'), (5.5, 0.5, 'B4'),
             (6, 1, 'C5'), (7, 1, 'E5'), (8, 1, 'D5'), (9, 1, 'A4'), (10, 0.5, 'F#4')]
    melody('B', t06, 'marimba', theme, 0.62, end=t10)
    # —— B' 14.7–22.8：变狠，借小调（Cm 的 E♭）：Em – Cm – Em – Cm ——
    chords("B'", t10, t14, [(0, 'Em'), (4, 'Cm'), (7, 'Em'), (9, 'Cm')])
    arp("B'", t10, t14, [0, 2, 1, 2, 0, 2, 1, 2], 'E4', 'C5', 0.38)
    bass("B'", 0.33)
    # 第七版：B' 从 14.0 起，路线图“回到狠”的闷铃在第 2 拍多一点；原来第 2 拍那个长 E5 压在铃上，挪到第 3 拍，铃那里空着
    theme_m = [(0, 1, 'B4'), (1, 0.5, 'G4'), (1.5, 0.5, 'B4'), (3, 1, 'E5'), (4, 1, 'Eb5'), (5, 1, 'D5'), (6, 1, 'C5'),
               (7, 1, 'B4'), (8, 1, 'G4'), (9, 2, 'Eb5'), (11, 1, 'D5'), (12, 1.5, 'C5')]
    melody("B'", t10, 'marimba', theme_m, 0.56, end=t14)

    # —— C 22.8–30.9：世界冷了：没有琶音、没有低音；每两拍一声冷的玻璃音，很薄的垫音；S15 全停时也停 ——
    tc = [t14, s15b + 0.01, t_('S17') - 0.5, t_('S17') + 0.9]
    CHORDS.extend([(t14, s15b, 'Emadd9', 'C'), (s15b, tc[2], 'Cmaj7', 'C'), (tc[2], tc[3], 'Am9', 'C'), (tc[3], t18, 'Em', 'C')])
    cold_line = ['B4', 'F#5', 'E5', 'G5', 'E5', 'B4', 'G4', 'B4']
    k = 0
    t = t14
    while t < t18 - 0.3:
        if not (s15a - 0.05 <= t < s15b + 0.3):
            ch = chord_at(t)
            nm = cold_line[k % len(cold_line)]
            pcs = {PC[x] for x in CHORD[ch].split()}
            m = mid(nm)
            while m % 12 not in pcs:            # 落到这一刻的和弦音上（往下找）
                m -= 1
            note(t, 'chime', m, 2.0, 0.42, sec='C', send=0.5)
            k += 1
        t += 2 * Q
    for a, z, ch, sec in [c for c in CHORDS if c[3] == 'C']:
        fq = [hz(m) for m in tones(ch, 'E4', 'B5')][:4]
        note(a, 'pad_cold', fq, max(0.3, z - a - 0.2), 0.32, sec='C', send=0.45)

    # —— D 30.9–45.2：一点点回暖 ——
    d1 = t18
    chords('D', d1, t19f0, [(0, 'Em'), (2, 'C'), (5, 'G'), (8, 'D')])
    # 琶音：先四分音符、隔一个弹一个，33.9（第 5 拍）起每个四分音符，35.7（第 8 拍）起八分音符
    arp('D', d1, t19f0, [0, 2, 1, 2, 3, 2, 1, 2], 'G4', 'D5', lambda t: 0.26 + 0.12 * min(1, (t - d1) / 5.0),
        mask=lambda k, t: (k % 4 == 0) if t < d1 + 5 * Q else (k % 2 == 0) if t < d1 + 8 * Q else True)
    bass('D', 0.26)
    CHORDS.append((t19f1, t21, 'Em', 'D'))                   # S20：只留一个和弦（S19 定住结束后轻轻起）
    note(t19f1 + 0.05, 'pad', [hz(mid(x)) for x in ('E4', 'G4', 'B4')], t21 - t19f1 - 0.1, 0.4, sec='D')
    # S21 38.2–40.6 “没完没了”：一来一回，和乒乓同一个格（每 0.4 秒 = 四分三连音）；你出手低、他出手高
    q0, q1 = E('S21', 'pong')
    per = sfx.T(0.4)
    CHORDS.extend([(t21, t21 + 4 * per / FPS - 0.1, 'G', 'D'), (t21 + 4 * per / FPS - 0.1, t22, 'D', 'D')])
    leg = 0
    while q0 + per * leg < q1:
        t = (q0 + per * leg) / FPS
        ch = chord_at(t)
        lo, hi = ('G4', 'D5') if ch == 'G' else ('D4', 'A4')
        m = mid(lo) if leg % 2 == 0 else mid(hi)
        note(t, 'kalimba', m, 1.0, 0.44, pan=-0.2 if leg % 2 == 0 else 0.2, sec='D')
        leg += 1
    note(t21, 'piano', mid('G3'), 4 * per / FPS, 0.26, sec='D')
    note(t21 + 4 * per / FPS - 0.1, 'piano', mid('D3'), t22 - t21 - 4 * per / FPS + 0.1, 0.26, sec='D')
    # 40.6 起：柔和的钢琴接旋律，C – D – G – Em – C
    chords('D', t22, t24, [(0, 'C'), (2, 'D'), (3, 'G'), (5, 'Em'), (6, 'C')])
    arp('D', t22, t24, [0, 1, 2, 1, 3, 2, 1, 2], 'G4', 'D5', 0.4)
    bass('D', 0.3, skip=tuple(c[0] for c in CHORDS if c[3] == 'D' and c[0] < t22 - 1e-6))
    melody('D', t22, 'piano', [(0, 1, 'E5'), (1, 1, 'G5'), (2, 1, 'F#5'), (3, 1.5, 'D5'), (4.5, 0.5, 'B4'), (5, 1, 'E5'),
                              (6, 1, 'E5'), (7, 0.67, 'D5')], 0.46, end=t24)

    # —— E 45.2–51.4：最暖最满，但仍轻；四盏灯（lamps）响时旋律让开 ——
    chords('E', t24, t26, [(0, 'G'), (2, 'Em'), (4, 'C'), (5, 'D'), (6, 'G'), (9, 'C')])
    arp('E', t24, t26, [0, 1, 2, 3, 4, 3, 2, 1], 'G4', 'A5', 0.44)
    bass('E', 0.32)
    melody('E', t24, 'piano', [(0, 1, 'D5'), (1, 0.5, 'B4'), (1.5, 0.5, 'D5'), (2, 2, 'G5'), (4, 1, 'E5'), (5, 1, 'F#5'),
                              (9, 1, 'E5'), (10, 0.33, 'D5')], 0.48, end=t26)
    for a, z, ch, sec in [c for c in CHORDS if c[3] == 'E']:
        vo = [m for m in tones(ch, 'G3', 'D5')][:4]
        for m in vo:
            note(a, 'piano', m, z - a, 0.22, sec='E')
        note(a, 'pad', [hz(m) for m in tones(ch, 'D4', 'D5')][:4], z - a, 0.45, sec='E')

    # —— U（第七版三改 S26“原谅的世界里，好欺负的人多了”）：安稳里透出一点不安，别太暗。还是大调，琶音变成每拍一个、往下走，
    #    没有旋律；G → Em → C，最后半拍 C 里的 E 换成 E♭（Cm），往下一拍的暗处带一下 ——
    tu0, tu1 = t_('S26'), t_('S26b')
    chords('U', tu0, tu1, [(0, 'G'), (2, 'Em'), (3, 'C'), (3.5, 'Cm')])
    arp('U', tu0, tu1, [3, 2, 1, 0], 'G4', 'D5', 0.34, step=Q, ring=1.6)
    bass('U', 0.24)
    for a, z, ch, sec in [c for c in CHORDS if c[3] == 'U']:
        note(a, 'pad', [hz(m) for m in tones(ch, 'D4', 'D5')][:3], z - a, 0.36, sec='U')

    # —— F（第七版三改挪到 S26b“狠人又过得好了，大家又学狠”）：转暗、变稀，和前面的回暖反差。没有琶音、没有旋律，
    #    只剩每拍一下的低音和暗的垫音：run2 起 Cm（借来的小调 iv）；第 860 代停住那一刻落到 A♭（降 II），挂着不动，
    #    比 G 只高半音，S25 一进来就往下落半音回到 G ——
    t26 = t_('S26b')
    t27 = t_('S25')                                          # 暗段到 S25 开头为止（变量名沿用）
    r0, r1 = s_('S26b', 'run2', 0), s_('S26b', 'run2', 1)
    tab = r1                                                 # 停住那一刻换到 A♭
    CHORDS.extend([(t26, tab, 'Cm', 'F'), (tab, t27, 'Ab', 'F')])
    k = 0
    while r0 + k * Q < tab - 0.3:                            # 跑的时候每拍一下低音 C + G，越来越重
        for nm in ('C3', 'G3'):
            note(r0 + k * Q, 'piano', mid(nm), Q * 0.95, 0.34 + 0.03 * k, sec='F')
        k += 1
    for nm in ('Ab2', 'Eb3', 'C4'):                          # 停住：A♭ 一下，挂到 S25
        note(tab, 'piano', mid(nm), t27 - tab, 0.36, sec='F')
    note(r0, 'pad_dark', [hz(mid(x)) for x in ('C4', 'Eb4', 'G4')], tab - r0, 0.5, sec='F')
    note(tab, 'pad_dark', [hz(mid(x)) for x in ('Ab3', 'C4', 'Eb4')], t27 - tab - 0.2, 0.55, sec='F')

    # —— W（第七版重排 S25 四个你＋带走句，S27–S27h 不出字）：回暖、回到开头的动机。S25 一开头一个软的 G 和弦；
    #    四盏灯（G5 B5 D6 G6，lamps）往上走完以后，拇指琴低一个八度把开头动机答一遍（G B D E D B），灯响时不弹，灯的起音干净；
    #    S27 起和音效的暖音一起收薄，S28 前淡完，把地方留给钟表“嘀” ——
    tw, tw1, lamps = t_('S25'), t_('S27'), [f / FPS for f in E('S25', 'lamps')]
    tm = lamps[-1] + EI * 0.5                                # 最后一盏灯之后半个八分音符起
    CHORDS.extend([(tw, tm + 1 * Q, 'G', 'W'), (tm + 1 * Q, tw1, 'Cadd9', 'W'), (tw1, t28, 'G', 'W')])
    for nm in ('G3', 'D4', 'B4'):
        note(tw, 'piano', mid(nm), tm - tw, 0.26, sec='W')
    note(tw, 'pad', [hz(mid(x)) for x in ('D4', 'G4', 'B4')], tw1 - tw, 0.42, sec='W')
    for b, nm in motif:
        if tm + b * Q < t_('S27h') - 0.05:                 # 第七版三改：S27＋S27h 压到 1 秒，动机截在 S27h 之前
            note(tm + b * Q, 'kalimba', mid(nm), 1.4, 0.4 - 0.04 * b, sec='W')
    note(tm + 1 * Q, 'pad', [hz(mid(x)) for x in ('C4', 'E4', 'G4', 'D5')], tw1 - tm - Q, 0.36, sec='W')

    # —— G 55.65–59.65：回到开头的动机；两个选项亮起那 0.6 秒让开；停在 D9sus4 上，接回第 0 帧的 G ——
    o1, o2 = E('S28', 'opt1') / FPS, E('S28', 'opt2') / FPS
    tq = o2 + 0.45 + EI * 2
    CHORDS.append((t28, tq, 'G', 'G'))
    for b, nm in motif[:3]:
        note(t28 + b * Q, 'kalimba', mid(nm), 1.4, 0.4, sec='G')
    note(o2 + 0.45, 'kalimba', mid('E5'), 1.4, 0.36, sec='G')       # 动机的 E：选项都亮了以后再问一次
    CHORDS.append((tq, NF / FPS, 'D9sus4', 'G'))
    for nm in ('D3', 'A3', 'C4', 'E4', 'G4'):
        note(tq, 'piano', mid(nm), NF / FPS - tq, 0.36, sec='G')
    note(tq, 'pad', [hz(mid(x)) for x in ('D4', 'A4', 'C5', 'E5')], NF / FPS - tq, 0.42, sec='G')
    NOTES.sort(key=lambda n: n['t'])


# ======================================================================
# 渲染
# ======================================================================
INST_DB = {'kalimba': -4.0, 'marimba': -2.0, 'piano': -3.0, 'pad': -15.0, 'pad_cold': -19.0, 'pad_dark': -13.0, 'chime': -7.0,
           'rev': -8.0}


def render_note(n, rng):
    inst = n['inst']
    if inst == 'kalimba':
        return kalimba(rng, hz(n['m']), n['vel'], ring=max(1.0, n['dur']))
    if inst == 'marimba':
        return marimba(rng, hz(n['m']), n['vel'])
    if inst == 'piano':
        return piano(rng, hz(n['m']), n['dur'], n['vel'])
    if inst == 'chime':
        return chime(rng, hz(n['m']), n['vel'])
    if inst == 'pad':
        return n['vel'] * pad(rng, n['m'], n['dur'])
    if inst == 'pad_dark':        # 暗的垫音：900 Hz 以上都不要
        return n['vel'] * pad(rng, n['m'], n['dur'], att=0.5, rel=0.4, lp=900, hp=120)
    if inst == 'pad_cold':
        return n['vel'] * pad(rng, n['m'], n['dur'], att=1.2, rel=1.4, lp=1300, hp=380)
    if inst == 'rev':          # 倒放的 G 和弦：把三个拇指琴音合起来倒过来，截到 dur 那么长，末尾 8 毫秒收住（接主旋律第一拍）
        y = sum(kalimba(rng, hz(m), 1.0, ring=1.0) for m in n['m'])
        y = y[::-1][-int(n['dur'] * SR):].copy()
        y[-int(0.008 * SR):] *= np.linspace(1, 0, int(0.008 * SR))
        return n['vel'] * y
    raise ValueError(inst)


def arc_db(t):
    """整体的起伏（dB）：A 轻起，B 正常，B' 低 2 dB（变狠不变响），C 冷、轻，D 慢慢回来，E 最满（只高 1 dB），F 转暗（低 4 dB），
    W 回暖（S25），S27 起收薄、S28 前淡完，G 轻。
    都是缓坡，没有突然的高潮。"""
    pts = [(0.0, -5.0), (t_('S02'), -2.5), (t_('S04'), -2.5), (t_('S06'), 0.0), (t_('S10'), 0.0), (t_('S10') + 1.2, -2.0),
           (t_('S14'), -2.0), (t_('S14') + 1.2, -5.0),
           (t_('S18'), -5.0), (t_('S21'), -2.5), (t_('S24'), 0.0), (t_('S24') + 1.5, 1.0), (t_('S26'), 1.0),
           (t_('S26') + 0.6, -2.0), (t_('S26b'), -2.5), (t_('S26b') + 0.3, -3.0), (t_('S25') - 0.3, -4.0), (t_('S25'), -2.0),
           (t_('S27'), -3.0), (t_('S28') - 0.3, -14.0),
           (t_('S28') - 0.02, -60.0), (t_('S28'), -3.0), (NF / FPS, -3.0)]
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    return np.interp(t, x, y)


def gate_curve(t):
    """配乐也停的地方（和 sfx.gate_curve 同一套）：倒带让开、S15 全停、S19 定住；最后一秒淡到 0。"""
    g = np.ones_like(t)

    def cut(a, b, fall, back):
        m = (t >= a) & (t < a + fall)
        g[m] = np.minimum(g[m], 1 - (t[m] - a) / fall)
        g[(t >= a + fall) & (t < b)] = 0
        m = (t >= b) & (t < b + back)
        g[m] = np.minimum(g[m], (t[m] - b) / back)
    r0 = s_('S05', 'rewind', 0)
    m = (t >= r0) & (t < r0 + 0.08)
    g[m] = np.minimum(g[m], 1 - (t[m] - r0) / 0.08)
    g[(t >= r0 + 0.08) & (t < t_('S06'))] = 0               # 倒带那一段：让开（倒放的 G 和弦单独加，不受它管）
    cut(s_('S15', 'lines', 0), s_('S15', 'freeze', 1), 0.15, 0.6)
    cut(s_('S19', 'freeze', 0), s_('S19', 'freeze', 1), 0.1, 0.3)
    s29 = t_('S29')
    g *= np.clip(1 - (t - s29) / (NF / FPS - s29), 0, 1) ** 1.5
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
    rev_layer = np.zeros(N)
    for i, n in enumerate(NOTES):
        r = np.random.default_rng([SEED, i])
        y = render_note(n, r) * 10 ** (INST_DB[n['inst']] / 20)
        st = int(round(n['t'] * SR))
        if n['inst'] == 'rev':
            st = int(round(n['t'] * SR))
            m = min(len(y), N - st)
            rev_layer[st:st + m] += y[:m]
            continue
        m = min(len(y), N - st)
        if m <= 0:
            continue
        p = n['pan']
        dry[st:st + m, 0] += y[:m] * math.cos((p + 1) * math.pi / 4) * 1.414
        dry[st:st + m, 1] += y[:m] * math.sin((p + 1) * math.pi / 4) * 1.414
        send[st:st + m] += y[:m] * n['send']
    ir = sfx.make_ir(rng0, 1.3, 200, 4000, pre=0.02)
    wet = sfx.conv(send, ir)
    t = np.arange(N) / SR
    keys = [e['t'] for e in json.load(open(SFX_EVENTS)) if e['key']]
    duck, duck_db = duck_curve(t, keys)
    shape_g = 10 ** (arc_db(t) / 20) * gate_curve(t)
    music = (dry + 0.9 * wet) * (shape_g * duck)[:, None]
    # 倒放的和弦：倒带那一段配乐整体是让开的，它单独加（只受结尾淡出管，倒带时本来就不在）
    music += np.stack([rev_layer, rev_layer], 1) * (10 ** (arc_db(t) / 20) * duck)[:, None]
    music = np.stack([sfx.shape(music[:, c], 150, 2400, order=2) for c in range(2)], 1)
    music[: int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]
    return music, dict(duck_db=duck_db, shape_g=shape_g, keys=keys)


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


def key_band(mono, I, evs):
    """和 check.py 同一个口径：key 点第 N±2 帧 1–4 kHz 电平 ≥ I − 26。"""
    out = []
    for e in evs:
        if not e['key']:
            continue
        seg = mono[max(0, int((e['frame'] - 2) / FPS * SR)):int((e['frame'] + 3) / FPS * SR)]
        n = 2048
        if len(seg) < n:
            seg = np.pad(seg, (0, n - len(seg)))
        fr = np.lib.stride_tricks.sliding_window_view(seg, n)[::n // 2]
        w = np.hanning(n)
        P = (np.abs(np.fft.rfft(fr * w, axis=1)) ** 2).mean(axis=0) * 2 / (n * np.sum(w ** 2))
        f = np.fft.rfftfreq(n, 1 / SR)
        out.append(dict(t=e['t'], label=e['label'], db=round(10 * math.log10(P[(f >= 1000) & (f < 4000)].sum() + 1e-20), 1)))
    thr = I - 26
    return dict(threshold=round(thr, 1), n=len(out), failed=[r for r in out if r['db'] < thr], weakest=sorted(out, key=lambda r: r['db'])[:4])


def harmony_checks():
    """有音高的音效落下那一刻，配乐是什么和弦，音效的音在不在和弦里（不在的列出来，看是不是只差一个经过音）。"""
    pitched = []
    for k in sfx.ROUTE:
        if k['act'] in ('reveal', 'on'):
            pitched.append(((k['f'] + sfx.ROUTE_LAND[k['act']]) / FPS, sfx.ROUTE_NOTES[k['i']], '路线图 ' + TL['route']['stages'][k['i']]['label']))
        elif k['act'] == 'in':
            pitched.append((k['f'] / FPS, sfx.ROUTE_NOTES[0], '路线图 淡入'))
        elif k['act'] == 'ask':
            pitched += [(k['f'] / FPS, sfx.ROUTE_NOTES[2], 'ask 1'), (k['f'] / FPS + 0.1, sfx.ROUTE_NOTES[3], 'ask 2')]
    for i, f in enumerate(E('S25', 'lamps')):
        pitched.append((f / FPS, sfx.ROUTE_NOTES[i], f'第 {i + 1} 盏灯'))
    pitched += [(E('S28', 'opt1') / FPS, sfx.ROUTE_NOTES[2], '选项 再约一次'), (E('S28', 'opt2') / FPS, sfx.ROUTE_NOTES[3], '选项 拉黑'),
                (E('S22', 'warm') / FPS, 880.0, '照样递出（暖叮 A5）'), (E('S13', 'grow')[0] / FPS, 1046.5, '上扬叮 C6'),
                (E('S24', 'ding') / FPS, 1760.0, '翻完 A6')]
    for bid in ('S09', 'S12'):
        pitched += [((E(bid, 'giveOk') + 7) / FPS, 1568.0, f'{bid} 递 G6'), ((E(bid, 'giveOk') + 13) / FPS, 1318.5, f'{bid} 递回来 E6')]
    pitched += [((E('S18', 'give') + 6) / FPS, 1568.0, 'S18 递 G6'), ((E('S18', 'giveBack') + 6) / FPS, 1318.5, 'S18 递回来 E6'),
                ((E('S22', 'giveBack') + 7) / FPS, 1568.0, 'S22 你也递回去 G6')]
    rows = []
    for t, f0, lab in sorted(pitched):
        ch = chord_at(t)
        pc = int(round(69 + 12 * math.log2(f0 / 440))) % 12
        inch = ch is not None and pc in {PC[x] for x in CHORD[ch].split()}
        inkey = pc in {0, 2, 4, 6, 7, 9, 11}
        rows.append(dict(t=round(t, 2), label=lab, chord=ch or '（配乐没声）', in_chord=inch, in_G_major=inkey))
    return rows


def main():
    music, info = render_music()
    sx, sr = sfx.read_wav(SFX_WAV)
    assert sr == SR and len(sx) == N and len(music) == N, (sr, len(sx), len(music), N)
    with tempfile.TemporaryDirectory() as tmp:
        I_sfx, _ = lufs(sx, tmp, 'sfx.wav')
        I_mus, _ = lufs(music, tmp, 'mus.wav')
        g_mus = 10 ** ((I_sfx + MUSIC_REL - I_mus) / 20)
        music = music * g_mus
        mix, gmin = master(sx + music, tmp)
        I_pre, _ = lufs(sx + music, tmp, 'pre2.wav')
        g_all = 10 ** ((MIX_TARGET - I_pre) / 20)
        music_out = music * g_all
        sfx.write_wav(OUT_MUSIC, music_out)
        sfx.write_wav(OUT_MIX, mix, dither=True, rng=np.random.default_rng(SEED + 1))
        x, _ = sfx.read_wav(OUT_MIX)
        mo, _ = sfx.read_wav(OUT_MUSIC)
        fin = sfx.ebur(OUT_MIX)
        ln = sfx.loudnorm_json(OUT_MIX)
        mus = sfx.ebur(OUT_MUSIC)
        pk = os.path.join(tmp, 'sfx_in_mix.wav')
        sfx.write_wav(pk, np.clip(sx * g_all, -1, 1))
        sfx_in = sfx.ebur(pk)
        hp = 'highpass=f=300:poles=2,highpass=f=300:poles=2'
        phone = sfx.ebur(OUT_MIX, hp)
        evs = json.load(open(SFX_EVENTS))
        kb = key_band(x.mean(axis=1), fin['I'], evs)
        # 各段配乐的瞬时响度（400 毫秒）中位数和最大，看起伏；短时响度（3 秒）每秒最多涨多少，看有没有突然的高潮
        M = mus['M']
        sp_ = lambda name, a, b: (f'{name} {a:.2f}–{b:.2f}', a, b)
        secs = [sp_('A 好奇', 0, t_('S04')), sp_('？ 没解决', t_('S04'), t_('S05')), sp_('B 主旋律', t_('S06'), t_('S10')),
                sp_("B' 变狠", t_('S10'), t_('S14')), sp_('C 世界冷了', t_('S14'), t_('S18')), sp_('D 回暖', t_('S18'), t_('S24')),
                sp_('其中 S21 一来一回', t_('S21'), t_('S22')), sp_('E 最暖最满', t_('S24'), t_('S26')),
                sp_('U 好欺负的人多了（安稳里透出不安）', t_('S26'), t_('S26b')),
                sp_('F 狠人又回来了（转暗）', t_('S26b'), t_('S25')), sp_('W 四个你＋带走句（回暖）', t_('S25'), t_('S27')),
                sp_('S27–S27h 收薄（给钟表让地方）', t_('S27'), t_('S28')),
                sp_('G 结尾', t_('S28'), NF / FPS)]
        sec_rows = {}
        for name, a, b in secs:
            m = (M[:, 0] >= a + 0.4) & (M[:, 0] <= b)
            v = M[m, 1]
            v = v[v > -70]
            sec_rows[name] = dict(M_median=round(float(np.median(v)), 1) if len(v) else None, M_max=round(float(v.max()), 1) if len(v) else None)
        # 短时响度：3 秒窗的能量（自己算，K 加权省掉，只看起伏），每 0.1 秒一点，1 秒内最多涨多少 dB
        mono_m = mo.mean(axis=1)
        c = np.concatenate([[0.0], np.cumsum(mono_m ** 2)])
        w3 = int(3 * SR)
        idx = np.arange(0, len(mono_m) - w3, SR // 10)
        sdb = 10 * np.log10((c[idx + w3] - c[idx]) / w3 + 1e-12)
        # 突然的高潮 = 这 3 秒比前 10 秒里最响的 3 秒还高多少（停顿以后重新进来不算，因为前 10 秒里有更响的）
        over = np.array([sdb[i] - sdb[max(0, i - 100):i].max() for i in range(30, len(sdb))])
        jump = float(over.max())
        jump_at = float((np.argmax(over) + 30) / 10 + 1.5)
        # 让开：每个 key 点那一刻配乐压了多少
        tt = np.arange(N) / SR
        dk = [float(info['duck_db'][min(N - 1, int(k * SR))]) for k in info['keys']]
        # 配乐和音效同一时刻比（手机频段 300 Hz 以上，400 毫秒瞬时响度）
        mus_ph = sfx.ebur(OUT_MUSIC, hp)['M']
        sfx_ph = sfx.ebur(pk, hp)['M']
        margins = []
        for e2 in evs:                  # 每个 key 点：起音后 0.05–0.45 秒（400 毫秒窗的末尾落在这里），音效最响减配乐最响
            if not e2['key']:
                continue
            ms = (sfx_ph[:, 0] >= e2['t'] + 0.05) & (sfx_ph[:, 0] <= e2['t'] + 0.45)
            mm = (mus_ph[:, 0] >= e2['t'] + 0.05) & (mus_ph[:, 0] <= e2['t'] + 0.45)
            margins.append((round(float(sfx_ph[ms, 1].max() - mus_ph[mm, 1].max()), 1), e2['t'], e2['label']))
        margins.sort()
        summary = dict(
            mix=dict(file=OUT_MIX, samples=len(x), frames=len(x) / SPF, I=fin['I'], LRA=fin['LRA'], TP=fin['TP'],
                     loudnorm_I=float(ln['input_i']), loudnorm_TP=float(ln['input_tp']), limiter_min_db=round(20 * math.log10(gmin), 2),
                     phone_I=phone['I']),
            music=dict(file=OUT_MUSIC, samples=len(mo), I=mus['I'], TP=mus['TP'], rel_to_sfx_LU=round(mus['I'] - sfx_in['I'], 1),
                       sfx_in_mix_I=sfx_in['I'], bands=band_share(mono_m, [(20, 200), (200, 2000), (1000, 4000), (2000, 20000)]),
                       sections=sec_rows, max_rise_over_prev10s_db=round(jump, 1), max_rise_at_s=round(jump_at, 1),
                       notes=len(NOTES), music_gain_db=round(20 * math.log10(g_mus), 1), total_gain_db=round(20 * math.log10(g_all), 1)),
            duck=dict(keys=len(dk), depth_db=[round(min(dk), 1), round(max(dk), 1)]),
            key_phone_margin=dict(median=float(np.median([m_[0] for m_ in margins])), lowest=margins[:4]),
            key_band=kb, harmony=harmony_checks(),
            chords=[(round(a, 2), round(z, 2), ch, sec) for a, z, ch, sec in sorted(CHORDS)],
        )
    json.dump(summary, open(OUT_CHECK, 'w'), ensure_ascii=False, indent=1)
    m = summary['mix']
    print(f"写出 {OUT_MIX}：{m['samples']} 个采样 = {m['frames']:.0f} 帧；I {m['I']} LUFS（loudnorm 复核 {m['loudnorm_I']}），"
          f"真峰值 {m['TP']} dBTP（复核 {m['loudnorm_TP']}），限幅最深 {m['limiter_min_db']} dB，300 Hz 以上 {m['phone_I']} LUFS")
    mu = summary['music']
    print(f"写出 {OUT_MUSIC}：{mu['notes']} 个音；整条 {mu['I']} LUFS，比音效低 {-mu['rel_to_sfx_LU']} LU；频段 {mu['bands']}；"
          f"最响的 3 秒比前 10 秒最响处高 {mu['max_rise_over_prev10s_db']} dB（{mu['max_rise_at_s']} 秒）")
    for k, v in mu['sections'].items():
        print('   ', k, v)
    print('让开', summary['duck'], '；每个 key 点音效比配乐高（手机频段 LU）', summary['key_phone_margin'])
    kb = summary['key_band']
    print(f"key 点 1–4 kHz（check.py 口径，门槛 {kb['threshold']} dBFS）：{kb['n']} 个，没过 {len(kb['failed'])} 个，最弱 {kb['weakest']}")
    bad = [r for r in summary['harmony'] if not r['in_chord']]
    print(f"有音高的音效 {len(summary['harmony'])} 个，不在当时和弦里的 {len(bad)} 个：", [(r['t'], r['label'], r['chord'], r['in_G_major']) for r in bad])


if __name__ == '__main__':
    main()
