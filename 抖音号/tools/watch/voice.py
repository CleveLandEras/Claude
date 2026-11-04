"""粗测一段音频里有没有人声。

做法：取 300–3400 Hz 语音频段的能量包络（100 Hz 采样），每 4 秒一段，
看包络在 3–7 Hz（音节速率）上的调制占比。说话一秒四五个音节，这一段会高；
持续的音乐低。另给“能量谷”占比：说话有大量音节间的停顿。
用法：python -I voice.py 音频文件
"""
import subprocess
import sys

import numpy as np

FFMPEG = "/Users/decheng.huang/Documents/dy/.venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"
SR = 16000


def load(path):
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def main(path):
    x = load(path)
    win, hop = 400, 160
    n = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    frames = x[idx] * np.hanning(win)
    spec = np.abs(np.fft.rfft(frames, n=512)) ** 2
    freqs = np.fft.rfftfreq(512, 1 / SR)
    band = spec[:, (freqs >= 300) & (freqs <= 3400)].sum(1)
    total = spec.sum(1) + 1e-12
    env = band  # 100 Hz
    seg = 400  # 4 秒
    mods, valleys, loud = [], [], []
    for s in range(0, len(env) - seg + 1, seg):
        e = env[s:s + seg]
        if e.mean() < 1e-7:
            mods.append(0.0); valleys.append(0.0); loud.append(0.0)
            continue
        le = np.log10(e + 1e-9)
        le = le - le.mean()
        m = np.abs(np.fft.rfft(le * np.hanning(seg))) ** 2
        mf = np.fft.rfftfreq(seg, 1 / 100)
        num = m[(mf >= 3) & (mf <= 7)].sum()
        den = m[(mf >= 0.5) & (mf <= 20)].sum() + 1e-12
        mods.append(num / den)
        med = np.median(e)
        valleys.append(float((e < 0.1 * med).mean()))
        loud.append(float(10 * np.log10(e.mean() + 1e-12)))
    mods = np.array(mods)
    voiced = mods > 0.33
    print(f"时长 {len(x)/SR:.1f}s  分段 {len(mods)}")
    print(f"音节调制 中位 {np.median(mods):.2f}  P75 {np.percentile(mods,75):.2f}")
    print(f"像人声的段占比 {voiced.mean():.0%}")
    print(f"能量谷占比 中位 {np.median(valleys):.2f}")
    print(f"语音频段占总能量 {float((band/total).mean()):.2f}")
    line = "".join("█" if v else "·" for v in voiced)
    print("逐段（每格 4 秒，█=像人声）：")
    for i in range(0, len(line), 60):
        print(f"  {i*4//60:>3}分 {line[i:i+60]}")


if __name__ == "__main__":
    main(sys.argv[1])
