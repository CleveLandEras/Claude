"""量观感：look.py 视频 [秒数=15]
每 0.5 秒取一帧（缩到 480 宽），打印几项和“好不好看”有关、能量出来的数：
  填满：亮度 > 40 的像素占比（画面有多少地方有东西）；
  亮度：平均亮度（0–255）；对比：亮度标准差；
  色彩：Hasler–Süsstrunk 彩色度（0 是黑白，>40 算鲜艳）；
  暖/冷：有颜色的像素里，橙金色（色相 15–65°）和蓝色（180–250°）各占多少；
  细节：平均梯度（纹理、笔触、颗粒多不多）。
看片的视频是下载来的，用 python -I 跑。"""
import io, subprocess, sys
import numpy as np
from PIL import Image
FF = '/Users/decheng.huang/Documents/dy/.venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
src = sys.argv[1]
T = float(sys.argv[2]) if len(sys.argv) > 2 else 15
raw = subprocess.run([FF, '-v', 'error', '-i', src, '-t', str(T), '-vf', 'fps=2,scale=480:-2', '-f', 'image2pipe', '-vcodec', 'png', '-'],
                     capture_output=True).stdout
PNG = b'\x89PNG\r\n\x1a\n'
rows = []
for p in raw.split(PNG)[1:]:
    im = Image.open(io.BytesIO(PNG + p)).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    rg, yb = r - g, 0.5 * (r + g) - b
    colorful = np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean())
    hsv = np.asarray(im.convert('HSV')).astype(np.float32)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2]
    col = (s > 0.25) & (v > 50)
    nc = max(1, col.sum())
    warm = ((h >= 15) & (h <= 65) & col).sum() / nc
    cool = ((h >= 180) & (h <= 250) & col).sum() / nc
    gy, gx = np.gradient(y)
    rows.append([(y > 40).mean(), y.mean(), y.std(), colorful, col.mean(), warm, cool, np.hypot(gx, gy).mean()])
m = np.array(rows).mean(axis=0)
print(f'填满 {m[0] * 100:.0f}%  亮度 {m[1]:.0f}  对比 {m[2]:.0f}  彩色度 {m[3]:.0f}  有色像素 {m[4] * 100:.0f}%  '
      f'其中暖 {m[5] * 100:.0f}% 冷 {m[6] * 100:.0f}%  细节 {m[7]:.1f}')
