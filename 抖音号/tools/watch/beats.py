"""量节拍：beats.py 视频 输出目录 [秒数=15]
抽 10 帧/秒的小灰度图算相邻帧差（找切点、量“静止”占比），再抽 2 帧/秒拼成带时间戳的对照图 sheet.png。
帧差写在 diff.txt（秒、帧差）；帧差 < 0.15 算这一刻画面完全不动。看片的视频是下载来的，用 python -I 跑。"""
import sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
FF = '/Users/decheng.huang/Documents/dy/.venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
src, out = sys.argv[1], sys.argv[2]
T = float(sys.argv[3]) if len(sys.argv) > 3 else 15
os.makedirs(out, exist_ok=True)
# 1) 10 fps 灰度 96x? 帧差
w = 96
raw = subprocess.run([FF, '-v', 'error', '-i', src, '-t', str(T), '-vf', f'fps=10,scale={w}:-2,format=gray', '-f', 'rawvideo', '-'],
                     capture_output=True).stdout
probe = subprocess.run([FF, '-v', 'error', '-i', src, '-t', '0.1', '-vf', f'scale={w}:-2', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
import io
h = Image.open(io.BytesIO(probe)).size[1]
n = len(raw) // (w * h)
fr = np.frombuffer(raw[:n * w * h], np.uint8).reshape(n, h, w).astype(np.float32)
d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
with open(os.path.join(out, 'diff.txt'), 'w') as fh:
    for i, v in enumerate(d):
        fh.write(f'{(i + 1) / 10:.1f}\t{v:.2f}\n')
# 2) 2 fps 对照图
big = subprocess.run([FF, '-v', 'error', '-i', src, '-t', str(T), '-vf', 'fps=2,scale=480:-2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
imgs, i = [], 0
PNG = b'\x89PNG\r\n\x1a\n'
parts = big.split(PNG)[1:]
for p in parts:
    imgs.append(Image.open(io.BytesIO(PNG + p)).convert('RGB'))
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 22)
iw, ih = imgs[0].size
cols = 6 if iw > ih else 10
rows = (len(imgs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (iw + 6), rows * (ih + 30)), 'white')
for k, im in enumerate(imgs):
    x, y = (k % cols) * (iw + 6), (k // cols) * (ih + 30)
    sheet.paste(im, (x, y + 28))
    ImageDraw.Draw(sheet).text((x + 4, y + 2), f'{k * 0.5:.1f}s', fill='black', font=font)
sheet.save(os.path.join(out, 'sheet.png'))
print(out, len(imgs), 'frames', sheet.size)
# 汇总：切点（帧差 > 8）、静止占比、最长连续静止
cuts = [f'{(i + 1) / 10:.1f}' for i, v in enumerate(d) if v > 8]
still = d < 0.15
run = best = 0
for s in still:
    run = run + 1 if s else 0
    best = max(best, run)
print(f'切点（帧差>8）：{" ".join(cuts)}')
print(f'静止占比 {still.mean() * 100:.0f}%，最长连续静止 {best / 10:.1f} 秒')
