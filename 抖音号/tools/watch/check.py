"""出片自查：每次渲完样片、成片都跑一遍。能量出来的规矩报 PASS / FAIL / WARN，不靠人记。

用法（在 /Users/decheng.huang/Documents/dy 下）：
  .venv/bin/python -I tools/watch/check.py 视频.mp4 时间表.json 输出目录 [--lufs -14] [--lufs-tol 1] [--peak -1] [--preview] [--sfx 事件表.json]
说明见同目录 check_用法.md。

查六样：
  1 规格：画幅、帧率、时长（和时间表差 ≤ 2 帧）；第 0 帧不是纯色、不闪。
  2 静止：每 0.1 秒一格帧差，算法照 beats.py（10 帧/秒、96 宽灰度、帧差 < 0.15 算这一格不动）。
     整幅静止 > 1.5 秒必须落在【停】拍里；列出 ≥ 0.5 秒的静止；帧差 > 中位数 4 倍算突变，标在不在拍的边界上。
  3 字幕：平均每秒字数 ≤ 4、无字拍 ≥ 三成、每拍按每秒 6.5 字读得完；字号（字幕 ≥ 54 px，第 0 秒的字 ≥ 50 px，按 1080 折算）。
  4 声音：有没有音轨；整条响度（ffmpeg ebur128）和真峰值；每拍 1–4 kHz 能量；时间表标了音效的地方，手机外放频段有没有明显能量。
     传了 --sfx 事件表：key 点前后 ±2 帧 1–4 kHz 没有明显能量就 FAIL；和画面突变（逐帧、8×6 块取最大）差超过 2 帧就 WARN。
  5 出图：12 格对照图、每拍第一帧拼图、帧差曲线、响度曲线。
  6 报告.md：先 FAIL，再 WARN，再 PASS，后面附明细表。
有 FAIL 时退出码是 1。只用 .venv 里的 numpy、Pillow、imageio-ffmpeg。
"""
import argparse
import datetime
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:  # 和 beats.py 用同一个 ffmpeg
    FF = '/Users/decheng.huang/Documents/dy/.venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'

# —— 规矩（出处：剪辑认知、制作工作流、现状.md“锁节奏的验收单”）——
DUR_TOL_FRAMES = 2       # 时长和时间表最多差 2 帧
STILL_DIFF = 0.15        # beats.py：帧差 < 0.15 算这一格不动
STILL_MAX = 1.5          # 验收单④：整幅静止不超过 1.5 秒（【停】除外）
STILL_LIST = 0.5         # 列出 0.5 秒以上的静止
STOP_SLACK = 0.15        # 静止段伸出【停】拍不超过这么多秒，仍算落在【停】里（帧差每格 0.1 秒，留一格余量）
JUMP_RATIO = 4.0         # check.sh：帧差 > 中位数 4 倍算突变
JUMP_FLOOR = 2.0         # 突变线的下限：片子大半静止时中位数接近 0，4 倍还是 0，不设下限会漏掉硬切
BOUNDARY_TOL = 0.15      # 突变离拍的边界不超过这么多秒，算落在边界上
MAX_CPS = 4.0            # 验收单②：字幕平均每秒 ≤ 4 字
MIN_NO_TEXT = 0.30       # 验收单③：无字拍 ≥ 三成
READ_CPS = 6.5           # 验收单⑤：每秒读 6.5 字
SUB_MIN_PX = 54          # 剪辑认知第 18 条：字幕 ≥ 54 px（1080 的画面）
FIRST_MIN_PX = 50        # 剪辑认知第 18 条：第 0 秒要读的字 ≥ 50 px
FLASH_DIFF = 6.0         # 第 0 帧和第 1 帧平均差 > 6，且比第 1→2 帧大 3 倍以上，算闪
PURE_STD = 2.0           # 第 0 帧三个通道的标准差都 < 2，算纯色
BAND = (1000.0, 4000.0)  # 剪辑认知第 30 条：手机外放听得见的频段
SFX_WIN = (-0.05, 0.30)  # 音效时间点前 0.05 秒到后 0.3 秒算这一下的声音
SFX_REL_OK = 26.0        # 1–4 kHz 电平 ≥ 整条响度 − 26 dB 算“明显”（−14 LUFS 时是 −40 dBFS）
SFX_REL_WEAK = 36.0      # 再低 10 dB 以内算“弱”（WARN），更低算“几乎没有”（FAIL）
# —— 传了 --sfx 事件表时 ——
EV_WIN = 2               # key 点前后 ±2 帧算这一下的声音；1–4 kHz 电平 ≥ 整条响度 − SFX_REL_OK 算明显，否则 FAIL
EV_ALIGN = 2             # 和画面突变差超过 2 帧就 WARN
EV_SEARCH = 15           # 在事件前后 15 帧（0.5 秒）里找画面突变
ONSET_RISE = 4.0         # 画面突变的起点：这一帧的局部变化比前两帧都高出 4 以上，而且翻了一倍
SFX_NAMES = re.compile(r'^(sfx|sound|whoosh|swoosh|swish|ding|chime|bell|pop|click|tick|thud|thump|boom|bang|snap|clap|beep|knock|'
                       r'嗖|叮|啪|咚|噗|啵|唰|嗒|呜)', re.I)

FONT_FILES = ['/System/Library/Fonts/Hiragino Sans GB.ttc', '/System/Library/Fonts/STHeiti Medium.ttc',
              '/System/Library/Fonts/Supplemental/Arial Unicode.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf']
# 图的颜色（dataviz 参考色板）
C_BG, C_INK, C_INK2, C_GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3de'
C_STOP = '#ecebe5'
C_BLUE, C_ORANGE, C_RED, C_YELLOW, C_AQUA = '#2a78d6', '#eb6834', '#e34948', '#eda100', '#1baf7a'


def font(size):
    for f in FONT_FILES:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                continue
    return ImageFont.load_default()


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout, r.stderr.decode('utf-8', 'replace')


# ———————————————————————————— 读视频 ————————————————————————————

def probe(path):
    _, err = sh([FF, '-hide_banner', '-i', path])
    info = dict(w=None, h=None, fps=None, dur=None, audio=None, frames=None)
    m = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', err)
    if m:
        info['dur'] = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    for line in err.splitlines():
        if 'Video:' in line and info['w'] is None:
            m = re.search(r',\s*(\d{2,5})x(\d{2,5})[\s,\[]', line + ' ')
            if m:
                info['w'], info['h'] = int(m[1]), int(m[2])
            m = re.search(r'(\d+(?:\.\d+)?) fps', line)
            if m:
                info['fps'] = float(m[1])
        if 'Audio:' in line and info['audio'] is None:
            info['audio'] = line.split('Audio:', 1)[1].strip()
    _, err = sh([FF, '-hide_banner', '-i', path, '-map', '0:v:0', '-c', 'copy', '-f', 'null', '-'])
    fr = re.findall(r'frame=\s*(\d+)', err)
    if fr:
        info['frames'] = int(fr[-1])
    return info


def motion(path, W, H):
    """和 beats.py 同一个算法：10 帧/秒、96 宽灰度、相邻两格平均绝对差。d[i] 是第 i 格到第 i+1 格，时间记为 (i+1)/10 秒。"""
    w = 96
    h = max(2, int(round(w * H / W / 2)) * 2)
    raw, _ = sh([FF, '-v', 'error', '-i', path, '-vf', f'fps=10,scale={w}:{h},format=gray', '-f', 'rawvideo', '-'])
    n = len(raw) // (w * h)
    fr = np.frombuffer(raw[:n * w * h], np.uint8).reshape(n, h, w).astype(np.float32)
    return np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))


def grab_frames(path, idxs, W, H, tw=640):
    """按帧号取帧（缩到 tw 宽），回 {帧号: RGB 数组}。"""
    idxs = sorted(set(int(i) for i in idxs if i >= 0))
    th = max(2, int(round(tw * H / W / 2)) * 2)
    expr = '+'.join(f'eq(n\\,{i})' for i in idxs)
    raw, err = sh([FF, '-v', 'error', '-i', path, '-vf', f'select={expr},scale={tw}:{th}', '-fps_mode', 'vfr',
                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    size = tw * th * 3
    m = len(raw) // size
    arr = np.frombuffer(raw[:m * size], np.uint8).reshape(m, th, tw, 3)
    return {i: arr[k] for k, i in enumerate(idxs[:m])}


def loudness(path):
    _, err = sh([FF, '-hide_banner', '-nostats', '-i', path, '-map', '0:a:0', '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    ts, M, S = [], [], []
    num = r'(-?\d+(?:\.\d+)?|-?inf|nan)'
    for m in re.finditer(r't:\s*(\d+(?:\.\d+)?)\s+TARGET:.*?M:\s*' + num + r'\s+S:\s*' + num, err):
        ts.append(float(m[1]))
        M.append(float(m[2]))
        S.append(float(m[3]))
    summ = err.split('Summary:')[-1] if 'Summary:' in err else ''
    g = lambda pat: (float(re.search(pat, summ)[1]) if re.search(pat, summ) else None)
    return dict(I=g(r'I:\s*' + num + r' LUFS'), LRA=g(r'LRA:\s*' + num + r' LU'), TP=g(r'Peak:\s*' + num + r' dBFS'),
                t=np.array(ts), M=np.array(M), S=np.array(S))


def pcm(path, sr=48000):
    raw, _ = sh([FF, '-v', 'error', '-i', path, '-map', '0:a:0', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'])
    return np.frombuffer(raw[:len(raw) // 4 * 4], np.float32).astype(np.float64)


def local_change(path, W, H):
    """逐帧的局部变化：缩成 96 宽灰度，画面分成 8×6 块，取这一帧和上一帧差得最多那一块的平均差。
    整幅帧差对小东西不灵（光点滑落、落地一闪只有 1 左右），按块取最大才看得出。m[k] 是第 k−1 帧到第 k 帧。"""
    w = 96
    h = max(6, int(round(w * H / W / 6)) * 6)
    raw, _ = sh([FF, '-v', 'error', '-i', path, '-vf', f'scale={w}:{h},format=gray', '-fps_mode', 'passthrough',
                 '-f', 'rawvideo', '-'])
    n = len(raw) // (w * h)
    fr = np.frombuffer(raw[:n * w * h], np.uint8).reshape(n, h, w).astype(np.float32)
    m = np.zeros(n)
    if n > 1:
        dd = np.abs(np.diff(fr, axis=0))
        m[1:] = dd.reshape(n - 1, 6, h // 6, 8, w // 8).mean(axis=(2, 4)).reshape(n - 1, -1).max(axis=1)
    return m


def onsets(m):
    """画面突变的起点：比前两帧都高出 ONSET_RISE 以上，而且是它们的两倍以上。回 {帧号: 高出多少}。"""
    out = {}
    for k in range(2, len(m)):
        prev = max(m[k - 1], m[k - 2])
        if m[k] - prev >= ONSET_RISE and m[k] >= 2 * max(prev, 0.5):
            out[k] = float(m[k] - prev)
    return out


def load_events(path, fps, beats, nf):
    """读 --sfx 事件表：[{"t": 秒, "frame": 帧号, "name": 名字, "beat": 拍号, "key": true/false}]。
    frame 和 t 有一个就行，都有时以 frame 为准。回 (事件列表, 问题列表)。"""
    data = json.load(open(path, encoding='utf-8'))
    if isinstance(data, dict):
        data = data.get('events', [])
    ids = {b['id']: b for b in beats}
    evs, probs = [], []
    for k, e in enumerate(data):
        name = str(e.get('name', f'#{k + 1}'))
        fr, t = e.get('frame'), e.get('t')
        if fr is None and t is None:
            probs.append(f'第 {k + 1} 条（{name}）没有 t 也没有 frame')
            continue
        if fr is None:
            fr = int(round(float(t) * fps))
        fr = int(fr)
        if t is not None and abs(float(t) * fps - fr) > 1:
            probs.append(f'{name}：t = {t} 秒是第 {float(t) * fps:.1f} 帧，frame 写的是 {fr}（按 frame 算）')
        if not 0 <= fr < nf:
            probs.append(f'{name}：第 {fr} 帧不在片子里（0–{nf - 1}）')
        actual = next((b['id'] for b in beats if b['f0'] <= fr < b['f1']), None)
        bid = e.get('beat')
        if bid is not None and bid not in ids:
            probs.append(f'{name}：拍号 {bid} 不在时间表里')
        elif bid is not None and actual is not None and bid != actual:
            probs.append(f'{name}：第 {fr} 帧在 {actual} 里，事件表写的是 {bid}')
        evs.append(dict(name=name, frame=fr, t=fr / fps, beat=bid or actual or '?', key=bool(e.get('key'))))
    return sorted(evs, key=lambda e: e['frame']), probs


def band_levels(x, sr):
    """回 (1–4 kHz 电平 dBFS, 全频电平 dBFS, 1–4 kHz 占比, 250 Hz 以下占比)。电平是均方根，正弦满幅约 −3 dBFS。"""
    n = 2048
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::n // 2]
    w = np.hanning(n)
    P = (np.abs(np.fft.rfft(fr * w, axis=1)) ** 2).mean(axis=0) * 2 / (n * np.sum(w ** 2))
    f = np.fft.rfftfreq(n, 1 / sr)
    band, full, low = P[(f >= BAND[0]) & (f < BAND[1])].sum(), P.sum(), P[f < 250].sum()
    db = lambda v: 10 * math.log10(v + 1e-20)
    return db(band), db(full), band / (full + 1e-20), low / (full + 1e-20)


# ———————————————————————————— 读时间表 ————————————————————————————

def seg_text(line):
    if isinstance(line, str):
        return line
    return ''.join(s if isinstance(s, str) else str(s[0]) for s in line)


def doc_chars(text):
    """口径：汉字一个算 1；一串数字或字母算 1（“1000”“5%”“99%”各算 1）；标点、空格、白点不算。0 秒大题另算进去。"""
    text = text.replace('●', '')
    n_tok = len(re.findall(r'[0-9A-Za-z]+%?', text))
    rest = re.sub(r'[0-9A-Za-z]+%?', '', text)
    return len(re.findall(r'[\u4e00-\u9fff]', rest)) + n_tok


def as_sec(v, fps):
    """时间表里的时刻：整数当帧号，带小数当秒（timeline.py 写出来的 question.big、字幕段出现时刻都是帧号）。"""
    return v / fps if isinstance(v, int) else float(v)


def load_beats(tl, fps):
    out = []
    for b in tl.get('beats', []):
        f0 = b.get('f0', round(b.get('t0', 0) * fps))
        f1 = b.get('f1', round(b.get('t1', 0) * fps))
        out.append(dict(id=b.get('id', f'#{len(out) + 1}'), f0=f0, f1=f1, t0=f0 / fps, t1=f1 / fps,
                        lines=b.get('lines') or [], stop=bool(b.get('stop')), raw=b))
    return out


def pieces(lines, t0, fps):
    """一句字幕拆成 (出现秒, 字数)：普通段在这一句开头出现；[字, 颜色, 帧] 那种段到那一帧才出现。"""
    out = []
    for line in lines:
        segs = [line] if isinstance(line, str) else line
        for s in segs:
            if isinstance(s, str):
                out.append((t0, doc_chars(s)))
            elif len(s) > 2 and isinstance(s[2], (int, float)):
                out.append((max(t0, as_sec(s[2], fps)), doc_chars(str(s[0]))))
            else:
                out.append((t0, doc_chars(str(s[0]))))
    return [p for p in out if p[1] > 0]


def subtitle_runs(tl, beats, fps):
    """同一句字幕连着挂几拍，算一句（字只算一次，读字时间按整段算）。0 秒大题也算一句。"""
    runs = []
    q = tl.get('question') or {}
    if q.get('text') and q.get('big'):
        a, b = as_sec(q['big'][0], fps), as_sec(q['big'][1], fps)
        runs.append(dict(t0=a, t1=b, text=q['text'] + '（大题）', ids=['大题'], pcs=[(a, doc_chars(q['text']))], title=True))
    prev = None
    for b in beats:
        L = b['lines']
        if L and L == prev and runs and not runs[-1].get('title'):
            runs[-1]['t1'] = b['t1']
            runs[-1]['ids'].append(b['id'])
        elif L:
            runs.append(dict(t0=b['t0'], t1=b['t1'], text='／'.join(seg_text(x) for x in L), ids=[b['id']],
                             pcs=pieces(L, b['t0'], fps), title=False))
        prev = L
    for r in runs:
        r['chars'] = sum(n for _, n in r['pcs'])
        fin = r['t0']
        for t, n in sorted(r['pcs']):
            fin = max(fin, t) + n / READ_CPS
        r['need'] = r['chars'] / READ_CPS
        r['have'] = r['t1'] - r['t0']
        r['finish'] = fin
        r['ok'] = fin <= r['t1'] + 1e-6
    return runs


def collect_sfx(tl, beats, fps):
    """时间表里标了音效的地方 → [(拍号, 名字, 秒)]。认三种写法：
    拍里的 sfx / sound / 音效 字段（{名字: 秒或[秒...]}，或 [[名字, 秒], ...]，或 [{"name":, "t": 秒 或 "f": 帧}]）；
    拍内事件 ev_s / ev 里名字像音效的（whoosh、ding、嗖、叮……）；时间表顶层的 sfx 列表。"""
    out = []

    def add(bid, name, v, unit_frames=False):
        vs = v if isinstance(v, list) else [v]
        for x in vs:
            if isinstance(x, (int, float)):
                out.append((bid, str(name), x / fps if unit_frames else float(x)))

    def parse(bid, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                add(bid, k, v)
        elif isinstance(obj, list):
            for it in obj:
                if isinstance(it, dict):
                    if 'f' in it:
                        add(bid, it.get('name', '音效'), it['f'], True)
                    else:
                        add(bid, it.get('name', '音效'), it.get('t'))
                elif isinstance(it, (list, tuple)) and len(it) >= 2:
                    add(bid, it[0], it[1])
    for b in beats:
        raw = b['raw']
        for key in ('sfx', 'sound', 'sounds', '音效'):
            if key in raw:
                parse(b['id'], raw[key])
        if 'ev_s' in raw:
            for k, v in raw['ev_s'].items():
                if SFX_NAMES.match(k):
                    add(b['id'], k, v)
        elif 'ev' in raw:
            for k, v in raw['ev'].items():
                if SFX_NAMES.match(k):
                    add(b['id'], k, v, True)
    top = tl.get('sfx')
    if top:
        parse('', top)
    fixed = []
    for bid, name, t in out:
        if not bid:
            bid = next((b['id'] for b in beats if b['t0'] <= t < b['t1']), '?')
        fixed.append((bid, name, t))
    return sorted(set(fixed), key=lambda x: x[2])


def text_sizes(tl):
    """回 (字幕字号列表 [(名字, px)], 其他字号列表, 第 0 秒的字号列表, 版面高, 版面宽)。"""
    lay = tl.get('layout') or {}
    H = lay.get('H') or tl.get('height')
    W = lay.get('W') or tl.get('width')
    subs, others, first = [], [], []
    sub = lay.get('sub') or {}
    for k in ('size', 'numSize'):
        if isinstance(sub.get(k), (int, float)):
            subs.append((f'layout.sub.{k}', sub[k]))
    for b in tl.get('beats', []):
        st = b.get('sub') or {}
        for k in ('size', 'num'):
            if isinstance(st.get(k), (int, float)):
                subs.append((f'{b.get("id")}.sub.{k}', st[k]))
    pat = re.compile(r'(size|Size|^num$|Num$|^word$|Word$|^text$|^title|^tag)')

    def walk(d, pre):
        for k, v in d.items():
            if pre == 'sub':
                continue
            name = f'{pre}.{k}' if pre else k
            if isinstance(v, dict):
                walk(v, name)
            elif isinstance(v, (int, float)) and not isinstance(v, bool) and pat.search(k):
                others.append((name, v))
    walk(lay, '')
    q = tl.get('question') or {}
    if q.get('big') and q['big'][0] == 0 and isinstance(lay.get('titleBig'), (int, float)):
        first.append(('layout.titleBig（0 秒大题）', lay['titleBig']))
    beats = tl.get('beats', [])
    if beats and beats[0].get('lines') and subs:
        first.append(('第一拍字幕', min(v for _, v in subs)))
    return subs, others, first, H, W


# ———————————————————————————— 画图 ————————————————————————————

def chart(path, title, tmax, panels, beats, foot=''):
    """panels: [{ylabel, ymin, ymax, yticks, series:[(xs, ys, 颜色, 粗细)], hlines:[(y, 颜色, 字)],
               spans:[(x0, x1, 颜色)], marks:[(x, 颜色)], bars:[(x0, x1, y, 颜色)]}]"""
    Wd, L, R, T, PH, GAP = 2400, 170, 40, 70, 380, 56
    Hd = T + len(panels) * (PH + GAP) + 50
    im = Image.new('RGB', (Wd, Hd), C_BG)
    dr = ImageDraw.Draw(im)
    f14, f18, f24 = font(14), font(18), font(26)
    dr.text((L, 18), title, fill=C_INK, font=f24)
    if foot:
        dr.text((L, Hd - 34), foot, fill=C_INK2, font=f18)
    X = lambda t: L + (Wd - L - R) * t / max(tmax, 1e-9)
    for k, p in enumerate(panels):
        y0 = T + k * (PH + GAP) + 24
        y1 = y0 + PH
        Y = lambda v, p=p, y0=y0, y1=y1: y1 - (y1 - y0) * (min(max(v, p['ymin']), p['ymax']) - p['ymin']) / (p['ymax'] - p['ymin'])
        for b in beats:                      # 【停】拍打底
            if b['stop']:
                dr.rectangle([X(b['t0']), y0, X(b['t1']), y1], fill=C_STOP)
        for x0, x1, c in p.get('spans', []):
            dr.rectangle([X(x0), y0, max(X(x1), X(x0) + 2), y1], fill=c)
        for v in p.get('yticks', []):
            dr.line([L, Y(v), Wd - R, Y(v)], fill=C_GRID, width=1)
            lab = f'{v:g}'
            dr.text((L - 10 - dr.textlength(lab, font=f14), Y(v) - 8), lab, fill=C_INK2, font=f14)
        for b in beats:                      # 拍的边界和拍号
            dr.line([X(b['t0']), y0, X(b['t0']), y1], fill='#c9c8c1', width=1)
            dr.text((X(b['t0']) + 3, y0 - 20), b['id'], fill=C_INK2, font=f14)
        for x0, x1, v, c in p.get('bars', []):
            dr.rectangle([X(x0) + 2, Y(v), X(x1) - 2, Y(p['ymin'])], fill=c)
        for v, c, lab in p.get('hlines', []):
            dr.line([L, Y(v), Wd - R, Y(v)], fill=c, width=2)
            dr.text((Wd - R - dr.textlength(lab, font=f14) - 4, Y(v) - 20), lab, fill=c, font=f14)
        for xs, ys, c, wdt in p.get('series', []):
            pts = [(X(x), Y(y)) for x, y in zip(xs, ys) if np.isfinite(y)]
            if len(pts) > 1:
                dr.line(pts, fill=c, width=wdt)
        for x, c in p.get('marks', []):
            dr.polygon([(X(x) - 7, y0 + 2), (X(x) + 7, y0 + 2), (X(x), y0 + 14)], fill=c)
        dr.rectangle([L, y0, Wd - R, y1], outline='#b5b4ad', width=1)
        dr.text((12, y0 + PH / 2 - 10), p['ylabel'], fill=C_INK, font=f18)
        for s in range(0, int(tmax) + 1, 5):
            dr.line([X(s), y1, X(s), y1 + 6], fill=C_INK2)
            dr.text((X(s) - 8, y1 + 8), f'{s}s', fill=C_INK2, font=f14)
    im.save(path)


def placeholder(path, text):
    im = Image.new('RGB', (1200, 300), C_BG)
    ImageDraw.Draw(im).text((40, 120), text, fill=C_INK, font=font(32))
    im.save(path)


def contact(path, items, cols, tw, label_h, f_label):
    """items: [(RGB 数组, [第一行字, 第二行字...])]"""
    imgs = [Image.fromarray(a).resize((tw, int(a.shape[0] * tw / a.shape[1]))) for a, _ in items]
    th = imgs[0].size[1]
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (tw + 8) + 8, rows * (th + label_h + 8) + 8), 'white')
    dr = ImageDraw.Draw(sheet)
    for k, (im, (_, labs)) in enumerate(zip(imgs, items)):
        x, y = 8 + (k % cols) * (tw + 8), 8 + (k // cols) * (th + label_h + 8)
        for j, lab in enumerate(labs):
            dr.text((x + 2, y + 2 + j * (f_label.size + 4)), lab, fill='black', font=f_label)
        sheet.paste(im, (x, y + label_h))
    sheet.save(path)


# ———————————————————————————— 主流程 ————————————————————————————

def fmt_t(t):
    return f'{t:.1f}'


def main():
    ap = argparse.ArgumentParser(description='出片自查（见 check_用法.md）')
    ap.add_argument('video')
    ap.add_argument('timeline')
    ap.add_argument('out')
    ap.add_argument('--lufs', type=float, default=-14.0, help='整条响度目标，默认 −14；要留配乐空间的片子传 −19')
    ap.add_argument('--lufs-tol', type=float, default=1.0, help='响度在目标 ± 这么多 LU 内算 PASS，再多 1 LU 内 WARN，默认 1')
    ap.add_argument('--peak', type=float, default=-1.0, help='真峰值上限 dBTP，默认 −1')
    ap.add_argument('--preview', action='store_true', help='预演 / 灰框：画幅按比例缩小、没有音轨只报 WARN，不报 FAIL')
    ap.add_argument('--sfx', help='音效事件表 json：[{"t", "frame", "name", "beat", "key"}]。传了就按它逐个查 key 点；不传就从时间表里找音效')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tl = json.load(open(a.timeline, encoding='utf-8'))
    res = []                       # (等级, 项, 说明)

    def add(level, item, msg):
        res.append((level, item, msg))

    # —— 1 规格 ——
    v = probe(a.video)
    if not v['w'] or not v['fps']:
        print('读不出视频流：', a.video)
        sys.exit(2)
    fps_tl = tl.get('fps') or v['fps']
    beats = load_beats(tl, fps_tl)
    nf_tl = tl.get('frames') or (beats[-1]['f1'] if beats else None)
    dur_tl = nf_tl / fps_tl if nf_tl else tl.get('dur')
    _, _, _, LH, LW = text_sizes(tl)
    if LW and LH:
        if (v['w'], v['h']) == (LW, LH):
            add('PASS', '画幅', f'{v["w"]}×{v["h"]}，和时间表一致')
        else:
            same = abs(v['w'] / v['h'] - LW / LH) < 0.01
            note = f'比例相同，是 {v["w"] / LW:g} 倍缩小渲的；成片要 {LW}×{LH}' if same else '比例也不同'
            add('WARN' if (a.preview and same) else 'FAIL', '画幅', f'{v["w"]}×{v["h"]}，时间表是 {LW}×{LH}。{note}')
    else:
        add('WARN', '画幅', f'{v["w"]}×{v["h"]}；时间表里没有画幅（layout.W/H），查不了')
    if abs(v['fps'] - fps_tl) < 0.01:
        add('PASS', '帧率', f'{v["fps"]:g} fps，和时间表一致')
    else:
        add('FAIL', '帧率', f'{v["fps"]:g} fps，时间表是 {fps_tl:g} fps')
    nf = v['frames'] or int(round((v['dur'] or 0) * v['fps']))
    if nf_tl:
        dn = nf - nf_tl
        note = ''
        if tl.get('dur') and abs(tl['dur'] * fps_tl - nf_tl) >= 0.5:
            note = f'（时间表 dur 字段写 {tl["dur"]} 秒，按帧数是 {nf_tl / fps_tl:.2f} 秒）'
        add('PASS' if abs(dn) <= DUR_TOL_FRAMES else 'FAIL', '时长',
            f'{nf} 帧 = {nf / v["fps"]:.2f} 秒，时间表 {nf_tl} 帧，差 {dn:+d} 帧（上限 ±{DUR_TOL_FRAMES}）{note}')
    else:
        add('WARN', '时长', f'{nf} 帧 = {nf / v["fps"]:.2f} 秒；时间表里没有总帧数，查不了')
    tmax = nf / v['fps']

    # 取帧：第 0、1、2 帧、第 1 秒、每拍第一帧、12 格
    i1s = int(round(v['fps']))
    grid_idx = [int(round(x)) for x in np.linspace(0, nf - 1, 12)]
    beat_idx = [min(b['f0'], nf - 1) for b in beats]
    frames = grab_frames(a.video, [0, 1, 2, i1s] + grid_idx + beat_idx, v['w'], v['h'])
    f0 = frames.get(0)
    if f0 is not None and 1 in frames and 2 in frames:
        x0, x1, x2 = (frames[i].astype(np.float32) for i in (0, 1, 2))
        stds = x0.reshape(-1, 3).std(axis=0)
        if stds.max() < PURE_STD:
            add('FAIL', '第 0 帧', f'是纯色（平均色 {tuple(int(c) for c in x0.reshape(-1, 3).mean(axis=0))}，三通道标准差 ≤ {stds.max():.1f}）')
        else:
            add('PASS', '第 0 帧不是纯色', f'三通道标准差 {stds.min():.0f}–{stds.max():.0f}')
        d01, d12 = np.abs(x1 - x0).mean(), np.abs(x2 - x1).mean()
        if d01 > FLASH_DIFF and d01 > 3 * max(d12, 1.0):
            add('FAIL', '第 0 帧闪', f'第 0→1 帧平均差 {d01:.1f}，第 1→2 帧 {d12:.1f}：第 0 帧和后面不是一个画面')
        else:
            add('PASS', '第 0 帧不闪', f'第 0→1 帧平均差 {d01:.2f}，第 1→2 帧 {d12:.2f}（闪的判法：> {FLASH_DIFF:g} 且是后者 3 倍以上）')
        if i1s in frames:
            cd = np.abs(x0.reshape(-1, 3).mean(axis=0) - frames[i1s].astype(np.float32).reshape(-1, 3).mean(axis=0)).max()
            if cd > FLASH_DIFF:
                add('WARN', '第 0 帧和第 1 秒的颜色', f'平均色差 {cd:.1f}（check.sh 口径 > 6 判闪色；1 秒内有切换时属正常，对着 12 格图认）')
            else:
                add('PASS', '第 0 帧和第 1 秒的颜色', f'平均色差 {cd:.1f}（check.sh 口径，≤ 6）')
    else:
        add('FAIL', '第 0 帧', '取不出第 0–2 帧')

    # —— 2 静止和突变 ——
    d = motion(a.video, v['w'], v['h'])
    with open(os.path.join(a.out, 'diff.txt'), 'w') as fh:
        for i, x in enumerate(d):
            fh.write(f'{(i + 1) / 10:.1f}\t{x:.2f}\n')
    stops = [(b['t0'], b['t1']) for b in beats if b['stop']]

    def in_stop(s, e):
        return sum(max(0.0, min(e, b) - max(s, a_)) for a_, b in stops)

    def beats_over(s, e):
        return [b['id'] for b in beats if b['t0'] < e - 1e-6 and b['t1'] > s + 1e-6]
    still = d < STILL_DIFF
    runs, i = [], 0
    while i < len(d):
        if still[i]:
            j = i
            while j + 1 < len(d) and still[j + 1]:
                j += 1
            s, e = i / 10, (j + 1) / 10
            runs.append(dict(s=s, e=e, dur=round(e - s, 1), stop=round(in_stop(s, e), 2), ids=beats_over(s, e)))
            i = j + 1
        else:
            i += 1
    for r in runs:
        r['out'] = round(r['dur'] - r['stop'], 2)
        r['where'] = '全在【停】里' if r['out'] <= STOP_SLACK else (f'部分在【停】里，停外 {r["out"]:.1f} 秒' if r['stop'] > 0 else '不在【停】里')
    longest = max([r['dur'] for r in runs], default=0.0)
    share, share15 = float(still.mean()) if len(d) else 0.0, float(still[:150].mean()) if len(d) else 0.0
    bad = [r for r in runs if r['dur'] > STILL_MAX + 1e-9 and r['out'] > STOP_SLACK]
    long_ok = [r for r in runs if r['dur'] > STILL_MAX + 1e-9 and r['out'] <= STOP_SLACK]
    listed = [r for r in runs if r['dur'] >= STILL_LIST - 1e-9]
    lst = '；'.join(f'{fmt_t(r["s"])}–{fmt_t(r["e"])}（{r["dur"]:.1f} 秒，{"/".join(r["ids"])}，{r["where"]}）' for r in listed) or '没有'
    base = f'全片静止 {share * 100:.0f}%，前 15 秒 {share15 * 100:.0f}%，最长 {longest:.1f} 秒'
    if bad:
        add('FAIL', '整幅静止 > 1.5 秒不在【停】里',
            '；'.join(f'{fmt_t(r["s"])}–{fmt_t(r["e"])}（{r["dur"]:.1f} 秒，停外 {r["out"]:.1f} 秒，{"/".join(r["ids"])}）' for r in bad) + f'。{base}')
    else:
        extra = f'；{len(long_ok)} 处超过 1.5 秒但都在【停】里' if long_ok else ''
        add('PASS', '整幅静止 ≤ 1.5 秒（【停】除外）', f'{base}{extra}')
    add('PASS', '0.5 秒以上的静止（只列出）', f'{len(listed)} 处：{lst}' + ('（都不超过 1.5 秒）' if listed and not bad and not long_ok else ''))
    # 突变
    med = float(np.median(d)) if len(d) else 0.0
    thr = max(JUMP_RATIO * med, JUMP_FLOOR)
    jumps, i = [], 0
    bounds = [b['t0'] for b in beats[1:]]
    evs = []                       # (起, 止, 名字)：两个数的列表当一段，其余每个数当一个时刻
    for b in beats:
        for k, val in (b['raw'].get('ev_s') or {}).items():
            if k == 'slipIndex':
                continue
            xs = [x for x in (val if isinstance(val, list) else [val]) if isinstance(x, (int, float))]
            if len(xs) == 2 and isinstance(val, list):
                evs.append((xs[0], xs[1], f'{b["id"]}.{k}'))
            else:
                evs.extend((x, x, f'{b["id"]}.{k}') for x in xs)

    def near_events(s, e):
        out = [n for a_, b_, n in evs if a_ - 0.3 <= e and b_ + 0.2 >= s]
        if not out:                # 附近没有，就报所在拍里最近开始的那个（推镜这种只写了起点的）
            b = next((b for b in beats if b['t0'] <= s < b['t1']), None)
            if b:
                cand = [(a_, n) for a_, _, n in evs if n.startswith(b['id'] + '.') and a_ <= s]
                if cand:
                    a_, n = max(cand)
                    out = [f'{n}（{a_:.2f} 起）']
        return list(dict.fromkeys(out))[:3]

    def near_bound(t0, t1):
        return next((x for x in bounds if t0 - BOUNDARY_TOL <= x <= t1 + BOUNDARY_TOL), None)
    while i < len(d):
        if d[i] > thr and thr > 0:
            j = i
            while j + 1 < len(d) and (d[j + 1] > thr or (j + 2 < len(d) and d[j + 2] > thr)):
                j += 1             # 中间只隔一格没过线的，算同一处
            j = max(k for k in range(i, j + 1) if d[k] > thr)
            s, e = i / 10, (j + 1) / 10
            pk = i + int(np.argmax(d[i:j + 1]))
            nb = near_bound(s, s + 0.1)                 # 起头落在边界上
            if nb is None:
                nb = near_bound(pk / 10, (pk + 1) / 10)  # 或者最猛的那一格落在边界上
            jumps.append(dict(s=s, e=e, peak=float(d[pk]), peak_t=(pk + 1) / 10, onb=nb is not None, nb=nb,
                              ids=beats_over(s, e), near=near_events(s, e) if nb is None else near_events(s, s + 0.1)))
            i = j + 1
        else:
            i += 1
    offb = [j for j in jumps if not j['onb']]
    jdesc = lambda j: (f'{fmt_t(j["s"])}–{fmt_t(j["e"])}（峰 {j["peak"]:.1f}，{"/".join(j["ids"])}'
                       + (f'，附近事件 {"、".join(j["near"])}' if j['near'] else '') + '）')
    head = f'帧差中位数 {med:.2f}，突变线 {thr:.2f}（' + ('4 倍' if thr > JUMP_FLOOR else f'4 倍不到 {JUMP_FLOOR:g}，用下限') + f'）；共 {len(jumps)} 处，{len(jumps) - len(offb)} 处在拍的边界上'
    if offb:
        add('WARN', '突变不在拍的边界上', f'{head}，{len(offb)} 处不在：' + '；'.join(jdesc(j) for j in offb) + '。计划好的打点可以留，没计划的要查')
    else:
        add('PASS', '突变都在拍的边界上', head)

    # —— 3 字幕 ——
    sruns = subtitle_runs(tl, beats, fps_tl)
    total = sum(r['chars'] for r in sruns)
    cps = total / dur_tl if dur_tl else 0
    has_title = any(r['title'] for r in sruns)
    add('PASS' if cps <= MAX_CPS + 1e-9 else 'FAIL', '字幕平均每秒字数',
        f'{total} 字 ÷ {dur_tl:.2f} 秒 = {cps:.2f}（上限 {MAX_CPS:g}；口径：汉字算 1，一串数字算 1，'
        + ('0 秒大题算字）' if has_title else '时间表里没有 0 秒大题）'))
    # 最密的 5 秒（字摊到它挂着的时间里）
    best, best_t, t = 0.0, 0.0, 0.0
    while t + 5 <= dur_tl + 1e-9:
        w = sum(r['chars'] * max(0.0, min(r['t1'], t + 5) - max(r['t0'], t)) / max(1e-9, r['t1'] - r['t0']) for r in sruns)
        if w > best:
            best, best_t = w, t
        t = round(t + 0.1, 1)
    # 无字拍
    title_t = next((r['t0'] for r in sruns if r['title']), None)
    new_ids = set()
    for r in sruns:
        if r['title']:
            continue
        new_ids.add(r['ids'][0])
        for tp, _ in r['pcs']:
            if tp > r['t0'] + 1e-6:
                b = next((b for b in beats if b['t0'] - 1e-6 <= tp < b['t1'] - 1e-6), None)
                if b:
                    new_ids.add(b['id'])
    if title_t is not None:
        b = next((b for b in beats if b['t0'] - 1e-6 <= title_t < b['t1'] - 1e-6), None)
        if b:
            new_ids.add(b['id'])
    for b in beats:
        b['new'] = b['id'] in new_ids
    if beats and beats[-1]['stop']:
        beats[-1]['new'] = False           # 结尾【停】算无字拍
    no_text = [b for b in beats if not b['new']]
    nshare = len(no_text) / len(beats) if beats else 0
    ntime = sum(b['t1'] - b['t0'] for b in no_text) / dur_tl if dur_tl else 0
    add('PASS' if nshare >= MIN_NO_TEXT - 1e-9 else 'FAIL', '无字拍比例',
        f'{len(no_text)}/{len(beats)}（{nshare * 100:.0f}%，下限 {MIN_NO_TEXT * 100:.0f}%），占时长 {ntime * 100:.1f}%：'
        + '、'.join(f'{b["id"]}（{b["t0"]:.1f}）' for b in no_text)
        + ('。正好卡在下限，没有余量' if abs(nshare - MIN_NO_TEXT) < 1e-9 else ''))
    bad_read = [r for r in sruns if not r['ok']]
    tight = sorted(sruns, key=lambda r: r['t1'] - r['finish'])[:3]
    tdesc = '；'.join(f'“{r["text"][:12]}”要 {r["finish"] - r["t0"]:.2f} 秒、有 {r["have"]:.2f} 秒' for r in tight)
    if bad_read:
        add('FAIL', '每拍按每秒 6.5 字读得完',
            '读不完：' + '；'.join(f'{"/".join(r["ids"])} “{r["text"]}” {r["chars"]} 字，读完要到 {r["finish"]:.2f} 秒，'
                                  f'这句 {r["t1"]:.2f} 秒就没了（差 {r["finish"] - r["t1"]:.2f} 秒）' for r in bad_read))
    else:
        add('PASS', '每拍按每秒 6.5 字读得完', f'{len(sruns)} 句全部读得完；最紧的三句：{tdesc}')
    add('PASS', '最密的 5 秒', f'{best_t:.1f}–{best_t + 5:.1f} 秒，每秒 {best / 5:.2f} 字（只列出来看，没有上限）')
    # 和时间表自带的统计对一下
    ck = (tl.get('stats') or {}).get('checklist')
    if ck:
        diffs = []
        if ck.get('chars') is not None and ck['chars'] != total:
            diffs.append(f'字数 {ck["chars"]}≠{total}')
        if ck.get('per_s') is not None and abs(ck['per_s'] - round(cps, 2)) > 0.01:
            diffs.append(f'每秒 {ck["per_s"]}≠{cps:.2f}')
        if ck.get('no_text') is not None and ck['no_text'] != len(no_text):
            diffs.append(f'无字拍 {ck["no_text"]}≠{len(no_text)}')
        if diffs:
            add('WARN', '时间表自带的统计', '和脚本算的不一样：' + '，'.join(diffs) + '（时间表的 stats 可能没重新生成，或口径不同）')
        else:
            add('PASS', '时间表自带的统计', f'和脚本算的一致（{ck.get("chars")} 字、每秒 {ck.get("per_s")}、无字拍 {ck.get("no_text")}/{ck.get("of")}）')
    # 字号
    subs, others, first, LH, LW = text_sizes(tl)
    short = min(LW, LH) if (LW and LH) else None
    k = short / 1080 if short else 1.0
    if subs:
        nm, mn = min(subs, key=lambda x: x[1])
        add('PASS' if mn >= SUB_MIN_PX * k - 1e-9 else 'FAIL', '字幕字号',
            f'最小 {mn:g} px（{nm}；下限 {SUB_MIN_PX * k:g} px，按 {short or 1080} 短边折算）；全部：'
            + '、'.join(f'{n} {x:g}' for n, x in subs))
    else:
        add('WARN', '字幕字号', '时间表里没有字号（layout.sub.size 或每拍的 sub.size），查不了；要查就在时间表里写字号')
    if first:
        nm, mn = min(first, key=lambda x: x[1])
        add('PASS' if mn >= FIRST_MIN_PX * k - 1e-9 else 'FAIL', '第 0 秒的字号', f'{mn:g} px（{nm}；下限 {FIRST_MIN_PX * k:g} px）')
    if others:
        small = [(n, x) for n, x in others if x < SUB_MIN_PX * k]
        if small:
            add('WARN', '其他字的字号', f'小于 {SUB_MIN_PX * k:g} px 的：' + '、'.join(f'{n} {x:g}' for n, x in small))
        else:
            add('PASS', '其他字的字号', f'{len(others)} 项都 ≥ {SUB_MIN_PX * k:g} px，最小 {min(x for _, x in others):g} px（{min(others, key=lambda x: x[1])[0]}）')

    # —— 4 声音 ——
    sfx = collect_sfx(tl, beats, fps_tl)
    events, ev_ok = None, False          # events：传了 --sfx 才有
    if a.sfx:
        try:
            events, ev_probs = load_events(a.sfx, fps_tl, beats, nf)
            ev_ok = True
        except Exception as ex:
            add('FAIL', '音效事件表', f'读不了 {a.sfx}：{ex}')
            events = []
        if ev_ok:
            nkey = sum(e['key'] for e in events)
            if ev_probs:
                add('WARN', '音效事件表', f'{len(events)} 条，key {nkey} 条；{len(ev_probs)} 处对不上：' + '；'.join(ev_probs))
            else:
                add('PASS', '音效事件表', f'{len(events)} 条，key {nkey} 条；帧号、秒数、拍号都对得上')
            # 和画面突变对齐（不用声音也能查）
            ons = onsets(local_change(a.video, v['w'], v['h']))
            for e in events:
                near = [k for k in ons if abs(k - e['frame']) <= EV_SEARCH]
                k = min(near, key=lambda k: (abs(k - e['frame']), -ons[k])) if near else None
                e.update(onset=k, off=None if k is None else k - e['frame'], rise=ons.get(k))
            keys = [e for e in events if e['key']]

            def off_desc(e):
                if e['off'] is None:
                    return f'前后 {EV_SEARCH} 帧内没有画面突变'
                if e['off'] == 0:
                    return f'画面突变就在第 {e["onset"]} 帧'
                return f'画面突变在第 {e["onset"]} 帧，声音{"早" if e["off"] > 0 else "晚"} {abs(e["off"])} 帧'
            if not keys:
                add('WARN', 'key 音效', '事件表里没有 key=true 的点，1–4 kHz 和对齐都没查')
            else:
                bad_al = [e for e in keys if e['off'] is None or abs(e['off']) > EV_ALIGN]
                if bad_al:
                    add('WARN', 'key 音效和画面突变对齐', f'{len(keys)} 个 key 点，{len(bad_al)} 个差超过 {EV_ALIGN} 帧：'
                        + '；'.join(f'{e["name"]}（{e["beat"]}，第 {e["frame"]} 帧）{off_desc(e)}' for e in bad_al)
                        + '。声音故意先到的（剪辑认知第 7 条）可以留')
                else:
                    add('PASS', 'key 音效和画面突变对齐', f'{len(keys)} 个 key 点都在画面突变 ±{EV_ALIGN} 帧内')
    au = None
    beat_audio = {}
    sfx_rows = []
    if not v['audio']:
        add('WARN' if a.preview else 'FAIL', '音轨', '没有音轨' + ('（预演，按 --preview 只报 WARN）' if a.preview else ''))
        if a.sfx:
            if ev_ok:
                keys = [e for e in events if e['key']]
                add('WARN', 'key 音效 1–4 kHz', f'没有音轨，查不了 {len(keys)} 个 key 点：'
                    + '、'.join(f'{e["name"]}（第 {e["frame"]} 帧）' for e in keys))
        elif sfx:
            add('WARN', '关键音效 1–4 kHz', f'没有音轨，查不了。时间表里标了音效的 {len(sfx)} 处：'
                + '、'.join(f'{bid} {n} {t:.2f} 秒' for bid, n, t in sfx))
        else:
            add('WARN', '关键音效 1–4 kHz', '没有音轨，查不了；时间表里也没标音效')
        placeholder(os.path.join(a.out, '响度曲线.png'), '没有音轨，画不出响度曲线')
    else:
        add('PASS', '音轨', v['audio'][:80])
        au = loudness(a.video)
        I, TP = au['I'], au['TP']
        if I is None or not np.isfinite(I) or I < -60:
            add('FAIL', '整条响度', f'音轨基本是静音（I = {I} LUFS）')
        else:
            dev = I - a.lufs
            lv = 'PASS' if abs(dev) <= a.lufs_tol + 1e-9 else 'WARN' if abs(dev) <= a.lufs_tol + 1 + 1e-9 else 'FAIL'
            add(lv, '整条响度', f'{I:.1f} LUFS（目标 {a.lufs:g} ± {a.lufs_tol:g}，差 {dev:+.1f}）；响度范围 LRA {au["LRA"]} LU')
        if TP is None:
            add('WARN', '真峰值', '读不出')
        else:
            add('PASS' if TP <= a.peak + 1e-9 else 'FAIL', '真峰值', f'{TP:.1f} dBTP（上限 {a.peak:g}）')
        sr = 48000
        x = pcm(a.video, sr)
        ref = I if (I is not None and np.isfinite(I) and I > -60) else a.lufs
        for b in beats:
            seg = x[int(b['t0'] * sr):int(b['t1'] * sr)]
            if len(seg) > 0:
                beat_audio[b['id']] = band_levels(seg, sr)
        if len(x):
            bd, fd, bs, ls = band_levels(x, sr)
            add('PASS', '整条 1–4 kHz', f'电平 {bd:.1f} dBFS，占全频能量 {bs * 100:.0f}%，250 Hz 以下占 {ls * 100:.0f}%（只列出来看）')
        if a.sfx:
            if ev_ok:
                for e in events:          # key 点前后 ±2 帧
                    seg = x[max(0, int((e['frame'] - EV_WIN) / v['fps'] * sr)):int((e['frame'] + EV_WIN + 1) / v['fps'] * sr)]
                    if len(seg) == 0:
                        e.update(bd=None, bs=None, ls=None, loud=False)
                        continue
                    bd, fd, bs, ls = band_levels(seg, sr)
                    e.update(bd=bd, bs=bs, ls=ls, loud=bd >= ref - SFX_REL_OK)
                keys = [e for e in events if e['key']]
                if keys:
                    bad_en = [e for e in keys if not e['loud']]
                    line = f'明显 = 第 N±{EV_WIN} 帧的 1–4 kHz 电平 ≥ 整条响度 − {SFX_REL_OK:g} dB（{ref - SFX_REL_OK:.0f} dBFS）。'
                    if bad_en:
                        add('FAIL', 'key 音效 1–4 kHz', line + f'{len(keys)} 个 key 点，{len(bad_en)} 个没有明显能量：'
                            + '；'.join(f'{e["name"]}（{e["beat"]}，第 {e["frame"]} 帧）'
                                       + (f'{e["bd"]:.1f} dBFS，250 Hz 以下占 {e["ls"] * 100:.0f}%' if e['bd'] is not None else '在音轨外')
                                       for e in bad_en))
                    else:
                        add('PASS', 'key 音效 1–4 kHz', line + f'{len(keys)} 个 key 点都有，最弱的是 '
                            + (lambda e: f'{e["name"]}（{e["bd"]:.1f} dBFS）')(min(keys, key=lambda e: e['bd'])))
        else:
            for bid, n, t in sfx:
                seg = x[max(0, int((t + SFX_WIN[0]) * sr)):int((t + SFX_WIN[1]) * sr)]
                pre = x[max(0, int((t - 0.35) * sr)):max(0, int((t - 0.05) * sr))]
                if len(seg) == 0:
                    sfx_rows.append((bid, n, t, None, None, None, None, 'FAIL', '时间点在音轨外'))
                    continue
                bd, fd, bs, ls = band_levels(seg, sr)
                rise = bd - band_levels(pre, sr)[0] if len(pre) > 0 else None
                lv = 'PASS' if bd >= ref - SFX_REL_OK else 'WARN' if bd >= ref - SFX_REL_WEAK else 'FAIL'
                word = {'PASS': '明显', 'WARN': '弱', 'FAIL': '几乎没有'}[lv]
                sfx_rows.append((bid, n, t, bd, bs, ls, rise, lv, word))
            if not sfx:
                add('WARN', '关键音效 1–4 kHz', '时间表里没标音效（拍里的 sfx 字段，或 ev 里 whoosh、ding 一类名字），也没传 --sfx 事件表，关键拍查不了；每拍的 1–4 kHz 见明细')
            else:
                worst = {'PASS': 0, 'WARN': 1, 'FAIL': 2}
                lv = max((r[7] for r in sfx_rows), key=lambda s: worst[s])
                desc = '；'.join(f'{r[0]} {r[1]} {r[2]:.2f} 秒：{r[8]}' + (f'（{r[3]:.1f} dBFS）' if r[3] is not None else '') for r in sfx_rows)
                add(lv, '关键音效 1–4 kHz', f'（从时间表找的）明显 = 电平 ≥ 整条响度 − {SFX_REL_OK:g} dB（{ref - SFX_REL_OK:.0f} dBFS）。{desc}')
        # 响度曲线
        bars = []
        for b in beats:
            if b['id'] in beat_audio:
                bars.append((b['t0'], b['t1'], beat_audio[b['id']][0], C_AQUA))
        if a.sfx:
            marks = [(e['t'], C_RED if e['key'] else '#9b9a93') for e in (events or [])]
            mark_note = '红三角 = 事件表的 key 点，灰三角 = 其他事件'
        else:
            marks = [(t, C_RED) for _, _, t in sfx]
            mark_note = '红三角 = 时间表里的音效'
        panels = [dict(ylabel='响度 LUFS', ymin=-60, ymax=0, yticks=[-60, -40, -30, -23, -14, -6, 0],
                       series=[(au['t'], np.clip(au['M'], -70, 0), '#9fc3ee', 2), (au['t'], np.clip(au['S'], -70, 0), C_BLUE, 3)],
                       hlines=[(a.lufs, C_ORANGE, f'目标 {a.lufs:g} LUFS')]),
                  dict(ylabel='1–4 kHz\n每拍 dBFS', ymin=-80, ymax=0, yticks=[-80, -60, -40, -20, 0], bars=bars, marks=marks,
                       hlines=[(ref - SFX_REL_OK, C_ORANGE, f'“明显”线 {ref - SFX_REL_OK:.0f} dBFS')])]
        chart(os.path.join(a.out, '响度曲线.png'), f'响度：浅蓝 = 瞬时（0.4 秒），深蓝 = 短时（3 秒）；下面是每拍 1–4 kHz 电平，{mark_note}', tmax,
              panels, beats, foot=f'整条 {au["I"]} LUFS，真峰值 {au["TP"]} dBTP。灰底 = 【停】拍。')

    # —— 5 出图 ——
    fl = font(20)
    beat_of = lambda fi: next((b['id'] for b in beats if b['f0'] <= fi < b['f1']), '')
    grid = [(frames[i], [f'{i / v["fps"]:.2f}s  第 {i} 帧  {beat_of(i)}']) for i in grid_idx if i in frames]
    if grid:
        contact(os.path.join(a.out, '对照_12格.png'), grid, 4, 480, 30, fl)
    items = []
    for b in beats:
        fi = min(b['f0'], nf - 1)
        if fi in frames:
            sub = '／'.join(seg_text(x) for x in b['lines'])
            sub = (sub[:20] + '…') if len(sub) > 20 else sub
            if not sub and title_t is not None and b['t0'] - 1e-6 <= title_t < b['t1'] - 1e-6:
                sub = '（0 秒大题）' + (tl.get('question') or {}).get('text', '')
            items.append((frames[fi], [f'{b["id"]}  {b["t0"]:.2f}s{"  【停】" if b["stop"] else ""}', sub if b['new'] else ('（无新字）' + sub[:12] if sub else '（无字）')]))
    if items:
        horiz = v['w'] >= v['h']
        contact(os.path.join(a.out, '每拍第一帧.png'), items, 5 if horiz else 8, 400 if horiz else 240, 56, font(18))
    if len(d):
        tt = np.arange(1, len(d) + 1) / 10
        spans = [(r['s'], r['e'], '#fbd9c9' if r['out'] > STOP_SLACK else '#d5ecdf') for r in listed]
        spans += [(r['s'], r['e'], '#f5a3a3') for r in bad]
        ymax = max(float(np.percentile(d, 99)) * 1.15, thr * 1.5, 1.0)
        chart(os.path.join(a.out, '帧差曲线.png'),
              '帧差（每 0.1 秒一格，beats.py 同一算法）：橙底 = 0.5 秒以上的静止（不在【停】里），绿底 = 在【停】里，红底 = 超 1.5 秒；三角 = 突变（蓝在拍边界，红不在）',
              tmax,
              [dict(ylabel='帧差', ymin=0, ymax=ymax, yticks=[0, round(thr, 2), round(ymax / 2, 1), round(ymax, 1)],
                    series=[(tt, d, C_BLUE, 2)], spans=spans, hlines=[(thr, C_ORANGE, f'突变线 {thr:.2f}')],
                    marks=[(j['peak_t'], C_BLUE if j['onb'] else C_RED) for j in jumps]),
               dict(ylabel='帧差\n放大 0–2', ymin=0, ymax=2, yticks=[0, STILL_DIFF, 0.5, 1, 1.5, 2],
                    series=[(tt, d, C_BLUE, 2)], spans=spans, hlines=[(STILL_DIFF, C_RED, f'静止线 {STILL_DIFF}')])],
              beats, foot=f'{base}。灰底 = 【停】拍，竖线 = 拍的边界。')

    # —— 6 报告 ——
    order = {'FAIL': 0, 'WARN': 1, 'PASS': 2}
    cnt = {k: sum(1 for r in res if r[0] == k) for k in order}
    L = []
    L.append('# 出片自查报告\n')
    L.append(f'- 视频：`{os.path.abspath(a.video)}`（{v["w"]}×{v["h"]}，{v["fps"]:g} fps，{nf} 帧 = {nf / v["fps"]:.2f} 秒，'
             + ('有音轨' if v['audio'] else '没有音轨') + '）')
    L.append(f'- 时间表：`{os.path.abspath(a.timeline)}`（{len(beats)} 拍，{nf_tl} 帧，{len(stops)} 拍标了【停】）')
    L.append(f'- 跑的时间：{datetime.datetime.now():%Y-%m-%d %H:%M}；参数：响度目标 {a.lufs:g} ± {a.lufs_tol:g} LUFS，真峰值 ≤ {a.peak:g} dBTP'
             + ('，预演模式（--preview）' if a.preview else '') + (f'，音效事件表 `{a.sfx}`' if a.sfx else ''))
    L.append(f'- 结果：**FAIL {cnt["FAIL"]} 项，WARN {cnt["WARN"]} 项，PASS {cnt["PASS"]} 项**\n')
    for lvl in ('FAIL', 'WARN', 'PASS'):
        L.append(f'## {lvl}\n')
        rows = [r for r in res if r[0] == lvl]
        L.extend(f'- **{it}**：{msg}' for _, it, msg in rows) if rows else L.append('- 没有')
        L.append('')
    L.append('---\n\n## 明细\n')
    L.append(f'### 静止段（≥ {STILL_LIST} 秒，帧差 < {STILL_DIFF}）\n')
    if listed:
        L.append('| 起–止（秒） | 长 | 跨哪几拍 | 【停】 |\n|---|---|---|---|')
        L.extend(f'| {fmt_t(r["s"])}–{fmt_t(r["e"])} | {r["dur"]:.1f} | {"、".join(r["ids"])} | {r["where"]} |' for r in listed)
    else:
        L.append('没有。')
    L.append(f'\n### 突变（帧差 > {thr:.2f}，中位数 {med:.2f} 的 4 倍，下限 {JUMP_FLOOR:g}；连着的几格合成一处，中间隔一格没过线的也算一处）\n')
    if jumps:
        L.append('| 起–止（秒） | 峰值 | 跨哪几拍 | 拍的边界 | 附近事件 |\n|---|---|---|---|---|')
        L.extend(f'| {fmt_t(j["s"])}–{fmt_t(j["e"])} | {j["peak"]:.1f} | {"、".join(j["ids"])} | '
                 + (f'在（{j["nb"]:.2f}）' if j['onb'] else '**不在**') + f' | {"、".join(j["near"])} |' for j in jumps)
    else:
        L.append('没有。')
    L.append('\n### 每拍字幕（时间按帧号换算；读字按每秒 6.5 字，同一句连挂几拍按整段算）\n')
    L.append('| 拍 | 起–止（秒） | 【停】 | 新字 | 字幕 | 字数 | 要读 | 有 | 读完 |\n|---|---|---|---|---|---|---|---|---|')
    tr0 = next((r for r in sruns if r['title']), None)
    run_of = {}
    for r in sruns:
        for bid in r['ids']:
            run_of.setdefault(bid, r)
    for b in beats:
        r = run_of.get(b['id'])
        first_of_run = r is not None and r['ids'][0] == b['id']
        txt = '／'.join(seg_text(x) for x in b['lines'])
        if not txt and tr0 is not None and b['t0'] - 1e-6 <= tr0['t0'] < b['t1'] - 1e-6:
            txt = f'（0 秒大题）{tr0["text"].replace("（大题）", "")}'
        L.append(f'| {b["id"]} | {b["t0"]:.2f}–{b["t1"]:.2f} | {"停" if b["stop"] else ""} | {"有" if b["new"] else "—"} | {txt or "（无）"} | '
                 + (f'{r["chars"]} | {r["finish"] - r["t0"]:.2f} | {r["have"]:.2f} | {"✓" if r["ok"] else "✗"} |' if first_of_run
                    else ('同上一句 | | | |' if r else ' | | | |')))
    tr = next((r for r in sruns if r['title']), None)
    if tr:
        L.append(f'\n0 秒大题“{tr["text"]}”：{tr["chars"]} 字，{tr["t0"]:.2f}–{tr["t1"]:.2f} 秒，要读 {tr["need"]:.2f} 秒，'
                 + ('读得完。' if tr['ok'] else '读不完。'))
    L.append('\n### 每拍声音（1–4 kHz）\n')
    if beat_audio:
        L.append('| 拍 | 起–止（秒） | 1–4 kHz 电平 | 全频电平 | 1–4 kHz 占比 | 250 Hz 以下占比 |\n|---|---|---|---|---|---|')
        for b in beats:
            if b['id'] in beat_audio:
                bd, fd, bs, ls = beat_audio[b['id']]
                L.append(f'| {b["id"]} | {b["t0"]:.2f}–{b["t1"]:.2f} | {bd:.1f} dBFS | {fd:.1f} dBFS | {bs * 100:.0f}% | {ls * 100:.0f}% |')
        if sfx_rows:
            L.append(f'\n关键音效（时间点前 {-SFX_WIN[0]:g} 秒到后 {SFX_WIN[1]:g} 秒）：\n')
            L.append('| 拍 | 音效 | 秒 | 1–4 kHz 电平 | 1–4 kHz 占比 | 250 Hz 以下占比 | 比前 0.3 秒高 | 判断 |\n|---|---|---|---|---|---|---|---|')
            for r in sfx_rows:
                if r[3] is None:
                    L.append(f'| {r[0]} | {r[1]} | {r[2]:.2f} | — | — | — | — | {r[8]} |')
                else:
                    L.append(f'| {r[0]} | {r[1]} | {r[2]:.2f} | {r[3]:.1f} dBFS | {r[4] * 100:.0f}% | {r[5] * 100:.0f}% | '
                             + (f'{r[6]:+.1f} dB' if r[6] is not None else '—') + f' | {r[8]} |')
    else:
        L.append('没有音轨。' + ('' if a.sfx else (f'时间表里标了音效的 {len(sfx)} 处：' + '、'.join(f'{bid} {n}（{t:.2f} 秒）' for bid, n, t in sfx) if sfx else '')))
    if a.sfx and ev_ok:
        L.append(f'\n### 音效事件表（`{os.path.abspath(a.sfx)}`）\n')
        L.append(f'key 点：第 N 帧前后 ±{EV_WIN} 帧的 1–4 kHz 电平；画面突变在前后 {EV_SEARCH} 帧里找（逐帧、8×6 块里变化最大的一块，'
                 f'比前两帧高出 {ONSET_RISE:g} 以上且翻倍算起点），差 = 突变帧 − 事件帧，正数是声音先到。非 key 的只列出，不判。\n')
        if events:
            L.append('| 事件 | 拍 | 帧 | 秒 | key | 1–4 kHz（±2 帧） | 250 Hz 以下占比 | 能量 | 最近的画面突变 | 差（帧） | 对齐 |\n|---|---|---|---|---|---|---|---|---|---|---|')
            for e in events:
                bd = e.get('bd')
                en = '—' if 'bd' not in e else ('在音轨外' if bd is None else ('明显' if e['loud'] else ('**没有**' if e['key'] else '弱')))
                al = '—' if not e['key'] else ('✓' if e['off'] is not None and abs(e['off']) <= EV_ALIGN else '**差太多**')
                L.append(f'| {e["name"]} | {e["beat"]} | {e["frame"]} | {e["t"]:.2f} | {"是" if e["key"] else ""} | '
                         + (f'{bd:.1f} dBFS | {e["ls"] * 100:.0f}% | ' if bd is not None else '— | — | ')
                         + f'{en} | ' + (f'第 {e["onset"]} 帧' if e['onset'] is not None else '没有') + ' | '
                         + (f'{e["off"]:+d}' if e['off'] is not None else '—') + f' | {al} |')
        else:
            L.append('事件表是空的。')
    L.append('\n### 出的图\n')
    L.append('- `对照_12格.png`：从第 0 帧到最后一帧均匀取 12 帧，标秒数、帧号、拍号。')
    L.append('- `每拍第一帧.png`：每拍第一帧，标拍号、起始秒、【停】、这一拍的字幕（没有新字的标“无新字”）。')
    L.append('- `帧差曲线.png`：上面整幅，下面放大到 0–2 看静止；`diff.txt` 是同一组数（秒、帧差），格式和 beats.py 一样。')
    L.append('- `响度曲线.png`：瞬时、短时响度和每拍 1–4 kHz 电平；没有音轨时只有一行字。')
    with open(os.path.join(a.out, '报告.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print(f'FAIL {cnt["FAIL"]}  WARN {cnt["WARN"]}  PASS {cnt["PASS"]}  → {os.path.join(a.out, "报告.md")}')
    for lvl, it, msg in sorted(res, key=lambda r: order[r[0]]):
        if lvl != 'PASS':
            print(f'{lvl}  {it}：{msg[:160]}')
    sys.exit(1 if cnt['FAIL'] else 0)


if __name__ == '__main__':
    main()
