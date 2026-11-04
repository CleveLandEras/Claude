"""把一条视频压成几张拼图，用最少的图看完整条片子。

做法：每秒抽一帧，和上一张留下的帧比（缩成 64×36 灰度，平均差超过阈值才留），
画面或字幕变了才留，最多隔 8 秒强制留一张。留下的帧缩到 640 宽，3×3 一页，
左上角印时间。页数超过上限时自动提高阈值重来。
用法：.venv/bin/python -I tools/watch/sheets.py 视频文件 输出目录 [最多几页，默认 8]
输出：输出目录/sheet_01.png …，并打印每页的时间范围。
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

FFMPEG = "/Users/decheng.huang/Documents/dy/.venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"
COLS, ROWS, W = 3, 3, 640


def extract(video, tmp):
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", video, "-vf",
                    f"fps=1,scale={W}:-2,format=yuvj420p", "-q:v", "4",
                    os.path.join(tmp, "%05d.jpg")], check=True)
    return sorted(f for f in os.listdir(tmp) if f.endswith(".jpg"))


def pick(tmp, files, thr):
    keep, last, last_t = [], None, -99
    for f in files:
        t = int(f[:-4]) - 1
        g = np.asarray(Image.open(os.path.join(tmp, f)).convert("L").resize((64, 36)), dtype=np.float32)
        if last is None or np.abs(g - last).mean() > thr or t - last_t >= 8:
            keep.append((t, f))
            last, last_t = g, t
    return keep


def main(video, out, max_pages=8):
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        files = extract(video, tmp)
        thr = 4.0
        keep = pick(tmp, files, thr)
        while len(keep) > max_pages * COLS * ROWS and thr < 60:
            thr *= 1.5
            keep = pick(tmp, files, thr)
        h = Image.open(os.path.join(tmp, files[0])).size[1]
        per = COLS * ROWS
        for p in range(0, len(keep), per):
            chunk = keep[p:p + per]
            sheet = Image.new("RGB", (COLS * W + (COLS - 1) * 6, ROWS * h + (ROWS - 1) * 6), "white")
            dr = ImageDraw.Draw(sheet)
            for i, (t, f) in enumerate(chunk):
                x, y = (i % COLS) * (W + 6), (i // COLS) * (h + 6)
                sheet.paste(Image.open(os.path.join(tmp, f)), (x, y))
                dr.rectangle([x, y, x + 46, y + 16], fill="black")
                dr.text((x + 4, y + 3), f"{t // 60}:{t % 60:02d}", fill="white")
            name = os.path.join(out, f"sheet_{p // per + 1:02d}.png")
            sheet.save(name)
            print(name, f"{chunk[0][0]}s-{chunk[-1][0]}s")
        print(f"共 {len(files)} 秒，留 {len(keep)} 帧，阈值 {thr:.1f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
